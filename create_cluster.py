import json, sys
from disposabledisco import  DisposableDisco
config = json.loads(open(sys.argv[1], "r").read())


if __name__ == "__main__":
    d = DisposableDisco(config)
    spots = d.get_instances()
    for spot in spots:
        print "%s\t%s\t%s\t%s" %spot
    masterstate = d.get_master_status()
    print "Status of master is %s" %(masterstate)
    if masterstate is None:
        print "Launching Master"
        d.launch_master()
    elif masterstate == "requested":
        print "Waiting for master to launch."
    elif masterstate == "running":
        sshline, proxyline = d.get_ssh_line()
        print "SSH to master using : %s" %sshline
        print "Set proxy env using : %s" %proxyline
        bootstrapped, running, pending = d.get_valid_slaves()
        print "%s slaves bootstrapped" %(len(bootstrapped))
        print "%s slaves running" %(len(running))
        print "%s slaves pending" %(len(pending))
        tolaunch = config["NUM_SLAVES"] - len(pending) - len(running) - len(bootstrapped)
        print "need to launch %s slaves" %(tolaunch)
        if tolaunch > 0:
            print "Launching %s instances" %(tolaunch)
            d.launch_slaves(tolaunch)
        d.initiate_slaves()
        print "Overwriting config: %s" %(d.reconfigure_disco())

    """
    print d.get_master_instance()
    print d.get_master_pub_host()
    print d.get_ssh_line()
    print d.get_master_private_host()
    print d.get_master_pub_key()
    print d.kill_cluster()
    #print d.launch_master()
    #Check if master is already running...
    """
