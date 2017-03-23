#!/bin/bash
dataset='small_polycyclic_table'
set -e
if [ -z ${RMG_BENCHMARK+x} ]; then 
	echo "RMG variable is unset. Exiting..."
	exit 0
fi

export ORIGIN_PYTHONPATH=$PYTHONPATH

###########
#BENCHMARK#
###########
# make folder for models generated by the benchmark version of RMG-Py/RMG-database:
export benchmark_tests=$DATA_DIR/tests/benchmark/${benchmark_py_sha}_${benchmark_db_sha}/
mkdir -p $benchmark_tests/thermo_val_jobs/$dataset
rm -rf $benchmark_tests/thermo_val_jobs/$dataset/*
cp $BASE_DIR/examples/thermo_val/thermo_sdata134k.py $benchmark_tests/thermo_val_jobs/thermo_sdata134k.py

source activate ${benchmark_env}
conda install pymongo -y
echo "benchmark version of RMG: "$RMG_BENCHMARK
export PYTHONPATH=$RMG_BENCHMARK:$ORIGIN_PYTHONPATH 

rm -rf ${RMG_BENCHMARK}/rmgpy/rmgrc
rmgrc="database.directory : "${RMGDB_BENCHMARK}/input/
echo $rmgrc >> ${RMG_BENCHMARK}/rmgpy/rmgrc

python $benchmark_tests/thermo_val_jobs/thermo_sdata134k.py > /dev/null

source deactivate
export PYTHONPATH=$ORIGIN_PYTHONPATH

#########
#TESTING#
# #########
# # make folder for models generated by the test version of RMG-Py and RMG-database:
# export testing_tests=$DATA_DIR/tests/testing/${testing_py_sha}_${testing_db_sha}/
# mkdir -p $testing_tests/thermo_val_jobs/$dataset
# rm -rf $testing_tests/thermo_val_jobs/$dataset/*
# cp $BASE_DIR/examples/rmg/$dataset/input.py $testing_tests/thermo_val_jobs/$dataset/input.py
# source activate ${testing_env}
# echo "test version of RMG: "$RMG_TESTING

# export PYTHONPATH=$RMG_TESTING:$ORIGIN_PYTHONPATH 

# rm -rf ${RMG_TESTING}/rmgpy/rmgrc
# rmgrc="database.directory : "${RMGDB_TESTING}/input/
# echo $rmgrc >> ${RMG_TESTING}/rmgpy/rmgrc

# python $RMG_TESTING/rmg.py $testing_tests/thermo_val_jobs/$dataset/input.py > /dev/null
# export PYTHONPATH=$ORIGIN_PYTHONPATH
# source deactivate

