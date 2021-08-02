#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
OLDPYTHONPATH=$PYTHONPATH
export PYTHONPATH="$DIR/../../boa"

echo "PYTHONPATH set to: $PYTHONPATH"

for test_file in $DIR/tests/*.py; do
    test_name=$(basename $test_file)
    test_name_length=$(expr ${#test_name} + 0)
    echo ""
    echo "Test: $test_name"
    echo -n "------"
    for ((i=1; i<=$test_name_length; i++)); do echo -n -; done
    echo ""

    python $test_file
done

export PYTHONPATH="$OLDPYTHONPATH"
echo -e "\nPYTHONPATH restored."
