import os
import json
import sys
import numpy as np
import glob
import argparse

parser = argparse.ArgumentParser(description="Input IOU threshold for precision/recall calculation")
parser.add_argument('-IOU', '-iou', required=True, help="intersection over union threshold for precision/recall",
						metavar="iou_threshold",
						type=float)

args = parser.parse_args()

IOU_t = args.IOU #intersection over union threshold

def IOU(bbox1, bbox2):
	minr_1, minc_1, maxr_1, maxc_1 = bbox1
	minr_2, minc_2, maxr_2, maxc_2 = bbox2

	isOverlapped = (minc_1 <= maxc_2 and minc_2 <= maxc_1 and minr_1 <= maxr_2 and minr_2 <= maxr_1)

	if isOverlapped:
		left = max(minc_1,minc_2)
		right = min(maxc_1, maxc_2)
		top = min(maxr_1,maxr_2)
		bottom = max(minr_1, minr_2)

		intersect_area = abs(left-right) * abs(top-bottom)
		union = abs((maxr_1-minr_1)*(maxc_1-minc_1)) + abs((maxr_2-minr_2)*(maxc_2-minc_2)) - intersect_area

		return float(intersect_area)/union
	else:
		return 0.0

# load json corresponding to classified plates
path_to_gt = os.getcwd() + os.sep + 'COCO_dataset' + os.sep + 'annotations' +os.sep + 'ideal_test.json'

with open(path_to_gt, 'rt', encoding='UTF-8') as gt:
	gt_json = json.load(gt)
	gt_annotations = gt_json["annotations"]

# read in unsupervised JSON output for single parameter regime
path_to_unsupervised = os.getcwd() + os.sep + 'Unsupervised_Output_fixedminmax_ideal' +os.sep

for filename in glob.glob(path_to_unsupervised + "*.json"):
	min_size = filename.strip().split('/')[-1].split('_')[2]
	max_size = filename.strip().split('/')[-1].split('_')[3]

	#print(min_size, max_size)

	with open(filename, 'rt', encoding='UTF-8') as unsupervised:
		predicted_annotations = json.load(unsupervised)

	#compute TP, FP, FN for precision and recall metrics per image
	precision_g = []
	precision_p = []

	recall_g = []
	recall_p = []

	#for a single image
	for p_ann in predicted_annotations:
		TP_p = 0
		TP_g = 0

		FP_p = 0
		FP_g = 0

		FN_p = 0
		FN_g = 0

		image_id = int(list(p_ann.keys())[0].split('_')[-1]) #the image corresponding to set of indexes

		gt_grande_bboxes = [ann['segmentation'][0][:2][::-1] + ann['segmentation'][0][2:][::-1] for ann in gt_annotations if ann['category_id'] == 2 and ann['image_id'] == image_id]
		gt_petite_bboxes = [ann['segmentation'][0][:2][::-1] + ann['segmentation'][0][2:][::-1] for ann in gt_annotations if ann['category_id'] == 1 and ann['image_id'] == image_id]

		grande_bboxes = [ann['bbox'] for ann in p_ann[list(p_ann.keys())[0]] if ann['category_id'] == 2]
		petite_bboxes = [ann['bbox'] for ann in p_ann[list(p_ann.keys())[0]] if ann['category_id'] == 1]

		#grande TP FP calculations
		for g_pred in grande_bboxes:
			good_prediction=False
			for g_gt in gt_grande_bboxes:
				#print(IOU(g_pred, g_gt))
				if IOU(g_pred, g_gt)>=IOU_t:
					TP_g+=1
					good_prediction=True
					break
			if good_prediction==False:
				FP_g+=1

		# petite TP FP calculations
		for p_pred in petite_bboxes:
			good_prediction = False
			for p_gt in gt_petite_bboxes:
				# print(IOU(g_pred, g_gt))
				if IOU(p_pred, p_gt) >= IOU_t:
					TP_p += 1
					good_prediction = True
					break
			if good_prediction == False:
				FP_p += 1

		# FN calculations
		FN_g = len(gt_grande_bboxes) - TP_g
		FN_p = len(gt_petite_bboxes) - TP_p

		if TP_g>0:
			precision_grande = float(TP_g)/(TP_g + FP_g)
			recall_grande = float(TP_g)/(TP_g + FN_g)
		else:
			precision_grande = 0.0
			recall_grande = 0.0

		if TP_p>0:

			precision_petite = float(TP_p)/ (TP_p + FP_p)
			recall_petite = float(TP_p)/ (TP_p + FN_p)
		else:
			precision_petite = 0.0
			recall_petite = 0.0


		precision_g.append(precision_grande)
		precision_p.append(precision_petite)

		recall_g.append(recall_grande)
		recall_p.append(recall_petite)
		
	# with open("unsupervised_ideal_pr_sweep_%2.2f.txt" %args.IOU, 'a') as output:
	# 	output.write(str(min_size) + "\t" + str(max_size) + "\t" + str(np.mean(precision_g))
	# 				 + "\t" + str(np.mean(recall_g)) + "\t" +
	# 				 str(np.mean(precision_p)) + "\t"+ str(np.mean(recall_p)) + "\n" )
	print(IOU_t, min_size, max_size, np.mean(precision_g), np.mean(recall_g), np.mean(precision_p), np.mean(recall_p))


