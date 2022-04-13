import main
import os
if __name__ == '__main__':
    md_dir = '/Users/chenyuanzhen/Desktop/mdTest'
    md_list = []
    main.getAllMdPath(md_list, md_dir)
    uploadDirName = main.generateNewDirPath(md_dir)
    # 创建一个新目录, 用于放置更新后的md
    os.mkdir(uploadDirName)
    for mdPath in md_list:
        main.uploadAndChangeMarkdownPhoto(mdPath, uploadDirName, None)


