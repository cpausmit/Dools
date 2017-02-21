#!/bin/bash
#===================================================================================================
#
# make sure we have a certificate valid for sufficiently long. First parameter is the minimum
# required in seconds, default is 100,000 seconds
#
#===================================================================================================
# determine what the minimum of seconds required are
minimum=100000
if [ "$1" != "" ]
then
  minimum=$1
fi

# determine how much time is left (in seconds)
timeleft=`voms-proxy-info -timeleft 2> /dev/null`

# check whether the certificate is valid for long enough
if [ -z "$timeleft" ] || (( $timeleft < $minimum ))
then
  if ! [ -z $DEBUG ]
  then
    echo " DEBUG - Re-initialize proxy."
  fi
  voms-proxy-init --quiet --valid 168:00 -voms cms
else
  if ! [ -z $DEBUG ]
  then
    echo " DEBUG - Proxy is still valid for $timeleft second."
  fi
fi
