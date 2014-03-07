import unittest
try:
    from collections import OrderedDict
except ImportError:
    from utils import OrderedDict

import re

class NoSingleValueFoundException(Exception):
    pass

def read_namelist_file(filename):
    return Namelist(open(filename, 'r').read())

class Namelist():
    """
    Parses namelist files in Fortran 90 format, recognised groups are
    available through 'groups' attribute.
    """

    def __init__(self, input_str):
        self.groups = OrderedDict()

        group_re = re.compile(r'&([^&/]+)/', re.DOTALL)  # allow blocks to span multiple lines
        array_re = re.compile(r'(\w+)\((\d+)\)')
        string_re = re.compile(r"\'\s*\w[^']*\'")
        self.complex_re = re.compile(r'^\((\d+.?\d*),(\d+.?\d*)\)$')

        # remove all comments, since they may have forward-slashes
        # TODO: store position of comments so that they can be re-inserted when
        # we eventually save
        filtered_lines = []
        for line in input_str.split('\n'):
            if line.strip().startswith('!'):
                continue
            else:
                filtered_lines.append(line)

        group_blocks = re.findall(group_re, "\n".join(filtered_lines))

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

                # commas at the end of lines seem to be optional
                if line.endswith(','):
                    line = line[:-1]

                k, v = line.split('=')
                variable_name = k.strip()
                variable_value = v.strip()

                variable_name_groups = re.findall(array_re, k)

                variable_index = None
                if len(variable_name_groups) == 1:
                    variable_name, variable_index = variable_name_groups[0]
                    variable_index = int(variable_index)-1 # python indexing starts at 0

                try:
                    parsed_value = self._parse_value(variable_value)

                    if variable_index is None:
                        group[variable_name] = parsed_value
                    else:
                        if not variable_name in group:
                            group[variable_name] = {'_is_list': True}
                        group[variable_name][variable_index] = parsed_value

                except NoSingleValueFoundException as e:
                    # see we have several values inlined
                    if variable_value.count("'") in [0, 2]:
                        variable_arr_entries = variable_value.split()
                    else:
                        # we need to be more careful with lines with escaped
                        # strings, since they might contained spaces
                        matches = re.findall(string_re, variable_value)
                        variable_arr_entries = [s.strip() for s in matches]


                    for variable_index, inline_value in enumerate(variable_arr_entries):
                        parsed_value = self._parse_value(inline_value)

                        if variable_index is None:
                            group[variable_name] = parsed_value
                        else:
                            if not variable_name in group:
                                group[variable_name] = {'_is_list': True}
                            group[variable_name][variable_index] = parsed_value

            self.groups[group_name] = group

            self._check_lists()

    def _parse_value(self, variable_value):
        """
        Tries to parse a single value, raises an exception if no single value is matched
        """
        try:
            parsed_value = int(variable_value)
        except ValueError:
            try:
                parsed_value = float(variable_value)
            except ValueError:
                # check for complex number
                complex_values = re.findall(self.complex_re, variable_value)
                if len(complex_values) == 1:
                    a, b = complex_values[0]
                    parsed_value = complex(float(a),float(b))
                elif variable_value in ['.true.', 'T']:
                    # check for a boolean
                    parsed_value = True
                elif variable_value in ['.false.', 'F']:
                    parsed_value = False
                else:
                    # see if we have an escaped string
                    if variable_value.startswith("'") and variable_value.endswith("'") and variable_value.count("'") == 2:
                        parsed_value = variable_value[1:-1]
                    else:
                        raise NoSingleValueFoundException(variable_value)

        return parsed_value

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

    def test_comment_with_forwardslash(self):
        input_str = """
        ! Interesting comment at the start
        &CCFMSIM_SETUP
        CCFMrad=800.0
        ! And a comment some where in the middle/halfway !
        var2=40
        /
        &GROUP2
        R=500.0
        /
        """
        namelist = Namelist(input_str)

        expected_output = {'CCFMSIM_SETUP': { 'CCFMrad': 800., 'var2': 40 },
                           'GROUP2': { 'R': 500. }}

        self.assertEqual(namelist.groups, expected_output)

    def test_inline_array(self):
        input_str = """
        ! can have blank lines and comments in the namelist input file
        ! place these comments between NAMELISTs

        !
        ! not every compiler supports comments within the namelist
        !   in particular vastf90/g77 does not
        !
        ! some will skip NAMELISTs not directly referenced in read
        !&BOGUS rko=1 /
        !
        &TTDATA
        TTREAL =  1.,
        TTINTEGER = 2,
        TTCOMPLEX = (3.,4.),
        TTCHAR = 'namelist',
        TTBOOL = T/
        &AADATA
        AAREAL =  1.  1.  2.  3.,
        AAINTEGER = 2 2 3 4,
        AACOMPLEX = (3.,4.) (3.,4.) (5.,6.) (7.,7.),
        AACHAR = 'namelist' 'namelist' 'array' ' the lot',
        AABOOL = T T F F/
        &XXDATA
        XXREAL =  1.,
        XXINTEGER = 2,
        XXCOMPLEX = (3.,4.)/! can have blank lines and comments in the namelist input file
        """

        expected_output = {
            'TTDATA': {
                'TTREAL': 1.,
                'TTINTEGER': 2,
                'TTCOMPLEX': 3. + 4.j,
                'TTCHAR': 'namelist',
                'TTBOOL': True,
            },
            'AADATA': {
                'AAREAL': [1., 1., 2., 3.,],
                'AAINTEGER': [2, 2, 3, 4],
                'AACOMPLEX': [3.+4.j, 3.+4.j, 5.+6.j, 7.+7.j],
                'AACHAR': ['namelist', 'namelist', 'array', ' the lot'],
                'AABOOL': [True, True, False, False],
            },
            'XXDATA': {
                'XXREAL': 1.,
                'XXINTEGER': 2.,
                'XXCOMPLEX': 3.+4.j,
            },
        }

        namelist = Namelist(input_str)

        self.assertEqual(dict(namelist.groups), expected_output)

if __name__=='__main__':
    unittest.main()
