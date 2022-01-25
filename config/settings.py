import os
"""
Default (finely tuned) petiteFinder inference parameters.
Leave default unless doing invasive tuning for your images.
"""

PROJECT_ROOT = os.path.abspath(os.getcwd() + os.sep)
MODEL_PATH = os.path.normpath(PROJECT_ROOT + "/config/model_weights/1024px_epoch_17_petiteFinder_publish-476b1e47.pth")
MODEL_CONFIG_PATH = os.path.normpath(PROJECT_ROOT + "/config/model_cfg/faster_rcnn_r50_fpn_1x_coco_petiteFinder.py")
TRAINED_IMAGE_WIDTH = 2376
TRAINED_IMAGE_HEIGHT = 2288
TRAINED_SLICE_HEIGHT = 512
TRAINED_SLICE_WIDTH = 512

# SAHI post-processing parameters optimized in grid search
MODEL_CLASS_NAME = "MmdetDetectionModel"
MODEL_CONFIDENCE_THRESHOLD = 0.6
POST_PROCESS_TYPE = "GREEDYNMM"
POST_PROCESS_METRIC = "IOS"
POST_PROCESS_MATCH_THRESHOLD = 0.5
OVERLAP_HEIGHT_RATIO = 0.2
OVERLAP_WIDTH_RATIO = 0.2
