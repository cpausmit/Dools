#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# Find missing files in all samples in a given book.
#
#---------------------------------------------------------------------------------------------------
import os,sys

MOUNT = "/mnt/hadoop"
TRUNC = "/cms"
DIR = "/store/user/paus"

def missingFilesInSample(book,sample,tmpDir):
    # find the files that are missing on the dropbox side

    if os.path.exists(tmpDir +'/missing_'+sample+'.list'):
        print ' Missing file list already exists. ' + tmpDir + '/missing_'+sample+'.list'
        return None

    os.system("echo; date")
    print " Working on sample: " + sample
    allFiles = []
    print ' Find all files (T2).'
    cmd = 'list ' + MOUNT + TRUNC + DIR + "/" + book \
        + '/' + sample + " | grep .root"
    for line in os.popen(cmd).readlines():
        file = line[:-1]
        file = (file.split(" ")).pop()
        file = (file.split("/")).pop()
        allFiles.append(file)
    
    doneFiles = []
    print ' Find done files (Dropbox).'
    cmd = "python "+ os.getenv("PYCOX_BASE", None) + "/pycox.py --action=ls --source=" \
        + TRUNC + DIR + '/'+ book + '/' + sample + "| grep root"
    for line in os.popen(cmd).readlines():
        file = line[:-1]
        file = (file.split(" ")).pop()
        file = (file.split("/")).pop()
        doneFiles.append(file)
    
    missingFiles = []
    print ' Find missing files (missing in Dropbox).'
    for file in allFiles:
        if file not in doneFiles:
            missingFiles.append(file)
            print TRUNC + DIR + "/" + book + '/' + sample + '/' + file        
    
    print ' Numbers all/done/missing:  %4d / %4d / %4d'%\
        (len(allFiles),len(doneFiles),len(missingFiles))

    if len(allFiles) == 0 and len(doneFiles) ==0 and len(missingFiles) ==0:
        cmd = ' removedir ' + TRUNC + DIR + "/" + book + '/' + sample
        print ' # RMDIR -- \n    ' + cmd

    with open(tmpDir + '/missing_'+sample+'.list','w') as fileH:
        for file in missingFiles:
            fileH.write(TRUNC + DIR + "/" + book + '/' + sample + '/' + file + '\n')

    return missingFiles

def removeSampleFromTier2(book,sample):
    # remove a given sample from the Tier-2 (it was checked this sample has a full copy in dropbox)

    print ' Remove from Tier-2 --  book: %s  sample: %s'%(book,sample)
    cmd = 'removedir ' + TRUNC + DIR + "/" + book + "/" + sample
    #print ' CMD: ' + cmd
    rc = os.system(cmd)

    return rc
    
#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------
book = sys.argv[1]
pattern = ''
option = ''
if len(sys.argv) > 2:
    pattern = sys.argv[2]
if len(sys.argv) > 3:
    option = sys.argv[3]

# is everything setup?
pycox = os.getenv("PYCOX_BASE", None)
if not pycox:
    print ' ERROR - pycox is not setup'
    sys.exit(1)
t2tools = os.getenv("T2TOOLS_BASE", None)
if not t2tools:
    print ' ERROR - t2tools is not setup'
    sys.exit(1)

# hi, here we are!
os.system("echo; date")

# make a list of all samples in this book
allSamples = []
print ' Find all samples (T2).'
cmd = 'list ' + MOUNT + TRUNC + DIR + "/" + book + "| grep ^D:0"
#print ' CMD: ' + cmd
if pattern != "":
    cmd += "| grep %s"%(pattern)
for line in os.popen(cmd).readlines():
    sample = (line[:-1].split("/")).pop()
    #print ' Sample: ' + sample
    allSamples.append(sample)

# say what we found
print ' Number of samples found: %d'%(len(allSamples))

# make a cache for the missing files
tmpDir = '/tmp/' + book.replace('/','_')
if not os.path.exists(tmpDir):
    cmd = 'mkdir -p ' + tmpDir
    print '\n Making cache for missing file summary (%s).\n'%(tmpDir)
    os.system('mkdir -p ' + tmpDir)
    
# now loop through all samples and find the missing files
missingFiles = []
for sample in allSamples:
    missingFiles = missingFilesInSample(book,sample,tmpDir)

    # in case removal is requested try to remove the Tier-2 copy
    if option == 'remove':
        if missingFiles != None and len(missingFiles) == 0:
            removeSampleFromTier2(book,sample)
