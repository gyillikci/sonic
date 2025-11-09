/**
 * Python bindings for SONIC-Stellarium Bridge
 *
 * Exposes C++ StellariumBridge class to Python using pybind11
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "sonic_stel_bridge.h"

namespace py = pybind11;

/**
 * Wrap renderFrame() to return NumPy array instead of raw pointer
 *
 * This is the KEY for seamless Python integration!
 */
py::array_t<unsigned char> renderFrameNumPy(sonic::StellariumBridge& self)
{
    // Get raw pointer from C++
    const unsigned char* data = self.renderFrame();

    if (!data) {
        throw std::runtime_error("Frame rendering failed");
    }

    // Wrap in NumPy array WITHOUT copying (zero-copy!)
    // Shape: (height, width, 4) for RGBA
    return py::array_t<unsigned char>(
        {self.getHeight(), self.getWidth(), 4},  // shape
        {self.getWidth() * 4, 4, 1},             // strides (row-major)
        data,                                     // data pointer
        py::cast(&self)                           // parent object (keeps alive)
    );
}

/**
 * pybind11 module definition
 */
PYBIND11_MODULE(sonic_stellarium, m) {
    m.doc() = "SONIC-Stellarium Bridge: Direct framebuffer access to Stellarium rendering";

    // Main bridge class
    py::class_<sonic::StellariumBridge>(m, "StellariumRenderer",
        R"pbdoc(
        Embedded Stellarium renderer with direct framebuffer access

        This class provides seamless integration between Stellarium
        and SONIC crater detection by rendering directly to memory
        without file I/O.

        Example:
            >>> import sonic_stellarium
            >>> import numpy as np
            >>>
            >>> # Create renderer
            >>> renderer = sonic_stellarium.StellariumRenderer(2048, 2048)
            >>> renderer.initialize()
            >>>
            >>> # Set up view
            >>> renderer.focus_object("Moon")
            >>> renderer.set_fov(1.0)  # 1 degree FOV
            >>>
            >>> # Render to NumPy array (ZERO-COPY!)
            >>> frame = renderer.render_frame()  # numpy array (2048, 2048, 4)
            >>>
            >>> # Use with SONIC immediately
            >>> from sonic.navigation import detect_craters
            >>> craters = detect_craters(frame[:,:,:3])  # RGB channels
        )pbdoc")

        // Constructor
        .def(py::init<int, int>(),
             py::arg("width") = 2048,
             py::arg("height") = 2048,
             R"pbdoc(
             Create Stellarium renderer

             Args:
                 width (int): Framebuffer width in pixels (default: 2048)
                 height (int): Framebuffer height in pixels (default: 2048)
             )pbdoc")

        // Initialization
        .def("initialize", &sonic::StellariumBridge::initialize,
             py::arg("config_dir") = "",
             R"pbdoc(
             Initialize Stellarium core

             Args:
                 config_dir (str): Path to Stellarium config (optional)

             Returns:
                 bool: True if initialization succeeded
             )pbdoc")

        .def("is_ready", &sonic::StellariumBridge::isReady,
             "Check if renderer is initialized and ready")

        // View control
        .def("set_fov", &sonic::StellariumBridge::setFOV,
             py::arg("degrees"),
             "Set field of view in degrees")

        .def("get_fov", &sonic::StellariumBridge::getFOV,
             "Get current field of view in degrees")

        .def("focus_object", &sonic::StellariumBridge::focusObject,
             py::arg("object_name"),
             "Focus view on celestial object (e.g., 'Moon', 'Tycho')")

        .def("set_view_direction", &sonic::StellariumBridge::setViewDirection,
             py::arg("azimuth"),
             py::arg("altitude"),
             "Set viewing direction (azimuth, altitude in degrees)")

        // Time control
        .def("set_time", &sonic::StellariumBridge::setTime,
             py::arg("jd"),
             "Set simulation time (Julian Day)")

        .def("set_datetime", &sonic::StellariumBridge::setDateTime,
             py::arg("year"),
             py::arg("month"),
             py::arg("day"),
             py::arg("hour"),
             py::arg("minute"),
             py::arg("second"),
             "Set simulation time from date/time components")

        .def("get_time", &sonic::StellariumBridge::getTime,
             "Get current simulation time as Julian Day")

        // Location
        .def("set_location", &sonic::StellariumBridge::setLocation,
             py::arg("latitude"),
             py::arg("longitude"),
             py::arg("altitude") = 0.0,
             py::arg("planet") = "Earth",
             R"pbdoc(
             Set observer location

             Args:
                 latitude (float): Latitude in degrees (-90 to +90)
                 longitude (float): Longitude in degrees (-180 to +180)
                 altitude (float): Altitude in meters (default: 0)
                 planet (str): Planet name (default: "Earth")
             )pbdoc")

        // Rendering (THE KEY METHOD!)
        .def("render_frame", &renderFrameNumPy,
             R"pbdoc(
             Render current view to NumPy array

             This is the KEY method for seamless integration!
             Returns direct access to framebuffer memory without file I/O.

             Returns:
                 numpy.ndarray: Frame as (height, width, 4) RGBA array
                                Zero-copy access to GPU framebuffer!

             Example:
                 >>> frame = renderer.render_frame()
                 >>> print(frame.shape)  # (2048, 2048, 4)
                 >>> print(frame.dtype)  # uint8
                 >>> rgb = frame[:,:,:3]  # Extract RGB channels
             )pbdoc")

        .def("save_frame", &sonic::StellariumBridge::saveFrame,
             py::arg("filename"),
             "Save current frame to file (for debugging)")

        // Dimensions
        .def("get_width", &sonic::StellariumBridge::getWidth,
             "Get framebuffer width in pixels")

        .def("get_height", &sonic::StellariumBridge::getHeight,
             "Get framebuffer height in pixels")

        // SONIC-specific
        .def("get_moon_phase", &sonic::StellariumBridge::getMoonPhase,
             "Get current Moon phase (0.0 to 1.0)")

        .def("is_moon_visible", &sonic::StellariumBridge::isMoonVisible,
             "Check if Moon is currently visible");

    // Module version
    m.attr("__version__") = "1.0.0";
}
