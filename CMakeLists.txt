cmake_minimum_required(VERSION 3.0)
project(pyelsed)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_STANDARD 14)

# Import OpenCV
message(STATUS "OpenCV_LOCATION: " $ENV{OpenCV_LOCATION})
find_package(OpenCV REQUIRED PATHS $ENV{OpenCV_LOCATION} NO_DEFAULT_PATH)
message(STATUS "OpenCV_FOUND: " ${OpenCV_FOUND})
message(STATUS "OpenCV_INCLUDE_DIRS: " ${OpenCV_INCLUDE_DIRS})
# message(STATUS "OpenCV_DIR: " ${OpenCV_DIR})
message(STATUS "OpenCV_LIBS: " ${OpenCV_LIBS})
include_directories(${OpenCV_INCLUDE_DIRS})

# Create the ELSED library
set(LIB_SOURCES "src/EdgeDrawer.cpp" "src/ELSED.cpp" "src/FullSegmentInfo.cpp")
include_directories(src)
add_library(elsed ${LIB_SOURCES})
target_link_libraries(elsed ${OpenCV_LIBS})

# ELSED executable demo
add_executable(elsed_main src/main.cpp)
target_link_libraries(elsed_main elsed ${OpenCV_LIBS})

set(PYTHON_LIBRARY $ENV{PYTHON_LIBRARY})
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

# Create the python library using pybind11
add_subdirectory(pybind11)
pybind11_add_module(pyelsed src/PYAPI.cpp)
target_link_libraries(pyelsed PRIVATE elsed ${PYTHON_LIBRARIES} ${OpenCV_LIBS})
target_compile_definitions(pyelsed PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
