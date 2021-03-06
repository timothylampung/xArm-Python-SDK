#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
Move Circle,
    1. explicit setting is_radian=True, set the default unit is radian
"""

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

arm = XArmAPI('192.168.1.145', is_radian=True)
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

pose = [
    [300,  0,   100, -3.14, 0.3, 0.5],
    [300,  100, 100, -3.14, 0.4, 0.1],
    [400,  100, 100, -3.14, 0.1, 0.2],
    [400, -100, 100, -3.14, 0.2, 0.2],
    [300,  0,   300, -3.14, 0.5, 0.3]
]


ret = arm.move_gohome(wait=True)
print('move_gohome, ret: {}'.format(ret))

ret = arm.set_position(*pose[0], speed=50, mvacc=100, wait=True)
print('set_position, ret: {}'.format(ret))

ret = arm.move_circle(pose1=pose[1], pose2=pose[2], percent=50, speed=50, mvacc=100, wait=True)
print('move_circle, ret: {}'.format(ret))

ret = arm.move_circle(pose1=pose[3], pose2=pose[4], percent=100, speed=50, mvacc=100, wait=True)
print('move_circle, ret: {}'.format(ret))


arm.disconnect()
