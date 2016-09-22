#!/usr/bin/env python
import os, pprint, subprocess, sys

usage = "\n  usage:  downloadSample.py  <mitcfg> <version> <dataset> [ <pattern> = 'miniaodsim' ]\n"

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def downloadFile(file,target):
    # download this file

    # cmd = 'xrdcp root://xrootd.cmsaf.mit.edu//store/user/paus' + file
    rc = 0
    cmd = 't2tools.py --action down --source ' + file + ' --target ' + target
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode

    if rc != 0:
        print " ERROR -- %d"%(rc)
        print out
        print err

    return rc

def getFile(file):
    # extract the unique file id

    f = file.split('/')
    fileName = f.pop()

    return fileName

def loadCompletedFiles(tgt,pattern):
    # load the files that already have been completed

    completedFiles = []

    cmd = '/bin/ls -1 ' + tgt
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode
    
    lines = out.split("\n")
    for line in lines:
        if not pattern in line:
            continue
        completedFiles.append(line)

    return completedFiles

def loadFilesToDownload(hadoop,dataset,pattern):
    # load the files from an existing temporary directory for cataloging and checks

    files = []

    cmd = 't2tools.py --action ls --source ' + hadoop + '/' + dataset
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode
    
    lines = out.split("\n")
    for line in lines:
        if not pattern in line:
            continue
        f = line.split(" ") 
        if len(f) > 1:
            files.append(f[1])

    return files

def updateXrootdName(fileName):
    # adjust entry for the file moving

    newFileName = fileName.replace('root://xrootd.cmsaf.mit.edu/','/cms')
    return newFileName

#===================================================================================================
#  M A I N
#===================================================================================================
# make sure command line is complete
if len(sys.argv) < 4:
    print " ERROR -- " + usage
    sys.exit(1)

# command line variables
mitcfg = sys.argv[1]
version = sys.argv[2]
dataset = sys.argv[3]
target = sys.argv[4]

pattern = "miniaodsim"
if len(sys.argv) > 5:
    pattern = sys.argv[5]
    

# derived vaiables
book = mitcfg + '/' + version
hadoop = "/cms/store/user/paus/" + book

# find the list of files to consider
files = loadFilesToDownload(hadoop,dataset,pattern)
# find the list of files already completed
completedFiles = loadCompletedFiles(target,pattern) # this might contain other dataset files

# loop over the files
nFiles = len(files)
i = 0
entries = []
for file in files:
    i += 1
    fileName = getFile(file)
    print "   -- next file: %s>%s (%d of %d)"%(file,fileName,i,nFiles)


    if fileName in completedFiles:
        print "     INFO - This file is already downloaded."
        continue
            
    # doing the downloading here
    rc = downloadFile(file,target)
