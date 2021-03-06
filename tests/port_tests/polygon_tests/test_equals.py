from typing import Tuple

from hypothesis import given

from tests.port_tests.hints import PortedPolygon
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.polygons)
def test_reflexivity(polygon: PortedPolygon) -> None:
    assert polygon == polygon


@given(strategies.polygons_pairs)
def test_symmetry(polygons_pair: Tuple[PortedPolygon, PortedPolygon]) -> None:
    first_polygon, second_polygon = polygons_pair

    assert equivalence(first_polygon == second_polygon,
                       second_polygon == first_polygon)


@given(strategies.polygons_triplets)
def test_transitivity(polygons_triplet: Tuple[PortedPolygon, PortedPolygon,
                                              PortedPolygon]) -> None:
    first_polygon, second_polygon, third_polygon = polygons_triplet

    assert implication(first_polygon == second_polygon
                       and second_polygon == third_polygon,
                       first_polygon == third_polygon)


@given(strategies.polygons_pairs)
def test_connection_with_inequality(polygons_pair: Tuple[PortedPolygon,
                                                         PortedPolygon]
                                    ) -> None:
    first_polygon, second_polygon = polygons_pair

    assert equivalence(not first_polygon == second_polygon,
                       first_polygon != second_polygon)
