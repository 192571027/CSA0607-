#!/bin/sh
# Re-runs every experiment; outputs (.txt logs and .png graphs) are written to each question's Output_Screenshots/.
# Take your own terminal screenshots of these runs for the submission.
set -e
for d in Q1_MaxMin_Binary_Search Q2_MergeSort_QuickSort Q3_Karatsuba_Multiplication Q4_Strassen_Matrix_Multiplication Q5_Divide_Conquer_Closest_Pair Q6_Advanced_Divide_Conquer; do
  for f in $d/Implementation_Code/*.py; do
    echo ">>> $f"; (cd $d/Implementation_Code && python3 $(basename $f))
  done
done
