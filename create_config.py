import json, os


try:
    pubkey = open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()
except:
    pubkey = "FILL THIS"

BASE_CONFIG = {
    "BASE_PACKAGES": ["python-pip", "python-dev", "lighttpd"],
    "ADDITIONAL_PACKAGES" : ["git", "libwww-perl", "mongodb-clients", "python-numpy", "python-scipy", "libzmq-dev", "s3cmd", "ntp", "libguess1", "python-dnspython", "python-dateutil", "pigz"],
    "PIP_REQUIREMENTS" : ["iso8601"],
    "AWS_ACCESS" : "IMPORTANT FILL THIS!!!1",
    "AWS_SECRET" : "IMPORTANT FILL THIS!!!1",
    "AMI" : "ami-6d3f9704",
    "MAX_BID" : "0.10",
    "INSTANCE_TYPE" : "c1.xlarge",
    "KEY_NAME" : "",
    "SECURITY_GROUPS" : [],
    "MGMT_KEY": pubkey,
    "TAG_KEY": "disposabledisco",
    "NUM_SLAVES" : 0,
    "MASTER_MULTIPLIER": 1,
    "SLAVE_MULTIPLIER": 1
}

print json.dumps(BASE_CONFIG, indent=4)