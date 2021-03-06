from functools import partial
from typing import List

from hypothesis import strategies

from tests.port_tests.factories import (scalars_to_ported_points,
                                        scalars_to_ported_points_lists)
from tests.port_tests.hints import (PortedContour,
                                    PortedPoint,
                                    PortedPolygon)
from tests.strategies import (booleans,
                              non_negative_integers,
                              non_negative_integers_lists,
                              scalars_strategies)
from tests.utils import (MAX_CONTOURS_COUNT,
                         Strategy,
                         identity,
                         to_builder,
                         to_pairs,
                         to_triplets)

booleans = booleans
non_negative_integers = non_negative_integers
non_negative_integers_lists = non_negative_integers_lists
points = scalars_strategies.flatmap(scalars_to_ported_points)


def to_contours(points_lists: Strategy[List[PortedPoint]],
                holes_lists: Strategy[List[int]] = non_negative_integers_lists,
                are_externals: Strategy[bool] = booleans) -> Strategy[
    PortedContour]:
    return strategies.builds(PortedContour, points_lists, holes_lists,
                             are_externals)


contours_lists_strategies = (scalars_strategies
                             .map(scalars_to_ported_points_lists)
                             .map(to_contours)
                             .map(partial(strategies.lists,
                                          max_size=MAX_CONTOURS_COUNT)))
contours_lists = contours_lists_strategies.flatmap(identity)
polygons_strategies = contours_lists_strategies.map(to_builder(PortedPolygon))
polygons = polygons_strategies.flatmap(identity)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
