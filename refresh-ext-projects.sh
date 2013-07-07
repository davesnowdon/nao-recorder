#! /bin/sh
# Copies files from external projects into NAO wanderer. This is to allow
# ease of use for others whilst still allowing other projects to be managed
# separately.

PYTHON_SRC="src/main/python"

EXT_PROJECTS="../naoutil/naoutil/src/main/python|naoutil ../FluentNao/src/main/python|fluentnao ../FluentNao/src/main/python|fluentnao/core"


for pspec in $EXT_PROJECTS
do
    # split base|sub-path into directory and sub folder
    IFS='|' read -ra proj <<< "$pspec"
    ploc=${proj[0]}
    pname=${proj[1]}
    ppath="${ploc}/${pname}"
    dest="${PYTHON_SRC}/${pname}"

    # delete old python files
    rm -f ${dest}/*.py*

    # replace with new ones
    cp ${ppath}/*.py $dest

    # make read-only to prevent accidental modification
    chmod 444 ${dest}/*.py
done
