#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# Analyse the in an input file specified fileIds.
#
#---------------------------------------------------------------------------------------------------
import os,sys

DEBUG = int(os.environ.get('T2TOOLS_DEBUG',0))

TRUNC = "/cms"
DIR = "/store/user/paus"

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------
book = sys.argv[1]
dset = sys.argv[2]
idFile = sys.argv[3]

# hi, here we are!
os.system("date")

# read all relevant Ids
with open(idFile,'r') as fileH:
    ids = fileH.read().splitlines()

# make a list of all files in crab directories in this book/dataset
fileSizesTmp = {}
cmd = 't2tools.py --action=ls --options=-l --source=' \
    + TRUNC + DIR + "/" + book + "/" + dset + "/crab_0_*/"
if DEBUG>0:
    print ' CMD: ' + cmd
for line in os.popen(cmd).readlines():
    line = line[:-1]
    f = line.split(" ")
    if len(f) == 8:
        fullFile = f[7]
        fileIdTmp = (fullFile.split("/")).pop()
        fileIdTmp = fileIdTmp.replace("_tmp.root","")
        fileSizesTmp[fileIdTmp] = f[4]
        if DEBUG>1:
            print " Adding: %s"%fileIdTmp

# make a list of all files in final directories in this book/dataset
fileSizes = {}
cmd = 't2tools.py --action=ls --options=-l --source=' \
    + TRUNC + DIR + "/" + book + "/" + dset + "/ | grep root"
if DEBUG>0:
    print ' CMD: ' + cmd
for line in os.popen(cmd).readlines():
    line = line[:-1]
    f = line.split(" ")
    if len(f) == 8:
        fullFile = f[7]
        fileId = (fullFile.split("/")).pop()
        fileId = fileId.replace(".root","")
        fileSizes[fileId] = f[4]
        if DEBUG>1:
            print " Adding: %s"%fileId

for id in ids:
    if id in fileSizes:
        print ' Found in final directory: %10d %s'%(fileSizes[id],id)  
    elif id in fileSizes:
        print ' Found in TMP   directory: %10d %s'%(fileSizesTmp[id],id)
    else:
        print ' ERROR DID NOT FIND      : %s'%(id)
