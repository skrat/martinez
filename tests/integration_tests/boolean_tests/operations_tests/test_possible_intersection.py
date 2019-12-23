from typing import Tuple

from _martinez import (Operation as Bound,
                       SweepEvent as BoundSweepEvent)
from hypothesis import given

from martinez.boolean import (Operation as Ported,
                              SweepEvent as PortedSweepEvent)
from . import strategies


@given(strategies.bound_with_ported_operations_pairs,
       strategies.bound_with_ported_nested_sweep_events_pairs_pairs)
def test_basic(bound_with_ported_operations_pair: Tuple[Bound, Ported],
               bound_with_ported_events_pair_pair:
               Tuple[Tuple[BoundSweepEvent, BoundSweepEvent],
                     Tuple[PortedSweepEvent, PortedSweepEvent]],
               ) -> None:
    bound, ported = bound_with_ported_operations_pair
    bound_events_pair, ported_events_pair = bound_with_ported_events_pair_pair
    first_bound_event, second_bound_event = bound_events_pair
    first_ported_event, second_ported_event = ported_events_pair

    bound_result = bound.possible_intersection(first_bound_event,
                                               second_bound_event)
    ported_result = ported.possible_intersection(first_ported_event,
                                                 second_ported_event)

    assert bound_result == ported_result