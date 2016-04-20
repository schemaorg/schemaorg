#
# code to simplify supporting older python versions
#


import sys

from decimal import Decimal

if sys.version_info[:2] < (2, 7):

    # Pre-2.7 decimal and float did not compare correctly

    def numeric_greater(a, b):
        if isinstance(a, Decimal) and isinstance(b, float):
            return float(a) > b
        elif isinstance(a, float) and isinstance(b, Decimal):
            return a > float(b)
        else:
            return a > b

else:

    def numeric_greater(a, b):
        return a > b
