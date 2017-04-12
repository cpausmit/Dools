#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Renew ticket with full lifetime (170 hours) if it is valid for less than <nHours>.
#---------------------------------------------------------------------------------------------------
usage=" usage:  vomit.sh  [ <nHours>=100 ]"
nHours="$1"
re='^[0-9]+$'

if [ -z "$nHours" ]
then
  nHours=170
elif ! [[ $nHours =~ $re ]]
then
  echo " ERROR - Not a number: $nHours" >&2
  echo " Please specify minimal number of hours required." >&2
  exit 1
fi

nHoursLeft=`voms-proxy-info -timeleft`
nHoursLeft=`expr $nHoursLeft / 3600`

if [[ $nHoursLeft -lt $nHours ]]
then
  echo " INFO - re-newing ticket for $nHours hr"
  voms-proxy-init --valid 170:00 -voms cms >& /dev/null
  rc=$?
  nHoursLeft=`voms-proxy-info -timeleft`
  nHoursLeft=`expr $nHoursLeft / 3600`
  echo " -RC: $rc- $nHoursLeft hr"
else
  echo " INFO - hours left: $nHoursLeft hr (requested are $nHours hr)."
fi

exit 0
