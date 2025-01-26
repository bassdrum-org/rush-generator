import cv2
import os
import random
import numpy as np
from typing import List, Optional, Tuple
from .frame_generator import create_blank_frame, resize_and_add_padding
from .caption_renderer import add_caption_to_frame
from .text_renderer import drawText
from .constants import (
    MediaConstants,
    FontScale,
    HorizontalAnchor,
    VerticalAnchor,
    FontConstants,
)

# メディアプロセッサー固有の定数
class ProcessorConstants:
    # ランダムカラーの範囲
    RANDOM_COLOR_MIN = 150
    RANDOM_COLOR_MAX = 255

def process_media_file(file_path: str, width: int, height: int, padding: int, fps: int,
                      project_name: str, text_ts_info: List[str], total_frame_number: int,
                      text_cut_num: List[str], text_cut_take: List[str], cut_status: List[str],
                      cut_staff: List[str], cut_filedate: str, video_index: int,
                      duration: Optional[int] = None) -> Tuple[List[np.ndarray], int]:
    """メディアファイル（画像/動画）を処理する

    Args:
        file_path (str): メディアファイルのパス
        width (int): 出力フレームの幅
        height (int): 出力フレームの高さ
        padding (int): パディングのサイズ
        fps (int): フレームレート
        project_name (str): プロジェクト名
        text_ts_info (List[str]): タイムスタンプ情報のリスト
        total_frame_number (int): 総フレーム数
        text_cut_num (List[str]): カット番号のリスト
        text_cut_take (List[str]): テイク番号のリスト
        cut_status (List[str]): カットステータスのリスト
        cut_staff (List[str]): スタッフ情報のリスト
        cut_filedate (str): ファイルの日付
        video_index (int): 動画のインデックス
        duration (Optional[int], optional): 画像ファイルの場合の表示時間（フレーム数）

    Returns:
        Tuple[List[np.ndarray], int]: (処理済みフレームのリスト, 処理したフレーム数)

    Raises:
        ValueError: 画像ファイルに対してdurationが指定されていない場合
    """
    frames = []
    local_frame_number = 0
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext in MediaConstants.IMAGE_EXTENSIONS:
        img = cv2.imread(file_path)
        if duration is None:
            raise ValueError("Duration is required for image files")
        
        for _ in range(duration):
            resize_img_frame = resize_and_add_padding(img, (width, height), padding)
            add_caption_img_frame = add_caption_to_frame(
                resize_img_frame, (width, height), fps, project_name,
                text_ts_info, total_frame_number + local_frame_number,
                text_cut_num, text_cut_take, cut_status, cut_staff,
                cut_filedate, local_frame_number, video_index
            )
            frames.append(add_caption_img_frame)
            local_frame_number += 1
            
    elif ext in MediaConstants.VIDEO_EXTENSIONS:
        video = cv2.VideoCapture(file_path)
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            resize_frame = resize_and_add_padding(frame, (width, height), padding)
            add_caption_frame = add_caption_to_frame(
                resize_frame, (width, height), fps, project_name,
                text_ts_info, total_frame_number + local_frame_number,
                text_cut_num, text_cut_take, cut_status, cut_staff,
                cut_filedate, local_frame_number, video_index
            )
            frames.append(add_caption_frame)
            local_frame_number += 1
        video.release()
        
    return frames, local_frame_number

def process_empty_directory(width: int, height: int, padding: int, fps: int,
                          project_name: str, text_ts_info: List[str], total_frame_number: int,
                          cut_num: List[str], cut_take: List[str], cut_status: List[str],
                          cut_staff: List[str], duration: int, video_index: int) -> Tuple[List[np.ndarray], int]:
    """空のディレクトリを処理する

    Args:
        width (int): フレームの幅
        height (int): フレームの高さ
        padding (int): パディングのサイズ
        fps (int): フレームレート
        project_name (str): プロジェクト名
        text_ts_info (List[str]): タイムスタンプ情報のリスト
        total_frame_number (int): 総フレーム数
        cut_num (List[str]): カット番号のリスト
        cut_take (List[str]): テイク番号のリスト
        cut_status (List[str]): カットステータスのリスト
        cut_staff (List[str]): スタッフ情報のリスト
        duration (int): 生成するフレーム数
        video_index (int): 動画のインデックス

    Returns:
        Tuple[List[np.ndarray], int]: (生成されたフレームのリスト, フレーム数)
    """
    frames = []
    random_color = tuple(random.randint(ProcessorConstants.RANDOM_COLOR_MIN, ProcessorConstants.RANDOM_COLOR_MAX) for _ in range(3))
    
    for local_frame_number in range(duration):
        blank_frame = create_blank_frame(width, height, padding)
        cv2.rectangle(blank_frame, (0, padding), (width, height + padding), random_color, -1)
        add_caption_blank_frame = add_caption_to_frame(
            blank_frame, (width, height), fps, project_name,
            text_ts_info, total_frame_number + local_frame_number, cut_num,
            cut_take, cut_status, cut_staff, MediaConstants.NO_FILE_TEXT,
            local_frame_number, video_index
        )
        drawText(HorizontalAnchor.CENTER.value, VerticalAnchor.CENTER.value,
                add_caption_blank_frame, MediaConstants.NO_FILE_TEXT,
                (width/2, height/2 + padding + 40), FontScale.EXTRA_LARGE,
                font_color=FontConstants.BLACK_COLOR)
        frames.append(add_caption_blank_frame)
    
    return frames, duration

def setup_video_writer(output_path: str, width: int, height: int, fps: int, padding: int) -> cv2.VideoWriter:
    """動画出力の設定を行う

    Args:
        output_path (str): 出力動画ファイルのパス
        width (int): 動画の幅
        height (int): 動画の高さ
        fps (int): フレームレート
        padding (int): パディングのサイズ

    Returns:
        cv2.VideoWriter: 設定された動画ライター

    Raises:
        RuntimeError: VideoWriterの初期化に失敗した場合
    """
    fourcc = cv2.VideoWriter_fourcc(*MediaConstants.VIDEO_CODEC)
    out = cv2.VideoWriter(output_path, int(fourcc), fps, (width, height + (padding*2)))
    
    if not out.isOpened():
        raise RuntimeError("VideoWriterを開けませんでした。コーデックやパスを見直してください。")
    
    return out