
(cl:in-package :asdf)

(defsystem "abb_control-srv"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :geometry_msgs-msg
)
  :components ((:file "_package")
    (:file "ArmGoal" :depends-on ("_package_ArmGoal"))
    (:file "_package_ArmGoal" :depends-on ("_package"))
  ))