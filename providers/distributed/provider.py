import os

import subprocess

import utils

from providers.Resources import ResourceProvider, Resource


class DistributedMachineProvider(ResourceProvider):
    _mode = "Pool"
    __pool = list()
    __checked_out = dict()

    def __init__(self, json_data):
        self._mode = json_data["VM_Mode"]  # Should only be pool for now
        self._username = json_data["VM_User"]
        self._key_path = json_data["VM_SSH_Key"]
        if self._mode == "Pool":
            for ip in json_data["VM_IP_Addresses"]:
                self.__pool.append(Machine(self._username, self._key_path, ip))

        else:
            raise RuntimeError("Only IP pools are implemented for now")

    def acquire_resource(self, ticket):
        # Check and wait for available IPs
        while len(self.__pool) == 0:
            time.sleep(10)

        vm = self.__pool.pop()
        self.__checked_out[ticket] = vm
        return vm

    def return_resource(self, ticket):
        vm = self.__checked_out.pop(ticket)
        self.__pool.append(vm)


class Machine(Resource):
    username = None
    key_path = None
    ip = None
    current_working_directory = None

    def __init__(self, username, key_path, ip):
        self.username = username
        self.key_path = key_path
        self.ip = ip

    def set_cwd(self, path):
        self.current_working_directory = path

    def verify_cwd(self, engine):
        # Execute the script
        p = subprocess.Popen(
            [
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "cloud_cd.sh"),
                "-target=" + self.ip,
                "-key=" + self.key_path,
                "-user=" + self.username,
                "-path=" + self.current_working_directory
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        for line in p.stdout:
            engine.info(line.strip())

        if p.returncode == 1:
            return False

        return True

    def execute(self, engine, execution_wrapper, script_arguments, ticket):
        self.set_cwd(engine.get_file_system().get_working_directory())
        if not self.verify_cwd(engine):
            engine.error("Could not set the working directory of the VM")
            return False

        # Execute the above script
        p = subprocess.Popen(
            [
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "cloud_job.sh"),
                "-target=" + self.ip,
                "-key=" + self.key_path,
                "-user=" + self.username,
                "-ticket=" + os.path.join(engine.get_file_system().get_monitor_directory(), ticket + ".txt"),
                "-script=" + os.path.join(engine.get_file_system().get_scripts_directory(), execution_wrapper.get_script()),
                "-wd=" + self.current_working_directory,
                "-sl=" + os.path.join(engine.get_file_system().get_working_directory(), execution_wrapper.get_script().replace(".", "-") + "_" + self.ip.replace(".", "-") + "_" + ticket + "_log.txt"),
                "-el=" + os.path.join(engine.get_file_system().get_working_directory(), execution_wrapper.get_script().replace(".", "-") + "_" + self.ip.replace(".", "-") + "_" + ticket + "_err.txt"),
                "-parameter_string=\"" + script_arguments + "\"",
                "-remote=" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "cloud_remote.sh")
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        for line in p.stdout:
            engine.info(line.strip())

        if p.returncode == 1:
            open(os.path.join(engine.get_file_system().get_monitor_directory(), ticket + ".txt"), 'a').close()
            return False

        return True


def build_provider(file_system):
    # Load our properties file
    properties = os.path.join(file_system.get_working_directory(), "cloud_properties.json")
    if not os.path.exists(properties):
        return False

    properties = utils.load_json(properties)
    if not properties:
        return False

    resource_provider = DistributedMachineProvider(properties)
    if not resource_provider:
        return False

    return resource_provider
