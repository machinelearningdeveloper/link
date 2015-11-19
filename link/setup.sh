#!/usr/bin/env bash

set -e

TMP_DIR=$(mktemp -d ./XXXXXX)
SRC_DIR=$(dirname $0)
CLEANUP_SCRIPT="${TMP_DIR}"/cleanup.sh

echo "Setting up a working directory in ${TMP_DIR}..."

cp -iv "${SRC_DIR}"/create_jobs "${TMP_DIR}"
cp -iv "${SRC_DIR}"/cmd_template.txt "${TMP_DIR}"
cp -iv "${SRC_DIR}"/job_template.txt "${TMP_DIR}"
cp -iv "${SRC_DIR}"/qmanager "${TMP_DIR}"
cp -iv "${SRC_DIR}"/qdel_all "${TMP_DIR}"
cp -iv "${SRC_DIR}"/link.py "${TMP_DIR}"
mkdir "${TMP_DIR}"/conf
cp -iv "${SRC_DIR}"/link.yaml "${TMP_DIR}"/conf

copy_data () {
    description=$1
    FN=''
    while [ ! -f "${FN}" ]; do
        read -p "What is the name of the file containing the ${description} data? " FN
        if [ ! -f "${FN}" ]; then
            echo "${FN} does not exist."
        fi
    done

    echo "Copying ${FN}..."
    cp -iv "${FN}" "${TMP_DIR}"

    SPLIT_FN_GLOB=$(basename "${FN}" | sed 's/\.txt/_*.txt/')
    echo "rm -v ${SPLIT_FN_GLOB}" >> "${CLEANUP_SCRIPT}"
}

copy_data earlier
copy_data later

echo "rm -v *.job" >> "${CLEANUP_SCRIPT}"
echo "rm -v *.job.[eo]*" >> "${CLEANUP_SCRIPT}"

echo "Set up working directory in ${TMP_DIR}."

