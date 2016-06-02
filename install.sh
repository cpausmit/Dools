#!/bin/bash
#---------------------------------------------------------------------------------------------------
# Install the dools interface.
#---------------------------------------------------------------------------------------------------

# generate the setup file
rm -f setup.sh
touch setup.sh

# first the base directory and the path
echo "# CAREFUL THIS FILE IS GENERATED AT INSTALL"                >> setup.sh
echo "export DOOLS_DEBUG=0"                                       >> setup.sh
echo "export DOOLS_BASE=`pwd`"                                    >> setup.sh
echo "export PATH=\"\${PATH}:\${DOOLS_BASE}/bin\""                >> setup.sh
echo "export PYTHONPATH=\"\${PYTHONPATH}:\${DOOLS_BASE}/python\"" >> setup.sh

exit 0
