import json

import os
import re

from Uploader import Uploader

configJsonPath = "./config.json"
"""
    使用方法:
    1. 在config.json中配置七牛云信息和md_dir
    2. 其中md_dir属性是指定.md文件所在目录, 程序会搜索md_dir中所有.md后缀文件, 包括子文件夹
    
    程序会在md_dir目录中创建一个uploadMd文件夹, 并将上传图片的.md文件放在该文件夹中
    - 若.md文件中的照片找不到会报错imageNotFound, 但不会打断进程
"""


"""
    mdPath: markdown绝对路径
    uploadDirName: 新md文件放置的文件夹路径
    uploader: 上传器
    前提: md的图片文件夹和md文件在同一目录下
"""


def uploadAndChangeMarkdownPhoto(mdPath, uploadDirName, uploader):
    dirPath = os.path.dirname(mdPath)
    # 文章内容先放到一个临时文件中, 每读一行, 写一行
    with open(os.path.join(uploadDirName, os.path.basename(mdPath)), "w") as tmp:
        with open(mdPath, "r") as markdown:
            line = markdown.readline()
            while line != "":
                imagePaths = re.findall(r"!\[.*\]\((.*)\)", line)
                imagePaths += re.findall(r'<img\s*?src="(.*?)"', line)
                # 此处认为图片文件夹和md文件在同一目录
                for imagePath in imagePaths:
                    # downloadUrl = os.path.join(dirPath, imagePath)
                    # print(downloadUrl)
                    downloadUrl = uploader.upload(os.path.join(dirPath, imagePath))
                    if downloadUrl is not None:
                        line = line.replace(imagePath, downloadUrl)
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


def generateNewDirPath(md_dir):
    uploadDirName = os.path.join(md_dir, "uploadMd")
    suffix = 1
    # 新目录文件夹名字不可用时, 追加数字后缀
    if os.path.isdir(uploadDirName) is True:
        while os.path.isdir(os.path.join(md_dir, "uploadMd" + str(suffix))) is True:
            suffix += 1
        uploadDirName = os.path.join(md_dir, "uploadMd" + str(suffix))
    return uploadDirName


def main():
    # 打开文件json路径
    with open(configJsonPath, "r") as f:
        config = json.load(f)
        print("从 {} 加载配置文件, 选定上传图床为: {}".format(configJsonPath, config["type"]))
        uploader = Uploader.getUploader(config)
        # 扫描当前目录下所有后缀.md的文件
        if os.path.isdir(config["md_dir"]) is False:
            print("{} 不存在, 请检查目录是否存在", config["md_dir"])
        else:
            # C:\Users\86155\Desktop\log.md
            mdPathList = []
            # 获得目录下所有的后缀.md文件
            getAllMdPath(mdPathList, config["md_dir"])
            # 生成新目录文件
            uploadDirName = generateNewDirPath(config["md_dir"])
            # 创建一个新目录, 用于放置更新后的md
            os.mkdir(uploadDirName)
            # 检查每一个md文件
            for mdPath in mdPathList:
                uploadAndChangeMarkdownPhoto(mdPath, uploadDirName + '/', uploader)
            uploader.sendSignal('finish')


if __name__ == '__main__':
    main()
