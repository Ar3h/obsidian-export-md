#!/usr/bin/env python3
# coding = utf-8
# Time   : 2023/2/17 00:32
# Author : Ar3h
# 专门处理obsidian中的导出md的图片问题
# 将obsidian中的的wiki格式，转为标准md格式，并复制图片到输出目录中的img目录中
# python3 obsidian-export-md.py [noteName/notePath]
# python3 obsidian-export-md.py [noteName/notePath] [outputPath]
# python3 obsidian-export-md.py [noteName/notePath] [outputPath] [imgPath]

import os.path
import re
import shutil
import sys
import time
import urllib.parse
import zipfile


notePath = ""
# 需要导出的笔记仓库根目录
noteBasePath = "{笔记仓库的目录}"  # 例如 /Users/xxx/Library/Mobile Documents/iCloud~md~obsidian/Documents/

# 输出md文件和图片的根目录
outputBasePath = "{输出文件目录}" # 例如 /Users/xxx/Desktop/ObsidianExport/
outputPath = outputBasePath + str(time.time())

# 设置相对md文件中的图片的根路径，可以设置任意个
imgPaths = ["{存放图片文件夹路径1}", # 例如 /Users/xxx/Library/Mobile Documents/iCloud~md~obsidian/Documents/xxx/img/
            "{存放图片文件夹路径2}"]

# 新创建存放图片的目录名，默认即可
newImgDirName = "img"

obWikiPattern = "\!\[\[(.*?)\]\]"
mdPattern = "\!\[.*?\]\((.*?)\)"

# 文件名
basename = ""


def findNotePathByName(noteName):
    if not noteName.endswith(".md"):
        noteName = noteName + ".md"
    for root, dirs, files in os.walk(noteBasePath):
        for file in files:
            if file == noteName:
                return os.path.join(root, file)  # 文件路径
    print("[-] not found " + noteName)
    exit()


def usage():
    print(f"Usage: python3 {sys.argv[0]} noteName/notePath")
    exit()


def createDir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def parseCli():
    global notePath, outputPath, imgPaths
    noteName = ""
    if len(sys.argv) == 2:
        if sys.argv[1] == "-h": usage()
        noteName = sys.argv[1]
    elif len(sys.argv) == 3:
        outputPath = sys.argv[2]
    elif len(sys.argv) == 4:
        imgPaths += sys.argv[3]
    else:
        usage()
    notePath = findNotePathByName(noteName)
    # print(f"[*] noteBasePath: {noteBasePath}")
    print(f"[*] Origin note path: {notePath}")
    # print(f"[*] outputPath: {outputPath}")
    # print(f"[*] imgPath: {imgPaths}")


# 复制所有图片到输出目录
def copyImages(allImages):
    total = len(allImages)
    # 复制文件
    for image, count in zip(allImages, range(1, 9999)):
        for imgPath in imgPaths:
            image = urllib.parse.unquote(image)
            imageSourcePath = os.path.join(imgPath, image)
            imagesDestDir = os.path.join(outputPath, newImgDirName)

            if not os.path.exists(imageSourcePath):
                continue

            createDir(imagesDestDir)

            img_basename = os.path.basename(image)  # 只提取文件名
            imagesDestPath = os.path.join(imagesDestDir, img_basename)

            shutil.copyfile(imageSourcePath, imagesDestPath)
            print(f"[*] {count}/{total} copy '{image}' successs")
        # else:
        # print(f"[-] {imageSourcePath} is not exist")


# 处理md文件中的链接，全部转为标准md格式
def handleLink(lines, obWikiImages, mdImages):
    newNoteContext = ""
    indexObWikiImages = 0
    indexMdImages = 0
    for line in lines:
        if re.search(obWikiPattern, line):
            newLine = re.sub(obWikiPattern, f"![]({newImgDirName}/{obWikiImages[indexObWikiImages]})",
                             line)  # 把obsidian中的wiki格式转为标准md格式
            indexObWikiImages += 1
        elif re.search(mdPattern, line):  # 处理普通md文件中的链接
            newLine = re.sub(mdPattern, f"![]({newImgDirName}/{mdImages[indexMdImages]})",
                             line)  # 把准备的md图片格式格式化一下，添加文件夹前缀
            indexMdImages += 1
        else:
            newLine = line

        newNoteContext += newLine
    # print(newNoteContext)
    global basename
    basename = os.path.basename(notePath)  # 获取笔记的文件名
    newNotePath = os.path.join(outputPath, basename)
    open(newNotePath, "w").write(newNoteContext)

    print(f"\033[32m[*] output path '{outputPath}'")
    print(f"[+] generate markdown '{newNotePath}' success")


def zipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    print(f"[+] generate zip success")


def main():
    parseCli()

    createDir(outputPath)

    t = open(notePath, "r")
    text = t.read()

    obWikiImages = re.findall(obWikiPattern, text)  # 获取所有链接中的文件名
    mdImages = re.findall(mdPattern, text)
    allImages = obWikiImages + mdImages  # 合并所有图片

    # 复制图片
    copyImages(allImages)

    # 处理obsidian的链接
    t.seek(0, 0)
    handleLink(t.readlines(), obWikiImages, mdImages)

    # 打包压缩md文件夹
    zipOutput = os.path.join(outputBasePath, basename.replace(".md", ".zip"))
    zipDir(outputPath, zipOutput)
    os.system(f"open {outputPath}")  # 自动打开文件夹


if __name__ == '__main__':
    main()
