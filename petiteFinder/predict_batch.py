from sahi.predict import predict
import os
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd() + os.sep, os.pardir))
print(PROJECT_ROOT)
model_type = "mmdet"
model_device = "cuda"  # or 'cuda:0'

model_path = os.path.normpath(
    PROJECT_ROOT + "/model_weights/1024px_epoch_17.pth")
model_config_path = os.path.normpath(PROJECT_ROOT + "/model_cfg"
                                                    "/faster_rcnn_r50_fpn_1x_coco_petiteFinder_wdb_chris.py")
source_image_path = os.path.normpath(PROJECT_ROOT + "/COCO_dataset/images/test/")
dataset_json_path = os.path.normpath(PROJECT_ROOT + "/COCO_dataset/annotations/test.json")

# create a temporary json pointing to COCO_dataset test images folder
# (previous pointers are to raw dataset not on github due to size (1.5GB))
with open(dataset_json_path, 'rt', encoding='UTF-8') as def_json:
    temp_json = json.load(def_json)

    for img in temp_json["images"]:
        img["file_name"] = os.path.normpath(source_image_path + os.sep+ img["file_name"].split('/')[-1])

temp_json_path = os.path.normpath(PROJECT_ROOT + "temp_test.json")

with open(temp_json_path, 'w', encoding='utf-8') as f:
    json.dump(temp_json, f, ensure_ascii=False, indent=4)

# optimizing on petite freq difference in val
model_confidence_threshold = 0.6
post_process_type = "GREEDYNMM"
post_process_metric = "IOS"
post_process_match_threshold = 0.5

slice_height = 512
slice_width = 512
overlap_height_ratio = 0.2
overlap_width_ratio = 0.2

predict(
        model_type=model_type,
        model_path=model_path,
        model_config_path=model_config_path,
        model_device=model_device,
        postprocess_type=post_process_type,
        postprocess_match_threshold=post_process_match_threshold,
        model_confidence_threshold=model_confidence_threshold,
        postprocess_match_metric=post_process_metric,
        source=source_image_path,
        slice_height=slice_height,
        slice_width=slice_width,
        overlap_height_ratio=overlap_height_ratio,
        overlap_width_ratio=overlap_width_ratio,
        export_visual=True,
        no_standard_prediction=True,
        visual_text_size=0.5,
        visual_text_thickness=2,
        visual_export_format="png",
        dataset_json_path=temp_json_path,
        project="runs",
        name="test_exp",
        verbose=1
    )
