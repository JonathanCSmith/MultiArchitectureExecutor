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

	# Log cleanup
	-l=*)
	CLEANUP_LOG="${i#*=}"
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
JOB_ID=$(sbatch -o ${OUT} -e ${ERR} --open-mode=append --mem=64G ${SCRIPT} ${PARAMETERS})
if [[ $JOB_ID = *"error"* ]]; then
    echo "Error when submitting bash job. Retrying in 10 seconds"
    sleep 10
    JOB_ID=$(sbatch -o ${OUT} -e ${ERR} --open-mode=append --mem=64G ${SCRIPT} ${PARAMETERS})
fi

JOB_ID=${JOB_ID##* }
echo "Job ID: ${JOB_ID}"

OUTPUT=$(sbatch -d afterany:${JOB_ID} --kill-on-invalid-dep=yes --open-mode=append -o ${OUT} -e ${ERR} ${CLEANUP_SCRIPT} -ticket=${TICKET} -l=${CLEANUP_LOG} -j=${JOB_ID} -out_log=${OUT} -err_log=${ERR})
if [[ $OUTPUT = *"error"* ]]; then
    echo "Error when submitting bash job. Retrying in 10 seconds"
    sleep 10
    OUTPUT=$(sbatch -d afterany:${JOB_ID} --kill-on-invalid-dep=yes --open-mode=append -o ${OUT} -e ${ERR} ${CLEANUP_SCRIPT} -ticket=${TICKET} -l=${CLEANUP_LOG} -j=${JOB_ID} -out_log=${OUT} -err_log=${ERR})
fi
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> CLUSTER JOB WORKER SIDE END"
echo "=================================================================="