DATA_PATH = ""                  # Path to folder which includes pointclouds and labels
YAML_PATH = ""                  # Path to semantic-kitti.yaml
SAVE_PATH = ""                  # Path where augmented pointclouds and labels are saved

LABEL_ID = 252                   # ID of object to be extracted (should match .yaml)
MIN_PTS  = 200                   # Minimum number of points that each extracted instance should contain

PLACEMENT_IDS = [40, 44, 49, 72] # IDs where extracted instances will be placed
OBJ_PASTE_NAME = 'moving-car'    # Name of folder where extracted objects are stored

NUMBER_INSTANCES = 1             # Number of instances augmented per pointcloud