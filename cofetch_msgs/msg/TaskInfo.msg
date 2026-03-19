# Task information
string id              # Unique task identifier
string task_type       # Task type (explore, pick_and_place, navigate)
string object_id       # Target object ID
string object_color    # Target object color (red, green, blue)
geometry_msgs/Point target_position  # Target position
float32 priority       # Task priority (higher = more important)
string status          # Task status (pending, assigned, in_progress, completed, failed)
string assigned_robot  # Robot assigned to this task