#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
Example: Send gcode command
"""

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

arm = XArmAPI(port='192.168.1.113')
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

time.sleep(1)

arm.reset(wait=True)

print(arm.send_cmd_sync('G1 X300 Y0 Z150 F300'))  # set_position
print(arm.send_cmd_sync('G1 X300 Y-200 Z150 F300'))  # set_position
print(arm.send_cmd_sync('G1 X500 Y-200 Z150 F300'))  # set_position
print(arm.send_cmd_sync('G1 X500 Y200 Z150 F300'))  # set_position
print(arm.send_cmd_sync('G1 X300 Y0 Z150 F300'))  # set_position
print(arm.send_cmd_sync('G7 I0 J0 K0 L0 M0 N0 O0 F50'))  # set_servo_angle

arm.reset(wait=True)
arm.disconnect()
