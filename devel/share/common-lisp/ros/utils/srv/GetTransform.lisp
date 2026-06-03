; Auto-generated. Do not edit!


(cl:in-package utils-srv)


;//! \htmlinclude GetTransform-request.msg.html

(cl:defclass <GetTransform-request> (roslisp-msg-protocol:ros-message)
  ((target_frame
    :reader target_frame
    :initarg :target_frame
    :type cl:string
    :initform "")
   (source_frame
    :reader source_frame
    :initarg :source_frame
    :type cl:string
    :initform ""))
)

(cl:defclass GetTransform-request (<GetTransform-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <GetTransform-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'GetTransform-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name utils-srv:<GetTransform-request> is deprecated: use utils-srv:GetTransform-request instead.")))

(cl:ensure-generic-function 'target_frame-val :lambda-list '(m))
(cl:defmethod target_frame-val ((m <GetTransform-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader utils-srv:target_frame-val is deprecated.  Use utils-srv:target_frame instead.")
  (target_frame m))

(cl:ensure-generic-function 'source_frame-val :lambda-list '(m))
(cl:defmethod source_frame-val ((m <GetTransform-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader utils-srv:source_frame-val is deprecated.  Use utils-srv:source_frame instead.")
  (source_frame m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <GetTransform-request>) ostream)
  "Serializes a message object of type '<GetTransform-request>"
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'target_frame))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'target_frame))
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'source_frame))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'source_frame))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <GetTransform-request>) istream)
  "Deserializes a message object of type '<GetTransform-request>"
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'target_frame) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'target_frame) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'source_frame) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'source_frame) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<GetTransform-request>)))
  "Returns string type for a service object of type '<GetTransform-request>"
  "utils/GetTransformRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'GetTransform-request)))
  "Returns string type for a service object of type 'GetTransform-request"
  "utils/GetTransformRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<GetTransform-request>)))
  "Returns md5sum for a message object of type '<GetTransform-request>"
  "4c5026dc3bd8461725969574664a41aa")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'GetTransform-request)))
  "Returns md5sum for a message object of type 'GetTransform-request"
  "4c5026dc3bd8461725969574664a41aa")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<GetTransform-request>)))
  "Returns full string definition for message of type '<GetTransform-request>"
  (cl:format cl:nil "string target_frame~%string source_frame~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'GetTransform-request)))
  "Returns full string definition for message of type 'GetTransform-request"
  (cl:format cl:nil "string target_frame~%string source_frame~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <GetTransform-request>))
  (cl:+ 0
     4 (cl:length (cl:slot-value msg 'target_frame))
     4 (cl:length (cl:slot-value msg 'source_frame))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <GetTransform-request>))
  "Converts a ROS message object to a list"
  (cl:list 'GetTransform-request
    (cl:cons ':target_frame (target_frame msg))
    (cl:cons ':source_frame (source_frame msg))
))
;//! \htmlinclude GetTransform-response.msg.html

(cl:defclass <GetTransform-response> (roslisp-msg-protocol:ros-message)
  ((success
    :reader success
    :initarg :success
    :type cl:boolean
    :initform cl:nil)
   (transform
    :reader transform
    :initarg :transform
    :type geometry_msgs-msg:TransformStamped
    :initform (cl:make-instance 'geometry_msgs-msg:TransformStamped)))
)

(cl:defclass GetTransform-response (<GetTransform-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <GetTransform-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'GetTransform-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name utils-srv:<GetTransform-response> is deprecated: use utils-srv:GetTransform-response instead.")))

(cl:ensure-generic-function 'success-val :lambda-list '(m))
(cl:defmethod success-val ((m <GetTransform-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader utils-srv:success-val is deprecated.  Use utils-srv:success instead.")
  (success m))

(cl:ensure-generic-function 'transform-val :lambda-list '(m))
(cl:defmethod transform-val ((m <GetTransform-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader utils-srv:transform-val is deprecated.  Use utils-srv:transform instead.")
  (transform m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <GetTransform-response>) ostream)
  "Serializes a message object of type '<GetTransform-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'success) 1 0)) ostream)
  (roslisp-msg-protocol:serialize (cl:slot-value msg 'transform) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <GetTransform-response>) istream)
  "Deserializes a message object of type '<GetTransform-response>"
    (cl:setf (cl:slot-value msg 'success) (cl:not (cl:zerop (cl:read-byte istream))))
  (roslisp-msg-protocol:deserialize (cl:slot-value msg 'transform) istream)
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<GetTransform-response>)))
  "Returns string type for a service object of type '<GetTransform-response>"
  "utils/GetTransformResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'GetTransform-response)))
  "Returns string type for a service object of type 'GetTransform-response"
  "utils/GetTransformResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<GetTransform-response>)))
  "Returns md5sum for a message object of type '<GetTransform-response>"
  "4c5026dc3bd8461725969574664a41aa")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'GetTransform-response)))
  "Returns md5sum for a message object of type 'GetTransform-response"
  "4c5026dc3bd8461725969574664a41aa")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<GetTransform-response>)))
  "Returns full string definition for message of type '<GetTransform-response>"
  (cl:format cl:nil "bool success~%geometry_msgs/TransformStamped transform~%~%================================================================================~%MSG: geometry_msgs/TransformStamped~%# This expresses a transform from coordinate frame header.frame_id~%# to the coordinate frame child_frame_id~%#~%# This message is mostly used by the ~%# <a href=\"http://wiki.ros.org/tf\">tf</a> package. ~%# See its documentation for more information.~%~%Header header~%string child_frame_id # the frame id of the child frame~%Transform transform~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: geometry_msgs/Transform~%# This represents the transform between two coordinate frames in free space.~%~%Vector3 translation~%Quaternion rotation~%~%================================================================================~%MSG: geometry_msgs/Vector3~%# This represents a vector in free space. ~%# It is only meant to represent a direction. Therefore, it does not~%# make sense to apply a translation to it (e.g., when applying a ~%# generic rigid transformation to a Vector3, tf2 will only apply the~%# rotation). If you want your data to be translatable too, use the~%# geometry_msgs/Point message instead.~%~%float64 x~%float64 y~%float64 z~%================================================================================~%MSG: geometry_msgs/Quaternion~%# This represents an orientation in free space in quaternion form.~%~%float64 x~%float64 y~%float64 z~%float64 w~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'GetTransform-response)))
  "Returns full string definition for message of type 'GetTransform-response"
  (cl:format cl:nil "bool success~%geometry_msgs/TransformStamped transform~%~%================================================================================~%MSG: geometry_msgs/TransformStamped~%# This expresses a transform from coordinate frame header.frame_id~%# to the coordinate frame child_frame_id~%#~%# This message is mostly used by the ~%# <a href=\"http://wiki.ros.org/tf\">tf</a> package. ~%# See its documentation for more information.~%~%Header header~%string child_frame_id # the frame id of the child frame~%Transform transform~%~%================================================================================~%MSG: std_msgs/Header~%# Standard metadata for higher-level stamped data types.~%# This is generally used to communicate timestamped data ~%# in a particular coordinate frame.~%# ~%# sequence ID: consecutively increasing ID ~%uint32 seq~%#Two-integer timestamp that is expressed as:~%# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')~%# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')~%# time-handling sugar is provided by the client library~%time stamp~%#Frame this data is associated with~%string frame_id~%~%================================================================================~%MSG: geometry_msgs/Transform~%# This represents the transform between two coordinate frames in free space.~%~%Vector3 translation~%Quaternion rotation~%~%================================================================================~%MSG: geometry_msgs/Vector3~%# This represents a vector in free space. ~%# It is only meant to represent a direction. Therefore, it does not~%# make sense to apply a translation to it (e.g., when applying a ~%# generic rigid transformation to a Vector3, tf2 will only apply the~%# rotation). If you want your data to be translatable too, use the~%# geometry_msgs/Point message instead.~%~%float64 x~%float64 y~%float64 z~%================================================================================~%MSG: geometry_msgs/Quaternion~%# This represents an orientation in free space in quaternion form.~%~%float64 x~%float64 y~%float64 z~%float64 w~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <GetTransform-response>))
  (cl:+ 0
     1
     (roslisp-msg-protocol:serialization-length (cl:slot-value msg 'transform))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <GetTransform-response>))
  "Converts a ROS message object to a list"
  (cl:list 'GetTransform-response
    (cl:cons ':success (success msg))
    (cl:cons ':transform (transform msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'GetTransform)))
  'GetTransform-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'GetTransform)))
  'GetTransform-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'GetTransform)))
  "Returns string type for a service object of type '<GetTransform>"
  "utils/GetTransform")