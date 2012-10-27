from boto.ec2.connection import EC2Connection
from utils.make_init_script import make_init_script
import paramiko
from time import sleep


INSTANCE_TYPES = {
    "m1.small": 1,
    "m1.medium": 1,
    "m1.large": 2,
    "m1.xlarge": 4,
    "t1.micro": 1,
    "m2.xlarge": 2,
    "m2.2xlarge": 4,
    "m2.4xlarge": 8,
    "c1.medium": 2,
    "c1.xlarge": 8,
    "cc1.4xlarge": 16,
    "cc2.8xlarge": 32,
    "cg1.4xlarge": 16,
    "hi1.4xlarge": 16
}


class WarningPolicy(paramiko.WarningPolicy):
    def missing_host_key(self, client, hostname, key):
        """
        Dont know if security risk or not..
        """
        pass

class DisposableDisco():
    def __init__(self, config):
        self.config = config
        self.conn = EC2Connection(config.get("AWS_ACCESS"), config.get("AWS_SECRET"))

    def get_instances(self):
        """
        Lists all spot instances tagged with the configured tag
        """
        spots = self.conn.get_all_spot_instance_requests(filters={"tag-key": self.config["TAG_KEY"]})
        instances = []
        for req in spots:
            instances +=  [(req.tags[self.config["TAG_KEY"]], req,  req.instance_id, self.get_instance_state(req.instance_id))]
        return instances

    def get_instance_state(self, instance_id):
        """
        Gets actual instance details
        """
        instance = self.get_instance_from_name(instance_id)
        if instance:
            return instance.state

    def get_instance_from_name(self, instance_id):
        reservation = self.conn.get_all_instances(filters={"instance-id": instance_id})
        if len(reservation) < 1:
            return None
        if len(reservation[0].instances) < 1:
            return None
        return reservation[0].instances[0]


    def get_master_status(self):
        """
        Returns one off None, requested, pending or running
        """
        spots = self.get_instances()
        status = None
        for spot in spots:
            if spot[0] == "master":
                if spot[3] == "running":
                    return "running"
                elif spot[1].state == "open":
                    status = "requested"
        return status

    def get_valid_slaves(self):
        running = []
        pending = []
        bootstrapped = []
        for spot in self.get_instances():
            if spot[0].startswith("slave"):
                #This is indeed a slave..
                if spot[3] == "running":
                    if "init" in spot[0]:
                        bootstrapped += [spot]
                    else:
                        running += [spot]
                elif spot[3] == "pending":
                    pending += [spot]
                elif spot[1].state == "open":
                    pending += [spot]
        return bootstrapped, running, pending



    def kill_cluster(self):
        """
        Kills all instances
        """
        for spot in self.get_instances():
            spot[1].cancel()
            print "Killing", spot[1]
            instance_id = spot[2]
            if instance_id is not None:
                for reservation in self.conn.get_all_instances(filters={"instance-id": instance_id}):
                    for instance in reservation.instances:
                        instance.terminate()
                        print "killing", instance

    def launch_master(self):
        """
        Launches a master instance
        """
        #Kill all instances, this will be fresh cluster
        self.kill_cluster()
        init_script = make_init_script(self.config, open("master-init.sh", "r").read())
        sr = self.conn.request_spot_instances(
            price=self.config["MAX_BID"],
            image_id = self.config["AMI"],
            count = 1,
            type = 'one-time',
            key_name= self.config["KEY_NAME"],
            user_data = init_script,
            instance_type = self.config.get("MASTER_INSTANCE_TYPE", self.config["INSTANCE_TYPE"]),
            security_groups = self.config["SECURITY_GROUPS"]
        )
        sp = sr[0]
        sp.add_tag(self.config["TAG_KEY"], "master")
        #This sleep is intentional. Spot request api seems to be eventually consistent
        sleep(15)
        return sp, sp.tags

    def get_master_instance(self):
        """
        Iterate thru all spot requests tagged as master, and return the current active master
        """
        for item in self.get_instances():
            if item[0] == "master":
                if item[2]:
                    reservation = self.conn.get_all_instances(filters={"instance-id": item[2]})
                    if len(reservation[0].instances) > 0:
                        if reservation[0].instances[0].state == "running":
                            return reservation[0].instances[0]

    def get_master_pub_host(self):
        """
        Get public hostname of master so we can connect to it for dev
        """
        instance = self.get_master_instance()
        if instance:
            return instance.public_dns_name

    def get_master_private_host(self):
        """
        Get hostname of master, the one we use in disco config. Cant be FQDN :(
        """
        instance = self.get_master_instance()
        if instance:
            return instance.private_dns_name.split(".")[0]


    def launch_slaves(self, count):
        """
        TODO: Launch count slaves...
        Perhaps only after master is ready...
        """
        master_pub_key = self.get_master_pub_key()
        if master_pub_key:
            #Master is ready...
            init_script = make_init_script(self.config, open("slave-init.sh", "r").read(), master_pub_key=master_pub_key)

            sr = self.conn.request_spot_instances(
                price=self.config["MAX_BID"],
                image_id = self.config["AMI"],
                count = count,
                type = 'one-time',
                key_name= self.config["KEY_NAME"],
                user_data = init_script,
                instance_type = self.config.get("SLAVE_INSTANCE_TYPE", self.config["INSTANCE_TYPE"]),
                security_groups = self.config["SECURITY_GROUPS"]
            )
            sp = sr[0]
            sp.add_tag(self.config["TAG_KEY"], "slave")
            #This sleep is intentional. Spot request api seems to be eventually consistent
            sleep(15)
            return sp, sp.tags
        else:
            print "Master not ready yet..."

    def get_master_pub_key(self):
        """
        Get public key from master, to install on slave
        """
        master = self.get_master_pub_host()
        if master:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(WarningPolicy())
            client.connect(master, 22, username="disco")
            stdin, stdout, stderr = client.exec_command("cat ~/.ssh/id_dsa.pub")
            pubkey = stdout.readlines()[0]
            client.close()
            if len(pubkey) < 100:
                #Means pubket portion of the script hasnt run yet
                return None
            return pubkey

    def initiate_slaves(self):
        """
        Todo: Bootstrap a slave into the cluster
        1) Load masters pub key (done with init)
        2) ssh into master, scp erlang cookie
        """
        master = self.get_master_pub_host()
        if master:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(WarningPolicy())
            client.connect(master, 22, username="disco")

            bootstrapped, running, pending = self.get_valid_slaves()
            for item in running:
                instance = self.get_instance_from_name(item[2])
                prvt = instance.private_dns_name.split(".")[0]
                command = "scp -o StrictHostKeyChecking=no ~/.erlang.cookie %s:" %(prvt)
                print command
                stdin, stdout, stderr = client.exec_command(command)
                err = stderr.readlines()
                if 'Permission denied (publickey).\r\n' not in err:
                    item[1].add_tag(self.config["TAG_KEY"], value="slave-init")
                else:
                    print err
            client.close()

    def reconfigure_disco(self):
        """
        Change disco's config on master.
        Takes actual multipliers and core count into account...
        """
        config = []
        master = self.get_master_instance()
        if master:
            config += [[master.private_dns_name.split(".")[0] , str(int(INSTANCE_TYPES.get(master.instance_type, 1) * self.config.get("MASTER_MULTIPLIER", 1) ))]]
            bootstrapped, running, pending = self.get_valid_slaves()
            for spot in bootstrapped:
                i = self.get_instance_from_name(spot[2])
                config += [[i.private_dns_name.split(".")[0] , str(int(INSTANCE_TYPES.get(i.instance_type, 1) * self.config.get("SLAVE_MULTIPLIER", 1)))]]
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(WarningPolicy())
            client.connect(master.public_dns_name, 22, username="disco")
            command = """echo "
from disco.core import Disco
d = Disco()
d.set_config(%s)" | python
            """ %(config)
            stdin, stdout, stderr = client.exec_command(command)
        return config
            


    def get_ssh_line(self):
        """
        Print the ssh command to connect to master and open a tunnel.
        Also print command for exporting DISCO_PROXY variable
        Maybe in future open tunnel and export variable directly from here..
        """
        hostname = self.get_master_pub_host()
        if hostname:
            sshline = "ssh disco@%s -L 8090:localhost:8999" %(hostname)
            proxyline = "export DISCO_PROXY=http://localhost:8090"
            return sshline, proxyline
        return None, None