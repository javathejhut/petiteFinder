from sahi.predict import predict
import os
import json

PROJECT_ROOT = os.getcwd() + os.sep

model_type = "mmdet"
model_device = "cuda"  # or 'cuda:0'

model_path = os.path.normpath(
    PROJECT_ROOT + "model_weights/faster_rcnn_r50_fpn_1x_coco_petiteFinder_0.01_0.5_epoch_13.pth")
model_config_path = os.path.normpath(PROJECT_ROOT + "model_cfg/faster_rcnn_r50_fpn_1x_coco_petiteFinder.py")
source_image_path = os.path.normpath(PROJECT_ROOT + "COCO_dataset/images/test/")
dataset_json_path = os.path.normpath(PROJECT_ROOT + "COCO_dataset/annotations/test.json")

# create a temporary json pointing to COCO_dataset test images folder
# (previous pointers are to raw dataset not on github due to size (1.5GB))
with open(dataset_json_path, 'rt', encoding='UTF-8') as def_json:
    temp_json = json.load(def_json)

    for img in temp_json["images"]:
        img["file_name"] = os.path.normpath(source_image_path + os.sep+ img["file_name"].split('/')[-1])

temp_json_path = os.path.normpath(PROJECT_ROOT + "temp_test.json")

with open(temp_json_path, 'w', encoding='utf-8') as f:
    json.dump(temp_json, f, ensure_ascii=False, indent=4)

model_confidence_threshold = 0.9
slice_height = 512
slice_width = 512
overlap_height_ratio = 0.2
overlap_width_ratio = 0.2

predict(
    model_type=model_type,
    model_path=model_path,
    model_config_path=model_config_path,
    model_device=model_device,
    model_confidence_threshold=model_confidence_threshold,
    source=source_image_path,
    slice_height=slice_height,
    slice_width=slice_width,
    overlap_height_ratio=overlap_height_ratio,
    overlap_width_ratio=overlap_width_ratio,
    export_visual=True,
    no_standard_prediction=True,
    visual_bbox_thickness=1,
    visual_text_size=0.5,
    visual_text_thickness=2,
    visual_export_format="png",
    dataset_json_path=temp_json_path,
    verbose=1
)
