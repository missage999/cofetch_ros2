# Navigation status
string robot_name      # Robot identifier
string status          # Navigation status (idle, navigating, goal_reached, obstacle_detected, failed)
geometry_msgs/Pose current_position  # Current robot pose
geometry_msgs/Pose target_position  # Target pose
float32 distance_to_goal  # Distance to goal
float32 angle_to_goal     # Angle to goal