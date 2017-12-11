import logging
import os
import threading
import time
import uuid


class Engine:
    _engine_uuid = str(uuid.uuid4())
    _logger = None
    _runtime = None
    _file_system = None

    # Batch properties
    _dead = False
    _locked = False
    _tickets = list()
    _monitor_thread = None

    def __init__(self, file_system):
        self._file_system = file_system
        self._file_system.set_engine(self)
        self._build_logger()

    def _build_logger(self):
        self._logger = logging.getLogger()

        # Prevents multiple handlers when the engine is called more than once per compilation :P
        if len(self._logger.handlers) > 0:
            return

        log_file = os.path.join(self._file_system.get_working_directory(), "PipelineController_" + self._engine_uuid + "_log.txt")
        logging.basicConfig(filename=log_file, filemode="w", level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

    def debug(self, message):
        self._logger.debug(message)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message):
        self._logger.error(message)

    def exception(self, ex):
        self._logger.exception(ex)

    def set_runtime(self, runtime):
        self.info("Set the engine's runtime")
        self._runtime = runtime

    def set_file_system(self, file_system):
        self.info("Set the engine's file system")
        self._file_system = file_system

    def get_file_system(self):
        return self._file_system

    def submit_chunk_and_wait_for_execution(self, batch_size, chunk_size, execute_wrapper):
        # Handle zero chunk sizes - allow 1 as it forces serial processing?!
        if chunk_size == 0:
            return self.submit_batch_and_wait_for_execution(batch_size, execute_wrapper)

        num_cycles = batch_size // chunk_size
        remainder = batch_size % chunk_size

        # Call do before
        execute_wrapper.do_before(self)

        # Loop through complete cycles
        for i in range(0, num_cycles):

            # Batch indices
            begin = i * chunk_size
            end = (i + 1) * chunk_size

            # Execute & wait
            if self.__submit_chunk_for_execution(begin, end, execute_wrapper):
                outcome = self.wait_for_execution()

                # Exit if bad outcome - no point in continuing
                if not outcome:
                    return False

            else:
                return False

        # Remainder
        if remainder != 0:
            begin = num_cycles * chunk_size
            end = begin + remainder

            if self.__submit_chunk_for_execution(begin, end, execute_wrapper):
                outcome = self.wait_for_execution()

                # Exit if bad outcome - no point continuing
                if not outcome:
                    return False

            else:
                return False

        # Call do after
        execute_wrapper.do_after(self)

        return True

    def __submit_chunk_for_execution(self, begin, end, execute_wrapper):
        if self._locked:
            self.warning("Cannot execute a chunk as we are currently locked submitting or waiting.")
            return False

        self.info("Submitting a chunk from: " + str(begin) + " to: " + str(end) + " (exclusive of end) for execution.")
        self._tickets.clear()

        # Construct a new monitor - it has to be first, as otherwise we may be stuck queueing for resource without clearing it
        self._build_monitor()

        # Loop through the chunk
        for i in range(begin, end):
            completion_marker = str(uuid.uuid4())
            self._tickets.append(completion_marker)
            try:
                if not self._execute(execute_wrapper, completion_marker, script_arguments=execute_wrapper.map_arguments(self, i)):
                    return False

            except Exception as ex:
                self.error("Caught an exception whilst attempting to execute.")
                self.error("Will force the program to exit!")
                self._dead = True
                time.sleep(10)  # Allow locks to resove and threads to die
                raise ex

        return True

    def submit_batch_and_wait_for_execution(self, batch_size, execute_wrapper):
        if self.__submit_batch_for_execution(batch_size, execute_wrapper):
            return self.wait_for_execution()

        return False

    def __submit_batch_for_execution(self, batch_size, execute_wrapper):
        if self._locked:
            self.warning("Cannot execute a batch as we are currently locked submitting or waiting")
            return False

        self.info("Submitting a batch of " + str(batch_size) + " for execution")
        self._tickets.clear()

        # Construct a new monitor - it has to be first, as otherwise we may be stuck queuing for resource without clearing it
        self._build_monitor()

        # Call do before
        execute_wrapper.do_before(self)

        # Loop through the requests
        for i in range(0, batch_size):
            completion_marker = str(uuid.uuid4())
            self._tickets.append(completion_marker)
            try:
                if not self._execute(execute_wrapper, completion_marker, script_arguments=execute_wrapper.map_arguments(self, i)):
                    return False

            except Exception as ex:
                self.error("Caught an exception whilst attempting to execute.")
                self.error("Will force the program to exit!")
                self._dead = True
                time.sleep(10)  # Allow locks to resove and threads to die
                raise ex

        # Call do after
        execute_wrapper.do_after(self)

        return True

    def submit_and_wait_for_execution(self, execute_wrapper):
        if self.__submit_for_execution(execute_wrapper):
            return self.wait_for_execution()

        return False

    def __submit_for_execution(self, execute_wrapper):
        if self._locked:
            self.warning("Cannot execute whilst we are currently locked submitting or waiting")
            return False

        # Build an execution lock
        self.info("Submitting a script for execution")
        self._tickets.clear()
        completion_marker = str(uuid.uuid4())
        self._tickets.append(completion_marker)

        # Construct a new monitor - it has to be first, as otherwise we may be stuck queuing for resource without clearing it
        self._build_monitor()

        # Call do before
        execute_wrapper.do_before(self)

        # Submit & Execute
        if not self._execute(execute_wrapper, completion_marker, script_arguments=execute_wrapper.map_arguments(self, 0)):
            return False

        # Call do after
        execute_wrapper.do_after(self)

        return True

    def wait_for_execution(self):
        if not self._locked:
            self.warning("Cannot wait for a batch to finish executing if a batch has not yet been submitted!")
            return False

        # Join our monitor thread!
        self._monitor_thread.join()
        if self._dead:
            return False

        return True

    def _execute(self, execute_wrapper, completion_marker, script_arguments):
        # You cannot execute without a monitor, this prevents resources from being acquired without the ability to recover them.
        if not self._monitor_thread.is_alive():
            return False

        resource = self._runtime.acquire_resource(completion_marker)
        return resource.execute(self, execute_wrapper, script_arguments, completion_marker)

    def _build_monitor(self):
        self._monitor_thread = threading.Thread(target=self._monitor)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def _monitor(self):
        self._locked = True
        processing = True
        while processing and not self._dead:
            pass_through = True
            copy = self._tickets
            for ticket in copy:
                if not os.path.exists(os.path.join(self._file_system.get_monitor_directory(), ticket + ".txt")):
                    if os.path.exists(os.path.join(self._file_system.get_monitor_directory(), ticket + "_fail.txt")):
                        self.error("Delegate " + ticket + " failed.")
                        self._dead = True

                    pass_through = False

                # This allows us to free pooled resources
                else:
                    self.debug("Freed resource: " + ticket)
                    self._runtime.free_resource(ticket)
                    self._tickets.remove(ticket)

            if pass_through:
                # This should be a last ditch attempt to ensure no new tickets will be submitted to this monitor. It will delay execution cycles by 1 sec each time.
                # Despite the inefficiency, this ensures that resource requests that are enqueued will not be processed with a dead monitor
                time.sleep(1)
                if len(self._tickets) == 0:
                    processing = False

            else:
                time.sleep(60)

        self._locked = False
