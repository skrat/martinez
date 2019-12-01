from _martinez import BoundingBox as Bound
from hypothesis import given

from martinez.bounding_box import BoundingBox as Ported
from tests.utils import are_bound_ported_bounding_boxes_equal
from . import strategies


@given(strategies.floats, strategies.floats,
       strategies.floats, strategies.floats)
def test_basic(x_min: float, y_min: float, x_max: float, y_max: float) -> None:
    bound, ported = (Bound(x_min, y_min, x_max, y_max),
                     Ported(x_min, y_min, x_max, y_max))

    assert are_bound_ported_bounding_boxes_equal(bound, ported)
