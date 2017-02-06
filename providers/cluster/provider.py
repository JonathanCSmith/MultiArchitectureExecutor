import os

import subprocess

import utils

from providers.Resources import ResourceProvider, Resource


class ClusterProvider(ResourceProvider):
    _username = None
    _key_path = None
    _login_ip = None
    _submitter = None
    __valid = True

    def __init__(self, json_data):
        self._username = json_data["cluster_user"]
        self._key_path = json_data["cluster_key"]
        self._login_ip = json_data["login_ip"]
        self._submitter = json_data["submission_wrapper"]

        # Allow passing of complete file paths or local
        if not os.path.isfile(self._submitter):
            self._submitter = os.path.join(os.path.dirname(os.path.realpath(__file__)), self._submitter)
            if not os.path.isfile(self._submitter):
                self._valid = False

    def acquire_resource(self, ticket):
        return ClusterConnection(self._username, self._key_path, self._login_ip, self._submitter)

    def return_resource(self, ticket):
        pass  # The connection self disposes

    def valid(self):
        return self.__valid


class ClusterConnection(Resource):
    username = None
    key_path = None
    ip = None
    submitter = None

    def __init__(self, username, key_path, ip, submitter):
        self.username = username
        self.key_path = key_path
        self.ip = ip
        self.submitter = submitter

    def execute(self, engine, execution_wrapper, script_arguments, ticket):
        working_directory = engine.get_file_system().get_working_directory()

        # Execute the above script
        p = subprocess.Popen(
            [
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "cluster_job.sh"),
                "-target=" + self.ip,
                "-key=" + self.key_path,
                "-user=" + self.username,
                "-ticket=" + os.path.join(engine.get_file_system().get_monitor_directory(), ticket + ".txt"),
                "-script=" + os.path.join(engine.get_file_system().get_scripts_directory(), execution_wrapper.get_script()),
                "-wd=" + working_directory,
                "-sl=" + os.path.join(engine.get_file_system().get_working_directory(), execution_wrapper.get_script().replace(".", "-") + "_" + self.ip.replace(".", "-") + "_" + ticket + "_log.txt"),
                "-el=" + os.path.join(engine.get_file_system().get_working_directory(), execution_wrapper.get_script().replace(".", "-") + "_" + self.ip.replace(".", "-") + "_" + ticket + "_err.txt"),
                "-parameter_string=\"" + script_arguments + "\"",
                "-remote=" + self.submitter,
                "-c=" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "cluster_cleanup.sh"),
                "-cf=" + os.path.join(os.path.dirname(os.path.realpath(__file__)), "fail_cluster_cleanup.sh")
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
    properties = os.path.join(file_system.get_working_directory(), "cluster_properties.json")
    if not os.path.exists(properties):
        return False

    properties = utils.load_json(properties)
    if not properties:
        return False

    resource_provider = ClusterProvider(properties)
    if not resource_provider:
        return False

    return resource_provider
