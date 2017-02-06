#!/usr/bin/env bash

echo "=================================================================="
echo "> CLOUD JOB WORKER SIDE"
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
i="${i%\"}"
i="${i#\"}"
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
esac
done

echo "=================================================================="
echo "> "

# Execute our target script
echo "=================================================================="
echo "> Beginning script call for ${SCRIPT} with parameters: '${PARAMETERS}'"
bash ${SCRIPT} ${PARAMETERS} && echo "> Successful execution of the provided shell script." || echo "> Failure when executing the provided shell script."
echo "=================================================================="
echo ">"

# Let's build the reporter that will inform our monitors of our completion
echo "=================================================================="
echo "> Creating monitor file: ${TICKET}"
touch ${TICKET}
echo "=================================================================="
echo ">"
echo "=================================================================="
echo "> CLOUD JOB WORKER SIDE END"
echo "=================================================================="
