#!/usr/bin/env bash

echo "=================================================================="
echo "> CLOUD JOB CONTROLLER SIDE"
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
esac
done

echo "=================================================================="
echo ">"

# Lets get on to our target machine!
echo "=================================================================="
echo "> SSHing to target ip: ${TARGET} to nohup the script ${SCRIPT} with parameters '${PARAMETERS}'."
echo "> Logs will be placed in ${LOG_OUT} and ${LOG_ERR}"
ssh -i "${SSH_KEY}" "${USERNAME}"@"${TARGET}" << EOF
    # Change to our working directory
    cd ${WORKING_DIRECTORY}

    # Delegate the execution call to the client
    nohup ${REMOTE_SCRIPT} -s=${SCRIPT} -t=${TICKET} \"-p=${PARAMETERS}\" > "${LOG_OUT}" 2> "${LOG_ERR}" < /dev/null &
EOF
echo "> SSH complete"
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> CLOUD JOB CONTROLLER SIDE END"
echo "=================================================================="
