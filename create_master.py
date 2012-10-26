import json, sys
from disposabledisco import  DisposableDisco
config = json.loads(open(sys.argv[1], "r").read())


if __name__ == "__main__":
    d = DisposableDisco(config)
    #print d.get_instances()
    #print d.launch_master()
    #Check if master is already running...
