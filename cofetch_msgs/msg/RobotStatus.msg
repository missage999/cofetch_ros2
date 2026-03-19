# Robot status
string id              # Unique robot identifier
geometry_msgs/Point position  # Robot position
geometry_msgs/Quaternion orientation  # Robot orientation
string current_task_id  # ID of the current task being executed
float32 battery_level   # Battery level (0.0-1.0)
string status          # Robot status (idle, busy, charging, error)