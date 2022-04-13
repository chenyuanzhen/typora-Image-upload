import base64
from qiniu import Auth, put_file
import time
import os
import github


class AbstractUploader:
    config = {}

    def __init__(self, config):
        self.config = config

        pass

    def checkConfig(self):
        pass

    def upload(self, imagePath):
        pass

    def sendSignal(self, signal):
        print("{} is not accept {} signal", type(self).__name__, signal)


class QiNiuUploader(AbstractUploader):
    def __init__(self, config):
        super().__init__(config)

    def upload(self, imagePath):
        q = Auth(self.config['access_key'], self.config['secret_key'])
        # key = 时间戳 + filename
        key = generateKey(imagePath)

        # 上传文件到存储后， 存储服务将文件名和文件大小回调给业务服务器。
        policy = {
            'callbackUrl': self.config['host_name'],
            'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
        }
        token = q.upload_token(self.config['bucket_name'], key, 3600, policy)
        try:
            ret, info = put_file(token, key, imagePath, version='v2')
        except FileNotFoundError:
            imageNotFound(imagePath)
            return None

        return "http://" + self.config['external_domain_name'] + '/' + key


class GithubUploader(AbstractUploader):
    cacheFiles = []

    def __init__(self, config):
        super().__init__(config)

    def checkConfig(self):
        defaultValue = {
            "commit_message": "upload by python",
            "branch": "main",
            "cacheSize": 10,
            "remote_prefix_path": "/image"
        }
        for key in defaultValue.keys():
            if self.config[key] is None:
                self.config[key] = defaultValue[key]

    def upload_github(self, files):
        if files is None or len(files) == 0:
            return None
        g = github.Github(self.config['access_token'])
        repo = g.get_repo("{}/{}".format(self.config['owner'], self.config['repo_name']))
        branch = repo.get_branch(self.config['branch'])
        # get HEAD
        head_sha = branch.commit
        tree = repo.get_git_tree(sha=head_sha.sha)

        treeElements = []
        for f in files:
            # create blob for each file
            fileContent = f['content']
            blob1 = repo.create_git_blob(fileContent.decode('utf-8'), "base64")
            element = github.InputGitTreeElement(path=f['remote_path'], mode='100644', type='blob', sha=blob1.sha)
            treeElements.append(element)

        commit_message = self.config['commit_message']
        # build new tree
        new_tree = repo.create_git_tree(treeElements, tree)
        parent = repo.get_git_commit(sha=head_sha.sha)
        # create commit
        commit = repo.create_git_commit(commit_message, new_tree, [parent])
        # modify refs
        branch_refs = repo.get_git_ref('heads/{}'.format(self.config['branch']))
        branch_refs.edit(sha=commit.sha)
        print("push {} photos to github", len(files))

    def upload(self, imagePath):
        # github考虑目录, 一个目录文件数目有上限
        # 1. 缓存imagePath
        # 2. 当imagePath到达一定指定数目后, 上传并commit, 上传数目 >= cacheSize 时才会上传
        if os.path.exists(imagePath):
            uploadFilename = generateKey(imagePath)
            self.cacheFiles.append({
                "remote_path": "{remote_prefix_path}/{uploadFilename}".format(
                    remote_prefix_path=self.config["remote_prefix_path"], uploadFilename=uploadFilename),
                "content": base64.b64encode(open(imagePath, mode='rb').read())
            })
            if len(self.cacheFiles) >= self.config["cacheSize"]:
                self.upload_github(self.cacheFiles)
                self.cacheFiles = []
            return format("https://github.com/{owner}/{repo_name}/blob/{branch}/{remote_prefix_path}/{uploadFilename}?raw=true"
                          .format(owner=self.config["owner"], repo_name=self.config["repo_name"],
                                  branch=self.config["branch"], remote_prefix_path=self.config["remote_prefix_path"],
                                  uploadFilename=uploadFilename))
        else:
            imageNotFound(imagePath)
            return None

    def sendSignal(self, signal):
        if signal == 'finish':
            self.upload_github(self.cacheFiles)
            self.cacheFiles = []
        else:
            super().sendSignal(signal)


def imageNotFound(path):
    print("imageNotFound: %s", path)


# string为文件路径
def generateKey(string):
    strList = string.split('/')
    key = time.strftime("%Y-%m-%d_%H:%M:%S-", time.localtime()) + strList[-1]
    if len(key) >= 255:
        return key[0:255]
    return key


# 根据配置文件获取上传器
def getUploader(config):
    if config["type"] == 'github':
        return GithubUploader(config["github"])
    elif config["type"] == 'qiniu':
        return QiNiuUploader(config["qiniu"])
    else:
        print("please figure out which uploader is used")
        return None
