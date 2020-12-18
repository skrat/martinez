from decimal import Decimal
from numbers import Real
from typing import (Callable,
                    TypeVar)

Scalar = TypeVar('Scalar', Real, Decimal)

T = TypeVar('T')

UserLerp = Callable[[T, T, Scalar], T]
