#!/bin/bash

########################################
############# CSCI 2951-O ##############
########################################
E_BADARGS=65
if [ $# -ne 1 ]
then
	echo "Usage: `basename $0` <input>"
	exit $E_BADARGS
fi
	
input=$1

# Update this file with instructions on how to run your code given an input
# java -cp src/ solver.sat.Main $input
python3 src/main.py $input
# pypy3.6-v7.1.1 src/Main.py $input