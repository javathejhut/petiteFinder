import json
import os
from pathlib import Path
from tools import utils

target_file = 'runs/SAHI_sweep_results.txt'

run_info = []
with open(target_file, 'r') as summary:
    for line in summary:
        model_confidence_threshold = float(line.split('\t')[0])
        post_process_type = str(line.split('\t')[1])
        post_process_metric = str(line.split('\t')[2])
        post_process_threshold = float(line.split('\t')[3])
        mAP_total= float(line.split('\t')[4])
        mAP_05 = float(line.split('\t')[5])
        mAP_075 = float(line.split('\t')[6])

        output = [model_confidence_threshold, post_process_type, post_process_metric, post_process_threshold,
                  mAP_total, mAP_05, mAP_075]

        run_info.append(output)


for ele in sorted(run_info,key=lambda l:l[5], reverse=True)[0:10]:
    print(ele)
