#!/usr/bin/env bash

echo "=================================================================="
echo "> CLUSTER JOB CONTROLLER SIDE"
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> Provided parameters:"
echo "> $@"
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> Parameter splits:"

for i in "$@"
do

echo "${i}"

case ${i} in
	# Err Log
	-el=*)
	LOG_ERR="${i#*=}"
	shift
	;;

	# Out Log
	-sl=*)
	LOG_OUT="${i#*=}"
	shift
	;;

    # Target address
    -target=*)
    TARGET="${i#*=}"
    shift
    ;;

    # SSH Key
    -key=*)
    SSH_KEY="${i#*=}"
    shift
    ;;

    # USERNAME
    -user=*)
    USERNAME="${i#*=}"
    shift
    ;;

	# Target Script
	-script=*)
	SCRIPT="${i#*=}"
	shift
	;;

	# Ticket
	-ticket=*)
	TICKET="${i#*=}"
	shift
	;;

    # Working directory
    -wd=*)
    WORKING_DIRECTORY="${i#*=}"
    shift
    ;;

	# Parameter String
	-parameter_string=*)
	PARAMETERS="${i#*=}"
	shift
	;;

	# Remote Script
	-remote=*)
	REMOTE_SCRIPT="${i#*=}"
	shift
	;;

	# Cleanup Script
	-c=*)
	CLEANUP_SCRIPT="${i#*=}"
	shift
	;;

	# Cleanup Script
	-cf=*)
	FAIL_CLEANUP_SCRIPT="${i#*=}"
	shift
	;;
esac
done

echo "=================================================================="
echo ">"

# Lets get on to our target machine!
echo "=================================================================="
echo "> SSHing to target ip: ${TARGET} to submit the script ${SCRIPT} with parameters '${PARAMETERS}' using the submission script ${REMOTE_SCRIPT}."
echo "> Logs will be placed in ${LOG_OUT} and ${LOG_ERR}"
# Change to our working directory
cd ${WORKING_DIRECTORY}

# Delegate the execution call to our scheduler specific interpreter
${REMOTE_SCRIPT} -s=${SCRIPT} -t=${TICKET} -c=${CLEANUP_SCRIPT} -cf=${FAIL_CLEANUP_SCRIPT} -out="${LOG_OUT}" -err="${LOG_ERR}" -p="${PARAMETERS}"
echo "> SSH complete"
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> CLUSTER JOB CONTROLLER SIDE END"
echo "=================================================================="