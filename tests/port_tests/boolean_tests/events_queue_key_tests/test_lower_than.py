from typing import (Any,
                    Tuple)

import pytest
from hypothesis import given

from martinez.boolean import EventsQueueKey
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.nested_events_queue_keys)
def test_irreflexivity(key: EventsQueueKey) -> None:
    assert not key < key


@given(strategies.nested_events_queue_keys_pairs)
def test_asymmetry(keys_pair: Tuple[EventsQueueKey, EventsQueueKey]) -> None:
    first_key, second_key = keys_pair

    assert implication(first_key < second_key, not second_key < first_key)


@given(strategies.nested_events_queue_keys_triplets)
def test_transitivity(keys_triplet: Tuple[EventsQueueKey, EventsQueueKey,
                                          EventsQueueKey]) -> None:
    first_key, second_key, third_key = keys_triplet

    assert implication(first_key < second_key < third_key,
                       first_key < third_key)


@given(strategies.nested_events_queue_keys_pairs)
def test_connection_with_greater_than(keys_pair: Tuple[EventsQueueKey,
                                                       EventsQueueKey]
                                      ) -> None:
    first_key, second_key = keys_pair

    assert equivalence(first_key < second_key, second_key > first_key)


@given(strategies.nested_events_queue_keys, strategies.non_events_queue_keys)
def test_non_key(key: EventsQueueKey, non_key: Any) -> None:
    with pytest.raises(TypeError):
        key < non_key
