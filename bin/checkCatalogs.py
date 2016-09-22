#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#
# Check catalogs and remove any suspicious entries. There is no cataloging of files done here.
#
#---------------------------------------------------------------------------------------------------
import os,sys,subprocess
import fileIds

DEBUG = int(os.environ.get('T2TOOLS_DEBUG',0))

TRUNC = "/cms"
DIR = "/store/user/paus"

#---------------------------------------------------------------------------------------------------
#  H E L P E R S
#---------------------------------------------------------------------------------------------------
def cleanFile(file,patterns):
    # take a given file and remove all lines that match any of the given patterns

    print " Clean file: %s"%(file)
    print " Remove: "
    badWords = []
    for badWord in sorted(patterns):
        if badWord != '':
            badWords.append(badWord)
            print "  " + badWord
    
    lRemove = False
    out = ''
    with open(file) as fH:
        for line in fH:
            if not any(badWord in line for badWord in badWords):
                out += line
            else:
                lRemove = True
                print ' REMOVED: ' + line[:-1]

    # was there something removed?
    if lRemove:
        with open(file,'w') as fH:
            fH.write(out)

    return

def removePatternsFromCatalog(catalog,book,dataset,patterns):
    # clean the existing catalog files and remove the files matching the given pattern

    directory = catalog + '/' + book + '/' + dataset

    for filename in os.listdir(directory):
        if "Files" in filename: 
            cleanFile(directory + '/' + filename,patterns)

def loadCatalog(catalog,book,dataset):
    # load the unique file ids of the existing catalog for existence checks (careful)

    mitcfg = book.split("/")[0]
    version = book.split("/")[1]

    catalogedIds = fileIds.fileIds()

    # first make sure the catalog is compact

    rc = 0
    cmd = "cat " + catalog + '/' + book + '/' + dataset + '/RawFiles.00'
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode

    if rc != 0:
        print " ERROR -- %d"%(rc)
        print out
        print err
        #sys.exit(1)
    
    for line in out.split("\n"):
        f = line.split(" ")
        if len(f) > 2:
            name = f[0]
            nEvents = int(f[1])
            catalogedId = fileIds.fileId(name,nEvents)
            catalogedIds.addFileId(catalogedId)

    return catalogedIds
    
    
def findLfns(dataset):

    lfnIds = fileIds.fileIds()

    # find the correct file

    lfnFile = "/home/cmsprod/cms/jobs/lfns/" + dataset + ".lfns"
    if DEBUG>0:
        print " LFN file: " + lfnFile
    
    rc = 0
    cmd = "cat " + lfnFile
    list = cmd.split(" ")
    p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    rc = p.returncode

    if rc != 0:
        print " ERROR -- %d"%(rc)
        print out
        print err
        #sys.exit(1)
    
    for line in out.split("\n"):
        f = line.split(" ")
        if len(f) > 2:
            name = f[1]
            nEvents = int(f[2])
            lfnId = fileIds.fileId(name,nEvents)
            lfnIds.addFileId(lfnId)

    return lfnIds

#---------------------------------------------------------------------------------------------------
#  M A I N
#---------------------------------------------------------------------------------------------------
catalog = "/home/cmsprod/catalog/t2mit"

book = sys.argv[1]
pattern = ''
if len(sys.argv) > 2:
    pattern = sys.argv[2]

# hi, here we are!
os.system("date")

# make a list of all crab directories
allDatasets = []
if pattern == '':
    print ' Find all datasets.'
else:
    print ' Find all datasets matching %s.'%(pattern)

cmd = 'list ' + TRUNC + DIR + "/" + book
if pattern != "":
    cmd += "| grep %s"%(pattern)

if DEBUG>0:
    print ' CMD: ' + cmd

for line in os.popen(cmd).readlines():
    f = (line[:-1].split("/"))[-1:]
    dataset = "/".join(f)
    allDatasets.append(dataset)

    #print ' Found Dataset: ' + dataset

    lfnIds = findLfns(dataset)

    # check whether we oaded correctly
    uniqueLfnIds = lfnIds.getIds()
    if len(uniqueLfnIds) > 0:
        if DEBUG>0:
            print '  --> %d lfns'%(len(uniqueLfnIds))        

    # now from the catalog
    catalogedIds = loadCatalog(catalog,book,dataset)
    #catalogedIds.show()

    # check for duplicated Ids and remove them
    duplicatedIds = catalogedIds.getDuplicatedIds()
    #catalogedIds.showDuplicates()
    if len(duplicatedIds) > 0:
        removePatternsFromCatalog(catalog,book,dataset,duplicatedIds)

    # test whether event counts are good
    incompleteIds = {}
    uniqueIds = catalogedIds.getIds()
    for id in sorted(uniqueIds):
        nEventsLfn = lfnIds.getFileId(id).nEvents
        nEvents = catalogedIds.getFileId(id).nEvents
        if nEvents != nEventsLfn:
            if DEBUG>0:
                print " ERROR(%s) -- count is different  %d  !=  %d"%(id,nEventsLfn,nEvents)
            incompleteIds[id] = 1

    if len(incompleteIds) > 0:
        removePatternsFromCatalog(catalog,book,dataset,incompleteIds)

    print '  --> %6d/%6d/%6d incomplete/unique/total - %s'%(len(incompleteIds),len(uniqueIds),len(uniqueLfnIds),dataset)


print ' Number of datasets found: %d'%(len(allDatasets))
