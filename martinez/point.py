import math
from typing import Optional, Generic, TypeVar

from reprit.base import generate_repr

from .bounding_box import BoundingBox
from .hints import (Scalar, T)


T = T

class Point(Generic[T]):
    __slots__ = '_x', '_y', '_user'

    def __init__(self, x: Scalar, y: Scalar, user: Optional[T]=None) -> None:
        self._x = x
        self._y = y
        self._user = user

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Point') -> bool:
        return (self._x == other._x and self._y == other._y
                if isinstance(other, Point)
                else NotImplemented)

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self._x, self._y, self._x, self._y)

    @property
    def x(self) -> Scalar:
        return self._x

    @property
    def y(self) -> Scalar:
        return self._y

    @property
    def user(self):
        return self._user

    def distance_to(self, other: 'Point') -> Scalar:
        return math.sqrt((self._x - other._x) ** 2 + (self._y - other._y) ** 2)
