#!/usr/bin/env bash

echo "=================================================================="
echo "> CLUSTER JOB WORKER SIDE"
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> Provided parameters:"
echo "> $@"
echo "=================================================================="
echo "> "
echo "=================================================================="
echo "> Parameter splits:"

for i in "$@"
do

# Removes wrapping quotes - an artifact of the calling heredoc, working out
# why I need to do this will take too long...
echo "${i}"

case ${i} in
    # Target Script
	-s=*)
	SCRIPT="${i#*=}"
	shift
	;;

	# Parameter String
	-p=*)
	PARAMETERS="${i#*=}"
	shift
	;;

	# Ticket
	-t=*)
	TICKET="${i#*=}"
	shift
	;;

	# Cleanup
	-c=*)
	PASS_CLEANUP_SCRIPT="${i#*=}"
	shift
	;;

	# Cleanup
	-cf=*)
	FAIL_CLEANUP_SCRIPT="${i#*=}"
	shift
	;;

	# Out
	-out=*)
	OUT="${i#*=}"
	shift
	;;

	# Err
	-err=*)
	ERR="${i#*=}"
	shift
	;;
esac
done

PARAMETERS="${PARAMETERS%\"}"
PARAMETERS="${PARAMETERS#\"}"

echo "=================================================================="
echo "> "

# Execute our target script
echo "=================================================================="
echo "> Beginning script submission for ${SCRIPT} with parameters: '${PARAMETERS}'"
JOB_ID=$(sbatch -o ${OUT} -e ${ERR} --open-mode=append --mem=224G --exclusive ${SCRIPT} ${PARAMETERS})
JOB_ID=${JOB_ID##* }
echo "Job ID: ${JOB_ID}"
echo "Queueing the cleanup job: ${PASS_CLEANUP_SCRIPT} with the ticket: ${TICKET} and dependent on Job ID: ${JOB_ID}"
sbatch -d afterok:${JOB_ID} --kill-on-invalid-dep=yes --output=/dev/null --error=/dev/null ${PASS_CLEANUP_SCRIPT} -ticket=${TICKET}
sbatch -d afternotok:${JOB_ID} --kill-on-invalid-dep=yes --output=/dev/null --error=/dev/null ${FAIL_CLEANUP_SCRIPT} -ticket=${TICKET}
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> CLUSTER JOB WORKER SIDE END"
echo "=================================================================="