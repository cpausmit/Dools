#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Ask for full cataloging action.
#---------------------------------------------------------------------------------------------------

# make catalog lists
makeCatalogsList.sh filefi/044 > ~/cms/work/fibs/makeCatalog.list-tmp

# reserve a lock an execute the update
fibsLock.py --cmd="mv ~/cms/work/fibs/makeCatalog.list-tmp ~/cms/work/fibs/makeCatalog.list" \
            --configFile ~/Tools/FiBS/config/makeCatalog.cfg &

exit 0
