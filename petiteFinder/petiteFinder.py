from sahi.predict import get_sliced_prediction
import os
import json
import argparse
from sahi.utils.file import Path, import_class, increment_path, list_files, save_json, save_pickle
from PIL import Image
from settings import *
from tools import utils

target_location = PROJECT_ROOT + "/petiteFinder/petiteFinder_json_guitest/"

slice_height=512
slice_width=512

def compute_optimal_slices(target_img_height, target_img_width):
    """
       compute SAHI slice height/width that best recreates trained sliced
       image view of petri dish
       Args:
           target_img_height: int
               height in pixels of target image
           target_img_width: int
               width in pixels of target image

       Returns:
           slice_height, slice_width: (int, int)
               slice height, slice width
    """
    target_img_area = target_img_height * target_img_width
    trained_img_fraction = TRAINED_SLICE_WIDTH*TRAINED_SLICE_HEIGHT/(TRAINED_IMAGE_HEIGHT*TRAINED_IMAGE_WIDTH)


def perform_inference_coco(target, model_device):
    """
       load model with SAHI wrapper and return coco json for image(s)
       Args:
           target: str
               "~/plate_images/"
           model_device: str
               "cuda" or "cpu"

       Returns:
           coco_dict: list
               coco formatted dictionary for predicted annotations on image(s)
    """
    coco_dict = {"annotations": [], "images": []}

    # target structure (always list of file paths)
    if os.path.isdir(target):
        image_path_list = list_files(
            directory=target,
            contains=[".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
            verbose=1
        )
    else:
        image_path_list = [target]

    # load model with SAHI wrapper
    DetectionModel = import_class(MODEL_CLASS_NAME)
    detection_model = DetectionModel(
        model_path=MODEL_PATH,
        config_path=MODEL_CONFIG_PATH,
        confidence_threshold=MODEL_CONFIDENCE_THRESHOLD,
        device=model_device,
        category_mapping=None,
        category_remapping=None,
        load_at_init=False,
        image_size=None,
    )
    detection_model.load_model()

    # iterate over image targets
    for img_id, img in enumerate(image_path_list):

        # store image information
        im = Image.open(img)
        width, height = im.size
        coco_dict["images"].append({"file_name": img, "height": height, "width": width, "id": img_id})

        pred_result = get_sliced_prediction(image=img, detection_model=detection_model, slice_height=slice_height,
                                            slice_width=slice_width, overlap_height_ratio=OVERLAP_HEIGHT_RATIO,
                                            overlap_width_ratio=OVERLAP_WIDTH_RATIO, perform_standard_pred=False,
                                            postprocess_type=POST_PROCESS_TYPE,
                                            postprocess_match_metric=POST_PROCESS_METRIC,
                                            postprocess_match_threshold=POST_PROCESS_MATCH_THRESHOLD, verbose=1)

        # get SAHI prediction json list
        coco_annotations = []
        object_prediction_list = pred_result.object_prediction_list
        for object_prediction in object_prediction_list:
            coco_prediction = object_prediction.to_coco_prediction()
            coco_prediction.image_id = img_id
            coco_prediction_json = coco_prediction.json
            if coco_prediction_json["bbox"]:
                coco_annotations.append(coco_prediction_json)
        coco_dict["annotations"].extend(coco_annotations)

    return coco_dict

output = perform_inference_coco(target_location, "cuda")

utils.save_coco_json(dest=os.getcwd() +os.sep+ "/petiteFinder_json_guitest/petiteFinder_output.json",
                     annotations=output["annotations"],
                     images=output["images"])

#
#     test_img_path,
#     detection_model=None,
#     image_size: int = None,
#     slice_height: int = 512,
#     slice_width: int = 512,
#     overlap_height_ratio: float = 0.2,
#     overlap_width_ratio: float = 0.2,
#     perform_standard_pred: bool = True,
#     postprocess_type: str = "GREEDYNMM",
#     postprocess_match_metric: str = "IOS",
#     postprocess_match_threshold: float = 0.5,
#     postprocess_class_agnostic: bool = False,
#     verbose: int = 1,
# )

# def main():
#
#     args = get_cli_arguments()
#
#
# def get_cli_arguments():
#
#     parser = argparse.ArgumentParser(description="Run automated yeast Petite frequency/colony pipeline")
#     parser.add_argument('-IOU', '-iou', required=True, help="intersection over union threshold for precision/recall",
#                         metavar="iou_threshold",
#                         type=float)
#
#     parser =

# predict(
#     model_type=model_type,
#     model_path=model_path,
#     model_config_path=model_config_path,
#     model_device=model_device,
#     model_confidence_threshold=model_confidence_threshold,
#     source=source_image_path,
#     slice_height=slice_height,
#     slice_width=slice_width,
#     overlap_height_ratio=overlap_height_ratio,
#     overlap_width_ratio=overlap_width_ratio,
#     export_visual=True,
#     no_standard_prediction=True,
#     visual_bbox_thickness=1,
#     visual_text_size=0.5,
#     visual_text_thickness=2,
#     visual_export_format="png",
#     dataset_json_path=temp_json_path,
#     verbose=1
# )
