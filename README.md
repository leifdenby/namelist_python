# Fortran namelist files in Python

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

## Features
 - Parses ints, float, booleans, escaped strings and complex numbers.
 - Parses arrays in index notation and inlined.
 - Can output in namelist format.

## Missing features
 - Currently can't handle variable definitions across multiple lines
 - Comments are not kept, and so won't exist in output.

## Contribute
Please send any namelist files that don't parse correctly or fix the code
yourself and send me a pull request :)

Thanks,
Leif
