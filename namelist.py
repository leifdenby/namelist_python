import unittest
try:
    from collections import OrderedDict
except ImportError:
    from utils import OrderedDict

import re

class Namelist():
    def __init__(self, input_str):
        self.groups = OrderedDict()

        group_re = re.compile(r'&([^&/]+)/', re.DOTALL)
        array_re = re.compile(r'(\w+)\((\d+)\)')

        group_blocks = re.findall(group_re, input_str)

        for group_block in group_blocks:
            block_lines = group_block.split('\n')
            group_name = block_lines.pop(0).strip()

            group = {}

            for line in block_lines:
                line = line.strip()
                if line == "":
                    continue
                if line.startswith('!'):
                    continue

                k, v = line.split('=')
                variable_name = k.strip()
                variable_value = v.strip()

                variable_name_groups = re.findall(array_re, k)

                variable_index = None
                if len(variable_name_groups) == 1:
                    variable_name, variable_index = variable_name_groups[0]
                    variable_index = int(variable_index)-1 # python indexing starts at 0

                try:
                    parsed_value = int(variable_value)
                except ValueError:
                    try:
                        parsed_value = float(variable_value)
                    except ValueError:
                        parsed_value = variable_value.replace("'","")
                        if parsed_value.lower() == '.true.':
                            parsed_value = True
                        elif parsed_value.lower() == '.false.':
                            parsed_value = False

                if variable_index is None:
                    group[variable_name] = parsed_value
                else:
                    if not variable_name in group:
                        group[variable_name] = {'_is_list': True}
                    group[variable_name][variable_index] = parsed_value

            self.groups[group_name] = group

            self._check_lists()

    def _check_lists(self):
        for group in self.groups.values():
            for variable_name, variable_values in group.items():
                if isinstance(variable_values, dict):
                    if '_is_list' in variable_values and variable_values['_is_list']:
                        variable_data = variable_values
                        del(variable_data['_is_list'])

                        num_entries = len(variable_data.keys())
                        variable_list = [None]*num_entries

                        for i, value in variable_data.items():
                            if i >= num_entries:
                                raise Exception("The variable '%s' has an array index assignment that is inconsistent with the number of list values" % variable)
                            else:
                                variable_list[i] = value

                        group[variable_name] = variable_list


class MultilineTests(unittest.TestCase):
    def test_single_value(self):
        input_str = """
        &CCFMSIM_SETUP
        CCFMrad=800.0
        /
        """
        namelist = Namelist(input_str)

        expected_output = {'CCFMSIM_SETUP': { 'CCFMrad': 800. }}

        self.assertEqual(namelist.groups, expected_output)

    def test_multigroup(self):
        input_str = """
        &CCFMSIM_SETUP
        CCFMrad=800.0
        /
        &GROUP2
        R=500.0
        /
        """
        namelist = Namelist(input_str)

        expected_output = {'CCFMSIM_SETUP': { 'CCFMrad': 800. },
                           'GROUP2': { 'R': 500. }}

        self.assertEqual(namelist.groups, expected_output)

    def test_comment(self):
        input_str = """
        ! Interesting comment at the start
        &CCFMSIM_SETUP
        CCFMrad=800.0
        ! And a comment some where in the middle
        /
        &GROUP2
        R=500.0
        /
        """
        namelist = Namelist(input_str)

        expected_output = {'CCFMSIM_SETUP': { 'CCFMrad': 800. },
                           'GROUP2': { 'R': 500. }}

        self.assertEqual(namelist.groups, expected_output)

    def test_array(self):
        input_str = """
        &CCFMSIM_SETUP
        ntrac_picture=4
        var_trac_picture(1)='watcnew'
        des_trac_picture(1)='cloud_water'
        var_trac_picture(2)='watpnew'
        des_trac_picture(2)='rain'
        var_trac_picture(3)='icecnew'
        des_trac_picture(3)='cloud_ice'
        var_trac_picture(4)='granew'
        des_trac_picture(4)='graupel'
        /
        """
        namelist = Namelist(input_str)

        expected_output = {
            'CCFMSIM_SETUP': {
                'ntrac_picture': 4,
                'var_trac_picture': [
                    'watcnew',
                    'watpnew',
                    'icecnew',
                    'granew',
                ],
                'des_trac_picture': [
                    'cloud_water',
                    'rain',
                    'cloud_ice',
                    'graupel',
                ],
            },
        }

        self.assertEqual(dict(namelist.groups), expected_output)

    def test_boolean_sciformat(self):
        input_str = """
        &ATHAM_SETUP

        nz      =300
        zstart  =0.
        ztotal  =15000.
        dzzoom  =50.
        kcenter =20
        nztrans =0
        nztrans_boundary =6

        cpumax  =9.e6

        no_uwind=.false.
        no_vwind=.true.
        /
        """
        namelist = Namelist(input_str)

        expected_output = {
            'ATHAM_SETUP': {
                'nz': 300,
                'zstart': 0.,
                'ztotal': 15000.,
                'dzzoom': 50.,
                'kcenter': 20,
                'nztrans': 0,
                'nztrans_boundary': 6,
                'cpumax': 9.e6,
                'no_uwind': False,
                'no_vwind': True,
            }
        }

        self.assertEqual(dict(namelist.groups), expected_output)


if __name__=='__main__':
    unittest.main()
