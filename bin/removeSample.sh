#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Remove an existing sample from disk, catalog and the request database.
#
#---------------------------------------------------------------------------------------------------
function usage {
  echo ""
  echo " "`basename $0`" <book>  <dataset>  [ <location> = T2MIT, '' ] "
  echo ""
  echo "   book     - book of the sample in question. Example: filefi/041"
  echo "   dataset  - name of the sample in question. Example: JetHT+Run2015B-PromptReco-v1+AOD"
  echo ""
  exit 0
}

BASE_LFN=/cms/store/user/paus
CATALOG=~cmsprod/catalog
SERVER="srm://se01.cmsaf.mit.edu:8443/srm/v2/server?SFN="

RMT2="rglexec hdfs   dfs -rm -r"
RMT3="        hdfs   dfs -rm -r"

BOOK="$1"
SAMPLE="$2"
LOCATION="$3"

# make sure parameters make sense
if [ "$BOOK" == "" ] || [ "$SAMPLE" == "" ]
then
  echo ""
  echo " Sample and book have to be defined.... "
  usage
else
  echo ""
  echo " Removing sample: $SAMPLE from book: $BOOK"
  echo ""
fi

# remove the remote physical files
echo " CMD: $RMT2 $BASE_LFN/${BOOK}/$SAMPLE"
$RMT2 $BASE_LFN/${BOOK}/$SAMPLE >& /dev/null
echo " Return code from Tier2: $?"
echo ""

# remove the local physical files in the cache (Tier-3)
echo " CMD: $RMT3 $BASE_LFN/${BOOK}/$SAMPLE"
$RMT3 $BASE_LFN/${BOOK}/$SAMPLE >& /dev/null
echo " Return code from Tier3: $?"
echo ""

# remove catalogs
if [ -d $CATALOG/t2mit/$BOOK/$SAMPLE ]
then
  echo " rm -rf $CATALOG/t2mit/$BOOK/$SAMPLE"
  rm -rf $CATALOG/t2mit/$BOOK/$SAMPLE
  echo "# NOT DOING IT "
else
  echo " THERE IS NO CATALOG"
fi

exit 0
