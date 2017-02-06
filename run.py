import argparse
import sys

from execute import run


def parse_and_use_sys_args(args):
    parser = argparse.ArgumentParser("The Renal Pipeline's runtime execution arguments.")

    parser.add_argument(
        "--runtime_provider",
        required=True,
        help="A string value representing the path to the resource provider."
    )

    parser.add_argument(
        "--source_directory",
        required=True,
        help="The directory in which the inputs for a single unit of work can be found across all resources (i.e. the run folder for a sequencing run. It is expected that all ancillary information is also present within this folder."
    )

    parser.add_argument(
        "--scripts_directory",
        default=None,
        help="The directory in which the scripts for the pipeline are located across all resources. If this value is not provided, it is expected that all relevant scripts can be found in the current working directory."
    )

    parser.add_argument(
        "--pipeline_controller",
        default=None,
        help="The path to the pipeline controller script across all resources. This script will be provided with the current engine object via the function execute_pipeline(engine). If the script is not provided, it is assumed that it will be present within the scripts directory and called controller.py"
    )

    parser.add_argument(
        "--working_directory",
        default=None,
        help="The path to your working directory across all resources."
    )

    parser.add_argument(
        "--output_directory",
        default=None,
        help="The path to your output directory across all resources."
    )

    args = parser.parse_args(args)

    run(runtime_provider=args.runtime_provider, source_directory=args.source_directory, scripts_directory=args.scripts_directory, pipeline_controller=args.pipeline_controller, working_directory=args.working_directory, output_directory=args.output_directory)


# Core Runtime Entry Point
parse_and_use_sys_args(sys.argv[1:])
