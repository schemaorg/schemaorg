"""
Function/methods to help supporting 2.5-2.7
"""

# Collection ABCs

try:
    from collections import Mapping, MutableMapping  # was added in 2.6

except:
    from UserDict import DictMixin

    class MutableMapping(DictMixin):
        def keys(self):
            return list(self)

    Mapping = MutableMapping


# OrderedDict

try:
    from collections import OrderedDict  # was added in 2.7
except ImportError:
    from ordereddict import OrderedDict  # extra module

import sys

if sys.version_info[:2] < (2, 7):

    from decimal import Decimal
    # Pre-2.7 decimal and float did not compare correctly

    def _numericKey(n):
        if isinstance(n, Decimal):
            return float(n)
        else:
            return n

    def num_max(*args, **kwargs):
        kwargs["key"] = _numericKey
        return max(*args, **kwargs)

    def num_min(*args, **kwargs):
        kwargs["key"] = _numericKey
        return min(*args, **kwargs)

else:

    num_max = max
    num_min = min
