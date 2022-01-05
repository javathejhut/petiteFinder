#!/bin/bash
declare -a lrs=(0.0001 0.001 0.01 0.1 0.15 0.2 0.25)
declare -a moms=(0.5 0.6 0.7 0.8 0.9)

for lr in "${lrs[@]}" 
do
	for mom in "${moms[@]}" 
	do
		python mmdetection/tools/train.py mmdetection/configs/Petites/faster_rcnn_r50_fpn_1x_coco_petiteFinder.py --cfg-options optimizer.lr=$lr optimizer.momentum=$mom  --work-dir /media/groot/HDD_storage/work_dirs/faster_rcnn_r50_fpn_1x_coco_petiteFinder_"$lr"_"$mom"
		echo $lr $mom
	done
done
