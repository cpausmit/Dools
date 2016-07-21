#!/bin/bash

book="$1"
if [ "$book" == "" ]
then
  echo " Please specify book: ex. filefi/044"
  exit 1
fi

# based on data on tier-2

hadoop=/cms/store/user/paus/$book
dsets=`t2tools.py --action ls --source $hadoop | sed "s@.*$book/@@"`
mybook=`echo $book | tr / ' '`
for dset in $dsets
do
  echo "$mybook $dset $REMOVE"
done
