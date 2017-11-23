import re

from namelist_python import Namelist


def test_single_value():
    input_str = """
    &CCFMSIM_SETUP
    CCFMrad=800.0
    /
    """
    namelist = Namelist(input_str)

    expected_output = {'CCFMSIM_SETUP': { 'CCFMrad': 800. }}

    assert namelist.groups == expected_output

def test_multigroup():
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

    assert namelist.groups == expected_output

def test_comment():
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

    assert namelist.groups == expected_output

def test_array():
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

    assert dict(namelist.groups) == expected_output

def test_boolean_sciformat():
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

    assert dict(namelist.groups) == expected_output

def test_comment_with_forwardslash():
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

    assert namelist.groups == expected_output

def test_inline_array():
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

    assert dict(namelist.groups) == expected_output


def test_inline_array_comma():
    input_str = """
                &foo
                bar = 7.2, 4.3, 3.14,
                /
                """
    expected_output = {'foo': {'bar':[7.2, 4.3, 3.14]}}
    namelist = Namelist(input_str)

    assert dict(namelist.groups) == expected_output


def test_dump_single_value():
    input_str = """&CCFMSIM_SETUP
  CCFMrad = 800.
/"""
    namelist = Namelist(input_str)

    assert namelist.dump() == input_str

def test_dump_multigroup():
    input_str = """&CCFMSIM_SETUP
  CCFMrad = 800.
/
&GROUP2
  R = 500.
/"""
    namelist = Namelist(input_str)

    assert namelist.dump() == input_str

def test_commongroup_names():
    re_common = re.compile(r'RELEASE')
    input_str = """&REL_CTRL
NSPEC=        1,
SPECNUM_REL= 100,   
/
&RELEASE
IDATE1=  20100101,
ITIME1=  000000,
IDATE2=  20100201,
ITIME2=  000000,
/
&RELEASE
IDATE1=  20100101,
ITIME1=  000000,
IDATE2=  20100201,
ITIME2=  000000,
/"""
    namelist = Namelist(input_str)
    common1 = re.findall(re_common, input_str)
    common2 = re.findall(re_common, namelist.dump(array_inline=False))

    assert common1 == common2

def test_dump_path():
    input_str = """&settings
  path = '/home/monkey/'
/"""
    namelist = Namelist(input_str)

    assert namelist.dump(array_inline=False) ==  input_str

def test_dump_array():
    input_str = """&CCFMSIM_SETUP
  var_trac_picture(1) = 'watcnew'
  var_trac_picture(2) = 'watpnew'
  var_trac_picture(3) = 'icecnew'
  var_trac_picture(4) = 'granew'
  des_trac_picture(1) = 'cloud_water'
  des_trac_picture(2) = 'rain'
  des_trac_picture(3) = 'cloud_ice'
  des_trac_picture(4) = 'graupel'
/"""
    namelist = Namelist(input_str)

    assert namelist.dump(array_inline=False) == input_str

def test_dump_inline_array():
    input_str = """&AADATA
  AACOMPLEX = (3.,4.) (3.,4.) (5.,6.) (7.,7.)
/"""

    namelist = Namelist(input_str)

    assert namelist.dump() == input_str
