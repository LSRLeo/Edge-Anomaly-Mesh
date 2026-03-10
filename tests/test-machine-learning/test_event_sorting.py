"""
Tests for insert_event_in_order sorting logic.

Covers:
  - Out-of-order sequence insertion
  - Duplicate sequence handling
  - Edge cases (missing seq, None seq, non-int seq)
  - Buffer shape and order correctness
  - Robustness to extra fields
"""

import sys
from pathlib import Path
import pytest

ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from redis_insteam import RedisSubscriber  # noqa: E402

class _TestableRedisSubscriber(RedisSubscriber):
    def __init__(self):
        # Skip Redis connection setup for unit tests
        self.node_states = {}
        self.seen_seqs = {}

@pytest.fixture
def subscriber():
    return _TestableRedisSubscriber()

def test_out_of_order_insertion(subscriber):
    """Ensures buffer is sorted by seq after out-of-order insertion."""
    buffer = []
    events = [
        {"seq": 3, "data": "a"},
        {"seq": 1, "data": "b"},
        {"seq": 2, "data": "c"},
        {"seq": 5, "data": "d"},
        {"seq": 4, "data": "e"},
    ]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    sorted_seqs = [e["seq"] for e in buffer]
    assert sorted_seqs == [1, 2, 3, 4, 5]

def test_duplicate_seq(subscriber):
    """Duplicate seq numbers are ignored."""
    buffer = []
    events = [
        {"seq": 1, "data": "a"},
        {"seq": 2, "data": "b"},
        {"seq": 2, "data": "c"},  # duplicate seq
    ]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    sorted_seqs = [e["seq"] for e in buffer]
    assert sorted_seqs == [1, 2]

def test_missing_seq(subscriber):
    """Events without seq are discarded."""
    buffer = []
    events = [
        {"seq": 1, "data": "b"},
        {"data": "a"},  # no seq
    ]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    assert len(buffer) == 1
    assert buffer[0].get("seq") == 1

def test_none_seq(subscriber):
    """Events with seq=None are discarded."""
    buffer = []
    events = [
        {"seq": 1, "data": "a"},
        {"seq": None, "data": "b"},
        {"seq": 2, "data": "c"},
    ]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    assert [e.get("seq") for e in buffer] == [1, 2]

def test_non_int_seq(subscriber):
    """Events with non-integer seq are discarded."""
    buffer = []
    events = [
        {"seq": 1, "data": "a"},
        {"seq": "not_int", "data": "b"},
        {"seq": 2, "data": "c"},
    ]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    assert [e.get("seq") for e in buffer] == [1, 2]

def test_extra_fields(subscriber):
    """Events with extra fields are sorted correctly and extra fields are ignored."""
    buffer = []
    events = [
        {"seq": 2, "data": "a", "extra": 123},
        {"seq": 1, "data": "b", "foo": "bar"},
    ]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    assert [e.get("seq") for e in buffer] == [1, 2]
    assert buffer[0]["foo"] == "bar"
    assert buffer[1]["extra"] == 123

def test_large_buffer(subscriber):
    """Handles large number of events efficiently."""
    buffer = []
    events = [{"seq": i, "data": f"event{i}"} for i in range(1000, 0, -1)]
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    assert [e.get("seq") for e in buffer][:3] == [1, 2, 3]
    assert len(buffer) == 1000