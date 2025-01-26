import cv2
import numpy as np
from typing import Tuple

def calculate_text_position(anchor_x: str, anchor_y: str, text: str, position: Tuple[int, int], 
                          font_scale: float, thickness: int = 2) -> Tuple[int, int]:
    """テキストの描画位置を計算する

    Args:
        anchor_x (str): X軸のアンカーポイント ('left', 'center', 'right')
        anchor_y (str): Y軸のアンカーポイント ('top', 'center', 'bottom')
        text (str): 描画するテキスト
        position (Tuple[int, int]): 基準となる座標 (x, y)
        font_scale (float): フォントスケール
        thickness (int, optional): フォントの太さ. デフォルト値は2

    Returns:
        Tuple[int, int]: テキストの描画開始位置の座標 (x, y)
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    pos_x, pos_y = position
    
    # X方向のオフセット計算
    if anchor_x == 'left':
        offset_x = 0
    elif anchor_x == 'center':
        offset_x = -(size[0] / 2)
    elif anchor_x == 'right':
        offset_x = -size[0]
    
    # Y方向のオフセット計算
    if anchor_y == 'top':
        offset_y = 0
    elif anchor_y == 'center':
        offset_y = -(size[1] / 2)
    elif anchor_y == 'bottom':
        offset_y = -size[1]
        
    return int(pos_x + offset_x), int(pos_y + offset_y)

def drawText(anchor_x: str, anchor_y: str, frame: np.ndarray, text: str, 
             position: Tuple[int, int], font_scale: float, font_color: Tuple[int, int, int] = (255, 255, 255)):
    """フレームにテキストを描画する

    Args:
        anchor_x (str): X軸のアンカーポイント ('left', 'center', 'right')
        anchor_y (str): Y軸のアンカーポイント ('top', 'center', 'bottom')
        frame (np.ndarray): 描画対象のフレーム
        text (str): 描画するテキスト
        position (Tuple[int, int]): テキストの基準位置 (x, y)
        font_scale (float): フォントスケール
        font_color (Tuple[int, int, int], optional): フォントの色 (B,G,R). デフォルト値は白 (255,255,255)
    """
    # 使用するフォントを設定
    font = cv2.FONT_HERSHEY_SIMPLEX
    # フォントの太さを設定
    thickness = 2
    # テキストの描画位置を計算
    pos = calculate_text_position(anchor_x, anchor_y, text, position, font_scale, thickness)
    # フレームにテキストを描画
    cv2.putText(frame, text, pos, font, font_scale, font_color, thickness)