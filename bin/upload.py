#!/usr/bin/env python
import os, pprint, subprocess, sys

usage = "\n  usage:  upload.py  <mitcfg> <version> <dataset> <target> [ pattern = 'root' ]\n"

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def uploadFile(file,target):
    # upload this file

    rc = 0
    #cmd = 't2tools.py --action up --source /mnt/hadoop' + target + '/' + file + ' --target ' + target
    cmd = 'gfal-copy /mnt/hadoop' + target + '/' + file + \
        ' gsiftp://se01.cmsaf.mit.edu:2811/' + target + '/' + file
    #print cmd

    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode

    if rc != 0:
        print " ERROR -- %d"%(rc)
        print out
        print err

    return rc

def makeDir(target):
    # make the directory

    rc = 0
    cmd = 'makedir %s'%(target)
    os.system(cmd)

    return

def getFile(file):
    # extract the unique file id

    f = file.split('/')
    fileName = f.pop()

    return fileName

def loadCompletedFiles(tgt,pattern):
    # load the files that already have been completed

    completedFiles = []

    cmd = 'list ' + tgt
    print " CMD: %s"%(cmd)
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode
    
    lines = out.split("\n")
    for line in lines:
        if not pattern in line:
            continue
        f = line.split("/") 
        if len(f) > 1:
            completedFiles.append(f[-1])

    print "completed:"
    print completedFiles

    return completedFiles

def loadFilesToUpload(hadoop,dataset,pattern):
    # load the files from an existing temporary directory for cataloging and checks

    files = []

    cmd = 'ls -1 /mnt/hadoop' + hadoop + '/' + dataset
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode
    
    lines = out.split("\n")
    for line in lines:
        if not pattern in line:
            continue
        files.append(line)

    print "toUpload:"
    print files

    return files

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

pattern = "root"
if len(sys.argv) > 5:
    pattern = sys.argv[5]

# derived vaiables
book = mitcfg + '/' + version
hadoop = "/cms/store/user/paus/" + book

# find the list of files to consider
files = loadFilesToUpload(hadoop,dataset,pattern)
# find the list of files already completed
completedFiles = loadCompletedFiles(target,pattern) # this might contain other dataset files

# make the target directory
rc = makeDir(target)

# loop over the files
nFiles = len(files)
i = 0
entries = []
for file in files:
    i += 1
    fileName = getFile(file)
    print "   -- next file: %s -> %s (%d of %d)"%(file,fileName,i,nFiles)


    if fileName in completedFiles:
        print "     INFO - This file is already uploaded."
        continue
            
    # doing the uploading here
    rc = uploadFile(file,target)
