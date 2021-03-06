#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET
import re
import json


class BlocklyTool(object):
    def __init__(self, path):
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()
        self.namespace = self.get_namespace()
        self._ops = {
            'EQ': '==',
            'NEQ': '!=',
            'LT': '<',
            'LTE': '<=',
            'GT': '>',
            'GTE': '>='
        }
        self._code_list = []
        self._hasEvent = False
        self._events = {}
        self._funcs = {}
        self._func_index = 0
        self._index = -1
        self._first_index = 0
        self._is_insert = False
        self.codes = ''
        self._succeed = True
        self._show_comment = False

    @property
    def index(self):
        self._index += 1
        return self._index

    @property
    def func_index(self):
        self._func_index += 1
        return self._func_index

    @property
    def first_index(self):
        self._first_index += 1
        self._index += 1
        return self._first_index

    def _append_to_file(self, data):
        if not self._is_insert:
            self._code_list.append(data)
        else:
            self._code_list.insert(self.first_index, data)

    def _insert_to_file(self, i, data):
        self._code_list.insert(i, data)

    def get_namespace(self):
        try:
            r = re.compile('({.+})')
            if r.search(self.root.tag) is not None:
                ns = r.search(self.root.tag).group(1)
            else:
                ns = ''
        except Exception as e:
            # print(e)
            ns = ''
        return ns

    def get_node(self, tag, root=None):
        if root is None:
            root = self.root
        return root.find(self.namespace + tag)

    def get_nodes(self, tag, root=None, descendant=False, **kwargs):
        if root is None:
            root = self.root
        nodes = []
        if descendant:
            func = root.iter
        else:
            func = root.findall
        for node in func(self.namespace + tag):
            flag = True
            for k, v in kwargs.items():
                if node.attrib[k] != v:
                    flag = False
            if flag:
                nodes.append(node)
        return nodes

    def _init_py3(self, arm=None, clean_err_warn=True, motion_enable=True, mode=0, state=0, error_exit=True):
        self._insert_to_file(self.index, '#!/usr/bin/env python3')
        self._insert_to_file(self.index, '# Software License Agreement (BSD License)\n#')
        self._insert_to_file(self.index, '# Copyright (c) 2019, UFACTORY, Inc.')
        self._insert_to_file(self.index, '# All rights reserved.\n#')
        self._insert_to_file(self.index, '# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>\n')
        self._insert_to_file(self.index, 'import sys')
        self._insert_to_file(self.index, 'import time')
        self._insert_to_file(self.index, 'import threading\n')
        self._insert_to_file(self.index, '# xArm-Python-SDK: https://github.com/xArm-Developer/xArm-Python-SDK')
        self._insert_to_file(self.index, '# git clone git@github.com:xArm-Developer/xArm-Python-SDK.git')
        self._insert_to_file(self.index, '# cd xArm-Python-SDK')
        self._insert_to_file(self.index, '# python setup.py install')
        self._insert_to_file(self.index, 'from xarm.wrapper import XArmAPI\n')
        if arm is None:
            self._insert_to_file(self.index, 'arm = XArmAPI(sys.argv[1])')
        elif isinstance(arm, str):
            self._insert_to_file(self.index, 'arm = XArmAPI(\'{}\')'.format(arm))
        self._insert_to_file(self.index, 'time.sleep(0.5)')
        if clean_err_warn:
            self._insert_to_file(self.index, 'arm.clean_warn()')
            self._insert_to_file(self.index, 'arm.clean_error()')
        if motion_enable:
            self._insert_to_file(self.index, 'arm.motion_enable(True)')
        self._insert_to_file(self.index, 'arm.set_mode({})'.format(mode))
        self._insert_to_file(self.index, 'arm.set_state({})'.format(state))
        self._insert_to_file(self.index, 'time.sleep(1)\n')
        self._insert_to_file(self.index, 'params = {\'speed\': 100, \'acc\': 2000, '
                                         '\'angle_speed\': 20, \'angle_acc\': 500, '
                                         '\'events\': {}, \'variables\': {}}')
        if error_exit:
            self._insert_to_file(self.index, '\n\n# Register error/warn changed callback')
            self._insert_to_file(self.index, 'def error_warn_change_callback(data):')
            self._insert_to_file(self.index, '    if data and data[\'error_code\'] != 0:')
            self._insert_to_file(self.index, '        arm.set_state(4)')
            self._insert_to_file(self.index, '        sys.exit(1)')
            self._insert_to_file(self.index, 'arm.register_error_warn_changed_callback(error_warn_change_callback)')
            # self._insert_to_file(self.index, '\n\n# Register state changed callback')
            # self._insert_to_file(self.index, 'def state_change_callback(data):')
            # self._insert_to_file(self.index, '    if data and data[\'state\'] == 4:')
            # self._insert_to_file(self.index, '        sys.exit(1)')
            # self._insert_to_file(self.index, 'arm.register_state_changed_callback(state_change_callback)\n')
        self._first_index = self._index

    def _finish_py3(self):
        if self._hasEvent:
            self._append_to_file('\n# Main loop')
            self._append_to_file('while arm.connected and arm.error_code == 0:')
            self._append_to_file('    time.sleep(1)')

    def to_python(self, path=None, arm=None, clean_err_warn=True, motion_enable=True, mode=0, state=0,
                  error_exit=True, show_comment=False):
        self._show_comment = show_comment
        self._succeed = True
        self._init_py3(arm, clean_err_warn, motion_enable, mode, state, error_exit)
        self.parse()
        self._finish_py3()
        self.codes = '\n'.join(self._code_list)
        if path is not None:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('{}\n'.format(self.codes))
        return self._succeed

    def parse(self, root=None, prefix=''):
        blocks = self.get_nodes('block', root=root)
        if blocks:
            for block in blocks:
                is_statement = root is None
                if root is not None:
                    if root.tag == self.namespace + 'statement':
                        is_statement = True
                while block is not None:
                    if not is_statement:
                        block = self.get_node('next', root=block)
                        if not block:
                            break
                        block = self.get_node('block', root=block)
                    else:
                        is_statement = False
                    if block.attrib.get('disabled', False):
                        continue
                    func = getattr(self, '_handle_{}'.format(block.attrib['type']), None)
                    if func:
                        func(block, prefix)
                    else:
                        self._succeed = False
                        print('block {} can\'t convert to python code'.format(block.attrib['type']))
        # block = self.get_node('block', root=root)
        # while block is not None:
        #     if not is_statement:
        #         block = self.get_node('next', root=block)
        #         if not block:
        #             break
        #         block = self.get_node('block', root=block)
        #     else:
        #         is_statement = False
        #     if block.attrib.get('disabled', False):
        #         continue
        #     func = getattr(self, '_handle_{}'.format(block.attrib['type']), None)
        #     if func:
        #         func(block, prefix)
        #     else:
        #         print('block {} can\'t convert to python code'.format(block.attrib['type']))

    def _handle_set_speed(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'speed\'] = {}'.format(prefix, value))

    def _handle_set_acceleration(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'acc\'] = {}'.format(prefix, value))

    def _handle_set_angle_speed(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'angle_speed\'] = {}'.format(prefix, value))

    def _handle_set_angle_acceleration(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'angle_acc\'] = {}'.format(prefix, value))

    def _handle_reset(self, block, prefix=''):
        self._append_to_file('{}if arm.error_code == 0:'.format(prefix))
        self._append_to_file('{}    arm.reset()'.format(prefix))

    def _handle_sleep(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}# set sleep time'.format(prefix))
        self._append_to_file('{}if arm.error_code == 0:'.format(prefix))
        self._append_to_file('{}    arm.set_sleep_time({})'.format(prefix, value))

    def _handle_move(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        orientation = fields[0].text
        wait = fields[1].text == 'TRUE'
        value = fields[2].text
        if orientation == 'forward':
            param = 'x'
        elif orientation == 'backward':
            param = 'x'
            value = '-{}'.format(value)
        elif orientation == 'left':
            param = 'y'
        elif orientation == 'right':
            param = 'y'
            value = '-{}'.format(value)
        elif orientation == 'up':
            param = 'z'
        elif orientation == 'down':
            param = 'z'
            value = '-{}'.format(value)
        else:
            return

        if self._show_comment:
            self._append_to_file('{}# relative move'.format(prefix))
        self._append_to_file('{}if arm.error_code == 0:'.format(prefix))
        self._append_to_file(
            '{}    arm.set_position({}={}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
            'relative=True, wait={})'.format(prefix, param, value, wait))

    def _handle_move_arc_to(self, block, prefix=''):
        value = self.get_node('value', root=block)
        p_block = self.get_node('block', root=value)
        fields = self.get_nodes('field', root=p_block)
        values = []
        for field in fields[:-2]:
            values.append(float(field.text))
        radius = float(fields[-2].text)
        wait = fields[-1].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# move{}line and {}'.format(
                prefix, ' arc ' if float(radius) >= 0 else ' ', 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0:'.format(prefix))
        self._append_to_file('{}    arm.set_position(*{}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
                             'radius={}, wait={})'.format(prefix, values, radius, wait))

    def _handle_move_circle(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        percent = self.get_nodes('field', root=values[2], descendant=True)[0].text
        wait = self.get_nodes('field', root=values[3], descendant=True)[0].text == 'TRUE'

        p1_block = self.get_node('block', root=values[0])
        fields = self.get_nodes('field', root=p1_block)
        pose1 = []
        for field in fields:
            pose1.append(float(field.text))

        p2_block = self.get_node('block', root=values[1])
        fields = self.get_nodes('field', root=p2_block)
        pose2 = []
        for field in fields:
            pose2.append(float(field.text))
        if self._show_comment:
            self._append_to_file('{}# move circle and {}'.format(
                prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0:'.format(prefix))
        self._append_to_file('{}    arm.move_circle({}, {}, {}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
                             'wait={})'.format(prefix, pose1, pose2, percent, wait))

    def _handle_move_7(self, block, prefix=''):
        value = self.get_node('value', root=block)
        p_block = self.get_node('block', root=value)
        fields = self.get_nodes('field', root=p_block)
        values = []
        for field in fields[:-1]:
            values.append(float(field.text))
        wait = fields[-1].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# move joint and {}'.format(prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0:'.format(prefix))
        self._append_to_file(
            '{}    arm.set_servo_angle(angle={}, speed=params[\'angle_speed\'], '
            'mvacc=params[\'angle_acc\'], wait={})'.format(prefix, values, wait))

    def _handle_motion_stop(self, block, prefix=''):
        if self._show_comment:
            self._append_to_file('{}# emergency stop'.format(prefix))
        self._append_to_file('{}arm.emergency_stop()'.format(prefix))

    def _handle_tool_message(self, block, prefix=''):
        fields = self.get_nodes('field', block)
        message = json.loads(json.dumps(fields[-1].text))
        self._append_to_file('{}print(\'{}\')'.format(prefix, message))

    def _handle_wait(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}time.sleep({})'.format(prefix, value))

    def _handle_gpio_set_digital(self, block, prefix=''):
        io = self.get_node('field', block).text
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        if self._show_comment:
            self._append_to_file('{}# set gpio-{} digital'.format(prefix, io))
        self._append_to_file('{}arm.set_gpio_digital({}, {})'.format(prefix, io, value))

    def _handle_set_collision_sensitivity(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}arm.set_collision_sensitivity({})'.format(prefix, value))

    def _handle_set_teach_sensitivity(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}arm.set_teach_sensitivity({})'.format(prefix, value))

    def _handle_set_tcp_load(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        weight = self.get_nodes('field', root=values[0], descendant=True)[0].text
        x = self.get_nodes('field', root=values[1], descendant=True)[0].text
        y = self.get_nodes('field', root=values[2], descendant=True)[0].text
        z = self.get_nodes('field', root=values[3], descendant=True)[0].text
        self._append_to_file('{}arm.set_tcp_load({}, [{}, {}, {}])'.format(prefix, weight, x, y, z))

    def _handle_set_gravity_direction(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        x = self.get_nodes('field', root=values[0], descendant=True)[0].text
        y = self.get_nodes('field', root=values[1], descendant=True)[0].text
        z = self.get_nodes('field', root=values[2], descendant=True)[0].text
        self._append_to_file('{}arm.set_gravity_direction([{}, {}, {}])'.format(prefix, x, y, z))

    def _handle_set_tcp_offset(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        x = self.get_nodes('field', root=values[0], descendant=True)[0].text
        y = self.get_nodes('field', root=values[1], descendant=True)[0].text
        z = self.get_nodes('field', root=values[2], descendant=True)[0].text
        roll = self.get_nodes('field', root=values[3], descendant=True)[0].text
        pitch = self.get_nodes('field', root=values[4], descendant=True)[0].text
        yaw = self.get_nodes('field', root=values[5], descendant=True)[0].text
        self._append_to_file('{}arm.set_tcp_offset([{}, {}, {}, {}, {}, {}])'.format(prefix, x, y, z, roll, pitch, yaw))

    def _handle_gripper_set(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        pos = self.get_nodes('field', root=values[0], descendant=True)[0].text
        speed = self.get_nodes('field', root=values[1], descendant=True)[0].text
        wait = self.get_nodes('field', root=values[2], descendant=True)[0].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# set gripper position and '.format(prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}arm.set_gripper_position({}, wait={}, speed={})'.format(prefix, pos, wait, speed))

    def _handle_event_gpio_digital(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        io = fields[0].text
        trigger = fields[1].text

        if 'gpio' not in self._events:
            num = 1
        else:
            num = self._events['gpio'] + 1
        name = '{}_io{}_is_{}_{}'.format(block.attrib['type'], io, trigger.lower(), num)
        self._append_to_file('\n\n{}# Define GPIO-{} is {} callback'.format(prefix, io, trigger))
        self._append_to_file('{}def {}():'.format(prefix, name))
        old_prefix = prefix
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))
        self._append_to_file('\n{}params[\'events\'][\'gpio\'].callbacks[\'IO{}\'][{}].append({})'.format(
            old_prefix, io, 1 if trigger == 'HIGH' else 0, name))
        self._append_to_file('{}if not params[\'events\'][\'gpio\'].alive:'.format(old_prefix))
        self._append_to_file('{}    params[\'events\'][\'gpio\'].start()'.format(old_prefix))

        if 'gpio' not in self._events:
            name2 = 'EventGPIOThread'.format(io, trigger.capitalize())
            self._insert_to_file(self.index, '\n\n# Define GPIO callback handle thread')
            self._insert_to_file(self.index, 'class {}(threading.Thread):'.format(name2))
            self._insert_to_file(self.index, '    def __init__(self, *args, **kwargs):'
                                             '\n        threading.Thread.__init__(self, *args, **kwargs)')
            self._insert_to_file(self.index, '        self.daemon = True')
            self._insert_to_file(self.index, '        self.alive = False')
            self._insert_to_file(self.index, '        self.digital = [-1, -1]')
            self._insert_to_file(self.index, '        self.callbacks = {\'IO1\': {0: [], 1: []}, '
                                             '\'IO2\': {0: [], 1: []}}')
            self._insert_to_file(self.index, '\n    def run(self):')
            self._insert_to_file(self.index, '        self.alive = True')
            self._insert_to_file(self.index, '        while arm.connected and arm.error_code == 0:')
            self._insert_to_file(self.index, '            _, digital = arm.get_gpio_digital()')
            self._insert_to_file(self.index, '            if _ == 0:')
            self._insert_to_file(self.index, '                if digital[0] != self.digital[0]:')
            self._insert_to_file(self.index, '                    for callback in self.callbacks[\'IO1\'][digital[0]]:')
            self._insert_to_file(self.index, '                        callback()')
            self._insert_to_file(self.index, '                if digital[1] != self.digital[1]:')
            self._insert_to_file(self.index, '                    for callback in self.callbacks[\'IO2\'][digital[1]]:')
            self._insert_to_file(self.index, '                        callback()')
            self._insert_to_file(self.index, '            if _ == 0:')
            self._insert_to_file(self.index, '                self.digital = digital')
            self._insert_to_file(self.index, '            time.sleep(0.1)')
            self._insert_to_file(self.index, '\nparams[\'events\'][\'gpio\'] = {}()'.format(name2))

        if 'gpio' not in self._events:
            self._events['gpio'] = 2
        else:
            self._events['gpio'] += 1

        self._hasEvent = True

    def _handle_procedures_defnoreturn(self, block, prefix=''):
        if not self._funcs:
            name = 'MyDef'
            self._insert_to_file(self.first_index, '\n\n# Define Mydef class')
            self._insert_to_file(self.first_index, 'class {}(object):'.format(name))
            self._insert_to_file(self.first_index,
                                 '    def __init__(self, *args, **kwargs):\n        pass')
        field = self.get_node('field', block).text
        if not field:
            field = '1'
        if field not in self._funcs:
            name = 'function_{}'.format(self.func_index)
        else:
            name = self._funcs[field]
        self._is_insert = True
        try:
            self._append_to_file('\n    @classmethod')
            self._append_to_file('    def {}(cls):'.format(name))
            prefix = '        '
            comment = self.get_node('comment', block).text
            self._append_to_file('{}"""'.format(prefix))
            self._append_to_file('{}{}'.format(prefix, comment))
            self._append_to_file('{}"""'.format(prefix))
            statement = self.get_node('statement', root=block)
            if statement:
                self.parse(statement, prefix)
            else:
                self._append_to_file('{}pass'.format(prefix))
            self._funcs[field] = name
        except:
            self._succeed = False
        self._is_insert = False

    def _handle_procedures_defreturn(self, block, prefix=''):
        self._handle_procedures_defnoreturn(block, prefix)
        value = self.get_node('value', root=block)
        expression = self.__get_condition_expression(value)
        self._is_insert = True
        prefix = '        '
        self._append_to_file('{}return {}'.format(prefix, expression))
        self._is_insert = False

    def _handle_procedures_callnoreturn(self, block, prefix=''):
        mutation = self.get_node('mutation', block).attrib['name']
        if not mutation:
            mutation = '1'
        if mutation in self._funcs:
            name = self._funcs[mutation]
        else:
            name = 'function_{}'.format(self.func_index)
        self._append_to_file('{}MyDef.{}()'.format(prefix, name))
        self._funcs[mutation] = name

    def _handle_procedures_ifreturn(self, block, prefix=''):
        self._is_insert = True
        values = self.get_nodes('value', block)
        expression = self.__get_condition_expression(values[0])
        self._append_to_file('{}if {}:'.format(prefix, expression))
        expression = self.__get_condition_expression(values[1])
        self._append_to_file('{}    return {}'.format(prefix, expression))
        self._is_insert = False

    def _handle_procedures_callreturn(self, block, prefix=''):
        self._handle_procedures_callnoreturn(block, prefix)

    def _handle_variables_set(self, block, prefix=''):
        field = self.get_node('field', block).text
        value = self.get_node('value', root=block)
        expression = self.__get_condition_expression(value)
        self._append_to_file('{}params[\'variables\'][\'{}\'] = {}'.format(prefix, field, expression))

    def _handle_math_change(self, block, prefix=''):
        field = self.get_node('field', block).text
        value = self.get_node('value', root=block)
        shadow = self.get_node('shadow', root=value)
        val = self.get_node('field', root=shadow).text
        self._append_to_file('{}params[\'variables\'][\'{}\'] = {}'.format(prefix, field, val))

    def _handle_controls_repeat_ext(self, block, prefix=''):
        value = self.get_node('value', root=block)
        times = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}for i in range({}):'.format(prefix, times))
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    # def handle_controls_for(self, block, prefix=''):
    #     print(block.attrib.get('disabled', False))

    def _handle_controls_whileUntil(self, block, prefix=''):
        field = self.get_node('field', root=block)
        if field.text == 'WHILE':
            value = self.get_node('value', root=block)
            expression = self.__get_condition_expression(value)
            self._append_to_file('{}while {}:'.format(prefix, expression))
        elif field.text == 'UNTIL':
            value = self.get_node('value', root=block)
            expression = self.__get_condition_expression(value)
            self._append_to_file('{}while not {}:'.format(prefix, expression))
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    def _handle_loop_run_forever(self, block, prefix=''):
        self._append_to_file('{}while True:'.format(prefix))
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    def _handle_loop_break(self, block, prefix=''):
        self._append_to_file('{}break'.format(prefix))

    def _handle_tool_comment(self, block, prefix=''):
        field = self.get_node('field', block)
        self._append_to_file('{}# {}'.format(prefix, field.text))
        statement = self.get_node('statement', block)
        if statement:
            self.parse(statement, prefix)

    def _handle_tool_remark(self, block, prefix=''):
        field = self.get_node('field', block)
        self._append_to_file('{}# {}'.format(prefix, field.text))

    def _handle_controls_if(self, block, prefix=''):
        value = self.get_node('value', root=block)
        expression = self.__get_condition_expression(value)
        self._append_to_file('{}if {}:'.format(prefix, expression))
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    def __get_condition_expression(self, value_block):
        block = self.get_node('block', value_block)
        if block.attrib['type'] == 'logic_boolean':
            return str(self.get_node('field', block).text == 'TRUE')
        elif block.attrib['type'] == 'logic_compare':
            op = self._ops.get(self.get_node('field', block).text)
            cond_a = 0
            cond_b = 0
            values = self.get_nodes('value', block)
            if len(values) > 0:
                cond_a = self.__get_condition_expression(values[0])
                if len(values) > 1:
                    cond_b = self.__get_condition_expression(values[1])
            return '{} {} {}'.format(cond_a, op, cond_b)
        elif block.attrib['type'] == 'logic_operation':
            op = self.get_node('field', block).text.lower()
            cond_a = False
            cond_b = False
            values = self.get_nodes('value', block)
            if len(values) > 0:
                cond_a = self.__get_condition_expression(values[0])
                if len(values) > 1:
                    cond_b = self.__get_condition_expression(values[1])
            return '{} {} {}'.format(cond_a, op, cond_b)
        elif block.attrib['type'] == 'logic_negate':
            value = self.get_node('value', root=block)
            return 'not ({})'.format(self.__get_condition_expression(value))
        elif block.attrib['type'] == 'gpio_get_digital':
            io = self.get_node('field', block).text
            return 'arm.gpio_get_digital({})[{}]'.format(io, 1)
        elif block.attrib['type'] == 'gpio_get_analog':
            io = self.get_node('field', block).text
            return 'arm.get_gpio_analog({})[{}]'.format(io, 1)
        elif block.attrib['type'] == 'math_number':
            val = self.get_node('field', block).text
            return val
        elif block.attrib['type'] == 'variables_get':
            field = self.get_node('field', block).text
            return 'params[\'variables\'].get(\'{}\', 0)'.format(field)
        elif block.attrib['type'] == 'procedures_callreturn':
            mutation = self.get_node('mutation', block).attrib['name']
            if not mutation:
                mutation = '1'
            if mutation in self._funcs:
                name = self._funcs[mutation]
            else:
                name = 'function_{}'.format(self.func_index)
            return 'MyDef.{}()'.format(name)


if __name__ == '__main__':
    blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm6\\app\\myapp\local_test_1\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm6\\app\\myapp\\app_template\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm6\\app\\myapp\\test_gpio\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm7\\app\\myapp\\pour_water\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm7\\app\\myapp\\233\\app.xml')
    import os
    target_path = os.path.join(os.path.expanduser('~'), '.UFACTORY', 'app', 'tmp')
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    target_file = os.path.join(target_path, 'blockly_app.py')
    blockly.to_python(target_file, arm='192.168.1.145')
