#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Ask for full cataloging action.
#---------------------------------------------------------------------------------------------------

# make catalog lists
makeCatalogsList.sh filefi/045 filefi/044 > ~/cms/work/fibs/makeCatalog.list-tmp

#makeCatalogsList.sh filefi/045 filefi/044 fullsm/044 fastsm/043 \
#                    > ~/cms/work/fibs/makeCatalog.list-tmp

# reserve a lock and execute the update
fibsLock.py --cmd="mv ~/cms/work/fibs/makeCatalog.list-tmp ~/cms/work/fibs/makeCatalog.list" \
            --configFile ~/Tools/FiBS/config/makeCatalog.cfg &

exit 0
