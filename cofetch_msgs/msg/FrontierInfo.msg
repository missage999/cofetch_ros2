# Frontier information
string robot_name      # Robot identifier
geometry_msgs/Point centroid  # Frontier centroid position
float32 size          # Frontier size (number of cells)
float32 cost          # Exploration cost to reach this frontier
float32 value         # Exploration value (expected information gain)
bool is_assigned      # Whether the frontier is assigned