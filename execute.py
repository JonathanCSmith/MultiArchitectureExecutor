import os
import sys

from engine import Engine
from filesystem import FileSystem
from runtime import Runtime


def run(runtime_provider, source_directory, scripts_directory, pipeline_controller=None, working_directory=None, output_directory=None, no_exit=False):
    # Build a file system
    file_system = FileSystem(source_directory, working_directory=working_directory, scripts_directory=scripts_directory, output_directory=output_directory)

    # Core
    engine = Engine(file_system)
    engine.info("Logging setup complete")

    # Build the runtime environment
    engine.info("Beginning setup of the runtime environment")
    runtime = Runtime(engine)
    engine.info("Runtime setup complete")

    # Load the appropriate resource properties
    # TODO: What if we want to be able to do both? :D
    engine.info("Loading resource properties")
    if not runtime.set_runtime_provider(runtime_provider, file_system):
        engine.error("Failed to setup the runtime provider.")
        return False

    # Evaluate pipeline controller
    if not pipeline_controller or not os.path.exists(pipeline_controller):
        pipeline_controller = os.path.join(file_system.get_scripts_directory(), "controller.py")
        if not os.path.exists(pipeline_controller):
            engine.error("No valid path to a pipeline controller script was provided. Looked for: " + pipeline_controller + ". Exiting...")
            sys.exit(1)

    # Execute the pipeline - this is a delegate script call to allow pipelines to be provided dynamically
    engine.info("Beginning pipeline execution")
    try:
        version = sys.version_info
        if version >= (3, 5):
            import importlib.util
            spec = importlib.util.spec_from_file_location("pipeline", pipeline_controller)
            pipeline = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pipeline)

        elif version >= (3, 3):
            from importlib.machinery import SourceFileLoader
            pipeline = SourceFileLoader("pipeline", pipeline_controller).load_module()

        else:
            engine.error("Python 2 is currently not supported")
            return

        # Make a blind function call - we assume that the loaded script conforms to our standards. If not, we catch it
        engine.info("Attempting engine injection")
        if pipeline.execute_pipeline(engine):
            file_system.cleanup_monitors()
            if no_exit:
                engine.debug("Returning positive outcome: True")
                return True
            else:
                engine.debug("Returning positive outcome: 0")
                sys.exit(0)
        else:
            file_system.cleanup_monitors()
            if no_exit:
                engine.debug("Returning negative outcome: False")
                return False
            else:
                engine.debug("Returning negative outcome: 1")
                sys.exit(1)

    except Exception as ex:
        engine.error("Caught exception in pipeline delegate")
        engine.exception(ex)
        sys.exit(1)

