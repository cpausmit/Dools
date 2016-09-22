#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# Find all empty directories and remove them.
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
pattern = ''
if len(sys.argv) > 2:
    pattern = sys.argv[2]

# hi, here we are!
os.system("date")

# make a list of all empty directories (matching a pattern if requested)
allDirs = []
if pattern == '':
    print ' Find all empty directories.'
else:
    print ' Find all empty directories matching %s.'%(pattern)

cmd = 'list ' + TRUNC + DIR + "/" + book
if DEBUG>0:
    print ' CMD: ' + cmd
if pattern != "":
    cmd += "| grep %s"%(pattern)
for line in os.popen(cmd).readlines():
    sample = line[:-1].split("/").pop()
    
    cmdEmpty = 't2tools.py --action=du --source=' + TRUNC + DIR + "/" + book + '/' + sample
    lEmpty = True
    for line in os.popen(cmdEmpty).readlines():
        if line != '':
            lEmpty = False
            break

    if lEmpty:
        print ' Found empty directory: ' + sample
        allDirs.append(sample)

# say what we found
print ' Number of empty directories found: %d'%(len(allDirs))

for sample in allDirs:
    cmd = 'removedir ' + TRUNC + DIR + "/" + book + "/" + sample
    if DEBUG>0:
        print ' CMD: ' + cmd
    # make sure it really is just the crab directory
    if cmd.find('crab_0_') != -1:
        os.system(cmd)
    else:
        print ' ERROR -- it looks like a wrong directory was up for deletion.'
        print '       -- directory:  %s  is not deleting a crab directory.'%(cmd)
        sys.exit(1)
