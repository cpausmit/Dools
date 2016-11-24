#!/usr/bin/python
#===================================================================================================
# Add a new dataset into the Bambu database.
#
# v1.0                                                                                  Sep 19, 2014
#===================================================================================================
import sys,os,subprocess,getopt
import MySQLdb
import rex
import json

def convertSizeToGb(sizeTxt):

    # first make sure string has proper basic format
    if len(sizeTxt) < 3:
        print ' ERROR - string for sample size (%s) not compliant. EXIT.'%(sizeTxt)
        sys.exit(1)

    if sizeTxt.isdigit(): # DAS decides to give back size in bytes
        sizeGb = int(sizeTxt)/1000./1000./1000.        
    else:              # DAS gives human readable size with unit integrated
        # this is the text including the size units, that need to be converted
        sizeGb  = float(sizeTxt[0:-2])
        units   = sizeTxt[-2:]
        # decide what to do for the given unit
        if   units == 'MB':
            sizeGb = sizeGb/1000.
        elif units == 'GB':
            pass
        elif units == 'TB':
            sizeGb = sizeGb*1000.
        else:
            print ' ERROR - Could not identify size. EXIT!'
            sys.exit(0)

    # return the size in GB as a float
    return sizeGb

def getProxy():
    cmd = 'voms-proxy-info -path'
    for line in subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.readlines():
        proxy = line[:-1]
    
    return proxy

def testLocalSetup(dataset,debug=0):
    # test all relevant components and exit is something is off

    # check the user proxy
    rc = os.system("voms-proxy-info -exists")

    if debug > 0:
        print 'Return code: %d'%(rc)

    if rc==0:
        if debug > 0:
            print ' User proxy is valid.'
    else:
        print ' Error - no valid proxy. EXIT!'
        sys.exit(1)

    # check the input parameters
    if dataset == '':
        print ' Error - no dataset specified. EXIT!\n'
        print usage
        sys.exit(1)

    # check basic dataset parameters
    if dataset[0] != '/':
        dataset = '/' + dataset.replace('+','/')
        print " DATASET: " + dataset
    f = dataset.split('/')
    if len(f) != 4 or f[0] != '':
        print '\n ERROR in dataset format. Please check dataset name.\n'
        print usage
        sys.exit(1)
	
    # check das_client.py tool
    cmd = 'which das_client'
    for line in subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.readlines():
        line    = line[:-1]
    if line != "":
        if debug > 0:
            print ' Using das_client from: ' + line
    else:
        print ' Error - das_client in your path, please find it and add it to PATH. EXIT!'
        sys.exit(1)

    return dataset

def removeDataset(db,datasetId,debug=0):

    cursor = db.cursor()

    # Prepare SQL query to REMOVE existing record from the database.
    sql = "delete from Requests where DatasetId=%d"%(datasetId)
    
    if debug>0:
        print ' delete: ' + sql

    try:
        # Execute the SQL command
        cursor.execute(sql)
    except:
        print ' ERROR -- delete in Requests table failed.'
        sys.exit(1)

    sql = "delete from Datasets where DatasetId=%d"%(datasetId)

    if debug>0:
        print ' delete: ' + sql

    try:
        # Execute the SQL command
        cursor.execute(sql)
    except:
        print ' ERROR -- delete in Datasets table failed.'
        sys.exit(1)

    return 0

def selectDataset(db,process,setup,tier,debug=0):

    # Prepare SQL query to SELECT existing record from the database.
    sql = "select * from Datasets where DatasetProcess='%s' and DatasetSetup='%s' "%(process,setup) \
        + "and DatasetTier='%s'"%(tier)

    cursor = db.cursor()

    if debug>0:
        print ' select: ' + sql

    try:
        # Execute the SQL command
        cursor.execute(sql)
        results = cursor.fetchall()
    except:
        print " Error (%s): unable to fetch data."%(sql)
        sys.exit(0)

    return results

def insertDataset(db,process,setup,tier,dbsInst,sizeGb,nFiles,debug=0):
    
    # Prepare SQL query to INSERT a new record into the database.
    sql = "insert into Datasets(" \
        + "DatasetProcess,DatasetSetup,DatasetTier,DatasetDbsInstance,DatasetSizeGb,DatasetNFiles" \
        + ") values('%s','%s','%s','%s',%f,%d)"%(process,setup,tier,dbsInst,sizeGb,nFiles)
    
    if debug>0:
        print ' insert: ' + sql

    try:
        # Execute the SQL command
        db.cursor().execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        print ' ERROR -- insert failed, rolling back.'
        # Rollback in case there is any error
        db.rollback()
        sys.exit(1)

    return 0

def updateDataset(db,process,setup,tier,sizeGb,nFiles,debug=0):

    # Prepare SQL query to UPDATE existing record from the database.
    sql = "update Datasets set DatasetSizeGb=%f, DatasetNFiles=%d where "%(sizeGb,nFiles) + \
        " DatasetProcess='%s' and DatasetSetup='%s' and DatasetTier='%s'"%(process,setup,tier)

    cursor = db.cursor()

    if debug>0:
        print " Sql: " + sql

    try:
        # Execute the SQL command
        cursor.execute(sql)
        print ' database entry was updated.'
    except:
        print ' Error (%s) -- update failed.'%(sql)
        sys.exit(1)

    return 0

def isDatasetValid(dataset,dbsInst,debug=0):
    # test whether this dataset is a valid dataset

    proxy = getProxy()
    #url = '/usr/bin/curl -s --cert %s -k -H "Accept: application/json"'%proxy \
    #    + ' "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/'  \
    #    + 'datasets?instance=%s&dataset_access_type=VALID&dataset=%s"'%(dbsInst,dataset)
    url = 'curl -s --cert %s -k -H "Accept: application/json"'%proxy \
        + ' "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/'  \
        + 'datasets?dataset_access_type=VALID&dataset=%s"'%(dataset)

    if debug>1:
        print ' CURL: ' + url

    nTries = 0
    dbsList = 'FAKE CMSWEB Error FAKE'
    while 'CMSWEB Error' in dbsList and nTries < 4:

        if nTries>0 and debug>1:
            print ' CMSWEB error -- RETRY -- %d'%nTries

        process = subprocess.Popen(url,stdout=subprocess.PIPE,shell=True)
        dbsList, error = process.communicate()

        if process.returncode != 0 or nTries > 2:
            print " Received non-zero exit status: " + str(process.returncode)
            raise Exception(" ERROR -- Call to dbs failed, stopping!")

        nTries += 1

    if debug>1:
        print ' dbsList: ' + dbsList

    datasetValid = True
    if dbsList == '[]':
        datasetValid = False

    return datasetValid

def findDatasetProperties(dataset,dbsInst,debug=0):
    # test whether this is a legitimate dataset by asking DAS and determine size and number of files

    if not isDatasetValid(dataset,dbsInst,debug):
        return (-1,-1)

    proxy = getProxy()
    #url = '/usr/bin/curl -s --cert %s -k -H "Accept: application/json"'%proxy \
    #    + ' "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/'  \
    #    + 'files?instance=%s&dataset_access_type=VALID&dataset=%s&detail=true"'%(dbsInst,dataset)
    url = 'curl -s --cert %s -k -H "Accept: application/json"'%proxy \
        + ' "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/'  \
        + 'files?dataset=%s&detail=true"'%(dataset)

    myRex = rex.Rex()
    (rc,out,err) = myRex.executeLocalAction(url)

    if rc != 0:
        print ' ERROR ocurred in %s'%(url)
        sys.exit(1)

    data = json.loads(out)

    units = 'GB'
    nFiles = 0
    totalSize = 0
    for entry in data:
        valid = int(entry["is_file_valid"])
        fileName = entry["logical_file_name"]
        size = int(entry["file_size"])
        if valid == 1:
            nFiles += 1
            totalSize += size
            #print '%s: %d %f'%(fileName,nFiles,totalSize/1000./1000./1000.)

    try:
        sizeGb = convertSizeToGb(str(totalSize))
    except:
        print '\n Error - could not convert size and number of files (%s %s / %s).'\
            %(totalSize,units,nFiles)
        sys.exit(1)

    print '\n DBS - %s --> %.1f %s (nFiles: %d)\n'%(dataset,sizeGb,units,nFiles)
#    
#     
#
#    #cert = "--cert ~/.globus/usercert.pem --key ~/.globus/userkey.pem "
#    cmd = 'das_client --format=plain --limit=0 --query="file dataset=' \
#        + dataset + ' status=valid instance=' + dbsInst \
#        + ' | count(file), sum(file.size)"| sort -u'    
#    nFiles = ''
#    size = ''
#    line = ''
#    units = 'GB'
#
#    if debug>1:
#        print " CMD " + cmd
#
#    for line in subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.readlines():
#        line    = line[:-1]
#        f = line.split('=')
#        if f[0] == 'count(file)':
#            nFiles = f[1]
#        if f[0] == 'sum(file.size)':
#            size = f[1]
#
#    if line != '':
#        try:
#            #print ' SIZE %s  NFILES: %s'%(size,nFiles)
#                # this is the text including the size units, that need to be converted
#            sizeGb = convertSizeToGb(size)
#            #print ' SIZE %f'%(sizeGb)
#            nFiles = int(nFiles)
#            #print ' NFiles %d'%(nFiles)
#        except:
#            print '\n Error - could not convert size and number of files (%s %s / %s).'\
#                %(size,units,nFiles)
#            sys.exit(1)
#        print '\n DAS - %s --> %.1f %s (nFiles: %d)\n'%(dataset,sizeGb,units,nFiles)
#    else:
#	print '\n Error - dataset not found with das_client.\n'
#	sys.exit(1)

    return (sizeGb, nFiles)
    
#===================================================================================================
# Main starts here
#===================================================================================================
# Define string to explain usage of the script
usage =  " Usage: addDataset.py  --dataset=<name>\n"
usage += "                     [ --dbs='prod/global' ]\n"
usage += "                     [ --debug=0 ]\n"
usage += "                     [ --exec ]\n"
usage += "                     [ --help ]\n\n"

# Define the valid options which can be specified and check out the command line
valid = ['dataset=','dbs=','debug=','exec','help']
try:
    opts, args = getopt.getopt(sys.argv[1:], "", valid)
except getopt.GetoptError, ex:
    print usage
    print str(ex)
    sys.exit(1)

# --------------------------------------------------------------------------------------------------
# Get all parameters for the production
# --------------------------------------------------------------------------------------------------
# Set defaults for each command line parameter/option
debug = 0
dataset  = ''
dbsInst = 'prod/global'
exe = False

# Read new values from the command line
for opt, arg in opts:
    if opt == "--help":
        print usage
        sys.exit(0)
    if opt == "--dataset":
        dataset = arg
    if opt == "--dbs":
        dbsInst = arg
    if opt == "--debug":
        debug = arg
    if opt == "--exec":
        exe = True

dataset = testLocalSetup(dataset,debug)

# Open database connection
db = MySQLdb.connect(read_default_file="/etc/my.cnf",read_default_group="mysql",db="Bambu")
# Prepare a cursor object using cursor() method
cursor = db.cursor()

# Decompose dataset into the three pieces (process, setup, tier)
f = dataset.split('/')
process = f[1]
setup   = f[2]
tier    = f[3]

# First check whether this download request already exists in the database
results = selectDataset(db,process,setup,tier,debug)

# Check the dataset in dbs (DAS)
(sizeGb, nFiles) = findDatasetProperties(dataset,dbsInst,debug)
if sizeGb < 0:
    print ' Dataset does not exist or is invalid (%s).'%dataset
    if len(results) > 0:
        print ' Dataset was found in Bambu database. (nResults=%d)'%(len(results))
        rc = 0
        for row in results:
            datasetId = int(row[0])
            if exe:
                rc = removeDataset(db,datasetId,debug)
            else:
                print ' not removing dataset: use --exec option'
        if rc == 0:
            print ' Invalid dataset successfully removed from Bambu database (%s).'%(dataset)
        else:
            print ' Error removing invalid dataset from Bambu database (%s).'%(dataset)
    sys.exit(0)

# Dataset is valid now see what remains to be done
if len(results) == 1:
    print ' Dataset exists in database. Will update properties now.\n'
    for row in results:
        process = row[1]
        setup = row[2]
        tier = row[3]
        dbsInst = row[4]
        dbSizeGb = float(row[5])
        dbNFiles = int(row[6])
    # check whether information correct and adjust if needed
    if dbSizeGb != sizeGb or dbNFiles != nFiles:
        print " Update!  Size: %.3f -> %.3f  nFiles: %d -> %d"%(dbSizeGb,sizeGb,dbNFiles,nFiles)
        rc = 0
        if exe:
            rc = updateDataset(db,process,setup,tier,sizeGb,nFiles,debug)
        else:
            print ' not updating dataset: use --exec option'

        if rc == 0:
            print ' Updated dataset successfully in Bambu database (%s).'%(dataset)
        else:
            print ' Error updating dataset in Bambu database (%s).'%(dataset)
    else:
        print " Database is up to date.\n"
    sys.exit(0)

elif len(results) > 1:
    print ' Dataset exists already multiple times in database. ERROR please fix.'
    sys.exit(0)

rc = 0 
if exe:
    rc = insertDataset(db,process,setup,tier,dbsInst,sizeGb,nFiles,debug)
else:
    print ' not inserting dataset: use --exec option'

if rc == 0:
    print ' New dataset successfully inserted into the database (%s).'%(dataset)
else:
    print ' Error inserting dataset (%s).'%(dataset)

# disconnect from server
db.close()
