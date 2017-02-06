#!/usr/bin/env bash

for i in "$@"
do
case ${i} in
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
    -path=*)
    TARGET_PATH="${i#*=}"
    shift
    ;;

esac
done

# Lets get on to our target machine!
echo "SSHing to target ip: ${TARGET} using ${SSH_KEY} for user: ${USERNAME}"
ssh -i "${SSH_KEY}" "${USERNAME}"@"${TARGET}" << EOF
    cd ${TARGET_PATH}
    echo \$?
EOF

echo $?  # Should have caught the cd exit code && the ssh code