# Fortran namelist files in Python

[![Build
Status](https://travis-ci.org/leifdenby/namelist_python.svg?branch=master)](https://travis-ci.org/leifdenby/namelist_python)

Install with `pip`

    pip install namelist_python

Read in a namelist file:
```
from namelist_python import read_namelist_file
namelist = read_namelist_file('SIM_CONFIG.nl')
```

`namelist` is an instance of `namelist_python.Namelist` and all groups are
stored in the attribute `groups` with each variable in a nested dictionary
structure (using `OrderedDict` so that the order will be remembered).

Write a `Namelist` object back to a file:
```
with open('NEW_FILE.nl', 'w') as f:
	f.write(namelist.dump())
```

`dump` takes an optional argument `array_inline` a boolean which sets whether
arrays should be inline or given in index notation.

If you use ipython there is usefull attribute called `data` which allows you to
do tab completion on the group and variable names, and do assignment:

```
In [7]: namelist.data.ATHAM_SETUP.dt
namelist.data.ATHAM_SETUP.dt
namelist.data.ATHAM_SETUP.dtmax
namelist.data.ATHAM_SETUP.dtmin
In [7]: namelist.data.ATHAM_SETUP.dt
Out[7]: 3.0

In [8]: namelist.data.ATHAM_SETUP.dt = 4.0

In [9]: namelist.data.ATHAM_SETUP.dt
Out[9]: 4.0
```

## Features
 - Parses ints, floats, booleans, escaped strings and complex numbers.
 - Parses arrays in index notation and inlined.
 - Can output in namelist format.
 - Tab-completion and variable assignment in interactive console

## Missing features
 - Currently can't handle complex variable definitions across multiple lines
 - Comments are not kept, and so won't exist in output.

## Contribute
Please send any namelist files that don't parse correctly or fix the code
yourself and send me a pull request :)

Thanks,
Leif
