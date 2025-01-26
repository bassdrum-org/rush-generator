import cv2
import numpy as np
from typing import Tuple

def create_blank_frame(width: int, height: int, padding: int, color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """指定したサイズの空のフレームを作成する

    Args:
        width (int): フレームの幅
        height (int): フレームの高さ
        padding (int): パディングのサイズ
        color (Tuple[int, int, int], optional): フレームの背景色 (B,G,R). デフォルト値は黒 (0,0,0)

    Returns:
        np.ndarray: 作成された空のフレーム
    """
    blank_height = height + (2 * padding)
    blank_frame = cv2.UMat(blank_height, width, cv2.CV_8UC3).get()
    blank_frame[:, :] = color
    return blank_frame

def resize_and_add_padding(frame: np.ndarray, target_resolution: Tuple[int, int], 
                          padding: int, color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """フレームをリサイズしてパディングを追加する

    Args:
        frame (np.ndarray): 入力フレーム
        target_resolution (Tuple[int, int]): 目標解像度 (width, height)
        padding (int): パディングのサイズ
        color (Tuple[int, int, int], optional): パディングの色 (B,G,R). デフォルト値は黒 (0,0,0)

    Returns:
        np.ndarray: リサイズされパディングが追加されたフレーム
    """
    resized_frame = cv2.resize(frame, target_resolution)
    padded_frame = create_blank_frame(target_resolution[0], target_resolution[1], padding, color)
    padded_frame[padding:padding + target_resolution[1], :, :] = resized_frame
    return padded_frame