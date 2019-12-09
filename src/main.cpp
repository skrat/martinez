#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <iomanip>
#include <limits>
#include <numeric>
#include <sstream>

#include "bbox_2.h"
#include "booleanop.h"
#include "point_2.h"
#include "polygon.h"
#include "segment_2.h"
#include "utilities.h"

namespace py = pybind11;

#define MODULE_NAME _martinez
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#define BOUNDING_BOX_NAME "BoundingBox"
#define CONTOUR_NAME "Contour"
#define EDGE_TYPE_NAME "EdgeType"
#define POINT_NAME "Point"
#define POLYGON_NAME "Polygon"
#define POLYGON_TYPE_NAME "PolygonType"
#define SEGMENT_NAME "Segment"
#define SWEEP_EVENT_NAME "SweepEvent"

static std::string join(const std::vector<std::string>& elements,
                        const std::string& separator) {
  if (elements.empty()) return std::string();
  return std::accumulate(
      std::next(std::begin(elements)), std::end(elements), elements[0],
      [&separator](const std::string& result, const std::string& value) {
        return result + separator + value;
      });
};

static std::ostringstream make_stream() {
  std::ostringstream stream;
  stream.precision(std::numeric_limits<double>::digits10 + 2);
  return stream;
}

static std::string point_repr(const cbop::Point_2& self) {
  auto stream = make_stream();
  stream << C_STR(MODULE_NAME) "." POINT_NAME "(" << self.x() << ", "
         << self.y() << ")";
  return stream.str();
}

static std::string polygon_type_repr(const cbop::PolygonType& type) {
  auto stream = make_stream();
  stream << C_STR(MODULE_NAME) "." POLYGON_TYPE_NAME "(" << type << ")";
  return stream.str();
}

static std::string edge_type_repr(const cbop::EdgeType& type) {
  auto stream = make_stream();
  stream << C_STR(MODULE_NAME) "." EDGE_TYPE_NAME "(" << type << ")";
  return stream.str();
}

static std::string bool_repr(bool value) { return py::str(py::bool_(value)); }

static std::string sweep_event_repr(const cbop::SweepEvent& self) {
  auto left_repr = bool_repr(self.left);
  std::string other_event_repr = self.otherEvent == nullptr
                                     ? std::string(py::str(py::none()))
                                     : sweep_event_repr(*self.otherEvent);
  auto stream = make_stream();
  stream << C_STR(MODULE_NAME) "." SWEEP_EVENT_NAME "(" << left_repr << ", "
         << point_repr(self.point) << ", " << other_event_repr << ", "
         << polygon_type_repr(self.pol) << ", " << edge_type_repr(self.type)
         << ")";
  return stream.str();
}

static std::vector<cbop::Point_2> contour_to_points(const cbop::Contour& self) {
  return std::vector<cbop::Point_2>(self.begin(), self.end());
}

static std::vector<unsigned int> contour_to_holes(const cbop::Contour& self) {
  std::vector<unsigned int> result;
  for (unsigned int index = 0; index < self.nholes(); ++index)
    result.push_back(self.hole(index));
  return result;
}

static std::vector<cbop::Contour> polygon_to_contours(
    const cbop::Polygon& self) {
  return std::vector<cbop::Contour>(self.begin(), self.end());
}

static bool are_contours_equal(const cbop::Contour& self,
                               const cbop::Contour& other) {
  return contour_to_points(self) == contour_to_points(other) &&
         contour_to_holes(self) == contour_to_holes(other) &&
         self.external() == other.external();
}

static bool are_sweep_events_equal(const cbop::SweepEvent& self,
                                   const cbop::SweepEvent& other) {
  if (self.otherEvent != nullptr) {
    if (other.otherEvent == nullptr)
      return false;
    else if (!are_sweep_events_equal(*self.otherEvent, *other.otherEvent))
      return false;
  } else if (other.otherEvent != nullptr)
    return false;
  return self.left == other.left && self.point == other.point &&
         self.pol == other.pol && self.type == other.type;
}

static std::string contour_repr(const cbop::Contour& self) {
  std::vector<std::string> points_reprs;
  for (auto& point : contour_to_points(self))
    points_reprs.push_back(point_repr(point));
  std::vector<std::string> holes_reprs;
  for (auto hole : contour_to_holes(self))
    holes_reprs.push_back(std::to_string(hole));
  auto stream = make_stream();
  stream << C_STR(MODULE_NAME) "." CONTOUR_NAME "("
         << "[" << join(points_reprs, ", ") << "]"
         << ", "
         << "[" << join(holes_reprs, ", ") << "]"
         << ", " << bool_repr(self.external()) << ")";
  return stream.str();
}

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(
        Python binding of polygon clipping algorithm by F. Martínez et al.
    )pbdoc";

  m.def(
      "find_intersections",
      [](const cbop::Segment_2& first_segment,
         const cbop::Segment_2& second_segment) -> py::tuple {
        cbop::Point_2 first_intersection_point, second_intersection_point;
        int intersections_count = cbop::findIntersection(
            first_segment, second_segment, first_intersection_point,
            second_intersection_point);
        switch (intersections_count) {
          case 0:
            return py::make_tuple(intersections_count, py::none(), py::none());
          case 1:
            return py::make_tuple(intersections_count, first_intersection_point,
                                  py::none());
          default:
            return py::make_tuple(intersections_count, first_intersection_point,
                                  second_intersection_point);
        }
      });
  m.def("sign", &cbop::sign, pybind11::arg("first_point"),
        pybind11::arg("second_point"), pybind11::arg("third_point"));

  py::enum_<cbop::EdgeType>(m, EDGE_TYPE_NAME)
      .value("NORMAL", cbop::EdgeType::NORMAL)
      .value("NON_CONTRIBUTING", cbop::EdgeType::NON_CONTRIBUTING)
      .value("SAME_TRANSITION", cbop::EdgeType::SAME_TRANSITION)
      .value("DIFFERENT_TRANSITION", cbop::EdgeType::DIFFERENT_TRANSITION)
      .export_values();

  py::enum_<cbop::BooleanOpType>(m, "OperationType")
      .value("INTERSECTION", cbop::BooleanOpType::INTERSECTION)
      .value("UNION", cbop::BooleanOpType::UNION)
      .value("DIFFERENCE", cbop::BooleanOpType::DIFFERENCE)
      .value("XOR", cbop::BooleanOpType::XOR)
      .export_values();

  py::enum_<cbop::PolygonType>(m, POLYGON_TYPE_NAME)
      .value("SUBJECT", cbop::PolygonType::SUBJECT)
      .value("CLIPPING", cbop::PolygonType::CLIPPING)
      .export_values();

  py::class_<cbop::Bbox_2>(m, BOUNDING_BOX_NAME)
      .def(py::init<double, double, double, double>(), py::arg("x_min") = 0.,
           py::arg("y_min") = 0., py::arg("x_max") = 0., py::arg("y_max") = 0.)
      .def(py::pickle(
          [](const cbop::Bbox_2& self) {  // __getstate__
            return py::make_tuple(self.xmin(), self.ymin(), self.xmax(),
                                  self.ymax());
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 4) throw std::runtime_error("Invalid state!");
            return cbop::Bbox_2(
                tuple[0].cast<double>(), tuple[1].cast<double>(),
                tuple[2].cast<double>(), tuple[3].cast<double>());
          }))
      .def("__repr__",
           [](const cbop::Bbox_2& self) -> std::string {
             auto stream = make_stream();
             stream << C_STR(MODULE_NAME) "." BOUNDING_BOX_NAME "("
                    << self.xmin() << ", " << self.ymin() << ", " << self.xmax()
                    << ", " << self.ymax() << ")";
             return stream.str();
           })
      .def("__eq__",
           [](const cbop::Bbox_2& self, const cbop::Bbox_2& other) {
             return self.xmin() == other.xmin() &&
                    self.ymin() == other.ymin() &&
                    self.xmax() == other.xmax() && self.ymax() == other.ymax();
           })
      .def_property_readonly("x_min", &cbop::Bbox_2::xmin)
      .def_property_readonly("y_min", &cbop::Bbox_2::ymin)
      .def_property_readonly("x_max", &cbop::Bbox_2::xmax)
      .def_property_readonly("y_max", &cbop::Bbox_2::ymax)
      .def("__add__", &cbop::Bbox_2::operator+);

  py::class_<cbop::Contour>(m, CONTOUR_NAME)
      .def(py::init<const std::vector<cbop::Point_2>&,
                    const std::vector<unsigned int>&, bool>(),
           py::arg("points"), py::arg("holes"), py::arg("is_external"))
      .def(py::pickle(
          [](const cbop::Contour& self) {  // __getstate__
            return py::make_tuple(contour_to_points(self),
                                  contour_to_holes(self), self.external());
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 3) throw std::runtime_error("Invalid state!");
            return cbop::Contour(tuple[0].cast<std::vector<cbop::Point_2>>(),
                                 tuple[1].cast<std::vector<unsigned int>>(),
                                 tuple[2].cast<bool>());
          }))
      .def("__repr__", contour_repr)
      .def("__eq__", are_contours_equal)
      .def(
          "__iter__",
          [](const cbop::Contour& self) {
            return py::make_iterator(self.begin(), self.end());
          },
          py::keep_alive<0, 1>())
      .def_property_readonly("points", contour_to_points)
      .def_property_readonly("holes", contour_to_holes)
      .def_property("is_external", &cbop::Contour::external,
                    &cbop::Contour::setExternal)
      .def_property_readonly("is_clockwise", &cbop::Contour::clockwise)
      .def_property_readonly("is_counterclockwise",
                             &cbop::Contour::counterclockwise)
      .def_property_readonly("bounding_box", &cbop::Contour::bbox)
      .def("add", &cbop::Contour::add, py::arg("add"))
      .def("add_hole", &cbop::Contour::addHole, py::arg("hole"))
      .def("clear_holes", &cbop::Contour::clearHoles)
      .def("reverse", &cbop::Contour::changeOrientation)
      .def("set_clockwise", &cbop::Contour::setClockwise)
      .def("set_counterclockwise", &cbop::Contour::setCounterClockwise);

  py::class_<cbop::Point_2>(m, POINT_NAME)
      .def(py::init<double, double>(), py::arg("x") = 0., py::arg("y") = 0.)
      .def(py::pickle(
          [](const cbop::Point_2& self) {  // __getstate__
            return py::make_tuple(self.x(), self.y());
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return cbop::Point_2(tuple[0].cast<double>(),
                                 tuple[1].cast<double>());
          }))
      .def("__repr__", point_repr)
      .def("__eq__", [](const cbop::Point_2& self,
                        const cbop::Point_2& other) { return self == other; })
      .def("distance_to", &cbop::Point_2::dist, py::arg("other"))
      .def_property_readonly("x", &cbop::Point_2::x)
      .def_property_readonly("y", &cbop::Point_2::y)
      .def_property_readonly("bounding_box", &cbop::Point_2::bbox);

  py::class_<cbop::Polygon>(m, POLYGON_NAME)
      .def(py::init<const std::vector<cbop::Contour>&>(), py::arg("contours"))
      .def(py::pickle(
          [](const cbop::Polygon& self) {  // __getstate__
            return polygon_to_contours(self);
          },
          [](const std::vector<cbop::Contour>& contours) {  // __setstate__
            return cbop::Polygon(contours);
          }))
      .def("__repr__",
           [](const cbop::Polygon& self) -> std::string {
             auto stream = make_stream();
             std::vector<std::string> contours_reprs;
             for (auto& contour : self)
               contours_reprs.push_back(contour_repr(contour));
             stream << C_STR(MODULE_NAME) "." POLYGON_NAME "("
                    << "[" << join(contours_reprs, ", ") << "]"
                    << ")";
             return stream.str();
           })
      .def("__eq__",
           [](const cbop::Polygon& self, const cbop::Polygon& other) {
             if (self.ncontours() != other.ncontours()) return false;
             for (size_t index = 0; index < self.ncontours(); ++index)
               if (!are_contours_equal(self[index], other[index])) return false;
             return true;
           })
      .def(
          "__iter__",
          [](const cbop::Polygon& self) {
            return py::make_iterator(self.begin(), self.end());
          },
          py::keep_alive<0, 1>())
      .def_property_readonly("bounding_box", &cbop::Polygon::bbox)
      .def_property_readonly("contours", polygon_to_contours)
      .def("join", &cbop::Polygon::join);

  py::class_<cbop::Segment_2>(m, SEGMENT_NAME)
      .def(py::init<cbop::Point_2, cbop::Point_2>(),
           py::arg("source") = cbop::Point_2(),
           py::arg("target") = cbop::Point_2())
      .def(py::pickle(
          [](const cbop::Segment_2& self) {  // __getstate__
            return py::make_tuple(self.source(), self.target());
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return cbop::Segment_2(tuple[0].cast<cbop::Point_2>(),
                                   tuple[1].cast<cbop::Point_2>());
          }))
      .def("__repr__",
           [](const cbop::Segment_2& self) -> std::string {
             auto stream = make_stream();
             stream << C_STR(MODULE_NAME) "." SEGMENT_NAME "("
                    << point_repr(self.source()) << ", "
                    << point_repr(self.target()) << ")";
             return stream.str();
           })
      .def("__eq__",
           [](const cbop::Segment_2& self, const cbop::Segment_2& other) {
             return self.source() == other.source() &&
                    self.target() == other.target();
           })
      .def_property("source", &cbop::Segment_2::source,
                    &cbop::Segment_2::setSource)
      .def_property("target", &cbop::Segment_2::target,
                    &cbop::Segment_2::setTarget)
      .def_property_readonly("max", &cbop::Segment_2::max)
      .def_property_readonly("min", &cbop::Segment_2::min)
      .def_property_readonly("is_degenerate", &cbop::Segment_2::degenerate)
      .def_property_readonly("is_vertical", &cbop::Segment_2::is_vertical)
      .def_property_readonly("reversed", &cbop::Segment_2::changeOrientation);

  py::class_<cbop::SweepEvent>(m, SWEEP_EVENT_NAME)
      .def(py::init<bool, const cbop::Point_2&, cbop::SweepEvent*,
                    cbop::PolygonType, cbop::EdgeType>(),
           py::arg("left"), py::arg("point"), py::arg("other_event"),
           py::arg("polygon_type"), py::arg("edge_type"))
      .def("__eq__", are_sweep_events_equal)
      .def("__repr__", sweep_event_repr)
      .def_readwrite("left", &cbop::SweepEvent::left)
      .def_readwrite("point", &cbop::SweepEvent::point)
      .def_readwrite("other_event", &cbop::SweepEvent::otherEvent)
      .def_readwrite("polygon_type", &cbop::SweepEvent::pol)
      .def_readwrite("edge_type", &cbop::SweepEvent::type);

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
