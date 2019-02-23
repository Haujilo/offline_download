# onedrive离线下载

## 原理

[onedrive](https://onedrive.live.com)的接口具有个人版的离线下载HTTP功能，此项目用于把接口的验证和调用自动化。

## 前提

1. 首先根据[微软文档](https://docs.microsoft.com/en-us/onedrive/developer/rest-api/getting-started/app-registration?view=odsp-graph-online)的步骤，创建APP，获取Client ID等参数。注：目前redirect_uri只支持https://login.microsoftonline.com/common/oauth2/nativeclient
2. 执行脚本的机器需要安装依赖工具（chrome, chromedriver, pipenv）。

## 用法

```shell
git clone https://github.com/Haujilo/offline_download.git
cd offline_download
pipenv install
touch offline_download.sh
chmod u+x offline_download.sh
```

offline_download.sh内容如下：
```shell
#! /bin/bash

export MS_USERNAME=""  # 此处修改成你的微软账号
export MS_PASSWORD=""  # 此处修改成你的微软密码
export MS_CLIENT_ID="" # 此处修改成你在前提中创建的App的id

# $1是在onedrive上创建的文件名，$2是远程的URL
exec ./offline_download.py --name $1 $2
```

```shell
# 替换掉{Name}和{URL},如此执行offline_download.sh即可，祝你开心！☺️
pipenv run ./offline_download.sh {Name} {URL}
```

## 备注

1. 暂未发现onedrive对离线下载有什么限制
2. 目前暂只支持离线下载到根目录

## TODO

1. 提供下载到某个目录的参数
2. 脚本可以打包在一起
3. 容器化
