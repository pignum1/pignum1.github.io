---
title: spring-boot连接mongodb
date: 2019-08-18 00:47:48
tags: [mongodb ,spring boot ]
type: "categories"
categories: spring boot
---
# linux(centos7)安装mongodb
我是在linux获取安装包，可以去官网下载对应的安装包。官网地址:https://www.mongodb.com/download-center?jmp=nav#community
我是安装在目录路径为 /usr/local/momgodb 下。
首先切换路径
```
/usr/local/momgodb
//下载安装包
wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-4.0.0.tgz
//下载完成之后解压缩
tar zxvf mongodb-linux-x86_64-4.0.0.tgz
//解压后的文件名重命名为（mongodb），这个看你自己的喜好，可以不改
mv mongodb-linux-x86_64-4.0.0 mongodb
//修改环境的配置变量
vim /etc/profile
//先按i进入文本编辑的insert模式，编辑完成后先 esc退出编辑，再:wq保存编辑,编辑类容如下
#Mongodb
export PATH=/usr/local/mongodb/mongodb/bin:$PATH
export PATH USER LOGNAME MAIL HOSTNAME HISTSIZE HISTCONTROL
//保存完毕后，使配置文件生效
source /etc/profile

//创建数据库目录
 cd /usr/mongodb/mongodb
$ touch mongodb.conf
$ mkdir db
$ mkdir log
$ cd log
$ touch mongodb.log

//修改mongodb的启动配置
vim /usr/local/mongodb/mongodb/mongodb.conf
//再配置文件中添加一下内容
port=27017 #端口
dbpath= /usr/local/mongodb/mongodb/db #数据库存文件存放目录
logpath= /usr/local/mongodb/mongodb/log/mongodb.log #日志文件存放路径
logappend=true #使用追加的方式写日志
fork=true #以守护进程的方式运行，创建服务器进程
maxConns=100 #最大同时连接数
noauth=true #不启用验证
journal=true #每次写入会记录一条操作日志（通过journal可以重新构造出写入的数据）。
#即使宕机，启动时wiredtiger会先将数据恢复到最近一次的checkpoint点，然后重放后续的journal日志来恢复。
storageEngine=wiredTiger  #存储引擎有mmapv1、wiretiger、mongorocks
bind_ip = 0.0.0.0  #这样就可外部访问了，例如从win10中去连虚拟机中的MongoDB
//上述文件配置完成以后，就可以以这个配置文件来启动mongodb
 mongod --config /usr/local/mongodb/mongodb/mongodb.conf
```

## 设置mongondb的开启自启动
```
//切换目录，创建服务的方式开机自启动 
cd /lib/systemd/system
//编辑文件（这个时候会创建这个文件）
vi mongodb.service
//添加一下文件，注意安装的路径不要写错了
	[Unit]  
    Description=mongodb  
    After=network.target remote-fs.target nss-lookup.target  
  
    [Service]  
    Type=forking  
    RuntimeDirectory=mongodb
    RuntimeDirectoryMode=0751
    PIDFile=/var/run/mongodb/mongod.pid
    ExecStart=/usr/local/momgodb/mongodb/bin/mongod --config /usr/local/mongodb/momgodb/mongodb.conf  
    ExecStop=/usr/local/momgodb/mongodb/bin/mongod --shutdown /usr/local/mongodb/momgodb/mongodb.conf  
    PrivateTmp=false  
  
    [Install]  
    WantedBy=multi-user.target
	
/// 设置mongodb.service权限
chmod 754 mongodb.service
#启动服务
systemctl start mongodb.service
#关闭服务
systemctl stop mongodb.service
#开机启动
systemctl enable mongodb.service

//mongodb.service启动测试,你重启下服务器试试呀~，通过工具连接判断是否生效
```
## 其他操作
```
//查看mongodb进程
ps aux |grep mongodb
//关闭mongodb服务
sudo kill pid(你查出来的进程pid)
```
使用mongodb的时候经常需要设置密码和用户，只需要注释调启动配置的noauth = true，再重启之前需要先添加用户信息来进行验证
```
//使用admin数据库
use admin
//给admin数据库添加管理员用户名和密码，用户名和密码请自行设置
db.createUser({user:"admin",pwd:"123456",roles:["root"]})
//验证是否成功，返回1则代表成功
db.auth("admin", "123456")
//切换到要设置的数据库,以test为例
use test
//为test创建用户,用户名和密码请自行设置。
db.createUser({user: "test", pwd: "123456", roles: [{ role: "dbOwner", db: "test" }]})
```
这里可以使用可视化连接工具,我使用的是robo 3t，安装方法比较简单，就不赘述喽

# spring boot 连接mongodb是先上传、下载、删除的功能
首先引入连接mongodb的依赖  compile group: 'org.springframework.boot', name: 'spring-boot-starter-data-mongodb', version: '2.1.4.RELEASE',
此时mongodb在注入了 MongoTemplate 和GridFsTemplate 。编写测试用例..
```
@RestController
@RequestMapping("/mongodb")
public class MongodbController {

    //简单的Collection存储对象
    @Autowired
    MongoTemplate mongotemplate;

    // 获得SpringBoot提供的mongodb的GridFS对象
    @Autowired
    private GridFsTemplate gridFsTemplate;

    @RequestMapping("/test")
    @ResponseBody
    public OperateResult home() {
        User user = new User();
        user.setUsername("test");
        user.setPassword("test");
        user.setEmail("test");
        user.setPhone("test");
        user.setQuestion("test");
        user.setAnswer("test");
        user.setRole(0);
        user.setId("test");
        user.setCreateTime(new Date());
        user.setCreateBy(0L);
        user.setLastModifiedTime(new Date());
        user.setLastModifiedBy("test");
        mongotemplate.save( user );
        return OperateResult.operationSuccess( "save1" );
    }


    @PostMapping("/fileSave")
    public OperateResult saveFile(@RequestParam("file")MultipartFile file){
        try {
            String fileName = file.getOriginalFilename();
            // 获得文件输入流
            InputStream ins = file.getInputStream();
            // 获得文件类型
            String contentType = file.getContentType();
            GridFSFile gridFSFile = gridFsTemplate.store(ins, fileName, contentType);
            FileInfo fileInfo = new FileInfo();
            fileInfo.setFileName("");
            fileInfo.setFileType("");
            fileInfo.setFileId("");
            fileInfo.setCreator("");
            return OperateResult.operationSuccess( "存文件成功" );
        }catch (Exception e){
            e.printStackTrace();
            return OperateResult.operationFailure( e.getMessage() );
        }
    }

    @RequestMapping("/downFile")
    public void downloadFile(@RequestParam(name = "file_id") String fileId,HttpServletRequest request,HttpServletResponse response) throws Exception {
        Query query = Query.query( Criteria.where("_id").is(fileId));
        GridFSDBFile gfsfile = gridFsTemplate.findOne(query);
        if (gfsfile == null) {
            return ;
        }

        String fileName = gfsfile.getFilename().replace(",", "");
        //处理中文文件名乱码
        if (request.getHeader("User-Agent").toUpperCase().contains("MSIE") ||
                request.getHeader("User-Agent").toUpperCase().contains("TRIDENT")
                || request.getHeader("User-Agent").toUpperCase().contains("EDGE")) {
            fileName = java.net.URLEncoder.encode(fileName, "UTF-8");
        } else {
            //非IE浏览器的处理：
            fileName = new String(fileName.getBytes("UTF-8"), "ISO-8859-1");
        }
        // 通知浏览器进行文件下载
        response.setContentType(gfsfile.getContentType());
        response.setHeader("Content-Disposition", "attachment;filename=\"" + fileName + "\"");
        gfsfile.writeTo(response.getOutputStream());
    }

    @PostMapping("/deleteFile")
    public OperateResult deleteFile(String fileId){
        Query query = Query.query(Criteria.where("_id").is(fileId));
        // 查询单个文件
        GridFSDBFile gfsfile = gridFsTemplate.findOne(query);
        if (gfsfile == null) {
            return OperateResult.operationFailure( "没有找到文件" );
        }
        gridFsTemplate.delete(query);
        return OperateResult.operationSuccess( "删除成功" );
    }

```