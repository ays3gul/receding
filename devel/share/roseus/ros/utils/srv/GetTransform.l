;; Auto-generated. Do not edit!


(when (boundp 'utils::GetTransform)
  (if (not (find-package "UTILS"))
    (make-package "UTILS"))
  (shadow 'GetTransform (find-package "UTILS")))
(unless (find-package "UTILS::GETTRANSFORM")
  (make-package "UTILS::GETTRANSFORM"))
(unless (find-package "UTILS::GETTRANSFORMREQUEST")
  (make-package "UTILS::GETTRANSFORMREQUEST"))
(unless (find-package "UTILS::GETTRANSFORMRESPONSE")
  (make-package "UTILS::GETTRANSFORMRESPONSE"))

(in-package "ROS")



(if (not (find-package "GEOMETRY_MSGS"))
  (ros::roseus-add-msgs "geometry_msgs"))


(defclass utils::GetTransformRequest
  :super ros::object
  :slots (_target_frame _source_frame ))

(defmethod utils::GetTransformRequest
  (:init
   (&key
    ((:target_frame __target_frame) "")
    ((:source_frame __source_frame) "")
    )
   (send-super :init)
   (setq _target_frame (string __target_frame))
   (setq _source_frame (string __source_frame))
   self)
  (:target_frame
   (&optional __target_frame)
   (if __target_frame (setq _target_frame __target_frame)) _target_frame)
  (:source_frame
   (&optional __source_frame)
   (if __source_frame (setq _source_frame __source_frame)) _source_frame)
  (:serialization-length
   ()
   (+
    ;; string _target_frame
    4 (length _target_frame)
    ;; string _source_frame
    4 (length _source_frame)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _target_frame
       (write-long (length _target_frame) s) (princ _target_frame s)
     ;; string _source_frame
       (write-long (length _source_frame) s) (princ _source_frame s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _target_frame
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _target_frame (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; string _source_frame
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _source_frame (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(defclass utils::GetTransformResponse
  :super ros::object
  :slots (_success _transform ))

(defmethod utils::GetTransformResponse
  (:init
   (&key
    ((:success __success) nil)
    ((:transform __transform) (instance geometry_msgs::TransformStamped :init))
    )
   (send-super :init)
   (setq _success __success)
   (setq _transform __transform)
   self)
  (:success
   (&optional (__success :null))
   (if (not (eq __success :null)) (setq _success __success)) _success)
  (:transform
   (&rest __transform)
   (if (keywordp (car __transform))
       (send* _transform __transform)
     (progn
       (if __transform (setq _transform (car __transform)))
       _transform)))
  (:serialization-length
   ()
   (+
    ;; bool _success
    1
    ;; geometry_msgs/TransformStamped _transform
    (send _transform :serialization-length)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _success
       (if _success (write-byte -1 s) (write-byte 0 s))
     ;; geometry_msgs/TransformStamped _transform
       (send _transform :serialize s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _success
     (setq _success (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;; geometry_msgs/TransformStamped _transform
     (send _transform :deserialize buf ptr-) (incf ptr- (send _transform :serialization-length))
   ;;
   self)
  )

(defclass utils::GetTransform
  :super ros::object
  :slots ())

(setf (get utils::GetTransform :md5sum-) "4c5026dc3bd8461725969574664a41aa")
(setf (get utils::GetTransform :datatype-) "utils/GetTransform")
(setf (get utils::GetTransform :request) utils::GetTransformRequest)
(setf (get utils::GetTransform :response) utils::GetTransformResponse)

(defmethod utils::GetTransformRequest
  (:response () (instance utils::GetTransformResponse :init)))

(setf (get utils::GetTransformRequest :md5sum-) "4c5026dc3bd8461725969574664a41aa")
(setf (get utils::GetTransformRequest :datatype-) "utils/GetTransformRequest")
(setf (get utils::GetTransformRequest :definition-)
      "string target_frame
string source_frame
---
bool success
geometry_msgs/TransformStamped transform

================================================================================
MSG: geometry_msgs/TransformStamped
# This expresses a transform from coordinate frame header.frame_id
# to the coordinate frame child_frame_id
#
# This message is mostly used by the 
# <a href=\"http://wiki.ros.org/tf\">tf</a> package. 
# See its documentation for more information.

Header header
string child_frame_id # the frame id of the child frame
Transform transform

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: geometry_msgs/Transform
# This represents the transform between two coordinate frames in free space.

Vector3 translation
Quaternion rotation

================================================================================
MSG: geometry_msgs/Vector3
# This represents a vector in free space. 
# It is only meant to represent a direction. Therefore, it does not
# make sense to apply a translation to it (e.g., when applying a 
# generic rigid transformation to a Vector3, tf2 will only apply the
# rotation). If you want your data to be translatable too, use the
# geometry_msgs/Point message instead.

float64 x
float64 y
float64 z
================================================================================
MSG: geometry_msgs/Quaternion
# This represents an orientation in free space in quaternion form.

float64 x
float64 y
float64 z
float64 w
")

(setf (get utils::GetTransformResponse :md5sum-) "4c5026dc3bd8461725969574664a41aa")
(setf (get utils::GetTransformResponse :datatype-) "utils/GetTransformResponse")
(setf (get utils::GetTransformResponse :definition-)
      "string target_frame
string source_frame
---
bool success
geometry_msgs/TransformStamped transform

================================================================================
MSG: geometry_msgs/TransformStamped
# This expresses a transform from coordinate frame header.frame_id
# to the coordinate frame child_frame_id
#
# This message is mostly used by the 
# <a href=\"http://wiki.ros.org/tf\">tf</a> package. 
# See its documentation for more information.

Header header
string child_frame_id # the frame id of the child frame
Transform transform

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: geometry_msgs/Transform
# This represents the transform between two coordinate frames in free space.

Vector3 translation
Quaternion rotation

================================================================================
MSG: geometry_msgs/Vector3
# This represents a vector in free space. 
# It is only meant to represent a direction. Therefore, it does not
# make sense to apply a translation to it (e.g., when applying a 
# generic rigid transformation to a Vector3, tf2 will only apply the
# rotation). If you want your data to be translatable too, use the
# geometry_msgs/Point message instead.

float64 x
float64 y
float64 z
================================================================================
MSG: geometry_msgs/Quaternion
# This represents an orientation in free space in quaternion form.

float64 x
float64 y
float64 z
float64 w
")



(provide :utils/GetTransform "4c5026dc3bd8461725969574664a41aa")


