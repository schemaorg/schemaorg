#!/bin/sh

# first the general development site
appcfg.py update .   -A webschemas-g

# then the release-specific one
### not so needed: 
### 
##### appcfg.py update .   -A sdo-deimos

appcfg.py update .   -A sdo-callisto
