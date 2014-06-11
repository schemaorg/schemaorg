#!/bin/sh

echo "Branches:\n"
git branch -a
echo "Comparing per-proposal branches with master.\n\n"
git shortlog sdo-itemlist..master
git shortlog sdo-mainentity..master
git shortlog sdo-sports..master

echo "Done.\n\n"

echo "Comparing sdo-meltingpot branch with master.\n\n"

git shortlog sdo-meltingpot..master
