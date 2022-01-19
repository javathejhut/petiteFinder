model = dict(
    type='FasterRCNN',
    backbone=dict(
        type='ResNet',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        frozen_stages=1,
        norm_cfg=dict(type='BN', requires_grad=True),
        norm_eval=True,
        style='pytorch',
        init_cfg=dict(type='Pretrained', checkpoint='torchvision://resnet50')),
    neck=dict(
        type='FPN',
        in_channels=[256, 512, 1024, 2048],
        out_channels=256,
        num_outs=5),
    rpn_head=dict(
        type='RPNHead',
        in_channels=256,
        feat_channels=256,
        anchor_generator=dict(
            type='AnchorGenerator',
            scales=[8],
            ratios=[0.5, 1.0, 2.0],
            strides=[4, 8, 16, 32, 64]),
        bbox_coder=dict(
            type='DeltaXYWHBBoxCoder',
            target_means=[0.0, 0.0, 0.0, 0.0],
            target_stds=[1.0, 1.0, 1.0, 1.0]),
        loss_cls=dict(
            type='CrossEntropyLoss', use_sigmoid=True, loss_weight=1.0),
        loss_bbox=dict(type='L1Loss', loss_weight=1.0)),
    roi_head=dict(
        type='StandardRoIHead',
        bbox_roi_extractor=dict(
            type='SingleRoIExtractor',
            roi_layer=dict(type='RoIAlign', output_size=7, sampling_ratio=0),
            out_channels=256,
            featmap_strides=[4, 8, 16, 32]),
        bbox_head=dict(
            type='Shared2FCBBoxHead',
            in_channels=256,
            fc_out_channels=1024,
            roi_feat_size=7,
            num_classes=2,
            bbox_coder=dict(
                type='DeltaXYWHBBoxCoder',
                target_means=[0.0, 0.0, 0.0, 0.0],
                target_stds=[0.1, 0.1, 0.2, 0.2]),
            reg_class_agnostic=False,
            loss_cls=dict(
                type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0),
            loss_bbox=dict(type='L1Loss', loss_weight=1.0))),
    train_cfg=dict(
        rpn=dict(
            assigner=dict(
                type='MaxIoUAssigner',
                pos_iou_thr=0.7,
                neg_iou_thr=0.3,
                min_pos_iou=0.3,
                match_low_quality=True,
                ignore_iof_thr=-1),
            sampler=dict(
                type='RandomSampler',
                num=256,
                pos_fraction=0.5,
                neg_pos_ub=-1,
                add_gt_as_proposals=False),
            allowed_border=-1,
            pos_weight=-1,
            debug=False),
        rpn_proposal=dict(
            nms_pre=2000,
            max_per_img=1000,
            nms=dict(type='nms', iou_threshold=0.7),
            min_bbox_size=0),
        rcnn=dict(
            assigner=dict(
                type='MaxIoUAssigner',
                pos_iou_thr=0.5,
                neg_iou_thr=0.5,
                min_pos_iou=0.5,
                match_low_quality=False,
                ignore_iof_thr=-1),
            sampler=dict(
                type='RandomSampler',
                num=512,
                pos_fraction=0.25,
                neg_pos_ub=-1,
                add_gt_as_proposals=True),
            pos_weight=-1,
            debug=False)),
    test_cfg=dict(
        rpn=dict(
            nms_pre=1000,
            max_per_img=1000,
            nms=dict(type='nms', iou_threshold=0.7),
            min_bbox_size=0),
        rcnn=dict(
            score_thr=0.05,
            nms=dict(type='nms', iou_threshold=0.5),
            max_per_img=100)))

dataset_type = 'CocoDataset'
data_root = '/home/groot/mmDetection/COCO_dataset_sliced/'
classes = ('g', 'p')

img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)

img_scale = (1024, 1024)

train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    #dict(type='Resize', img_scale=img_scale, keep_ratio=True, multiscale_mode="value"),
    dict(type='Resize', img_scale=img_scale, keep_ratio=True),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='RandomCrop', crop_type="relative_range", crop_size=(0.8,0.8)),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels'])
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=img_scale,
        flip=False,
        transforms=[
            #dict(type='Resize', keep_ratio=True, multiscale_mode="value"),
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            #dict(type='RandomCrop', crop_type="relative_range", crop_size=(0.9,0.9)),
            #dict(type='PhotoMetricDistortion'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img'])
        ])
]

data = dict(
    samples_per_gpu=2,
    workers_per_gpu=2,
    
    train=dict(
        type=dataset_type,
        ann_file = data_root + 'slice_coco_train/512_02/train_sliced_512.json',
        img_prefix = data_root + 'slice_coco_train/512_02/train_sliced_images_512/',
        pipeline=train_pipeline,
        classes = classes),
    
    val=dict(
        type=dataset_type,
        ann_file = data_root + 'slice_coco_validate/512_02/validate_sliced_512.json',
        img_prefix = data_root + 'slice_coco_validate/512_02/validate_sliced_images_512/',
        pipeline=test_pipeline,
        classes = classes),
    
    test=dict(
        type=dataset_type,
        ann_file = data_root + 'slice_coco_test/512_02/test_sliced_512.json',
        img_prefix = data_root + 'slice_coco_test/512_02/test_sliced_images_512/',
        pipeline=test_pipeline,
        classes = classes)
    )

evaluation = dict(interval=1, metric='bbox')


optimizer = dict(type='SGD', lr=0.001, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)

lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    step=[8, 11])

#lr_config = dict(
#    policy='CosineAnnealing',
#    min_lr_ratio=0.001,
#    by_epoch=False
#)

runner = dict(type='EpochBasedRunner', max_epochs=30)
checkpoint_config = dict(interval=1)

custom_hooks = [dict(type='NumClassCheckHook')]
dist_params = dict(backend='nccl')
log_level = 'INFO'
load_from = '/home/groot/mmDetection/checkpoints/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth'
resume_from = None
workflow = [('train', 1), ('val', 1)]

gpu_ids = range(0, 1)


project_name = 'petiteFinder'

name = 'exp_1024px_8anchor_linear_distortions_crop-0.8'
work_dir = '/media/klyshko/HDD/ML_runs/{}/{}'.format(project_name, name)


log_config = dict(
    interval=50,
    hooks = [ dict(type='TextLoggerHook'), dict(type='WandbLoggerHook', init_kwargs=dict(project=project_name,name=name))]
    )
