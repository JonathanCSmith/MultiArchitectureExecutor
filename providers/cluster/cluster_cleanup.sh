#!/usr/bin/env bash

for i in "$@"
do

case ${i} in
	# Ticket
	-ticket=*)
	TICKET="${i#*=}"
	shift
	;;

	# Out
	-out_log=*)
	OUT="${i#*=}"
	shift
	;;

	# Err
	-err_log=*)
	ERR="${i#*=}"
	shift
	;;

	# Log cleanup
	-l=*)
	CLEANUP_LOG="${i#*=}"
	shift
	;;

	# Job
	-j=*)
	JOB_ID="${i#*=}"
	shift
	;;
esac
done

# status
OUTCOME=$(sacct -j ${JOB_ID}.batch -P --format="State" | sed -n 2p)
echo "OUTCOME = $OUTCOME"
if [ "$OUTCOME" == "COMPLETED" ]; then
    echo "job succeeded"

    # Let's build the reporter that will inform our monitors of our completion
    echo "=================================================================="
    echo "> Creating monitor file: ${TICKET}"
    touch ${TICKET}
    echo "=================================================================="
elif [ "$OUTCOME" == "COMPLETING" ]; then
    echo "job succeeded"

    # Let's build the reporter that will inform our monitors of our completion
    echo "=================================================================="
    echo "> Creating monitor file: ${TICKET}"
    touch ${TICKET}
    echo "=================================================================="
else
    # status
    echo "job failed"

    # Let's build the reporter that will inform our monitors of our completion
    echo "=================================================================="
    echo "> Creating monitor file: ${TICKET}"
    file="${TICKET%.*}"
    touch "${file}_fail.txt"
    echo "=================================================================="
fi


# Cleanup log if thats what we should be doing
echo "Cleanup log? : ${CLEANUP_LOG}"
if [ "${CLEANUP_LOG}" = "True" ]; then
    echo "Cleaning: ${OUT} and ${ERR}"
    rm ${OUT}
    rm ${ERR}
fi

