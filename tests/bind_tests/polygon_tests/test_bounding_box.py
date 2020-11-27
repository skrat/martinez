from hypothesis import given

from tests.bind_tests.hints import (BoundPolygon, BoundingBox)
from tests.utils import (are_bounding_boxes_empty, implication)
from . import strategies


@given(strategies.polygons)
def test_basic(polygon: BoundPolygon) -> None:
    assert isinstance(polygon.bounding_box, BoundingBox)


@given(strategies.polygons)
def test_empty(polygon: BoundPolygon) -> None:
    assert implication(not polygon.contours,
                       are_bounding_boxes_empty(polygon.bounding_box))
