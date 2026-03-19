# Path information
string id              # Unique path identifier
geometry_msgs/Point start_position  # Start position
geometry_msgs/Point goal_position  # Goal position
geometry_msgs/Point[] waypoints  # Path waypoints
float32 length          # Path length
bool is_valid          # Whether the path is valid