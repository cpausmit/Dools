#!/bin/bash

list="$*"

for book in $list
do
  makeCatalogs.sh $book
done
