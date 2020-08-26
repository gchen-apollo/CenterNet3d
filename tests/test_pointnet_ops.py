import pytest
import torch

from mmdet3d.ops import (ball_query, furthest_point_sample, gather_points,
                         grouping_operation, three_interpolate, three_nn)


def test_fps():
    if not torch.cuda.is_available():
        pytest.skip()
    xyz = torch.tensor([[[-0.2748, 1.0020, -1.1674], [0.1015, 1.3952, -1.2681],
                         [-0.8070, 2.4137,
                          -0.5845], [-1.0001, 2.1982, -0.5859],
                         [0.3841, 1.8983, -0.7431]],
                        [[-1.0696, 3.0758,
                          -0.1899], [-0.2559, 3.5521, -0.1402],
                         [0.8164, 4.0081, -0.1839], [-1.1000, 3.0213, -0.8205],
                         [-0.0518, 3.7251, -0.3950]]]).cuda()

    idx = furthest_point_sample(xyz, 3)
    expected_idx = torch.tensor([[0, 2, 4], [0, 2, 1]]).cuda()
    assert torch.all(idx == expected_idx)


def test_ball_query():
    if not torch.cuda.is_available():
        pytest.skip()
    new_xyz = torch.tensor([[[-0.0740, 1.3147, -1.3625],
                             [-2.2769, 2.7817, -0.2334],
                             [-0.4003, 2.4666, -0.5116],
                             [-0.0740, 1.3147, -1.3625],
                             [-0.0740, 1.3147, -1.3625]],
                            [[-2.0289, 2.4952, -0.1708],
                             [-2.0668, 6.0278, -0.4875],
                             [0.4066, 1.4211, -0.2947],
                             [-2.0289, 2.4952, -0.1708],
                             [-2.0289, 2.4952, -0.1708]]]).cuda()

    xyz = torch.tensor([[[-0.0740, 1.3147, -1.3625], [0.5555, 1.0399, -1.3634],
                         [-0.4003, 2.4666,
                          -0.5116], [-0.5251, 2.4379, -0.8466],
                         [-0.9691, 1.1418,
                          -1.3733], [-0.2232, 0.9561, -1.3626],
                         [-2.2769, 2.7817, -0.2334],
                         [-0.2822, 1.3192, -1.3645], [0.1533, 1.5024, -1.0432],
                         [0.4917, 1.1529, -1.3496]],
                        [[-2.0289, 2.4952,
                          -0.1708], [-0.7188, 0.9956, -0.5096],
                         [-2.0668, 6.0278, -0.4875], [-1.9304, 3.3092, 0.6610],
                         [0.0949, 1.4332, 0.3140], [-1.2879, 2.0008, -0.7791],
                         [-0.7252, 0.9611, -0.6371], [0.4066, 1.4211, -0.2947],
                         [0.3220, 1.4447, 0.3548], [-0.9744, 2.3856,
                                                    -1.2000]]]).cuda()

    idx = ball_query(0.2, 5, xyz, new_xyz)
    expected_idx = torch.tensor([[[0, 0, 0, 0, 0], [6, 6, 6, 6, 6],
                                  [2, 2, 2, 2, 2], [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0]],
                                 [[0, 0, 0, 0, 0], [2, 2, 2, 2, 2],
                                  [7, 7, 7, 7, 7], [0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0]]]).cuda()

    assert torch.all(idx == expected_idx)


def test_grouping_points():
    if not torch.cuda.is_available():
        pytest.skip()
    idx = torch.tensor([[[0, 0, 0], [3, 3, 3], [8, 8, 8], [0, 0, 0], [0, 0, 0],
                         [0, 0, 0]],
                        [[0, 0, 0], [6, 6, 6], [9, 9, 9], [0, 0, 0], [0, 0, 0],
                         [0, 0, 0]]]).int().cuda()
    festures = torch.tensor([[[
        0.5798, -0.7981, -0.9280, -1.3311, 1.3687, 0.9277, -0.4164, -1.8274,
        0.9268, 0.8414
    ],
                              [
                                  5.4247, 1.5113, 2.3944, 1.4740, 5.0300,
                                  5.1030, 1.9360, 2.1939, 2.1581, 3.4666
                              ],
                              [
                                  -1.6266, -1.0281, -1.0393, -1.6931, -1.3982,
                                  -0.5732, -1.0830, -1.7561, -1.6786, -1.6967
                              ]],
                             [[
                                 -0.0380, -0.1880, -1.5724, 0.6905, -0.3190,
                                 0.7798, -0.3693, -0.9457, -0.2942, -1.8527
                             ],
                              [
                                  1.1773, 1.5009, 2.6399, 5.9242, 1.0962,
                                  2.7346, 6.0865, 1.5555, 4.3303, 2.8229
                              ],
                              [
                                  -0.6646, -0.6870, -0.1125, -0.2224, -0.3445,
                                  -1.4049, 0.4990, -0.7037, -0.9924, 0.0386
                              ]]]).cuda()

    output = grouping_operation(festures, idx)
    expected_output = torch.tensor([[[[0.5798, 0.5798, 0.5798],
                                      [-1.3311, -1.3311, -1.3311],
                                      [0.9268, 0.9268, 0.9268],
                                      [0.5798, 0.5798, 0.5798],
                                      [0.5798, 0.5798, 0.5798],
                                      [0.5798, 0.5798, 0.5798]],
                                     [[5.4247, 5.4247, 5.4247],
                                      [1.4740, 1.4740, 1.4740],
                                      [2.1581, 2.1581, 2.1581],
                                      [5.4247, 5.4247, 5.4247],
                                      [5.4247, 5.4247, 5.4247],
                                      [5.4247, 5.4247, 5.4247]],
                                     [[-1.6266, -1.6266, -1.6266],
                                      [-1.6931, -1.6931, -1.6931],
                                      [-1.6786, -1.6786, -1.6786],
                                      [-1.6266, -1.6266, -1.6266],
                                      [-1.6266, -1.6266, -1.6266],
                                      [-1.6266, -1.6266, -1.6266]]],
                                    [[[-0.0380, -0.0380, -0.0380],
                                      [-0.3693, -0.3693, -0.3693],
                                      [-1.8527, -1.8527, -1.8527],
                                      [-0.0380, -0.0380, -0.0380],
                                      [-0.0380, -0.0380, -0.0380],
                                      [-0.0380, -0.0380, -0.0380]],
                                     [[1.1773, 1.1773, 1.1773],
                                      [6.0865, 6.0865, 6.0865],
                                      [2.8229, 2.8229, 2.8229],
                                      [1.1773, 1.1773, 1.1773],
                                      [1.1773, 1.1773, 1.1773],
                                      [1.1773, 1.1773, 1.1773]],
                                     [[-0.6646, -0.6646, -0.6646],
                                      [0.4990, 0.4990, 0.4990],
                                      [0.0386, 0.0386, 0.0386],
                                      [-0.6646, -0.6646, -0.6646],
                                      [-0.6646, -0.6646, -0.6646],
                                      [-0.6646, -0.6646, -0.6646]]]]).cuda()
    assert torch.allclose(output, expected_output)


def test_gather_points():
    if not torch.cuda.is_available():
        pytest.skip()
    features = torch.tensor([[[
        -1.6095, -0.1029, -0.8876, -1.2447, -2.4031, 0.3708, -1.1586, -1.4967,
        -0.4800, 0.2252
    ],
                              [
                                  1.9138, 3.4979, 1.6854, 1.5631, 3.6776,
                                  3.1154, 2.1705, 2.5221, 2.0411, 3.1446
                              ],
                              [
                                  -1.4173, 0.3073, -1.4339, -1.4340, -1.2770,
                                  -0.2867, -1.4162, -1.4044, -1.4245, -1.4074
                              ]],
                             [[
                                 0.2160, 0.0842, 0.3661, -0.2749, -0.4909,
                                 -0.6066, -0.8773, -0.0745, -0.9496, 0.1434
                             ],
                              [
                                  1.3644, 1.8087, 1.6855, 1.9563, 1.2746,
                                  1.9662, 0.9566, 1.8778, 1.1437, 1.3639
                              ],
                              [
                                  -0.7172, 0.1692, 0.2241, 0.0721, -0.7540,
                                  0.0462, -0.6227, 0.3223, -0.6944, -0.5294
                              ]]]).cuda()

    idx = torch.tensor([[0, 1, 4, 0, 0, 0], [0, 5, 6, 0, 0, 0]]).int().cuda()

    output = gather_points(features, idx)
    expected_output = torch.tensor(
        [[[-1.6095, -0.1029, -2.4031, -1.6095, -1.6095, -1.6095],
          [1.9138, 3.4979, 3.6776, 1.9138, 1.9138, 1.9138],
          [-1.4173, 0.3073, -1.2770, -1.4173, -1.4173, -1.4173]],
         [[0.2160, -0.6066, -0.8773, 0.2160, 0.2160, 0.2160],
          [1.3644, 1.9662, 0.9566, 1.3644, 1.3644, 1.3644],
          [-0.7172, 0.0462, -0.6227, -0.7172, -0.7172, -0.7172]]]).cuda()

    assert torch.allclose(output, expected_output)


def test_three_interpolate():
    if not torch.cuda.is_available():
        pytest.skip()
    features = torch.tensor([[[2.4350, 4.7516, 4.4995, 2.4350, 2.4350, 2.4350],
                              [3.1236, 2.6278, 3.0447, 3.1236, 3.1236, 3.1236],
                              [2.6732, 2.8677, 2.6436, 2.6732, 2.6732, 2.6732],
                              [0.0124, 7.0150, 7.0199, 0.0124, 0.0124, 0.0124],
                              [0.3207, 0.0000, 0.3411, 0.3207, 0.3207,
                               0.3207]],
                             [[0.0000, 0.9544, 2.4532, 0.0000, 0.0000, 0.0000],
                              [0.5346, 1.9176, 1.4715, 0.5346, 0.5346, 0.5346],
                              [0.0000, 0.2744, 2.0842, 0.0000, 0.0000, 0.0000],
                              [0.3414, 1.5063, 1.6209, 0.3414, 0.3414, 0.3414],
                              [0.5814, 0.0103, 0.0000, 0.5814, 0.5814,
                               0.5814]]]).cuda()

    idx = torch.tensor([[[0, 1, 2], [2, 3, 4], [2, 3, 4], [0, 1, 2], [0, 1, 2],
                         [0, 1, 3]],
                        [[0, 2, 3], [1, 3, 4], [2, 1, 4], [0, 2, 4], [0, 2, 4],
                         [0, 1, 2]]]).int().cuda()

    weight = torch.tensor([[[3.3333e-01, 3.3333e-01, 3.3333e-01],
                            [1.0000e+00, 5.8155e-08, 2.2373e-08],
                            [1.0000e+00, 1.7737e-08, 1.7356e-08],
                            [3.3333e-01, 3.3333e-01, 3.3333e-01],
                            [3.3333e-01, 3.3333e-01, 3.3333e-01],
                            [3.3333e-01, 3.3333e-01, 3.3333e-01]],
                           [[3.3333e-01, 3.3333e-01, 3.3333e-01],
                            [1.0000e+00, 1.3651e-08, 7.7312e-09],
                            [1.0000e+00, 1.7148e-08, 1.4070e-08],
                            [3.3333e-01, 3.3333e-01, 3.3333e-01],
                            [3.3333e-01, 3.3333e-01, 3.3333e-01],
                            [3.3333e-01, 3.3333e-01, 3.3333e-01]]]).cuda()

    output = three_interpolate(features, idx, weight)
    expected_output = torch.tensor([[[
        3.8953e+00, 4.4995e+00, 4.4995e+00, 3.8953e+00, 3.8953e+00, 3.2072e+00
    ], [
        2.9320e+00, 3.0447e+00, 3.0447e+00, 2.9320e+00, 2.9320e+00, 2.9583e+00
    ], [
        2.7281e+00, 2.6436e+00, 2.6436e+00, 2.7281e+00, 2.7281e+00, 2.7380e+00
    ], [
        4.6824e+00, 7.0199e+00, 7.0199e+00, 4.6824e+00, 4.6824e+00, 2.3466e+00
    ], [
        2.2060e-01, 3.4110e-01, 3.4110e-01, 2.2060e-01, 2.2060e-01, 2.1380e-01
    ]],
                                    [[
                                        8.1773e-01, 9.5440e-01, 2.4532e+00,
                                        8.1773e-01, 8.1773e-01, 1.1359e+00
                                    ],
                                     [
                                         8.4689e-01, 1.9176e+00, 1.4715e+00,
                                         8.4689e-01, 8.4689e-01, 1.3079e+00
                                     ],
                                     [
                                         6.9473e-01, 2.7440e-01, 2.0842e+00,
                                         6.9473e-01, 6.9473e-01, 7.8619e-01
                                     ],
                                     [
                                         7.6789e-01, 1.5063e+00, 1.6209e+00,
                                         7.6789e-01, 7.6789e-01, 1.1562e+00
                                     ],
                                     [
                                         3.8760e-01, 1.0300e-02, 8.3569e-09,
                                         3.8760e-01, 3.8760e-01, 1.9723e-01
                                     ]]]).cuda()

    assert torch.allclose(output, expected_output, 1e-4)


def test_three_nn():
    if not torch.cuda.is_available():
        pytest.skip()
    known = torch.tensor([[[-1.8373, 3.5605,
                            -0.7867], [0.7615, 2.9420, 0.2314],
                           [-0.6503, 3.6637, -1.0622],
                           [-1.8373, 3.5605, -0.7867],
                           [-1.8373, 3.5605, -0.7867]],
                          [[-1.3399, 1.9991, -0.3698],
                           [-0.0799, 0.9698,
                            -0.8457], [0.0858, 2.4721, -0.1928],
                           [-1.3399, 1.9991, -0.3698],
                           [-1.3399, 1.9991, -0.3698]]]).cuda()

    unknown = torch.tensor([[[-1.8373, 3.5605, -0.7867],
                             [0.7615, 2.9420, 0.2314],
                             [-0.6503, 3.6637, -1.0622],
                             [-1.5237, 2.3976, -0.8097],
                             [-0.0722, 3.4017, -0.2880],
                             [0.5198, 3.0661, -0.4605],
                             [-2.0185, 3.5019, -0.3236],
                             [0.5098, 3.1020, 0.5799],
                             [-1.6137, 3.8443, -0.5269],
                             [0.7341, 2.9626, -0.3189]],
                            [[-1.3399, 1.9991, -0.3698],
                             [-0.0799, 0.9698, -0.8457],
                             [0.0858, 2.4721, -0.1928],
                             [-0.9022, 1.6560, -1.3090],
                             [0.1156, 1.6901, -0.4366],
                             [-0.6477, 2.3576, -0.1563],
                             [-0.8482, 1.1466, -1.2704],
                             [-0.8753, 2.0845, -0.3460],
                             [-0.5621, 1.4233, -1.2858],
                             [-0.5883, 1.3114, -1.2899]]]).cuda()

    dist, idx = three_nn(unknown, known)
    expected_dist = torch.tensor([[[0.0000, 0.0000, 0.0000],
                                   [0.0000, 2.0463, 2.8588],
                                   [0.0000, 1.2229, 1.2229],
                                   [1.2047, 1.2047, 1.2047],
                                   [1.0011, 1.0845, 1.8411],
                                   [0.7433, 1.4451, 2.4304],
                                   [0.5007, 0.5007, 0.5007],
                                   [0.4587, 2.0875, 2.7544],
                                   [0.4450, 0.4450, 0.4450],
                                   [0.5514, 1.7206, 2.6811]],
                                  [[0.0000, 0.0000, 0.0000],
                                   [0.0000, 1.6464, 1.6952],
                                   [0.0000, 1.5125, 1.5125],
                                   [1.0915, 1.0915, 1.0915],
                                   [0.8197, 0.8511, 1.4894],
                                   [0.7433, 0.8082, 0.8082],
                                   [0.8955, 1.3340, 1.3340],
                                   [0.4730, 0.4730, 0.4730],
                                   [0.7949, 1.3325, 1.3325],
                                   [0.7566, 1.3727, 1.3727]]]).cuda()
    expected_idx = torch.tensor([[[0, 3, 4], [1, 2, 0], [2, 0, 3], [0, 3, 4],
                                  [2, 1, 0], [1, 2, 0], [0, 3, 4], [1, 2, 0],
                                  [0, 3, 4], [1, 2, 0]],
                                 [[0, 3, 4], [1, 2, 0], [2, 0, 3], [0, 3, 4],
                                  [2, 1, 0], [2, 0, 3], [1, 0, 3], [0, 3, 4],
                                  [1, 0, 3], [1, 0, 3]]]).cuda()

    assert torch.allclose(dist, expected_dist, 1e-4)
    assert torch.all(idx == expected_idx)