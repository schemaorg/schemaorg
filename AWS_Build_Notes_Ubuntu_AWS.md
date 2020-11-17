Build Notes for Ubuntu - on an AWS EC2 Instance
===============================================

**AWS Specific Steps**

  * New Ubuntu AMI 
  * Add port 8080 inbound rule for EC2 Instance

**General Ubuntu Steps**

 * sudo apt-get update
 * sudo apt-get upgrade
 * sudo apt-get install git
 * sudo apt-get install python3-pip
 * git clone https://github.com/schemaorg/schemaorg.git
 * cd schemaorg
 * pip3 install -r requirements.txt
 * ./util/buildsite.py -a
 * Run locally: 
   * ./devserv.py --port 8080 --host 0.0.0.0
   * Should be visible via: 
     *  http://{public ip of AWS instance}:8080/

**To enable deployment to a gcloud appengine instance**

* Create or identify previously created Google Cloud Platform User
  * Download cloud SDK from: https://cloud.google.com/sdk/docs/install#deb
  * No need for additional components
  * run cloud init - identify cloud account and default project
* gcloud/deploy2gcloud.sh 


