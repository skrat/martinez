from operator import attrgetter
from typing import Generic

from reprit.base import generate_repr

from .hints import T
from .point import Point

points_key = attrgetter('x', 'y')


class Segment(Generic[T]):
    __slots__ = '_source', '_target'

    def __init__(self, source: Point[T], target: Point[T]):
        self._source = source
        self._target = target

    @property
    def source(self) -> Point[T]:
        return self._source

    @property
    def target(self) -> Point:
        return self._target

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Segment') -> bool:
        return (self._source == other._source and self._target == other._target
                if isinstance(other, Segment)
                else NotImplemented)

    @property
    def max(self) -> Point:
        return max(self._source, self._target,
                   key=points_key)

    @property
    def min(self) -> Point:
        return min(self._source, self._target,
                   key=points_key)

    @property
    def is_degenerate(self) -> bool:
        return self._source == self._target

    @property
    def is_vertical(self) -> bool:
        return self._source.x == self._target.x

    @property
    def reversed(self) -> 'Segment[T]':
        return Segment[T](self._target, self._source)
