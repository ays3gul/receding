# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "abb_control: 0 messages, 1 services")

set(MSG_I_FLAGS "-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(abb_control_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" NAME_WE)
add_custom_target(_abb_control_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "abb_control" "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" "geometry_msgs/Quaternion:geometry_msgs/Point:geometry_msgs/Pose"
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages

### Generating Services
_generate_srv_cpp(abb_control
  "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/abb_control
)

### Generating Module File
_generate_module_cpp(abb_control
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/abb_control
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(abb_control_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(abb_control_generate_messages abb_control_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" NAME_WE)
add_dependencies(abb_control_generate_messages_cpp _abb_control_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(abb_control_gencpp)
add_dependencies(abb_control_gencpp abb_control_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS abb_control_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages

### Generating Services
_generate_srv_eus(abb_control
  "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/abb_control
)

### Generating Module File
_generate_module_eus(abb_control
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/abb_control
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(abb_control_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(abb_control_generate_messages abb_control_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" NAME_WE)
add_dependencies(abb_control_generate_messages_eus _abb_control_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(abb_control_geneus)
add_dependencies(abb_control_geneus abb_control_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS abb_control_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages

### Generating Services
_generate_srv_lisp(abb_control
  "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/abb_control
)

### Generating Module File
_generate_module_lisp(abb_control
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/abb_control
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(abb_control_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(abb_control_generate_messages abb_control_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" NAME_WE)
add_dependencies(abb_control_generate_messages_lisp _abb_control_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(abb_control_genlisp)
add_dependencies(abb_control_genlisp abb_control_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS abb_control_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages

### Generating Services
_generate_srv_nodejs(abb_control
  "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/abb_control
)

### Generating Module File
_generate_module_nodejs(abb_control
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/abb_control
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(abb_control_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(abb_control_generate_messages abb_control_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" NAME_WE)
add_dependencies(abb_control_generate_messages_nodejs _abb_control_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(abb_control_gennodejs)
add_dependencies(abb_control_gennodejs abb_control_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS abb_control_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages

### Generating Services
_generate_srv_py(abb_control
  "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control
)

### Generating Module File
_generate_module_py(abb_control
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(abb_control_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(abb_control_generate_messages abb_control_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/ayse/Desktop/RecedingHorizon/src/robot/abb_control/srv/ArmGoal.srv" NAME_WE)
add_dependencies(abb_control_generate_messages_py _abb_control_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(abb_control_genpy)
add_dependencies(abb_control_genpy abb_control_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS abb_control_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/abb_control)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/abb_control
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(abb_control_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/abb_control)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/abb_control
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(abb_control_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/abb_control)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/abb_control
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(abb_control_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/abb_control)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/abb_control
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(abb_control_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control
    DESTINATION ${genpy_INSTALL_DIR}
    # skip all init files
    PATTERN "__init__.py" EXCLUDE
    PATTERN "__init__.pyc" EXCLUDE
  )
  # install init files which are not in the root folder of the generated code
  string(REGEX REPLACE "([][+.*()^])" "\\\\\\1" ESCAPED_PATH "${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control")
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/abb_control
    DESTINATION ${genpy_INSTALL_DIR}
    FILES_MATCHING
    REGEX "${ESCAPED_PATH}/.+/__init__.pyc?$"
  )
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(abb_control_generate_messages_py geometry_msgs_generate_messages_py)
endif()
