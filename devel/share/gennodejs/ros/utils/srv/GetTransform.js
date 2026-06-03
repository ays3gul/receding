// Auto-generated. Do not edit!

// (in-package utils.srv)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

let geometry_msgs = _finder('geometry_msgs');

//-----------------------------------------------------------

class GetTransformRequest {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.target_frame = null;
      this.source_frame = null;
    }
    else {
      if (initObj.hasOwnProperty('target_frame')) {
        this.target_frame = initObj.target_frame
      }
      else {
        this.target_frame = '';
      }
      if (initObj.hasOwnProperty('source_frame')) {
        this.source_frame = initObj.source_frame
      }
      else {
        this.source_frame = '';
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type GetTransformRequest
    // Serialize message field [target_frame]
    bufferOffset = _serializer.string(obj.target_frame, buffer, bufferOffset);
    // Serialize message field [source_frame]
    bufferOffset = _serializer.string(obj.source_frame, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type GetTransformRequest
    let len;
    let data = new GetTransformRequest(null);
    // Deserialize message field [target_frame]
    data.target_frame = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [source_frame]
    data.source_frame = _deserializer.string(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.target_frame);
    length += _getByteLength(object.source_frame);
    return length + 8;
  }

  static datatype() {
    // Returns string type for a service object
    return 'utils/GetTransformRequest';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '1cca159d7671f770d19e4e288854c223';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    string target_frame
    string source_frame
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new GetTransformRequest(null);
    if (msg.target_frame !== undefined) {
      resolved.target_frame = msg.target_frame;
    }
    else {
      resolved.target_frame = ''
    }

    if (msg.source_frame !== undefined) {
      resolved.source_frame = msg.source_frame;
    }
    else {
      resolved.source_frame = ''
    }

    return resolved;
    }
};

class GetTransformResponse {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.success = null;
      this.transform = null;
    }
    else {
      if (initObj.hasOwnProperty('success')) {
        this.success = initObj.success
      }
      else {
        this.success = false;
      }
      if (initObj.hasOwnProperty('transform')) {
        this.transform = initObj.transform
      }
      else {
        this.transform = new geometry_msgs.msg.TransformStamped();
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type GetTransformResponse
    // Serialize message field [success]
    bufferOffset = _serializer.bool(obj.success, buffer, bufferOffset);
    // Serialize message field [transform]
    bufferOffset = geometry_msgs.msg.TransformStamped.serialize(obj.transform, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type GetTransformResponse
    let len;
    let data = new GetTransformResponse(null);
    // Deserialize message field [success]
    data.success = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [transform]
    data.transform = geometry_msgs.msg.TransformStamped.deserialize(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += geometry_msgs.msg.TransformStamped.getMessageSize(object.transform);
    return length + 1;
  }

  static datatype() {
    // Returns string type for a service object
    return 'utils/GetTransformResponse';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '846e4c3d5961d5d48399d881e036019b';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    bool success
    geometry_msgs/TransformStamped transform
    
    ================================================================================
    MSG: geometry_msgs/TransformStamped
    # This expresses a transform from coordinate frame header.frame_id
    # to the coordinate frame child_frame_id
    #
    # This message is mostly used by the 
    # <a href="http://wiki.ros.org/tf">tf</a> package. 
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
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new GetTransformResponse(null);
    if (msg.success !== undefined) {
      resolved.success = msg.success;
    }
    else {
      resolved.success = false
    }

    if (msg.transform !== undefined) {
      resolved.transform = geometry_msgs.msg.TransformStamped.Resolve(msg.transform)
    }
    else {
      resolved.transform = new geometry_msgs.msg.TransformStamped()
    }

    return resolved;
    }
};

module.exports = {
  Request: GetTransformRequest,
  Response: GetTransformResponse,
  md5sum() { return '4c5026dc3bd8461725969574664a41aa'; },
  datatype() { return 'utils/GetTransform'; }
};
