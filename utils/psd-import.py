import os
import shutil
from pathlib import Path
from psd_tools import PSDImage
import fnmatch
import sys


#stupif fuckiynf rat
#line, col, shadow
# layers/groups with number in name get flattened
def hasNumber(name):
    i = 0
    while len(name) > i:
        if name[i].isdigit():
            return True
        i+=1
    return False

def psdParentsToPath(item):
    layer = item
    dirname = ""
    while layer.parent is not None and layer.parent.name.lower() != "root":
        dirname = (layer.parent.name + "/") + dirname
        layer = layer.parent
    return dirname

#bruh (not working)
def makeVisible(item):
    item.Visible = True
    try:
        for desc in item.descendants():
            desc.Visible = True
    except Exception:
        print(f"{item.parent.name}/{item.name} has no descendants, skipping")
    parent = item.parent
    while parent is not None:
        parent.Visible = True
        parent = parent.parent

#redundant
def replaceChar(str, old, new):
    nStr = ''
    for ch in str:
        if ch == old:
            nStr += new
        else:
            nStr += ch
    return nStr

#makes a new directory with name substr, deletes if directory already exists
#searches through dirPath recursively, moves folders with name containing substr to new dir
def groupByName(dirPath, destDir, substr):
    tempPath = './' + substr
    if os.path.exists(tempPath):
        shutil.rmtree(tempPath)
    os.mkdir(tempPath)
    recursiveGroupByName(Path(dirPath), tempPath, substr)
    destPath = destDir + "/" + substr
    if os.path.exists(destPath):
        shutil.rmtree(destPath)
    shutil.move(tempPath, destPath)
    
#MAY BE BUGGY (but works for now)
def recursiveGroupByName(dirPath, destPath, substr):
    for child in dirPath.iterdir():
        if substr in child.name:
            print(f"{substr} in child: ")
            print(child)
            print('\n')
            shutil.move(str(child), destPath)
        # there are files(nondir) in directory, or the directory is empty
        elif len(fnmatch.filter(os.listdir(child), '*.*')) > 0 or len(os.listdir(dirPath)) == 0:
            print("there are files(nondir) in directory, or the directory is empty")
            print(child)
            print('\n')
        else:
            print("poopy")
            print(child)
            print('\n')
            recursiveGroupByName(child, destPath, substr)


def writeIntoAssetsJson(srcDir, extension):
    jsonDirPath = Path("./public")
    jsonName = "assets.json"
    jsonPath = jsonDirPath / jsonName
    if os.path.exists(jsonPath):
        os.remove(jsonPath)
    with open(str(jsonPath), 'w') as dest:
        dest.write('[')
    writeIntoAssetsJsonRecursive(srcDir, extension, jsonPath, str(srcDir), 'public/')
    with open(str(jsonPath), 'a') as dest:
        dest.write(']')

#recursive function
# writes into assetsPath
# comma between datasets need fixing
def writeIntoAssetsJsonRecursive(srcDir, extension, destPath, keyRm, dirRemove):
    pathWritten = False
    parentDir = str(srcDir).replace(dirRemove, '')
    numFiles = len(fnmatch.filter(os.listdir(str(srcDir)), '*' + extension))
    numIter = 0
    #for child of srcDir
    for child in srcDir.iterdir():
        #if child has [extension], (write into file ALL the stuff)
        if extension in child.name:
            if not pathWritten:
                with open(str(destPath), 'a') as dest:
                    dest.write('{"path": "' + parentDir + '","files": [')
                pathWritten = True
            key = str(srcDir).replace(keyRm, "") 
            key = replaceChar(str(srcDir).replace(keyRm + '/', ""), '/', '.') #might wanna get rid of this and just use the preset replace
            key += '.' + child.stem
            url = child.name
            with open(str(destPath), 'a') as dest:
                dest.write('{"type": "image","key": "'+key+'","url": "'+url+'"}')
            numIter += 1
            if (numIter < numFiles):
                with open(str(destPath), 'a') as dest:
                    dest.write(',')
        else: 
            writeIntoAssetsJsonRecursive(child, extension, destPath, keyRm, dirRemove)
    if pathWritten:
        with open(str(destPath), 'a') as dest:
                dest.write(']},')

def isInSet(list, str):
    if list is None:
        return False
    for item in list:
        if item in str:
            return True
    return False


#currently kinda inefficient
# nameCondition should return a BOOL type, only take a string type as param, should be a condition about the item's name
# condition should return a BOOL type, only take a psd item as param, should be a condition about the item's state in the psd file
# nameException is a string type
# skipDir should be list
def psdExportProject(srcPath, destDir, condition = None, nameCondition = None, nameException = "", skipDir = None):
    psd = PSDImage.open(srcPath)
    toSkip = skipDir
    for item in psd.descendants():
        parentPath = psdParentsToPath(item)
        skip = isInSet(toSkip, parentPath)
        if skip:
            toSkip.add(parentPath)
        else:
            conditionMet = nameCondition(item.name) if nameCondition is not None else not item.is_group()
            conditionMet = condition(item) if condition is not None else conditionMet
            conditionMet = (nameException not in item.name and conditionMet) if nameException != '' else conditionMet
            if conditionMet:
                psdExportItem(srcPath, destDir, item, parentPath)
                toSkip.add(f"{parentPath}{item.name}")

#exports all groups with groupName in its name
#!!!!may still be buggy :/
def psdExportGroupsByName(srcPath, destDir, groupName, condition = None, nameCondition = None):
    psd = PSDImage.open(srcPath)
    toSkip = set()
    for item in psd.descendants():
        parentPath = psdParentsToPath(item)
        proceed = groupName in parentPath and not isInSet(toSkip, parentPath)
        if proceed:
            conditionMet = nameCondition(item.name) if nameCondition is not None else not item.is_group()
            conditionMet = condition(item) if condition is not None else conditionMet
            if conditionMet:
                psdExportItem(srcPath, destDir, item, parentPath)
                toSkip.add(f"{parentPath}{item.name}")

def psdExportItem(srcPath, destDir, psdItem, parentPath = None):
    makeVisible(psdItem)
    img = psdItem.composite(force = True)
    folder = parentPath + '/' if parentPath != "" else "/"
    if img:
        os.makedirs(f"{destDir}/{parentPath}", exist_ok=True)
        img.save(f"{destDir}/{folder}{psdItem.name}.png")
        print(f"saved {folder}{psdItem.name}")

def clearFolder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


# ----- mAYBE PUT SOME OF THE ABOVE IN THEIR OWN MODULE LMAO ---
def main():
    # #PATHS
    rattyPath = "./psd/ratty_dress_up.psd"
    uiPath = "./psd/UI.psd"
    destDir = "./public/img"

    #delete outdated assets
    clearFolder(destDir)

#!!!MASS EXPORT: MAIN FILE
    #rule: items with number in name get merged into pngs
    psdExportProject(rattyPath, destDir, None, hasNumber, "parent", {"no_export"})
    groupByName(destDir, destDir, 'hair')

#!!!MASS EXPORT: UI FILE
    #rule: 
    # 1. except for icon folder, items with number in name get merged into pngs
    # 2. for icon folder, all children get merged into pngs
    psdExportProject(uiPath, destDir, None, hasNumber, "", {"no_export", "icons"})

    isGroup = lambda psdItem : psdItem.is_group()
    psdExportGroupsByName(uiPath, destDir, "icons", isGroup)
    

#!!!JSON TRANSFORMATION
    writeIntoAssetsJson(Path(destDir), '.png')
    return 0

if __name__ == '__main__':
    sys.exit(main())