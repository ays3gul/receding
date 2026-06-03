# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "utils: 0 messages, 1 services")

set(MSG_I_FLAGS "-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(utils_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" NAME_WE)
add_custom_target(_utils_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "utils" "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" "geometry_msgs/Transform:geometry_msgs/Vector3:geometry_msgs/Quaternion:geometry_msgs/TransformStamped:std_msgs/Header"
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages

### Generating Services
_generate_srv_cpp(utils
  "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Transform.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/TransformStamped.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/utils
)

### Generating Module File
_generate_module_cpp(utils
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/utils
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(utils_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(utils_generate_messages utils_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" NAME_WE)
add_dependencies(utils_generate_messages_cpp _utils_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(utils_gencpp)
add_dependencies(utils_gencpp utils_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS utils_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages

### Generating Services
_generate_srv_eus(utils
  "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Transform.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/TransformStamped.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/utils
)

### Generating Module File
_generate_module_eus(utils
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/utils
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(utils_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(utils_generate_messages utils_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" NAME_WE)
add_dependencies(utils_generate_messages_eus _utils_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(utils_geneus)
add_dependencies(utils_geneus utils_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS utils_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages

### Generating Services
_generate_srv_lisp(utils
  "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Transform.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/TransformStamped.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/utils
)

### Generating Module File
_generate_module_lisp(utils
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/utils
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(utils_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(utils_generate_messages utils_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" NAME_WE)
add_dependencies(utils_generate_messages_lisp _utils_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(utils_genlisp)
add_dependencies(utils_genlisp utils_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS utils_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages

### Generating Services
_generate_srv_nodejs(utils
  "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Transform.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/TransformStamped.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/utils
)

### Generating Module File
_generate_module_nodejs(utils
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/utils
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(utils_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(utils_generate_messages utils_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" NAME_WE)
add_dependencies(utils_generate_messages_nodejs _utils_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(utils_gennodejs)
add_dependencies(utils_gennodejs utils_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS utils_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages

### Generating Services
_generate_srv_py(utils
  "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Transform.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/TransformStamped.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils
)

### Generating Module File
_generate_module_py(utils
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(utils_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(utils_generate_messages utils_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/common/utils/srv/GetTransform.srv" NAME_WE)
add_dependencies(utils_generate_messages_py _utils_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(utils_genpy)
add_dependencies(utils_genpy utils_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS utils_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/utils)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/utils
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(utils_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/utils)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/utils
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(utils_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/utils)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/utils
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(utils_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/utils)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/utils
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(utils_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils
    DESTINATION ${genpy_INSTALL_DIR}
    # skip all init files
    PATTERN "__init__.py" EXCLUDE
    PATTERN "__init__.pyc" EXCLUDE
  )
  # install init files which are not in the root folder of the generated code
  string(REGEX REPLACE "([][+.*()^])" "\\\\\\1" ESCAPED_PATH "${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils")
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/utils
    DESTINATION ${genpy_INSTALL_DIR}
    FILES_MATCHING
    REGEX "${ESCAPED_PATH}/.+/__init__.pyc?$"
  )
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(utils_generate_messages_py geometry_msgs_generate_messages_py)
endif()
