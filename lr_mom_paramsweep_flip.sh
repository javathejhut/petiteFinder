#!/bin/bash
#declare -a lrs=(0.0001 0.001 0.01)
#declare -a moms=(0.5 0.6 0.7 0.8 0.9)

declare -a lrs=(0.001)
declare -a moms=(0.9)

declare -a lr_config=("lr_config.policy='CosineAnnealing' lr_config.warmup='linear' lr_config.warmup_iters=1000 lr_config.warmup_ratio=0.1, lr_config.min_lr_ratio=0.00001" "lr_congfig.policy='step' lr_config.warmup='linear' lr_config.warmup_iters=500 lr_config.warmup_ratio=0.001 lr_ratio.step='[8,11]'")
declare -a optimizer=("optimizer.type='SGD'" "optimizer.type='adam'")

for lr in "${lrs[@]}" 
do
	for mom in "${moms[@]}" 
	do
		python mmdetection/tools/train.py petiteFinder_base_sweep_512_512.py --cfg-options optimizer.lr=$lr optimizer.momentum=$mom  --work-dir /media/groot/HDD_storage/work_dirs_512_512/faster_rcnn_r50_fpn_1x_coco_petiteFinder_"$lr"_"$mom"
		echo $lr $mom
	done
done
