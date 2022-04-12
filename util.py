import requests
import base64
import datetime
import github

"""
    commiter: 提交者信息
    repo_info: 仓库信息
    files: 需要上传的文件 
    
    Example Usage:
    committer = {
        "commit_message": update datetime to {str(datetime.datetime.now())}',
        "access_token": ""
    }

    repo_info = {
        "owner": "renaisun",
        "repo_name": "test",
        "branch": "customBranch",
    }

    files = [
        {
            "remote_path": "test/a.png",
            "content": base64.b64encode(open("testupl.png", mode='rb').read())
        }
    ]
    upload_github(committer, repo_info, files)
"""


def upload_github(committer, repo_info, files):
    # using access token
    g = github.Github(committer['access_token'])
    repo = g.get_repo("{}/{}".format(repo_info['owner'], repo_info['repo_name']))
    branch = repo.get_branch(repo_info['branch'])
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

    commit_message = committer['commit_message']
    # build new tree
    new_tree = repo.create_git_tree(treeElements, tree)
    parent = repo.get_git_commit(sha=head_sha.sha)
    # create commit
    commit = repo.create_git_commit(commit_message, new_tree, [parent])
    # modify refs
    branch_refs = repo.get_git_ref('heads/{}'.format(repo_info['branch']))
    branch_refs.edit(sha=commit.sha)


if __name__ == "__main__":
    committer = {
        "commit_message": "test util github image upload",
        "access_token": "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"
    }

    repo_info = {
        "owner": "chenyuanzhen",
        "repo_name": "chenyuanzhen.github.io",
        "branch": "image",
    }

    files = [
        {
            "remote_path": "image/a.png",
            "content": base64.b64encode(open("testImage/test1.png", mode='rb').read())
        },
        {
            "remote_path": "image/b.png",
            "content": base64.b64encode(open("testImage/test2.png", mode='rb').read())
         }
    ]
    upload_github(committer, repo_info, files)
