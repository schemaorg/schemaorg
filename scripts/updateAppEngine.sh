#!/bin/sh


# new:

gcloud app deploy webschemas.yaml --project webschemas-g 

# old:

# first the general development site
#appcfg.py update .   -A webschemas-g
#appcfg.py update webschemas.yaml   -A webschemas-g 

# then the release-specific one
### not so needed: 
### 

# appcfg.py update .   -A sdo-callisto
# prod: appcfg.py update schemaorg.yaml -A schemaorgae
