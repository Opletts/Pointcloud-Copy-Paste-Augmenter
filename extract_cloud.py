import os
import yaml
import numpy as np

from params import *

data_path = DATA_PATH

CFG = yaml.safe_load(open(YAML_PATH, 'r'))
label_dict = CFG['labels']

label_id = LABEL_ID
label_name = label_dict[label_id]

os.makedirs(label_name, exist_ok=True)

scan_names = os.listdir(os.path.join(data_path, "velodyne"))
scan_names.sort()

label_names = os.listdir(os.path.join(data_path, "labels"))
label_names.sort()

cnt = 1
min_pts = MIN_PTS

for i in range(len(scan_names)):
    scan = np.fromfile(os.path.join(data_path, "velodyne", scan_names[i]), dtype=np.float32)
    label = np.fromfile(os.path.join(data_path, "labels", label_names[i]), dtype=np.int32)

    scan = scan.reshape((-1, 4))
    label = label.reshape((-1, 1))

    if label.shape[0] == scan.shape[0]:
        sem_label  = label & 0xFFFF      # lower 16 bits extracted
        inst_label = label >> 16         # upper 16 bits
    
    else:
        print("Pointcloud and Label don't match.")
        exit(0)

    extract_idx = np.where(sem_label == label_id)[0]
    instances = inst_label[extract_idx]

    inst_idx = np.unique(instances)

    for id in inst_idx:
        id_instance = np.where(inst_label == id)[0]

        save_pts_idx = np.intersect1d(extract_idx, id_instance)
        save_pts = scan[save_pts_idx]

        if save_pts.shape[0] < min_pts:
            continue

        yaw = -np.arctan2(save_pts[:, 1], save_pts[:, 0])
        min_max_avg_yaw = np.array([np.min(yaw), np.max(yaw), np.mean(yaw), 0], dtype=np.float32)

        min_z_idx = np.argmin(save_pts[:, 2])
        min_xyz = save_pts[min_z_idx]

        save_pts = save_pts - min_xyz
        save_pts = np.vstack((save_pts, min_max_avg_yaw))

        print(label_name + str(cnt))
        save_pts.tofile(os.path.join(label_name, label_name + str(cnt) + '.bin'))
        cnt += 1
