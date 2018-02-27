#!/usr/bin/env bash

for i in "$@"
do

case ${i} in
	# Ticket
	-ticket=*)
	TICKET="${i#*=}"
	shift
	;;
esac
done

file="${TICKET%.*}"

# status
echo "job failed"

# Let's build the reporter that will inform our monitors of our completion
echo "=================================================================="
echo "> Creating monitor file: ${TICKET}"
touch "${file}_fail.txt"
echo "=================================================================="