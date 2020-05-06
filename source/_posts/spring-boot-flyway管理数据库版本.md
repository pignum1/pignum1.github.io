---
title: spring-boot flyway管理数据库版本
date: 2019-08-18 15:27:37
tags: [flyway ,spring boot ]
type: "categories"
categories: spring boot
---
# 使用flyway管理数据库版本
Flyway是一个简单开源数据库版本控制器（约定大于配置），主要提供migrate、clean、info、validate、baseline、repair等命令。它支持SQL（PL/SQL、T-SQL）方式和Java方式，支持命令行客户端等，还提供一系列的插件支持（Maven、Gradle、SBT、ANT等）。
更多用法详情，flyway的官方网站：https://flywaydb.org/，
因为我们项目是用的flyway来管理数据库版本的，这样子每次更新数据库设计的时候就能对比出表之间的变化，然后我也研究了下spring boot 和flyway的用法。我创建用的项目是gradle的多模块。如果你使用的是maven也可以当作参考
第一步当然是引入fayway的依赖
```
    // flyway
    compile group: 'org.flywaydb', name: 'flyway-core', version: '4.1.2
```
flyway的默认读取路径是resource的 db/migration,若果你的路径不一样，那就要在application.properties中写入 flyway.locations指明你的文件路径,在db/migration文件内创建文件 V1__Base_version.sql
```
DROP TABLE IF EXISTS user ;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(20) NOT NULL COMMENT '姓名',
  `age` int(5) DEFAULT NULL COMMENT '年龄',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
这个时候启动Application就能发现数据库中自动创建了实体表，如果你的数据中已经存在了表，只要加上flyway.baselineOnMigrate=true加上这句就阔以喽。
下面是flyway的一些常用配置，可以根据具体使用配置
```
## 设定 flyway 属性
flyway.enabled = true
# 启用或禁用 flyway
flyway.locations =classpath:/db.migration
# 设定 SQL 脚本的目录,多个路径使用逗号分隔, 比如取值为 classpath:db/migration,filesystem:/sql-migrations
flyway.baselineOnMigrate=true
# 如果指定 schema 包含了其他表,但没有 flyway schema history 表的话, 在执行 flyway migrate 命令之前, 必须先执行 flyway baseline 命令.
# 设置 spring.flyway.baseline-on-migrate 为 true 后, flyway 将在需要 baseline 的时候, 自动执行一次 baseline.
flyway.baselineVersion=1
# 指定 baseline 的版本号,缺省值为 1, 低于该版本号的 SQL 文件, migrate 的时候被忽略.
#spring.flyway.encoding=
# Encoding of SQL migrations (default: UTF-8)
flyway.table=flyway_schema_history_myapp
# 设定 flyway 的 metadata 表名, 缺省为 flyway_schema_history
flyway.outOfOrder=true
# 开发环境最好开启 outOfOrder, 生产环境关闭 outOfOrder .
#spring.flyway.schemas=
需要 flyway 管控的 schema list, 缺省的话, 使用的时 dbsource.connection直连上的那个 schema, 可以指定多个schema, 但仅会在第一个schema下建立 metadata 表, 也仅在第一个schema应用migration sql 脚本. 但flyway Clean 命令会依次在这些schema下都执行一遍.
```
# 第二种使用flyway的方法
项目结构如下图
![](/struct.png)
flyway在gradle中的使用。官方文档中有实例，这里我贴出我的代码,首先flyway的依赖和上面相同，然后再再根目录下创建gradle.properties文件，再里面配置数据源信息
```
//gradle.properties内
# ####################### flyway ##############################
flyway_driver=com.mysql.cj.jdbc.Driver
flyway_url=jdbc:mysql://localhost:3306/weixy?useSSL=false&serverTimezone=UTC
flyway_user=root
flyway_password=123456
```
然后在entity的模块的build中添加
```
apply plugin: 'org.springframework.boot'
apply plugin: 'org.flywaydb.flyway'
buildscript {
    repositories {
        //使用的仓库优先级
        mavenLocal()
        maven { url "http://maven.aliyun.com/nexus/content/groups/public" }
        maven { url "http://repo.spring.io/snapshot" }
        maven { url "http://repo.spring.io/milestone" }
        jcenter()
    }
    dependencies {
        classpath(group: 'org.flywaydb', name: 'flyway-gradle-plugin', version: "4.1.2")
        classpath("org.springframework.boot:spring-boot-gradle-plugin:1.4.5.RELEASE")
    }
}
flyway{
    driver = "${flyway_driver}"
    url = "$flyway_url"
    user = "$flyway_user"
    password = "$flyway_password"
    //flyway发布版本记录的表名称
    table = 'flyway_version'
    locations ='db/migration'
//    locations = 'db/migrations'
    baselineOnMigrate=true
    //
    //sqlMigrationPrefix = 'V'
    // 禁止flywayClean，在生产环境中非常重要
    cleanDisabled = false
}
```
这个时候刷新gradle ,点击flyway下的
![](/gradle.png)






