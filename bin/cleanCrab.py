#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# Find all crab left over directories on Tier-2 and remove them.
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

# make a list of all crab directories
allCrabDirs = []
if pattern == '':
    print ' Find all crab directories.'
else:
    print ' Find all crab directories matching %s.'%(pattern)

cmd = 'list --long=2 ' + TRUNC + DIR + "/" + book + "/*/ | grep crab_0_"
if DEBUG>0:
    print ' CMD: ' + cmd
if pattern != "":
    cmd += "| grep %s"%(pattern)
for line in os.popen(cmd).readlines():
    f = (line[:-1].split("/"))[-2:]
    sample = "/".join(f)
    allCrabDirs.append(sample)

    print ' Found directory: ' + sample

# say what we found
print ' Number of samples found: %d'%(len(allCrabDirs))

for sample in allCrabDirs:
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
