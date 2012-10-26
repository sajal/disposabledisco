from boto.ec2.connection import EC2Connection
from utils.make_init_script import make_init_script


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
        reservation = self.conn.get_all_instances(filters={"instance-id": instance_id})
        if len(reservation) < 1:
            return None
        if len(reservation[0].instances) < 1:
            return None
        return reservation[0].instances[0].state

    def kill_cluster(self):
        """
        Kills all instances
        """
        for spot in self.get_instances():
            spot.cancel()
            instance_id = spot.instance_id
            for reservation in self.conn.get_all_instances(filters={"instance-id": instance_id}):
                for instance in reservation.instances:
                    instance.terminate()

    def launch_master(self):
        """
        Launches a master instance
        """
        init_script = make_init_script(self.config, open("master-init.sh", "r").read())
        sr = self.conn.request_spot_instances(
            price=self.config["MAX_BID"],
            image_id = self.config["AMI"],
            count = 1,
            type = 'one-time',
            user_data = init_script,
            instance_type = self.config.get("MASTER_INSTANCE_TYPE", self.config["INSTANCE_TYPE"]),
            security_groups = self.config["SECURITY_GROUPS"]
        )
        sp = sr[0]
        sp.add_tag(self.config["TAG_KEY"], "master")
        print sp, sp.tags


    def launch_slaves(self, count):
        """
        TODO: Launch count slaves...
        Perhaps only after master is ready...
        """
        pass

    def get_master_pub_key(self):
        """
        TODO: Get public key from master, to install on slave
        """
        pass

    def initiate_slave(self):
        """
        Todo: Bootstrap a slave into the cluster
        1) Load masters pub key
        2) ssh into master, scp erlang cookie
        3) Add slave's hostname into disco config
        """
        pass

    def print_ssh_line(self):
        """
        TODO: Print the ssh command to connect to master and open a tunnel.
        Also print command for exporting DISCO_PROXY variable
        """
        pass