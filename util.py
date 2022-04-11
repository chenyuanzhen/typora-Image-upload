import requests
import base64
import datetime
import github


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


"""
Example Usage:
    committer = {
        "commit_message": f'update datetime to {str(datetime.datetime.now())}',
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
