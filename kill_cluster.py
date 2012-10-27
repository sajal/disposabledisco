import json, sys
from disposabledisco import  DisposableDisco
config = json.loads(open(sys.argv[1], "r").read())


if __name__ == "__main__":
    d = DisposableDisco(config)
    d.kill_cluster()