#!/usr/bin/env python
import os,re,pprint,subprocess,sys,datetime
import MySQLdb
import fileIds

DEBUG = int(os.environ.get('T2TOOLS_DEBUG',0))

TRUNC = "/cms"
DATA = "/store/user/paus"
CATA = "/home/cmsprod/catalog/t2mit"

Db = MySQLdb.connect(read_default_file="/etc/my.cnf",read_default_group="mysql",db="Bambu")
Cursor = Db.cursor()

usage = "\n   usage:  generateCatalogs.py  <book>  <pattern>  [ <nFilePerSet> ]\n"

#===================================================================================================
#  H E L P E R S
#===================================================================================================
def getFiles(book,dataset):
    # get all corresponding files

    version = book.split('/')[1]
    mitcfg = book.split('/')[0]

    # decode the dataset
    f = dataset.split('+')
    process = f[0]
    setup = f[1]
    tier = f[2]

    sql = "select FileName, NEvents from Files inner join Requests on " \
        + " Files.RequestId = Requests.RequestId inner join Datasets on " \
        + " Requests.DatasetId = Datasets.DatasetId where " \
        + " DatasetProcess = '%s' and DatasetSetup='%s' and DatasetTier='%s'"%(process,setup,tier) \
        + " and RequestConfig = '%s' and RequestVersion = '%s'"%(mitcfg,version)

    results = []
    try:
        # Execute the SQL command
        Cursor.execute(sql)
        results = Cursor.fetchall()
    except:
        print 'ERROR(%s) - could not find request id.'%(sql)

    # found the request Id
    catalogedIds = fileIds.fileIds()
    for row in results:
        fileId = row[0]
        nEvents = int(row[1])

        catalogedId = fileIds.fileId(fileId,nEvents)
        catalogedIds.addFileId(catalogedId)

    return catalogedIds

def writeRawFile(rawFile,book,dataset):
    # get all corresponding files

    nFiles = 0

    with open(rawFile,'w') as fHandle:
        #fHandle.write('# SAMPLE: %s - %s\n'%(book,dataset)) # this is confusing
        catalogedIds = getFiles(book,dataset)

        for id in sorted(catalogedIds.getIds()):
            fileId = catalogedIds.getFileId(id)
            nEvents = fileId.getNEvents()
            fileName = fileId.getFileName()
            fHandle.write('root://xrootd.cmsaf.mit.edu//store/user/paus/%s/%s/%s %d %d 1 1 1 1\n' \
                              %(book,dataset,fileName,nEvents,nEvents))
            nFiles += 1

    return nFiles

def makeCatalog(dir,nFilesPerSet):

    cmd = 'cat ' + dir + '/RawFiles.?? | grep root | sort -u'

    init = False
    iFileset = 0
    fileset = None

    filesetsOut = open(dir + '/Filesets','w')
    with open(dir + '/Files','w') as filesOut:
        for line in os.popen(cmd).readlines():  # run command
            line = line[:-1]
            line = " ".join(str(line).split()).strip()
            f = line.split(' ')
            g = f[0].split('/')
            dataDir  = '/'.join(g[:-1])

            if not init:
                fileset = fileIds.fileIdSet('0000',dataDir)
                init = True

            fileName = g[-1]
            if len(f) != 7:
                print ' Length is not six: %d'%len(f)
                sys.exit(1)

            file = fileIds.fileId(fileName,int(f[1]),int(f[2]),int(f[3]),int(f[4]),int(f[5]),int(f[6]));

            if (fileset.nFiles()<nFilesPerSet):
                fileset.addFile(file)
            else:
                fileset.showShort(filesetsOut,DEBUG)
                fileset.showShortFiles(filesOut,DEBUG)
                iFileset = iFileset + 1
                name     = '%04d'%iFileset
                fileset.reset(name,dataDir)
                fileset.addFile(file)

        # complete what you started (will never be empty if init is set)
        if init:
            fileset.showShort(filesetsOut,DEBUG)
            fileset.showShortFiles(filesOut,DEBUG)
            iFileset = iFileset + 1

    filesetsOut.close()

#===================================================================================================
#  M A I N
#===================================================================================================
# make sure command line is complete
if len(sys.argv) > 4 or  len(sys.argv) < 3:
    print " ERROR -- number of arguments." + usage
    sys.exit(1)

# command line variables
book = sys.argv[1]
pattern = sys.argv[2]
nEventsPerSet = -1
if len(sys.argv) > 3:
    nEventsPerSet = sys.argv[3]

cmd = 'list ' + TRUNC + DATA + "/" + book
if pattern != "":
    cmd += "| grep %s"%(pattern)

allDatasets = []
for line in os.popen(cmd).readlines():
    f = (line[:-1].split("/"))[-1:]
    dataset = "/".join(f)
    allDatasets.append(dataset)

print ' Number of datasets found: %d'%(len(allDatasets))

# loop over all matching datasets
for dataset in allDatasets:

    print ' --> %s'%(dataset)

    catalogDir = '%s/%s/%s'%(CATA,book,dataset)
    os.system('mkdir -p %s'%catalogDir)
    rawFile = '%s/RawFiles.00'%(catalogDir)
    nFiles = writeRawFile(rawFile,book,dataset)

    # decide how many files per fileset
    if nEventsPerSet > 0:
        makeCatalog(catalogDir,nEventsPerSet)
    else:
        if   nFiles > 400:
            makeCatalog(catalogDir,10)
        elif nFiles > 200:
            makeCatalog(catalogDir,5)
        else:
            makeCatalog(catalogDir,2)
