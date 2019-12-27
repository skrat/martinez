from typing import (List,
                    Tuple)

from hypothesis import given

from martinez.boolean import (Operation,
                              SweepEvent)
from . import strategies


@given(strategies.operations_with_events_lists)
def test_basic(operation_with_events: Tuple[Operation, List[SweepEvent]]
               ) -> None:
    operation, events = operation_with_events

    result = operation.connect_edges(events)

    assert result is None
