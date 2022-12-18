from sahi.predict import get_sliced_prediction
from sahi.utils.file import import_class
import os
import json
import argparse
from PIL import Image, ImageDraw, ImageFont
from config.settings import *
import math
import pandas as pd
from petiteGUI import amendGUI


def get_parsers():
    # top level parser
    parser = argparse.ArgumentParser(description="Run petiteFinder, an automated yeast Petite frequency"
                                                 "/colony detection pipeline.")

    subparsers = parser.add_subparsers(help='Run predict or ammend command in petiteFinder.',
                                       dest='command', title='subcommands')

    # predict parser
    predict_parser = subparsers.add_parser('predict', help="Predict Petite/Grande colony locations.")
    predict_parser.add_argument("-i", "--inputdir", dest="input_path", metavar="/path/to/images",
                                help="Enter the full path to the target image or directory containing your target "
                                     "plate images.",
                                required=True, type=str)

    predict_parser.add_argument("-o", "--outputdir", dest="output_path", metavar="/path/to/output",
                                help="Enter the full path where json/csv/annotated_images should be exported to.",
                                required=True, type=str)

    predict_parser.add_argument("-d", "--device", dest="device", metavar="cpu/cuda",
                                help="Enter the model device.",
                                type=str, required=False, default="cuda", choices=["cpu", "cuda"])

    predict_parser.add_argument("-p", "--predict", dest="predict", metavar="complete",
                                help="Enter the prediction mode. Choices are 'complete', 'frequency_only',"
                                     "'json_only', 'visualize_only'.",
                                type=str, required=False, default='complete', choices=["complete",
                                                                                       "frequency_only",
                                                                                       "json_only",
                                                                                       "visualize_only"])
    predict_parser.add_argument("-gs", "--grande_size", dest="grande_size", metavar="Grande diameter (pixels)",
                                help="Enter the typical (average) diameter of a Grande colony in pixels.",
                                type=int, required=False, default=None)

    predict_parser.add_argument("-n", "--name", dest="name", metavar="prefix",
                                help="Prefix of json annotation/csv frequency file.",
                                required=False, type=str, default="pF")

    # amend parser
    amend_parser = subparsers.add_parser('amend', help="Amend existing petiteFinder annotation with GUI.")
    amend_parser.add_argument("-i", "--inputjson", dest="json_path", metavar="/path/to/json",
                              help="Path to json to amend through GUI.",
                              required=True, type=str)

    amend_parser.add_argument("-n", "--name", dest="name", metavar="prefix",
                              help="Prefix to append to json after amending.",
                              required=False, type=str, default="amended")

    return parser


def compute_optimal_slices(target_img_width, target_img_height):
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
    trained_img_fraction = TRAINED_SLICE_WIDTH * TRAINED_SLICE_HEIGHT / (TRAINED_IMAGE_HEIGHT * TRAINED_IMAGE_WIDTH)

    slice_height = int(math.sqrt(target_img_area * trained_img_fraction))
    # slice_height = int((56.0*0.9)/50.0)*512
    slice_width = slice_height

    return slice_width, slice_height


def compute_prescribed_slices(grande_size):
    """
       compute SAHI slice height/width that maintains Grande colony to slice ratio
       in training data. Useful when colonies are drastically smaller/larger than even augmented
       training data.
       Args:
           grande_size: int
                Diameter in pixels of a typical Grande colony

       Returns:
           slice_height, slice_width: (int, int)
               slice height, slice width
    """

    slice_height = int(grande_size/TRAINED_GRANDE_SIZE)*TRAINED_SLICE_HEIGHT
    slice_width = slice_height

    return slice_width, slice_height


def list_image_files(directory):
    """
    provide list of image files of supported type in directory
    Args:
        directory: str
            "data/coco/"

    Returns:
        filepath_list : list
            List of file paths
    """
    filepath_list = []
    supported_types = [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]

    for file in os.listdir(directory):
        if any(somestr in file for somestr in supported_types):
            filepath = os.path.join(directory, file)
            filepath_list.append(filepath)

    number_of_files = len(filepath_list)
    folder_name = directory.split(os.sep)[-1]

    if folder_name == "":
        folder_name = directory.split(os.sep)[-2]
    print("There are {} image files in folder {} for petiteFinder to process.".format(number_of_files, folder_name))

    return filepath_list


def perform_inference_coco(target, model_device, grande_size):
    """
       load model with SAHI wrapper and return coco json for image(s)
       Args:
           target: str
               "~/plate_images/"
           model_device: str
               "cuda" or "cpu"
           grande_size: int
                Diameter in pixels of a typical Grande colony

       Returns:
           coco_dict: list
               coco formatted dictionary for predicted annotations on image(s)
    """
    coco_dict = {"annotations": [], "images": []}

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
        image_size=None
    )
    detection_model.load_model()

    if os.path.isdir(target):
        image_path_list = list_image_files(target)

    else:
        image_path_list = [target]

    # iterate over image targets
    for img_id, img in enumerate(image_path_list):

        # store image information
        im = Image.open(img)
        width, height = im.size
        if grande_size:
            slice_height, slice_width = compute_prescribed_slices(grande_size)
        else:
            slice_height, slice_width = compute_optimal_slices(width, height)
        coco_dict["images"].append({"file_name": img, "height": height, "width": width, "id": img_id})

        pred_result = get_sliced_prediction(image=img, detection_model=detection_model, slice_height=slice_height,
                                            slice_width=slice_width, overlap_height_ratio=OVERLAP_HEIGHT_RATIO,
                                            overlap_width_ratio=OVERLAP_WIDTH_RATIO, perform_standard_pred=False,
                                            postprocess_type=POST_PROCESS_TYPE,
                                            postprocess_match_metric=POST_PROCESS_METRIC,
                                            postprocess_match_threshold=POST_PROCESS_MATCH_THRESHOLD, verbose=0)
        print("Performed prediction on image {}: {}.".format(img_id, img.split(os.sep)[-1]))

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


def save_coco_json(destination, prefix, images=None, annotations=None, licenses=None, categories=None, info=None):
    if info is None:
        info = []
    if images is None:
        images = []
    if annotations is None:
        annotations = []
    if licenses is None:
        licenses = []
    if categories is None:
        categories = []

    with open(os.path.normpath(os.path.join(destination, prefix + "_predicted.json")), 'wt', encoding='UTF-8') \
            as coco_output:
        json.dump({'images': images, 'annotations': annotations, 'licenses': licenses, 'categories': categories,
                   'info': info}, coco_output, indent=2, sort_keys=True)


def load_coco_json(target_dir):
    with open(target_dir) as json_file:
        data = json.load(json_file)
    return data


def save_freq_csv(coco_dict, destination, prefix):
    cat_dicts = [get_category_count_per_img(coco_dict, 'g'), get_category_count_per_img(coco_dict, 'p')]

    raw_df = pd.concat([pd.DataFrame(cat, index=[0]) for cat in cat_dicts], axis=0)
    complete_df = raw_df.T

    complete_df.index.name = 'filename'
    id_to_filename_map = {img_id: file_name for (img_id, file_name) in [[entry["id"], entry["file_name"]]
                                                                        for entry in coco_dict["images"]]}

    complete_df.index = complete_df.index.to_series().map(id_to_filename_map)
    complete_df.columns = ['grande_count', 'petite_count']

    complete_df = complete_df.assign(
        percent_petite=complete_df['petite_count'] / (complete_df['grande_count'] + complete_df['petite_count']))
    complete_df = complete_df.assign(
        total_count=(complete_df['grande_count'] + complete_df['petite_count']))

    complete_df.to_csv(os.path.abspath(os.path.join(destination, prefix + "_freq.csv")))


def save_annotated_images(coco_dict, destination, prefix):
    images = [entry for entry in coco_dict["images"]]
    annotations = [entry for entry in coco_dict["annotations"]]

    folder_name = "pF_annotated_images"
    output_location = os.path.normpath(os.path.join(destination, folder_name))

    textbox_height = 12
    rect_thickness = 4
    font_size = int(1.5 * textbox_height)

    font = ImageFont.truetype(os.path.join(os.path.join(PROJECT_ROOT, "config" + os.sep + "fonts"), "FreeMono.ttf"),
                              size=font_size)
    if not os.path.exists(output_location):
        os.makedirs(output_location)

    for img in images:

        file_name = img["file_name"].split(os.sep)[-1]
        im_original = Image.open(img["file_name"])
        img_id = img["id"]
        im_copy = im_original.copy()
        draw = ImageDraw.Draw(im_copy)

        for ann in annotations:

            if ann["image_id"] == img_id:

                textbox_width_temp = max(ann["bbox"][2], font.getsize("g:%2.2f" % ann["score"])[0])
                bbox_to_rect = (ann["bbox"][0], ann["bbox"][1],
                                ann["bbox"][0] + ann["bbox"][2], ann["bbox"][1] + ann["bbox"][3])

                text_rect = (bbox_to_rect[0], bbox_to_rect[1] - textbox_height,
                             bbox_to_rect[0] + textbox_width_temp, bbox_to_rect[1])

                if ann["category_name"] == 'g':
                    colour = 'blue'
                    draw.rectangle(bbox_to_rect, outline=colour, width=rect_thickness)
                    draw.rectangle(text_rect,
                                   outline=colour, fill=colour)
                    draw.text((text_rect[0], text_rect[1] - textbox_height / 4), "g:%2.2f" % ann["score"], font=font)

                elif ann["category_name"] == 'p':
                    colour = 'orange'
                    draw.rectangle(bbox_to_rect, outline=colour, width=rect_thickness)
                    draw.rectangle(text_rect,
                                   outline=colour, fill=colour)
                    draw.text((text_rect[0], text_rect[1] - textbox_height / 4), "p:%2.2f" % ann["score"], font=font)

        im_copy.save(os.path.normpath(os.path.join(output_location, prefix + '_annotated_' + file_name)))


def get_category_count_per_img(coco_dict, category_name) -> dict:
    """
    Function for computing count of object category in image ('g' or 'p').

    Args:
        coco_dict (dict):
            standard coco json dict format

        category_name (str):
            'p' or 'g'

    Returns:
        count_per_img_dict (dict): key=image_id, value=count of category_name objects in image

    """

    count_per_img_dict = {}
    assert category_name in ['g', 'p'], "category not in ground truth category dict"

    img_ids = [entry["id"] for entry in coco_dict["images"]]
    annotations = [entry for entry in coco_dict["annotations"]]

    for img_id in img_ids:
        category_count = 0
        for ann in annotations:
            if ann["image_id"] == img_id:
                if ann["category_name"] == category_name:
                    category_count += 1
        count_per_img_dict[img_id] = category_count

    return count_per_img_dict


if __name__ == "__main__":
    top_parser = get_parsers()
    args = top_parser.parse_args()

    if args.command == "amend":
        parent_of_target = os.path.abspath(os.path.join(args.json_path, os.pardir))
        amended_json_path = os.path.join(parent_of_target, args.name + '_' + args.json_path.split(os.sep)[-1])
        amendGUI.build_amend_GUI(args.json_path, amended_json_path)
        print("also exporting amended csv...")
        coco_amend_dict = load_coco_json(amended_json_path)
        save_freq_csv(coco_dict=coco_amend_dict, destination=parent_of_target, prefix=args.name)

    elif args.command == "predict":

        if not os.path.exists(args.output_path):
            os.mkdir(args.output_path)

        if args.predict == "complete":
            coco_prediction_dict = perform_inference_coco(args.input_path, args.device, args.grande_size)
            save_coco_json(destination=args.output_path, prefix=args.name,
                           annotations=coco_prediction_dict["annotations"],
                           images=coco_prediction_dict["images"])
            save_annotated_images(coco_dict=coco_prediction_dict, destination=args.output_path, prefix=args.name)
            save_freq_csv(coco_dict=coco_prediction_dict, destination=args.output_path, prefix=args.name)

        elif args.predict == "json_only":
            coco_prediction_dict = perform_inference_coco(args.input_path, args.device, args.grande_size)
            save_coco_json(destination=args.output_path, prefix=args.name,
                           annotations=coco_prediction_dict["annotations"],
                           images=coco_prediction_dict["images"])

        elif args.predict == "frequency_only":
            coco_prediction_dict = perform_inference_coco(args.input_path, args.device, args.grande_size)
            save_freq_csv(coco_dict=coco_prediction_dict, destination=args.output_path, prefix=args.name)

        elif args.predict == "visualize_only":
            coco_prediction_dict = perform_inference_coco(args.input_path, args.device, args.grande_size)
            save_annotated_images(coco_dict=coco_prediction_dict, destination=args.output_path, prefix=args.name)
