---
title: gradle 打包
date: 2020-01-13 13:49:49
tags:
---

``` groovy
	apply plugin: "java"
	//打包插件，不含第三方依赖jar
    apply plugin: "maven-publish"
    apply plugin: 'idea'

    version = '1.0.0'

    // JVM 版本号要求
    sourceCompatibility = 1.8
    targetCompatibility = 1.8

    // java编译的时候缺省状态下会因为中文字符而失败
    [compileJava, compileTestJava, javadoc]*.options*.encoding = 'UTF-8'

    repositories {
        mavenLocal()
        maven { url "http://maven.aliyun.com/nexus/content/groups/public" }
        mavenCentral()
        jcenter()
        maven { url "http://repo.spring.io/snapshot" }
        maven { url "http://repo.spring.io/milestone" }
        maven { url 'http://maven.springframework.org/release' }
        maven { url 'http://maven.springframework.org/milestone' }
    }

    jar {
        manifest {
            attributes("Implementation-Title": "Gradle")
        }
    }

    // 显示当前项目下所有用于 compile 的 jar.
    task listJars(description: 'Display all compile jars.') << {
        configurations.compile.each { File file -> println file.name }
    }

    gradle.projectsEvaluated {
        tasks.withType(JavaCompile) {
            options.compilerArgs << "-Xlint:unchecked" << "-Xlint:deprecation"
        }
    }


    task "create-dirs" << {
        sourceSets*.java.srcDirs*.each {
            it.mkdirs()
        }
        sourceSets*.resources.srcDirs*.each{
            it.mkdirs()
        }
    }

    ext {
        set('springCloudVersion', "Dalston.SR5")
    }

    dependencies {
//        compile group: 'org.springframework.boot', name: 'spring-boot-starter-data-jpa', version: '2.1.4.RELEASE'
        compile group: 'org.springframework.boot', name: 'spring-boot-starter-data-jpa', version: '2.2.2.RELEASE'
        compile group: 'org.springframework.boot', name: 'spring-boot-starter-web', version: '2.2.2.RELEASE'
        // https://mvnrepository.com/artifact/org.projectlombok/lombok
        compile group: 'org.projectlombok', name: 'lombok', version: '1.18.8'

    }

    //设置动态属性
    ext {
        //发布到仓库用户名
        publishUserName = "dawei"
        //发布到仓库地址
        publishUserPassword = "qq1235789"
        //仓库地址
        publishURL = "http://47.102.99.93:8081/repository/panghu/"

        apiBaseJarName = "base"
        apiBaseJarVersion = '0.0.1'
        builtBy = "gradle 1.9"
    }

    //jar包名称组成：[baseName]-[appendix]-[version]-[classifier].[extension]
//打包class文件
    task apiBaseJar(type:Jar){
        version apiBaseJarVersion
        baseName apiBaseJarName
        from sourceSets.main.output
        destinationDir file("$buildDir/api-libs")
        includes ['com/example/**']
        manifest {
            attributes 'packageName': apiBaseJarName, 'Built-By': builtBy,'Built-date': new Date().format('yyyy-MM-dd HH:mm:ss'),'Manifest-Version':version
        }
    }
//打包源码
    task apiBaseSourceJar(type:Jar){
        version apiBaseJarVersion
        baseName apiBaseJarName
        classifier "sources"
        from sourceSets.main.allSource
        destinationDir file("$buildDir/api-libs")
        includes ['com/example/**']
        manifest {
            attributes 'packageName': apiBaseJarName+'-sources', 'Built-By': builtBy,'Built-date': new Date().format('yyyy-MM-dd HH:mm:ss'),'Manifest-Version':version
        }
    }
//上传jar包
    publishing {
        publications {
            publishing.publications.create('apiBase', MavenPublication) {
                groupId 'base-core'
                artifactId apiBaseJarName
                version apiBaseJarVersion
                //同时上传class包和源码包
                artifacts = [apiBaseJar, apiBaseSourceJar]
            }
        }
        repositories {
            maven {
                url publishURL
                credentials {
                    username = publishUserName
                    password = publishUserPassword
                }
            }
        }
    }
```

