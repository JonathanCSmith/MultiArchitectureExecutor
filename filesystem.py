import os


class FileSystem:
    _engine = None
    _source_directory = None
    _working_directory = None
    _monitor_directory = None
    _scripts_directory = None
    _output_directory = None

    def __init__(self, source_directory, working_directory=None, scripts_directory=None, output_directory=None):
        self._source_directory = source_directory

        # Set the working directory if it was specified
        if working_directory:
            if not os.path.isdir(working_directory):
                os.makedirs(working_directory)
            self._working_directory = working_directory
            os.chdir(working_directory)
        else:
            self._working_directory = os.getcwd()

        # Build a monitoring directory that we can use to monitor execution progress
        self._monitor_directory = os.path.join(self._working_directory, "monitors")
        if not os.path.isdir(self._monitor_directory):
            os.makedirs(self._monitor_directory)

        # If there is no script directory, we assume all the relevant scripts are in the working directory
        if scripts_directory:
            self._scripts_directory = scripts_directory
        else:
            self._scripts_directory = self._working_directory

        # If there is no output directory, we assume its our working directory
        if output_directory:
            self._output_directory = output_directory
        else:
            self._output_directory = self._working_directory

    def set_engine(self, engine):
        self._engine = engine

    def get_source_directory(self):
        return self._source_directory

    def get_working_directory(self):
        return self._working_directory

    def get_monitor_directory(self):
        return self._monitor_directory

    def get_scripts_directory(self):
        return self._scripts_directory

    def get_output_directory(self):
        return self._output_directory

    def set_output_directory(self, output_directory):
        self._output_directory = output_directory
