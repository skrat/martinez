from functools import partial
from typing import (Any,
                    List,
                    Optional,
                    Tuple,
                    TypeVar)

from _martinez import (Contour as BoundContour,
                       EdgeType as BoundEdgeType,
                       Point as BoundPoint,
                       Polygon as BoundPolygon,
                       PolygonType as BoundPolygonType,
                       Segment as BoundSegment,
                       SweepEvent as BoundSweepEvent)
from hypothesis import strategies

from martinez.boolean import (EdgeType as PortedEdgeType,
                              PolygonType as PortedPolygonType,
                              SweepEvent as PortedSweepEvent)
from martinez.contour import Contour as PortedContour
from martinez.hints import Scalar
from martinez.point import Point as PortedPoint
from martinez.polygon import Polygon as PortedPolygon
from martinez.segment import Segment as PortedSegment
from tests.utils import (BoundPortedPointsPair,
                         BoundPortedSweepEventsPair,
                         PortedPointsPair,
                         PortedPointsTriplet,
                         Strategy,
                         to_sweep_event_children_count)
from .literals import (booleans,
                       bound_edges_types,
                       bound_polygons_types,
                       floats,
                       ported_edges_types,
                       ported_polygons_types)


def scalars_to_ported_points(scalars: Strategy[Scalar]
                             ) -> Strategy[PortedPoint]:
    return strategies.builds(PortedPoint, scalars, scalars)


def scalars_to_ported_points_pairs(scalars: Strategy[Scalar]
                                   ) -> Strategy[PortedPointsPair]:
    points_strategy = strategies.builds(PortedPoint, scalars, scalars)
    return strategies.tuples(points_strategy, points_strategy)


def scalars_to_ported_points_triplets(scalars: Strategy[Scalar]
                                      ) -> Strategy[PortedPointsTriplet]:
    points_strategy = strategies.builds(PortedPoint, scalars, scalars)
    return strategies.tuples(points_strategy, points_strategy, points_strategy)


def scalars_to_ported_points_lists(scalars: Strategy[Scalar],
                                   *,
                                   min_size: int = 0,
                                   max_size: Optional[int] = None
                                   ) -> Strategy[List[PortedPoint]]:
    return strategies.lists(scalars_to_ported_points(scalars),
                            min_size=min_size,
                            max_size=max_size)


def scalars_to_ported_segments(scalars: Strategy[Scalar]
                               ) -> Strategy[PortedSegment]:
    points_strategy = scalars_to_ported_points(scalars)
    return strategies.builds(PortedSegment, points_strategy, points_strategy)


def to_bound_with_ported_points_pair(x: float, y: float
                                     ) -> BoundPortedPointsPair:
    return BoundPoint(x, y), PortedPoint(x, y)


def to_bound_with_ported_contours_pair(
        bound_with_ported_points_lists_pair: Tuple[List[BoundPoint],
                                                   List[PortedPoint]],
        holes: List[int],
        is_external: bool) -> Tuple[BoundContour, PortedContour]:
    bound_points, ported_points = bound_with_ported_points_lists_pair
    return (BoundContour(bound_points, holes, is_external),
            PortedContour(ported_points, holes, is_external))


def to_bound_with_ported_segments_pair(
        bound_with_ported_sources_pair: BoundPortedPointsPair,
        bound_with_ported_targets_pair: BoundPortedPointsPair
) -> Tuple[BoundSegment, PortedSegment]:
    bound_source, ported_source = bound_with_ported_sources_pair
    bound_target, ported_target = bound_with_ported_targets_pair

    return (BoundSegment(bound_source, bound_target),
            PortedSegment(ported_source, ported_target))


AnySweepEvent = TypeVar('AnySweepEvent', PortedSweepEvent, BoundSweepEvent)


def make_cyclic(sweep_events: Strategy[AnySweepEvent]
                ) -> Strategy[AnySweepEvent]:
    return strategies.builds(to_cyclic_sweep_event,
                             sweep_events,
                             strategies.integers(),
                             strategies.integers())


def to_cyclic_sweep_event(sweep_event: AnySweepEvent,
                          source_index_seed: int,
                          destination_index_seed: int) -> AnySweepEvent:
    children_count = to_sweep_event_children_count(sweep_event) or 1
    loop_sweep_event(sweep_event,
                     source_index_seed % children_count,
                     destination_index_seed % children_count)
    return sweep_event


def loop_sweep_event(sweep_event: AnySweepEvent,
                     source_index: int, destination_index: int) -> None:
    source = destination = sweep_event
    for _ in range(source_index - 1):
        source = source.other_event
    for _ in range(destination_index):
        destination = destination.other_event
    source.other_event = destination


def to_bound_with_ported_sweep_events(
        are_left: Strategy[bool],
        points_pairs: BoundPortedPointsPair,
        other_events: Strategy[Tuple[Optional[BoundSweepEvent],
                                     Optional[PortedSweepEvent]]],
        polygons_types_pairs: Strategy[Tuple[BoundPolygonType,
                                             PortedPolygonType]],
        edges_types_pairs: Strategy[Tuple[BoundEdgeType, PortedEdgeType]],
        in_outs: Strategy[bool],
        other_in_outs: Strategy[bool]) -> Strategy[BoundPortedSweepEventsPair]:
    def to_sweep_events(
            is_left: bool,
            points_pair: BoundPortedPointsPair,
            other_events_pair: Tuple[Optional[BoundSweepEvent],
                                     Optional[PortedSweepEvent]],
            polygons_types_pair: Tuple[BoundPolygonType, PortedPolygonType],
            edges_types_pair: Tuple[BoundEdgeType, PortedEdgeType],
            in_out: bool,
            other_in_out: bool) -> BoundPortedSweepEventsPair:
        bound_point, ported_point = points_pair
        (bound_other_event,
         ported_other_event) = other_events_pair
        (bound_polygon_type,
         ported_polygon_type) = polygons_types_pair
        bound_edge_type, ported_edge_type = edges_types_pair
        bound = BoundSweepEvent(is_left, bound_point, bound_other_event,
                                bound_polygon_type, bound_edge_type,
                                in_out, other_in_out)
        ported = PortedSweepEvent(is_left, ported_point, ported_other_event,
                                  ported_polygon_type, ported_edge_type,
                                  in_out, other_in_out)
        return bound, ported

    return strategies.builds(to_sweep_events,
                             are_left, points_pairs, other_events,
                             polygons_types_pairs, edges_types_pairs,
                             in_outs, other_in_outs)


def make_cyclic_bound_with_ported_sweep_events(
        sweep_events_pairs: Strategy[BoundPortedSweepEventsPair]
) -> Strategy[BoundPortedSweepEventsPair]:
    def to_cyclic_sweep_events(sweep_events_pair: BoundPortedSweepEventsPair,
                               source_index_seed: int,
                               destination_index_seed: int
                               ) -> BoundPortedSweepEventsPair:
        bound, ported = sweep_events_pair
        return (to_cyclic_sweep_event(bound, source_index_seed,
                                      destination_index_seed),
                to_cyclic_sweep_event(ported, source_index_seed,
                                      destination_index_seed))

    return strategies.builds(to_cyclic_sweep_events,
                             sweep_events_pairs,
                             strategies.integers(),
                             strategies.integers())


def scalars_to_plain_ported_sweep_events(
        scalars: Strategy[Scalar],
        other_events: Strategy[Optional[PortedSweepEvent]],
        *,
        polygons_types: Strategy[PortedPolygonType] = ported_polygons_types
) -> Strategy[PortedSweepEvent]:
    return strategies.builds(PortedSweepEvent, booleans,
                             scalars_to_ported_points(scalars), other_events,
                             polygons_types, ported_edges_types)


def scalars_to_acyclic_ported_sweep_events(
        scalars: Strategy[Scalar],
        other_events: Strategy[Optional[PortedSweepEvent]] = strategies.none(),
        **kwargs: Any
) -> Strategy[PortedSweepEvent]:
    events_factory = partial(scalars_to_plain_ported_sweep_events, scalars,
                             **kwargs)
    return strategies.recursive(events_factory(other_events), events_factory)


def scalars_to_nested_ported_sweep_events(scalars: Strategy[Scalar],
                                          **kwargs: Any
                                          ) -> Strategy[PortedSweepEvent]:
    acyclic_events = scalars_to_acyclic_nested_ported_sweep_events(scalars,
                                                                   **kwargs)
    return strategies.recursive(acyclic_events, make_cyclic)


def scalars_to_ported_sweep_events(scalars: Strategy[Scalar], **kwargs: Any
                                   ) -> Strategy[PortedSweepEvent]:
    acyclic_events = scalars_to_acyclic_ported_sweep_events(scalars, **kwargs)
    return strategies.recursive(acyclic_events, make_cyclic)


def scalars_to_acyclic_nested_ported_sweep_events(
        scalars: Strategy[Scalar],
        **kwargs: Any) -> Strategy[PortedSweepEvent]:
    events_factory = partial(scalars_to_acyclic_ported_sweep_events,
                             scalars, **kwargs)
    return events_factory(events_factory(strategies.none()))


def to_plain_bound_sweep_events(
        other_events: Strategy[Optional[BoundSweepEvent]],
        *,
        polygons_types: Strategy[BoundPolygonType] = bound_polygons_types
) -> Strategy[BoundSweepEvent]:
    return strategies.builds(BoundSweepEvent, booleans,
                             strategies.builds(BoundPoint, floats, floats),
                             other_events, polygons_types, bound_edges_types,
                             booleans, booleans)


def to_bound_sweep_events(**kwargs: Any) -> Strategy[PortedSweepEvent]:
    acyclic_events = to_acyclic_bound_sweep_events(strategies.none(), **kwargs)
    return strategies.recursive(acyclic_events, make_cyclic)


def to_nested_bound_sweep_events(**kwargs: Any) -> Strategy[PortedSweepEvent]:
    acyclic_events = to_acyclic_nested_bound_sweep_events(**kwargs)
    return strategies.recursive(acyclic_events, make_cyclic)


def to_acyclic_nested_bound_sweep_events(**kwargs: Any
                                         ) -> Strategy[BoundSweepEvent]:
    events_factory = partial(to_acyclic_bound_sweep_events, **kwargs)
    return events_factory(events_factory(strategies.none()))


def to_acyclic_bound_sweep_events(
        other_events: Strategy[Optional[BoundSweepEvent]],
        **kwargs: Any) -> Strategy[BoundSweepEvent]:
    events_factory = partial(to_plain_bound_sweep_events, **kwargs)
    return strategies.recursive(events_factory(other_events), events_factory)


def to_bound_with_ported_polygons_pair(
        bound_with_ported_contours_lists_pair: Tuple[List[BoundContour],
                                                     List[PortedContour]]
) -> Tuple[BoundPolygon, PortedPolygon]:
    bound_contours, ported_contours = bound_with_ported_contours_lists_pair
    return BoundPolygon(bound_contours), PortedPolygon(ported_contours)
