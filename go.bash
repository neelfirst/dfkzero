#!/bin/bash -e

for i in 1046 1050 1656 1071 203 1781 1498 620 557 706
do
  for j in 1046 1050 1656 1071 203 1781 1498 620 557 706
  do
    if [ $i -ne $j ]; then
      python3 summon_ev.py --h1 $i --h2 $j
    fi
  done
done
