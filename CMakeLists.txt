cmake_minimum_required(VERSION 3.0.0)

project(pcil VERSION 1.0.0)

add_library(pcil INTERFACE)

target_include_directories(pcil INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)