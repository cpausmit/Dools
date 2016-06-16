#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
# Script to cleanup the leftover stubs and files that cannot be used anymore.
#
# Author: C.Paus                                                                 (February 26, 2016)
#---------------------------------------------------------------------------------------------------
import os,sys,getopt,re,string

baseDir = '/mnt/hadoop/cms/store/user/paus'

def makeDirList(baseDir,book):
    # Make list of directories to consider for cleaning

    allDirs = []
    cmd = 'list ' + baseDir + '/' + book
    print ' CMD: ' + cmd
    for line in os.popen(cmd).readlines():
        line = line[:-1]
        dir = line
        f = dir.split("/")
        dir = f.pop()
        
        allDirs.append(baseDir + '/' + book + '/' + dir)

    return allDirs

def cleanupDir(dir,pattern):
    # Cleanup one directory only
    
    f = dir.split('/')
    hadoopDir = "/" + "/".join(f[3:])

    allHadoopDirs = []

    cmd = 'list ' + dir + '| grep crab_0_' + pattern
    print ' CMD: ' + cmd

    for line in os.popen(cmd).readlines():
        line = line[:-1]
        dir = line
        f = dir.split("/")
        dir = f.pop()
    
        allHadoopDirs.append(hadoopDir + '/' + dir)
        cmd = 'rglexec hdfs dfs -rm -r ' + hadoopDir + '/' + dir
        print ' Removing: ' + cmd

        status = os.system(cmd)
    
#===================================================================================================
# Main starts here
#===================================================================================================
# Define string to explain usage of the script
usage =  "Usage: cleanupOrphans.py --book=<name>  --pattern=<date/time-pattern>\n"
usage += "                         --help\n"

# Define the valid options which can be specified and check out the command line
valid = ['book=','pattern=','help']
try:
    opts, args = getopt.getopt(sys.argv[1:], "", valid)
except getopt.GetoptError, ex:
    print usage
    print str(ex)
    sys.exit(1)

# --------------------------------------------------------------------------------------------------
# Get all parameters for the production
# --------------------------------------------------------------------------------------------------
# Set defaults for each option
book = None
pattern = None

# Read new values from the command line
for opt, arg in opts:
    if opt == "--help":
        print usage
        sys.exit(0)
    if opt == "--book":
        book = arg
    if opt == "--pattern":
        pattern = arg

# Deal with obvious problems
if book == None:
    cmd = "--book=  required parameter not provided."
    raise RuntimeError, cmd
if pattern == None:
    cmd = "--pattern=  required parameter not provided."
    raise RuntimeError, cmd

# Produce the relevant directory list
allDirs = []
allDirs = makeDirList(baseDir,book)

# Analyze each directory for matching sub directories and clean up
for dir in allDirs:
    # cleanup the specific sub directories and the potentially containing files
    cleanupDir(dir,pattern)
