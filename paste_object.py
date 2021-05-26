import os
import random
import numpy as np

data_path = "./data/sequences/00"
save_path = "./aug_data/sequences/00"

scan_names = os.listdir(os.path.join(data_path, "velodyne"))
scan_names.sort()

label_names = os.listdir(os.path.join(data_path, "labels"))
label_names.sort()

cnt = 1

placement_id = 40
obj_paste_name = 'moving-car'
obj_paste_id = 252

def axis_overlap(a_min1, a_max1, a_min2, a_max2):
    return a_max1 >= a_min2 and a_max2 >= a_min1

def is_overlap(cloud, sem_cloud, inst_cloud, paste_id, bbox):
    obj_idx = np.where(sem_cloud == paste_id)[0]
    obj_inst = inst_cloud[obj_idx]

    unique_inst_ids = np.unique(obj_inst)
    
    for id in unique_inst_ids:
        inst_idx = np.where(inst_cloud == id)[0]

        obj_inst_idx = np.intersect1d(obj_idx, inst_idx)
        obj_inst = cloud[obj_inst_idx]
        
        inst_pt1 = (np.min(obj_inst[:, 0]), np.min(obj_inst[:, 1]), np.min(obj_inst[:, 2]))
        inst_pt2 = (np.max(obj_inst[:, 0]), np.max(obj_inst[:, 1]), np.max(obj_inst[:, 2]))

        paste_pt1 = bbox[0]
        paste_pt2 = bbox[1]

        x_overlap = axis_overlap(paste_pt1[0], paste_pt2[0], inst_pt1[0], inst_pt2[0])
        y_overlap = axis_overlap(paste_pt1[1], paste_pt2[1], inst_pt1[1], inst_pt2[1])
        z_overlap = axis_overlap(paste_pt1[2], paste_pt2[2], inst_pt1[2], inst_pt2[2])

        if x_overlap and y_overlap and z_overlap:
            return True
        
    return False

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

    object_list = os.listdir(obj_paste_name)
    obj_to_paste = np.fromfile(os.path.join(obj_paste_name, random.choice(object_list)), dtype=np.float32)
    obj_to_paste = obj_to_paste.reshape((-1, 4))

    obj_yaw = obj_to_paste[-1]
    obj_to_paste = obj_to_paste[:-1]

    placement_all = np.where(sem_label == placement_id)[0]
    placement_id_yaw = -np.arctan2(scan[placement_all, 1], scan[placement_all, 0])
    
    lower_limit = np.where(placement_id_yaw > obj_yaw[0])[0]
    upper_limit = np.where(placement_id_yaw < obj_yaw[1])[0]
    threshold = np.intersect1d(lower_limit, upper_limit)

    placement_idx = placement_all[threshold]

    while True:
        index = random.randint(0, len(placement_idx) - 1)
        location = scan[placement_idx[index]]
        obj_to_paste = obj_to_paste + location

        placement_idx = np.delete(placement_idx, index)

        min_x_obj = np.min(obj_to_paste[:, 0])
        max_x_obj = np.max(obj_to_paste[:, 0])

        min_y_obj = np.min(obj_to_paste[:, 1])
        max_y_obj = np.max(obj_to_paste[:, 1])

        min_z_obj = np.min(obj_to_paste[:, 2])
        max_z_obj = np.max(obj_to_paste[:, 2])

        bbox = [(min_x_obj, min_y_obj, min_z_obj), (max_x_obj, max_y_obj, max_z_obj)]
    
        if is_overlap(scan, sem_label, inst_label, obj_paste_id, bbox):
            continue

        break

    obj_idx = np.where(sem_label == obj_paste_id)[0]
    obj_inst = inst_label[obj_idx]

    new_inst_id = np.max(obj_inst) + 1

    obj_paste_lbl = np.full((obj_to_paste.shape[0], 1), obj_paste_id, dtype=np.int32)
    obj_paste_inst = np.full((obj_to_paste.shape[0], 1), new_inst_id, dtype=np.int32)
    
    obj_paste_inst = obj_paste_inst << 16
    obj_combined_lbl = obj_paste_lbl + obj_paste_inst

    save_scan = np.vstack((scan, obj_to_paste))
    save_label = np.vstack((label, obj_combined_lbl))

    save_scan.tofile(os.path.join(save_path, "velodyne", scan_names[i]))
    save_label.tofile(os.path.join(save_path, "labels", label_names[i]))

    print(scan_names[i], label_names[i])