Gcloud Deploy Scripts
=====================

To deploy the latest static image‡ of schema.org to various locations hosted on GCloud,
run the appropriate deploy script:

* The schema.org live site † :
      deploy2schema.org.sh

* The webschemas.org test/preview site † :
      deploy2webschemas.org.sh

* Any other test site hosted on gcloud made visible at {projectname}.appspot.com
      deploy2gcloud.sh


† Relevant access permissions will be required to deploy to these sites.

‡ To be confident that all changes are deployed, run the 'util/buildsite.py -a' command before deploying