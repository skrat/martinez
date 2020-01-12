from typing import (Optional,
                    Tuple)

from hypothesis import given

from martinez.boolean import (Operation,
                              SweepEvent)
from . import strategies


@given(strategies.operations_with_sweep_events_and_maybe_sweep_events)
def test_basic(
        operation_with_event_and_maybe_event: Tuple[Operation, SweepEvent,
                                                    Optional[SweepEvent]]
) -> None:
    operation, event, previous_event = operation_with_event_and_maybe_event

    result = operation.compute_fields(event, previous_event)

    assert result is None


@given(strategies.operations_with_sweep_events_and_maybe_sweep_events)
def test_properties(
        operation_with_event_and_maybe_event: Tuple[Operation, SweepEvent,
                                                    Optional[SweepEvent]]
) -> None:
    operation, event, previous_event = operation_with_event_and_maybe_event

    operation.compute_fields(event, previous_event)

    assert event.in_result is operation.in_result(event)
