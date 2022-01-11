from sahi.predict import predict
import os
import json
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd() + os.sep, os.pardir))
print(PROJECT_ROOT)
model_type = "mmdet"
model_device = "cuda"  # or 'cuda:0'

model_path = os.path.normpath(
    PROJECT_ROOT + "/model_weights/exp_500px_4-8anchor_linear_distortions_mult-scale_epoch_10.pth")
model_config_path = os.path.normpath(PROJECT_ROOT + "/model_cfg/faster_rcnn_r50_fpn_1x_coco_petiteFinder_wdb.py")
source_image_path = os.path.normpath(PROJECT_ROOT + "/COCO_dataset/images/validate/")
dataset_json_path = os.path.normpath(PROJECT_ROOT + "/COCO_dataset/annotations/validate.json")

# create a temporary json pointing to COCO_dataset test images folder
# (previous pointers are to raw dataset not on github due to size (1.5GB))
with open(dataset_json_path, 'rt', encoding='UTF-8') as def_json:
    temp_json = json.load(def_json)

    for img in temp_json["images"]:
        img["file_name"] = os.path.normpath(source_image_path + os.sep + img["file_name"].split('/')[-1])

temp_json_path = os.path.normpath(PROJECT_ROOT + "temp_validate.json")

with open(temp_json_path, 'w', encoding='utf-8') as f:
    json.dump(temp_json, f, ensure_ascii=False, indent=4)

# 192 combinations per person (6 hr runtime on my GPU)
post_process_type = ["GREEDYNMM", "NMS", "NMM"]
model_confidence_threshold = np.arange(0.6, 1, 0.1)
post_process_threshold = np.arange(0.2, 1, 0.1)
post_process_metric = ['IOS', 'IOU']

# fixed in sweep (but SHOULD change based on user input resolution)
project_name = "runs/GS_Eugene"
slice_height = 512
slice_width = 512
overlap_height_ratio = 0.2
overlap_width_ratio = 0.2

count=0
for pp_type in post_process_type:
    for mct in model_confidence_threshold:
        for ppt in post_process_threshold:
            for ppm in post_process_metric:
                output_name = "{}_{}_{}_{}".format(mct, pp_type, ppm, ppt)

                predict(
                    model_type=model_type,
                    model_path=model_path,
                    model_config_path=model_config_path,
                    model_device=model_device,
                    postprocess_type=pp_type,
                    postprocess_match_threshold=ppt,
                    model_confidence_threshold=mct,
                    postprocess_match_metric=ppm,
                    source=source_image_path,
                    slice_height=slice_height,
                    slice_width=slice_width,
                    overlap_height_ratio=overlap_height_ratio,
                    overlap_width_ratio=overlap_width_ratio,
                    export_visual=False,
                    no_standard_prediction=False,
                    visual_text_size=0.5,
                    visual_text_thickness=2,
                    visual_export_format="png",
                    dataset_json_path=temp_json_path,
                    project=project_name,
                    name=output_name,
                    verbose=0
                )

                count+=1
                print("\n\nprogress:", count, '/', len(post_process_type)*len(model_confidence_threshold) *
                      len(post_process_threshold) * len(post_process_metric), '\n')
