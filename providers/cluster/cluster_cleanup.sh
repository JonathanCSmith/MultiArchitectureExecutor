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

# Cleanup log if thats what we should be doing
if [ "${CLEANUP_LOG}" == "True" ]; then
    rm ${OUT}
    rm ${ERR}
fi

# Let's build the reporter that will inform our monitors of our completion
echo "=================================================================="
echo "> Creating monitor file: ${TICKET}"
touch ${TICKET}
echo "=================================================================="