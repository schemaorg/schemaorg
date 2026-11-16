Gcloud Deploy Scripts
=====================

To deploy the latest static image‡ of schema.org to various locations hosted on GCloud,
run the appropriate deploy script:

* The schema.org live site † :
      deploy2schema.org.sh

* The staging.schema.org test/preview site † :
      deploy2staging.schema.org.sh

* Any other test site hosted on gcloud made visible at {projectname}.appspot.com
      deploy2gcloud.sh


† Relevant access permissions will be required to deploy to these sites.

‡ To be confident that all changes are deployed, run 'software/scripts/buildsite.py -a --version latest' before deploying a published release (or 'software/scripts/buildsite.py -a' when previewing unreleased 'next' changes).
