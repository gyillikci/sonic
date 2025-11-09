# SONIC-Stellarium Integration Bridge
# Proof of Concept: Embedded Stellarium with Direct Framebuffer Access

cmake_minimum_required(VERSION 3.16)
project(SONICStellariumBridge VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Qt6 (required by Stellarium)
find_package(Qt6 COMPONENTS Core Gui OpenGL Widgets REQUIRED)

# Find Python for bindings
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Find pybind11 (for Python bindings)
find_package(pybind11 CONFIG)
if(NOT pybind11_FOUND)
    # Try to use pip-installed pybind11
    execute_process(
        COMMAND ${Python3_EXECUTABLE} -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    find_package(pybind11 CONFIG PATHS ${pybind11_DIR})
endif()

# Option 1: Link against Stellarium built in parent directory
# add_subdirectory(${CMAKE_SOURCE_DIR}/../stellarium stellarium_build)

# Option 2: Find system-installed Stellarium
# find_package(Stellarium REQUIRED)

# For now: Header-only proof of concept
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../stellarium/src/core
    ${Qt6Core_INCLUDE_DIRS}
    ${Qt6Gui_INCLUDE_DIRS}
    ${Qt6OpenGL_INCLUDE_DIRS}
)

# C++ Bridge Library
add_library(sonic_stel_bridge SHARED
    src/sonic_stel_bridge.cpp
    src/offscreen_renderer.cpp
)

target_link_libraries(sonic_stel_bridge
    PUBLIC
        Qt6::Core
        Qt6::Gui
        Qt6::OpenGL
)

# Python Module (pybind11)
if(pybind11_FOUND)
    pybind11_add_module(sonic_stellarium
        src/python_bindings.cpp
    )

    target_link_libraries(sonic_stellarium
        PRIVATE
            sonic_stel_bridge
            Qt6::Core
            Qt6::Gui
            Qt6::OpenGL
    )

    # Install to sonic_python package
    install(TARGETS sonic_stellarium
        LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/../sonic_python/sonic/
    )
else()
    message(WARNING "pybind11 not found. Python bindings will not be built.")
    message(STATUS "Install with: pip install pybind11")
endif()

# Installation
install(TARGETS sonic_stel_bridge
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/
    DESTINATION include/sonic_stellarium
)

# Print configuration
message(STATUS "===========================================")
message(STATUS "SONIC-Stellarium Bridge Configuration")
message(STATUS "===========================================")
message(STATUS "Qt6 Version: ${Qt6_VERSION}")
message(STATUS "Python3 Version: ${Python3_VERSION}")
message(STATUS "pybind11 Found: ${pybind11_FOUND}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "===========================================")
