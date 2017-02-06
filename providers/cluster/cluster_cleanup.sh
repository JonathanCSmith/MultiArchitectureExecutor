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

# Let's build the reporter that will inform our monitors of our completion
echo "=================================================================="
echo "> Creating monitor file: ${TICKET}"
touch ${TICKET}
echo "=================================================================="