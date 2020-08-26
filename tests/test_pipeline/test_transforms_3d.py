import mmcv
import numpy as np
import torch

from mmdet3d.core import Box3DMode, CameraInstance3DBoxes, LiDARInstance3DBoxes
from mmdet3d.datasets import ObjectNoise, ObjectSample, RandomFlip3D


def test_remove_points_in_boxes():
    points = np.array([[68.1370, 3.3580, 2.5160, 0.0000],
                       [67.6970, 3.5500, 2.5010, 0.0000],
                       [67.6490, 3.7600, 2.5000, 0.0000],
                       [66.4140, 3.9010, 2.4590, 0.0000],
                       [66.0120, 4.0850, 2.4460, 0.0000],
                       [65.8340, 4.1780, 2.4400, 0.0000],
                       [65.8410, 4.3860, 2.4400, 0.0000],
                       [65.7450, 4.5870, 2.4380, 0.0000],
                       [65.5510, 4.7800, 2.4320, 0.0000],
                       [65.4860, 4.9820, 2.4300, 0.0000]])

    boxes = np.array(
        [[30.0285, 10.5110, -1.5304, 0.5100, 0.8700, 1.6000, 1.6400],
         [7.8369, 1.6053, -1.5605, 0.5800, 1.2300, 1.8200, -3.1000],
         [10.8740, -1.0827, -1.3310, 0.6000, 0.5200, 1.7100, 1.3500],
         [14.9783, 2.2466, -1.4950, 0.6100, 0.7300, 1.5300, -1.9200],
         [11.0656, 0.6195, -1.5202, 0.6600, 1.0100, 1.7600, -1.4600],
         [10.5994, -7.9049, -1.4980, 0.5300, 1.9600, 1.6800, 1.5600],
         [28.7068, -8.8244, -1.1485, 0.6500, 1.7900, 1.7500, 3.1200],
         [20.2630, 5.1947, -1.4799, 0.7300, 1.7600, 1.7300, 1.5100],
         [18.2496, 3.1887, -1.6109, 0.5600, 1.6800, 1.7100, 1.5600],
         [7.7396, -4.3245, -1.5801, 0.5600, 1.7900, 1.8000, -0.8300]])

    points = ObjectSample.remove_points_in_boxes(points, boxes)
    assert points.shape == (10, 4)


def test_object_sample():
    db_sampler = mmcv.ConfigDict({
        'data_root': './tests/data/kitti/',
        'info_path': './tests/data/kitti/kitti_dbinfos_train.pkl',
        'rate': 1.0,
        'prepare': {
            'filter_by_difficulty': [-1],
            'filter_by_min_points': {
                'Pedestrian': 10
            }
        },
        'classes': ['Pedestrian', 'Cyclist', 'Car'],
        'sample_groups': {
            'Pedestrian': 6
        }
    })
    np.random.seed(0)
    object_sample = ObjectSample(db_sampler)
    points = np.fromfile(
        './tests/data/kitti/training/velodyne_reduced/000000.bin',
        np.float32).reshape(-1, 4)
    annos = mmcv.load('./tests/data/kitti/kitti_infos_train.pkl')
    info = annos[0]
    rect = info['calib']['R0_rect'].astype(np.float32)
    Trv2c = info['calib']['Tr_velo_to_cam'].astype(np.float32)
    annos = info['annos']
    loc = annos['location']
    dims = annos['dimensions']
    rots = annos['rotation_y']
    gt_names = annos['name']

    gt_bboxes_3d = np.concatenate([loc, dims, rots[..., np.newaxis]],
                                  axis=1).astype(np.float32)
    gt_bboxes_3d = CameraInstance3DBoxes(gt_bboxes_3d).convert_to(
        Box3DMode.LIDAR, np.linalg.inv(rect @ Trv2c))
    CLASSES = ('Pedestrian', 'Cyclist', 'Car')
    gt_labels = []
    for cat in gt_names:
        if cat in CLASSES:
            gt_labels.append(CLASSES.index(cat))
        else:
            gt_labels.append(-1)
    input_dict = dict(
        points=points, gt_bboxes_3d=gt_bboxes_3d, gt_labels_3d=gt_labels)
    input_dict = object_sample(input_dict)
    points = input_dict['points']
    gt_bboxes_3d = input_dict['gt_bboxes_3d']
    gt_labels_3d = input_dict['gt_labels_3d']
    repr_str = repr(object_sample)
    expected_repr_str = 'ObjectSample sample_2d=False, ' \
                        'data_root=./tests/data/kitti/, ' \
                        'info_path=./tests/data/kitti/kitti' \
                        '_dbinfos_train.pkl, rate=1.0, ' \
                        'prepare={\'filter_by_difficulty\': [-1], ' \
                        '\'filter_by_min_points\': {\'Pedestrian\': 10}}, ' \
                        'classes=[\'Pedestrian\', \'Cyclist\', \'Car\'], ' \
                        'sample_groups={\'Pedestrian\': 6}'
    assert repr_str == expected_repr_str
    assert points.shape == (800, 4)
    assert gt_bboxes_3d.tensor.shape == (1, 7)
    assert np.all(gt_labels_3d == [0])


def test_object_noise():
    np.random.seed(0)
    object_noise = ObjectNoise()
    points = np.fromfile(
        './tests/data/kitti/training/velodyne_reduced/000000.bin',
        np.float32).reshape(-1, 4)
    annos = mmcv.load('./tests/data/kitti/kitti_infos_train.pkl')
    info = annos[0]
    rect = info['calib']['R0_rect'].astype(np.float32)
    Trv2c = info['calib']['Tr_velo_to_cam'].astype(np.float32)
    annos = info['annos']
    loc = annos['location']
    dims = annos['dimensions']
    rots = annos['rotation_y']
    gt_bboxes_3d = np.concatenate([loc, dims, rots[..., np.newaxis]],
                                  axis=1).astype(np.float32)
    gt_bboxes_3d = CameraInstance3DBoxes(gt_bboxes_3d).convert_to(
        Box3DMode.LIDAR, np.linalg.inv(rect @ Trv2c))
    input_dict = dict(points=points, gt_bboxes_3d=gt_bboxes_3d)
    input_dict = object_noise(input_dict)
    points = input_dict['points']
    gt_bboxes_3d = input_dict['gt_bboxes_3d'].tensor
    expected_gt_bboxes_3d = torch.tensor(
        [[9.1724, -1.7559, -1.3550, 0.4800, 1.2000, 1.8900, 0.0505]])
    repr_str = repr(object_noise)
    expected_repr_str = 'ObjectNoise(num_try=100, ' \
                        'translation_std=[0.25, 0.25, 0.25], ' \
                        'global_rot_range=[0.0, 0.0], ' \
                        'rot_range=[-0.15707963267, 0.15707963267])'

    assert repr_str == expected_repr_str
    assert points.shape == (800, 4)
    assert torch.allclose(gt_bboxes_3d, expected_gt_bboxes_3d, 1e-3)


def test_random_flip_3d():
    random_flip_3d = RandomFlip3D(
        flip_ratio_bev_horizontal=1.0, flip_ratio_bev_vertical=1.0)
    points = np.array([[22.7035, 9.3901, -0.2848, 0.0000],
                       [21.9826, 9.1766, -0.2698, 0.0000],
                       [21.4329, 9.0209, -0.2578, 0.0000],
                       [21.3068, 9.0205, -0.2558, 0.0000],
                       [21.3400, 9.1305, -0.2578, 0.0000],
                       [21.3291, 9.2099, -0.2588, 0.0000],
                       [21.2759, 9.2599, -0.2578, 0.0000],
                       [21.2686, 9.2982, -0.2588, 0.0000],
                       [21.2334, 9.3607, -0.2588, 0.0000],
                       [21.2179, 9.4372, -0.2598, 0.0000]])
    bbox3d_fields = ['gt_bboxes_3d']
    img_fields = []
    box_type_3d = LiDARInstance3DBoxes
    gt_bboxes_3d = LiDARInstance3DBoxes(
        torch.tensor(
            [[38.9229, 18.4417, -1.1459, 0.7100, 1.7600, 1.8600, -2.2652],
             [12.7768, 0.5795, -2.2682, 0.5700, 0.9900, 1.7200, -2.5029],
             [12.7557, 2.2996, -1.4869, 0.6100, 1.1100, 1.9000, -1.9390],
             [10.6677, 0.8064, -1.5435, 0.7900, 0.9600, 1.7900, 1.0856],
             [5.0903, 5.1004, -1.2694, 0.7100, 1.7000, 1.8300, -1.9136]]))
    input_dict = dict(
        points=points,
        bbox3d_fields=bbox3d_fields,
        box_type_3d=box_type_3d,
        img_fields=img_fields,
        gt_bboxes_3d=gt_bboxes_3d)
    input_dict = random_flip_3d(input_dict)
    points = input_dict['points']
    gt_bboxes_3d = input_dict['gt_bboxes_3d'].tensor
    expected_points = np.array([[22.7035, -9.3901, -0.2848, 0.0000],
                                [21.9826, -9.1766, -0.2698, 0.0000],
                                [21.4329, -9.0209, -0.2578, 0.0000],
                                [21.3068, -9.0205, -0.2558, 0.0000],
                                [21.3400, -9.1305, -0.2578, 0.0000],
                                [21.3291, -9.2099, -0.2588, 0.0000],
                                [21.2759, -9.2599, -0.2578, 0.0000],
                                [21.2686, -9.2982, -0.2588, 0.0000],
                                [21.2334, -9.3607, -0.2588, 0.0000],
                                [21.2179, -9.4372, -0.2598, 0.0000]])
    expected_gt_bboxes_3d = torch.tensor(
        [[38.9229, -18.4417, -1.1459, 0.7100, 1.7600, 1.8600, 5.4068],
         [12.7768, -0.5795, -2.2682, 0.5700, 0.9900, 1.7200, 5.6445],
         [12.7557, -2.2996, -1.4869, 0.6100, 1.1100, 1.9000, 5.0806],
         [10.6677, -0.8064, -1.5435, 0.7900, 0.9600, 1.7900, 2.0560],
         [5.0903, -5.1004, -1.2694, 0.7100, 1.7000, 1.8300, 5.0552]])
    repr_str = repr(random_flip_3d)
    expected_repr_str = 'RandomFlip3D(sync_2d=True,' \
                        'flip_ratio_bev_vertical=1.0)'
    assert np.allclose(points, expected_points)
    assert torch.allclose(gt_bboxes_3d, expected_gt_bboxes_3d)
    assert repr_str == expected_repr_str