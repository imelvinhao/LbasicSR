import os
from os import path as osp
from PIL import Image
from glob import glob
from queue import Queue


def count_subdir(path):
    count = 0
    item_list = os.listdir(path)
    for item in item_list:
        item_path = osp.join(path, item)
        if osp.isdir(item_path):
            count += 1
    return count


def scandir(root_path):
    """This function could scan a directory, and return its leaf node subdirectories.

    Args:
        root_path (str): the directory which will be scanned.

    Returns:
        list: leaf node subdirectories.
    """
    leaf_list = set()
    queue = Queue()
    if count_subdir(root_path) > 0:
        queue.put(root_path)

    while not queue.empty():
        subdir = queue.get()
        for ssdir in os.listdir(subdir):
            ssdir = osp.join(subdir, ssdir)
            if osp.isdir(ssdir) and count_subdir(ssdir) > 0:
                queue.put(ssdir)
            elif count_subdir(ssdir) == 0:
                leaf_list.add(ssdir)
    return sorted(list(leaf_list))


def is_image(frame_name):
    format_list = ["png", "jpg", "jpeg"]
    if frame_name.split(".")[-1].lower() in format_list:
        return True
    else:
        return False


def get_img_info(img_path):
    img = Image.open(img_path)
    width, height = img.size
    mode = img.mode
    return width, height, mode


def get_seq_info(seq_path):
    frame_list = os.listdir(seq_path)
    assert len(frame_list) != 0, f"{seq_path} is an empty video sequence."
    width, height, mode = None, None, None
    for frame in frame_list:
        frame_path = osp.join(seq_path, frame)
        if is_image(frame):
            img = Image.open(frame_path)
            if (width, height, mode) == (None, None, None):
                width, height = img.size
                mode = img.mode
            else:
                assert (
                    width,
                    height,
                ) == img.size, f"{seq_path} have some frames with different size."
                assert mode == img.mode, f"{seq_path} have some frames with different mode."
    return width, height, len(frame_list), mode


def generate_meta_info():
    mode = "Video"
    gt_folder = "/home/xdu/mwh/MIG/train/VR/HR"
    meta_info_file = "meta_info_MIG.txt"

    assert mode in ["Image", "Video"]
    if mode == "Image":
        with open(meta_info_file, "w") as f:
            img_list = sorted(os.listdir(gt_folder))
            # img_list = glob(gt_folder+'/*/*')
            for idx, img_name in enumerate(img_list):
                img_name = osp.join(gt_folder, img_name)
                width, height, mode = get_img_info(img_name)
                # width, height, mode = get_img_info(img_name)

                if mode == "RGB":
                    n_channel = 3
                elif mode == "L":
                    n_channel = 1
                else:
                    n_channel = "unknown"

                img_path = osp.relpath(img_name, gt_folder)
                info = f"{img_path} ({height},{width},{n_channel})"
                print(idx + 1, info)
                f.write(f"{info}\n")

    elif mode == "Video":
        seq_list = scandir(gt_folder)
        with open(meta_info_file, "w") as f:
            for idx, seq_path in enumerate(seq_list):
                width, height, frame_num, mode = get_seq_info(seq_path)

                if mode == "RGB":
                    n_channel = 3
                elif mode == "L":
                    n_channel = 1
                else:
                    n_channel = "unknown"
                seq_path = osp.relpath(seq_path, gt_folder)
                info = f"{seq_path} {frame_num} ({height},{width},{n_channel})"
                print(info)
                f.write(f"{info}\n")


if __name__ == "__main__":
    generate_meta_info()
