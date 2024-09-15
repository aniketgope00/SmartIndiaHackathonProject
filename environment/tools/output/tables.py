# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2008-2024 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    tables.py
# @author  Yun-Pang Floetteroed
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @date    2008-03-18

"""
This file defines global tables used to:

- define the parameters in link cost functions
- define link cost functions
- conduct significance tests
"""
crCurveTable = {"CR2": (1., 2., 2.),
                "CR3": (1., 2., 1.),
                "CR4": (1.7, 2., 1.),
                "CR5": (1., 3., 0.9),
                "CR6": (1., 3., 0.8),
                "CR7": (1., 3., 0.5),
                "CR8": (3., 3., 0.8),
                "CR10": (1., 2., 1.5),
                "CR11": (1., 1., 1.),
                "CR12": (1., 4., 1.),
                "CR13": (1., 2., 1.3)}

# crCurveTable = {"CR1": (1., 2., 1.),
#                "CR2": (1., 2., 1.),
#                "CR3": (1., 2., 1.),
#                "CR4": (1., 2., 1.),
#                "CR5": (1., 2., 1.),
#                "CR6": (1., 2., 1.),
#                "CR10": (1., 2., 1.),
#                "CR11": (0.25, 2., 1.)}


def updateCurveTable(filename):
    f = open(filename)
    for line in f:
        elements = line.split()
        crCurveTable[elements[0]] = []
        for entry in elements[1:]:
            crCurveTable[elements[0]].append(float(entry))


laneTypeTable = {1: [[5, 200.0, "CR7"], [7, 412.5, "CR7"], [9, 600.0, "CR6"], [11, 800.0, "CR5"],
                     [13, 1125.0, "CR5"], [16, 1583.33, "CR4"], [18, 1100.0, "CR3"], [22, 1200.0, "CR3"],
                     [26, 1300.0, "CR3"], [30, 1400.0, "CR3"], [999., 1400.0, "CR3"]],
                 2: [[11, 800.0, "CR5"], [13, 875.0, "CR5"], [16, 1500.0, "CR4"], [30, 1800.0, "CR13"],
                     [999., 1800.0, "CR13"]],
                 3: [[11, 1333.33, "CR5"], [16, 1500.0, "CR3"], [30, 2000.0, "CR13"], [999., 2000.0, "CR13"]],
                 4: [[30, 2000.0, "CR13"], [999., 2000.0, "CR13"]]}

# laneTypeTable = {1:[[7., 200., "CR6"], [9., 800., "CR3"], [12., 800., "CR4"], [13., 800., "CR2"], [18., 1200., "CR2"],
#                    [19., 1300., "CR4"], [22., 1200., "CR2"], [25., 1300., "CR2"], [30., 1350., "CR1"],
#                    [33., 1400., "CR1"], [999., 1500., "CR1"]],
#                 2:[[7., 200., "CR6"], [9., 800., "CR3"], [13., 1000., "CR3"], [15., 1050., "CR2"],
#                    [16., 1100., "CR2"], [25., 1300., "CR2"], [27., 1400., "CR1"], [29., 1400., "CR3"],
#                    [30., 1500., "CR2"], [34., 1400., "CR2"], [999., 1500., "CR1"]],
#                 3:[[7., 200., "CR6"], [9., 800., "CR3"], [13., 1000, "CR3"], [16., 1100., "CR2"], [19., 1300., "CR2"],
#                    [25., 1400., "CR2"], [27., 1400., "CR1"], [30., 1500., "CR2"], [33., 1400., "CR1"],
#                    [999., 1500., "CR1"]],
# 4:[[7., 200., "CR6"], [9., 800., "CR3"], [13., 1000., "CR3"], [17,
# 1100., "CR2"], [19., 1300., "CR1"], [25., 1400., "CR2"], [27., 1400.,
# "CR2"], [29., 1400., "CR3"], [30., 1500., "CR2"], [33., 1400., "CR1"],
# [999., 1500., "CR1"]]}


chiSquareTable = \
    [[0,        0.10,     0.05,    0.025,     0.01,    0.001],
     [1,       2.706,    3.841,    5.024,    6.635,   10.828],
        [2,       4.605,    5.991,    7.378,    9.210,   13.816],
        [3,       6.251,    7.815,    9.348,   11.345,   16.266],
        [4,       7.779,    9.488,   11.143,   13.277,   18.467],
        [5,       9.236,   11.070,   12.833,   15.086,   20.515],
        [6,      10.645,   12.592,   14.449,   16.812,   22.458],
        [7,      12.017,   14.067,   16.013,   18.475,   24.322],
        [8,      13.362,   15.507,   17.535,   20.090,   26.125],
        [9,      14.684,   16.919,   19.023,   21.666,   27.877],
        [10,      15.987,   18.307,   20.483,   23.209,   29.588],
        [11,      17.275,   19.675,   21.920,   24.725,   31.264],
        [12,      18.549,   21.026,   23.337,   26.217,   32.910],
        [13,      19.812,   22.362,   24.736,   27.688,   34.528],
        [14,      21.064,   23.685,   26.119,   29.141,   36.123],
        [15,      22.307,   24.996,   27.488,   30.578,   37.697],
        [16,      23.542,   26.296,   28.845,   32.000,   39.252],
        [17,      24.769,   27.587,   30.191,   33.409,   40.790],
        [18,      25.989,   28.869,   31.526,   34.805,   42.312],
        [19,      27.204,   30.144,   32.852,   36.191,   43.820],
        [20,      28.412,   31.410,   34.170,   37.566,   45.315],
        [21,      29.615,   32.671,   35.479,   38.932,   46.797],
        [22,      30.813,   33.924,   36.781,   40.289,   48.268],
        [23,      32.007,   35.172,   38.076,   41.638,   49.728],
        [24,      33.196,   36.415,   39.364,   42.980,   51.179],
        [25,      34.382,   37.652,   40.646,   44.314,   52.620],
        [26,      35.563,   38.885,   41.923,   45.642,   54.052],
        [27,      36.741,   40.113,   43.195,   46.963,   55.476],
        [28,      37.916,   41.337,   44.461,   48.278,   56.892],
        [29,      39.087,   42.557,   45.722,   49.588,   58.301],
        [30,      40.256,   43.773,   46.979,   50.892,   59.703],
        [31,      41.422,   44.985,   48.232,   52.191,   61.098],
        [32,      42.585,   46.194,   49.480,   53.486,   62.487],
        [33,      43.745,   47.400,   50.725,   54.776,   63.870],
        [34,      44.903,   48.602,   51.966,   56.061,   65.247],
        [35,      46.059,   49.802,   53.203,   57.342,   66.619],
        [36,      47.212,   50.998,   54.437,   58.619,   67.985],
        [37,      48.363,   52.192,   55.668,   59.893,   69.347],
        [38,      49.513,   53.384,   56.896,   61.162,   70.703],
        [39,      50.660,   54.572,   58.120,   62.428,   72.055],
        [40,      51.805,   55.758,   59.342,   63.691,   73.402],
        [41,      52.949,   56.942,   60.561,   64.950,   74.745],
        [42,      54.090,   58.124,   61.777,   66.206,   76.084],
        [43,      55.230,   59.304,   62.990,   67.459,   77.419],
        [44,      56.369,   60.481,   64.201,   68.710,   78.750],
        [45,      57.505,   61.656,   65.410,   69.957,   80.077],
        [46,      58.641,   62.830,   66.617,   71.201,   81.400],
        [47,      59.774,   64.001,   67.821,   72.443,   82.720],
        [48,      60.907,   65.171,   69.023,   73.683,   84.037],
        [49,      62.038,   66.339,   70.222,   74.919,   85.351],
        [50,      63.167,   67.505,   71.420,   76.154,   86.661],
        [51,      64.295,   68.669,   72.616,   77.386,   87.968],
        [52,      65.422,   69.832,   73.810,   78.616,   89.272],
        [53,      66.548,   70.993,   75.002,   79.843,   90.573],
        [54,      67.673,   72.153,   76.192,   81.069,   91.872],
        [55,      68.796,   73.311,   77.380,   82.292,   93.168],
        [56,      69.919,   74.468,   78.567,   83.513,   94.461],
        [57,      71.040,   75.624,   79.752,   84.733,   95.751],
        [58,      72.160,   76.778,   80.936,   85.950,   97.039],
        [59,      73.279,   77.931,   82.117,   87.166,   98.324],
        [60,      74.397,   79.082,   83.298,   88.379,   99.607],
        [61,      75.514,   80.232,   84.476,   89.591,  100.888],
        [62,      76.630,   81.381,   85.654,   90.802,  102.166],
        [63,      77.745,   82.529,   86.830,   92.010,  103.442],
        [64,      78.860,   83.675,   88.004,   93.217,  104.716],
        [65,      79.973,   84.821,   89.177,   94.422,  105.988],
        [66,      81.085,   85.965,   90.349,   95.626,  107.258],
        [67,      82.197,   87.108,   91.519,   96.828,  108.526],
        [68,      83.308,   88.250,   92.689,   98.028,  109.791],
        [69,      84.418,   89.391,   93.856,   99.228,  111.055],
        [70,      85.527,   90.531,   95.023,  100.425,  112.317],
        [71,      86.635,   91.670,   96.189,  101.621,  113.577],
        [72,      87.743,   92.808,   97.353,  102.816,  114.835],
        [73,      88.850,   93.945,   98.516,  104.010,  116.092],
        [74,      89.956,   95.081,   99.678,  105.202,  117.346],
        [75,      91.061,   96.217,  100.839,  106.393,  118.599],
        [76,      92.166,   97.351,  101.999,  107.583,  119.850],
        [77,      93.270,   98.484,  103.158,  108.771,  121.100],
        [78,      94.374,   99.617,  104.316,  109.958,  122.348],
        [79,      95.476,  100.749,  105.473,  111.144,  123.594],
        [80,      96.578,  101.879,  106.629,  112.329,  124.839],
        [81,      97.680,  103.010,  107.783,  113.512,  126.083],
        [82,      98.780,  104.139,  108.937,  114.695,  127.324],
        [83,      99.880,  105.267,  110.090,  115.876,  128.565],
        [84,     100.980,  106.395,  111.242,  117.057,  129.804],
        [85,     102.079,  107.522,  112.393,  118.236,  131.041],
        [86,     103.177,  108.648,  113.544,  119.414,  132.277],
        [87,     104.275,  109.773,  114.693,  120.591,  133.512],
        [88,     105.372,  110.898,  115.841,  121.767,  134.746],
        [89,     106.469,  112.022,  116.989,  122.942,  135.978],
        [90,     107.565,  113.145,  118.136,  124.116,  137.208],
        [91,     108.661,  114.268,  119.282,  125.289,  138.438],
        [92,     109.756,  115.390,  120.427,  126.462,  139.666],
        [93,     110.850,  116.511,  121.571,  127.633,  140.893],
        [94,     111.944,  117.632,  122.715,  128.803,  142.119],
        [95,     113.038,  118.752,  123.858,  129.973,  143.344],
        [96,     114.131,  119.871,  125.000,  131.141,  144.567],
        [97,     115.223,  120.990,  126.141,  132.309,  145.789],
        [98,     116.315,  122.108,  127.282,  133.476,  147.010],
        [99,     117.407,  123.225,  128.422,  134.642,  148.230],
        [100,     118.498,  124.342,  129.561,  135.807,  149.449]]

tTable = \
    [[0, 0.25, 0.20, 0.15, 0.10, 0.05, 0.025, 0.02, 0.01, 0.005, 0.0025, 0.001, 0.0005],
     [1, 1.000, 1.376, 1.963, 3.078, 6.314, 12.71,
         15.89, 31.82, 63.66, 127.3, 318.3, 636.6],
        [2, 0.816, 1.061, 1.386, 1.886, 2.920, 4.303,
            4.849, 6.965, 9.925, 14.09, 22.33, 31.60],
        [3, 0.765, 0.978, 1.250, 1.638, 2.353, 3.182,
            3.482, 4.541, 5.841, 7.453, 10.21, 12.92],
        [4, 0.741, 0.941, 1.190, 1.533, 2.132, 2.776,
            2.999, 3.747, 4.604, 5.598, 7.173, 8.610],
        [5, 0.727, 0.920, 1.156, 1.476, 2.015, 2.571,
            2.757, 3.365, 4.032, 4.773, 5.893, 6.869],
        [6, 0.718, 0.906, 1.134, 1.440, 1.943, 2.447,
            2.612, 3.143, 3.707, 4.317, 5.208, 5.959],
        [7, 0.711, 0.896, 1.119, 1.415, 1.895, 2.365,
            2.517, 2.998, 3.499, 4.029, 4.785, 5.408],
        [8, 0.706, 0.889, 1.108, 1.397, 1.860, 2.306,
            2.449, 2.896, 3.355, 3.833, 4.501, 5.041],
        [9, 0.703, 0.883, 1.100, 1.383, 1.833, 2.262,
            2.398, 2.821, 3.250, 3.690, 4.297, 4.781],
        [10, 0.700, 0.879, 1.093, 1.372, 1.812, 2.228,
            2.359, 2.764, 3.169, 3.581, 4.144, 4.587],
        [11, 0.697, 0.876, 1.088, 1.363, 1.796, 2.201,
            2.328, 2.718, 3.106, 3.497, 4.025, 4.437],
        [12, 0.695, 0.873, 1.083, 1.356, 1.782, 2.179,
            2.303, 2.681, 3.055, 3.428, 3.930, 4.318],
        [13, 0.694, 0.870, 1.079, 1.350, 1.771, 2.160,
            2.282, 2.650, 3.012, 3.372, 3.852, 4.221],
        [14, 0.692, 0.868, 1.076, 1.345, 1.761, 2.145,
            2.264, 2.624, 2.977, 3.326, 3.787, 4.140],
        [15, 0.691, 0.866, 1.074, 1.341, 1.753, 2.131,
            2.249, 2.602, 2.947, 3.286, 3.733, 4.073],
        [16, 0.690, 0.865, 1.071, 1.337, 1.746, 2.120,
            2.235, 2.583, 2.921, 3.252, 3.686, 4.015],
        [17, 0.689, 0.863, 1.069, 1.333, 1.740, 2.110,
            2.224, 2.567, 2.898, 3.222, 3.646, 3.965],
        [18, 0.688, 0.862, 1.067, 1.330, 1.734, 2.101,
            2.214, 2.552, 2.878, 3.197, 3.611, 3.922],
        [19, 0.688, 0.861, 1.066, 1.328, 1.729, 2.093,
            2.205, 2.539, 2.861, 3.174, 3.579, 3.883],
        [20, 0.687, 0.860, 1.064, 1.325, 1.725, 2.086,
            2.197, 2.528, 2.845, 3.153, 3.552, 3.850],
        [21, 0.663, 0.859, 1.063, 1.323, 1.721, 2.080,
            2.189, 2.518, 2.831, 3.135, 3.527, 3.819],
        [22, 0.686, 0.858, 1.061, 1.321, 1.717, 2.074,
            2.183, 2.508, 2.819, 3.119, 3.505, 3.792],
        [23, 0.685, 0.858, 1.060, 1.319, 1.714, 2.069,
            2.177, 2.500, 2.807, 3.104, 3.485, 3.768],
        [24, 0.685, 0.857, 1.059, 1.318, 1.711, 2.064,
            2.172, 2.492, 2.797, 3.091, 3.467, 3.745],
        [25, 0.684, 0.856, 1.058, 1.316, 1.708, 2.060,
            2.167, 2.485, 2.787, 3.078, 3.450, 3.725],
        [26, 0.684, 0.856, 1.058, 1.315, 1.706, 2.056,
            2.162, 2.479, 2.779, 3.067, 3.435, 3.707],
        [27, 0.684, 0.855, 1.057, 1.314, 1.703, 2.052,
            2.15, 2.473, 2.771, 3.057, 3.421, 3.690],
        [28, 0.683, 0.855, 1.056, 1.313, 1.701, 2.048,
            2.154, 2.467, 2.763, 3.047, 3.408, 3.674],
        [29, 0.683, 0.854, 1.055, 1.311, 1.699, 2.045,
            2.150, 2.462, 2.756, 3.038, 3.396, 3.659],
        [30, 0.683, 0.854, 1.055, 1.310, 1.697, 2.042,
            2.147, 2.457, 2.750, 3.030, 3.385, 3.646],
        [40, 0.681, 0.851, 1.050, 1.303, 1.684, 2.021,
            2.123, 2.423, 2.704, 2.971, 3.307, 3.551],
        [50, 0.679, 0.849, 1.047, 1.295, 1.676, 2.009,
            2.109, 2.403, 2.678, 2.937, 3.261, 3.496],
        [60, 0.679, 0.848, 1.045, 1.296, 1.671, 2.000,
            2.099, 2.390, 2.660, 2.915, 3.232, 3.460],
        [80, 0.678, 0.846, 1.043, 1.292, 1.664, 1.990,
            2.088, 2.374, 2.639, 2.887, 3.195, 3.416],
        [100, 0.677, 0.845, 1.042, 1.290, 1.660, 1.984,
            2.081, 2.364, 2.626, 2.871, 3.174, 3.390],
        [1000, 0.675, 0.842, 1.037, 1.282, 1.646, 1.962, 2.056, 2.330, 2.581, 2.813, 3.098, 3.300]]
