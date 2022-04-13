import Uploader

if __name__ == "__main__":
    configGithub = {
        "commit_message": "test util github image upload",
        "access_token": "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",
        "owner": "chenyuanzhen",
        "repo_name": "chenyuanzhen.github.io",
        "branch": "image",
        # 必须指定一个 remote_prefix_path 不能为空
        "remote_prefix_path": "image",
        "cacheSize": 2
    }

    uploader = Uploader.GithubUploader(configGithub)
    imagePath = ['/Users/chenyuanzhen/Desktop/download.jpg', '/Users/chenyuanzhen/Desktop/download-1.jpg']
    for path in imagePath:
        print(uploader.upload(path))

    uploader.sendSignal('finish')



