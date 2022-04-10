import json

from qiniu import Auth, put_file, etag
import qiniu.config
import time
import os
import re

configJsonPath = "./config.json"
"""
    使用方法:
    1. 在config.json中配置七牛云信息和mdDir
    2. 其中mdDir属性是指定.md文件所在目录, 程序会搜索mdDir中所有.md后缀文件, 包括子文件夹
    
    程序会在mdDir目录中创建一个uploadMd文件夹, 并将上传图片的.md文件放在该文件夹中
    - 若.md文件中的照片找不到会报错imageNotFound, 但不会打断进程
"""

# string为文件路径
def generateKey(string):
    strList = string.split('/')
    key = time.strftime("%Y-%m-%d_%H:%M:%S-", time.localtime()) + strList[-1]
    if len(key) >= 255:
        return key[0:255]
    return key


def uploadAndGetUrl(configJson, filepath):
    q = Auth(configJson['access_key'], configJson['secret_key'])
    # key = 时间戳 + filename
    key = generateKey(filepath)

    # 上传文件到存储后， 存储服务将文件名和文件大小回调给业务服务器。
    policy = {
        'callbackUrl': configJson['host_name'],
        'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
    }
    token = q.upload_token(configJson['bucket_name'], key, 3600, policy)
    try:
        ret, info = put_file(token, key, filepath, version='v2')
    except FileNotFoundError:
        print("imageNotFound: %s", filepath)
        return None
    print(info)
    return "http://" + configJson['external_domain_name'] + '/' + key


"""
    filePath: markdown绝对路径
"""


def uploadAndChangeMarkdownPhoto(filePath, configJson, uploadDirName):
    pathList = filePath.split('/')[1:-1]
    dirPath = ""
    for path in pathList:
        dirPath += '/' + path
    dirPath += '/'
    # 文章内容先放到一个临时文件中, 每读一行, 就写一行, 更改临时文件名字
    with open(uploadDirName + filePath.split('/')[-1], "w") as tmp:
        with open(filePath, "r") as markdown:
            line = markdown.readline()
            while line != "":
                imagePaths = re.findall(r"!\[.*\]\((.*)\)", line)
                imagePaths += re.findall(r'<img\s*?src="(.*?)"', line)
                for path in imagePaths:
                    downloadUrl = uploadAndGetUrl(configJson, dirPath + path)
                    if downloadUrl is not None:
                        line = line.replace(path, downloadUrl)
                tmp.write(line)
                line = markdown.readline()


# 返回所有.md文件的绝对路径
def getAllMdPath(mdList, dirPath):
    # dirs是目录
    # files是文件
    for root, dirs, files in os.walk(dirPath):

        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list

        # 遍历文件
        for file in files:
            if re.search(r".*\.md", file) is not None:
                mdList.append(os.path.join(root, file))

        # 遍历所有的文件夹
        for subDir in dirs:
            getAllMdPath(mdList, subDir)


# 打开文件json路径
with open(configJsonPath, "r") as f:
    config = json.load(f)
    print("从" + configJsonPath + ", 加载配置文件")
    # 扫描当前目录下所有后缀.md的文件
    if os.path.isdir(config["mdDir"]) is False:
        print("%s 不存在, 请检查目录是否存在", config["mdDir"])
    else:
        mdList = []
        # 获得目录下所有的后缀.md文件
        getAllMdPath(mdList, config["mdDir"])
        uploadDirName = os.path.join(config["mdDir"], "uploadMd")
        suffix = 1
        # 创建一个新目录
        if os.path.isdir(uploadDirName) is True:
            while os.path.isdir(os.path.join(config["mdDir"], "uploadMd" + str(suffix))) is True:
                suffix += 1
            uploadDirName = os.path.join(config["mdDir"], "uploadMd" + str(suffix))

        os.mkdir(uploadDirName)
        for mdPath in mdList:
            uploadAndChangeMarkdownPhoto(mdPath, config, uploadDirName + '/')

