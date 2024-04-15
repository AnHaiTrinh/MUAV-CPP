import os.path

import cv2
import numpy as np
from numpy.random import choice

from core.map import Map


def load_map_from_file(filepath: str) -> Map:
    extension = filepath.split(".")[-1]
    if extension in ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "ico"]:
        return load_map_from_image_file(filepath)
    elif extension == "txt":
        return load_map_from_text_file(filepath)
    else:
        raise ValueError(
            f"Unsupported file extension: {extension} for file: {filepath}"
        )


def save_map_to_file(map_to_save: Map, filepath: str, sep: str = ",") -> None:
    extension = filepath.split(".")[-1]
    if extension in ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "ico"]:
        save_map_to_image_file(map_to_save, filepath)
    elif extension == "txt":
        save_map_to_text_file(map_to_save, filepath, sep)
    else:
        raise ValueError(
            f"Unsupported file extension: {extension} for file: {filepath}"
        )


def load_map_from_text_file(txt_file_path: str, sep: str = ",") -> Map:
    cells_np = np.loadtxt(txt_file_path, delimiter=sep, dtype=np.uint8)
    return Map.from_numpy(cells_np)


def load_map_from_image_file(img_file_path: str, img_dir: str = "images") -> Map:
    if not os.path.isfile(img_file_path):
        img_file_path = os.path.join(img_dir, img_file_path)
    img = cv2.imread(img_file_path, cv2.IMREAD_GRAYSCALE)
    img = (img == 0).astype(np.uint8)
    return Map.from_numpy(img)


def save_map_to_text_file(map_to_save: Map, txt_file_path: str, sep: str = ",") -> None:
    np.savetxt(txt_file_path, map_to_save.to_numpy(), delimiter=sep, fmt="%d")


def save_map_to_image_file(map_to_save: Map, img_file_path: str) -> None:
    img = (1 - map_to_save.to_numpy()) * 255
    cv2.imwrite(img_file_path, img)


def resize_map(original_map: Map, target_width: int, target_height: int) -> Map:
    original_map_binary = (1 - original_map.to_numpy()) * 255
    new_map = cv2.resize(
        original_map_binary,
        (target_width, target_height),
        interpolation=cv2.INTER_CUBIC,
    )
    new_map = (new_map == 0).astype(np.uint8)
    return Map.from_numpy(new_map)
