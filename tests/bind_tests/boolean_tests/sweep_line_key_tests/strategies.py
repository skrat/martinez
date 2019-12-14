from _martinez import (Point,
                       SweepEvent,
                       SweepLineKey)
from hypothesis import strategies

from tests.strategies import (booleans,
                              bound_edges_types,
                              bound_polygons_types,
                              floats,
                              make_cyclic,
                              to_bound_sweep_events)

booleans = booleans
points = strategies.builds(Point, floats, floats)
polygons_types = bound_polygons_types
edges_types = bound_edges_types
leaf_sweep_events = strategies.builds(SweepEvent, booleans, points,
                                      strategies.none(),
                                      bound_polygons_types, bound_edges_types)
acyclic_sweep_events = strategies.recursive(leaf_sweep_events,
                                            to_bound_sweep_events)
sweep_events = strategies.recursive(acyclic_sweep_events, make_cyclic)
sweep_line_keys = strategies.builds(SweepLineKey, sweep_events)
nested_sweep_events = to_bound_sweep_events(sweep_events)
nested_sweep_line_keys = strategies.builds(SweepLineKey,
                                           nested_sweep_events)
non_sweep_line_keys = strategies.builds(object)