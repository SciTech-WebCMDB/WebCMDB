#!/bin/bash
cd WebCMDBapi/bash
rm -rf machines
git clone git@github.com:SciTech-WebCMDB/machines.git
cd machines
rm -rf .git
if [ $? -eq 0 ]; then
echo "Fetch OK"
exit 0
else
>&2 echo "Something went wrong"
exit 1
fi