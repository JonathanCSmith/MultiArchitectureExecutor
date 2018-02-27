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
esac
done

# status
echo "job succeeded"

# Cleanup log if thats what we should be doing
echo "Cleanup log? : ${CLEANUP_LOG}"
if [ "${CLEANUP_LOG}" = "True" ]; then
    echo "Cleaning: ${OUT} and ${ERR}"
    rm ${OUT}
    rm ${ERR}
fi

# Let's build the reporter that will inform our monitors of our completion
echo "=================================================================="
echo "> Creating monitor file: ${TICKET}"
touch ${TICKET}
echo "=================================================================="