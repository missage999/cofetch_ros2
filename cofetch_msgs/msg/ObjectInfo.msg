# Object information
string id              # Unique object identifier
string color           # Object color (red, green, blue)
string shape           # Object shape (box, cylinder, circle, sphere, unknown)
geometry_msgs/Point position  # Object position (normalized 0-1 or 3D)
float32 size           # Object size estimate
float32 confidence     # Detection confidence (0-1)
bool is_grasped        # Whether the object is currently grasped