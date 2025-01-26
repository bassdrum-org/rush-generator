import cv2
import numpy as np
from typing import List, Optional, Tuple
from .text_renderer import drawText
from .timecode import calculate_timecode, format_timecode, calculate_timestamp

def generate_timecode_info(local_frame_number: int, total_frame_number: int, fps: int) -> Tuple[str, str, str, str]:
    """タイムコード関連の情報を生成する

    Args:
        local_frame_number (int): 現在のフレーム番号
        total_frame_number (int): 総フレーム数
        fps (int): フレームレート

    Returns:
        Tuple[str, str, str, str]: (総タイムコード, TCテキスト, TSテキスト, フレーム番号テキスト)
    """
    # 総フレーム数から総タイムコードを計算し、フォーマットする
    total_tc = calculate_timecode(total_frame_number, fps)
    total_text_tc = format_timecode(total_tc)
    
    # 現在のフレーム番号からローカルタイムコードを計算し、フォーマットする
    local_tc = calculate_timecode(local_frame_number, fps)
    text_tc = f"TC {format_timecode(local_tc)}"
    
    # 現在のフレーム番号からタイムスタンプを計算し、フォーマットする
    ts_seconds, ts_frames = calculate_timestamp(local_frame_number, fps)
    text_ts = f"TS ({ts_seconds}:{ts_frames:02})"
    
    # 現在のフレーム番号をテキストとしてフォーマットする
    text_local_frame = f"{(local_frame_number + 1):04}"
    
    # 計算した情報をタプルとして返す
    return total_text_tc, text_tc, text_ts, text_local_frame

def draw_project_info(frame: np.ndarray, project_name: str, text_ts_info: str,
                     width: int) -> None:
    """プロジェクト情報を描画する

    Args:
        frame (np.ndarray): 入力フレーム
        project_name (str): プロジェクト名
        text_ts_info (str): タイムスタンプ情報
        width (int): フレームの幅
    """
    drawText('left', 'top', frame, project_name, (50, 35), 1)
    drawText('left', 'bottom', frame, text_ts_info, (50, 100), 0.75)
    
def draw_cut_info(frame: np.ndarray, cut_num: str, cut_take: str,
                  cut_status: Optional[str]) -> None:
    """カット情報を描画する

    Args:
        frame (np.ndarray): 入力フレーム
        cut_num (str): カット番号
        cut_take (str): テイク番号
        cut_status (Optional[str]): カットステータス
    """
    # カット番号を描画
    drawText('left', 'top', frame, cut_num, (400, 30), 0.75)
    
    # テイク番号を描画
    drawText('left', 'center', frame, cut_take, (400, 65), 0.75)
    
    # カットステータスが存在する場合は描画し、存在しない場合は 'No File' を描画
    if cut_status is not None:
        drawText('left', 'bottom', frame, cut_status, (400, 100), 0.75)
    else:
        drawText('left', 'bottom', frame, 'No File', (200, 100), 0.75)

def draw_staff_info(frame: np.ndarray, cut_staff: Optional[str],
                    cut_filedate: str) -> None:
    """スタッフ情報を描画する

    Args:
        frame (np.ndarray): 入力フレーム
        cut_staff (Optional[str]): スタッフ情報
        cut_filedate (str): ファイルの日付
    """
    if cut_staff is not None:
        drawText('left', 'top', frame, cut_staff, (1600, 30), 0.75)
    else:
        drawText('left', 'top', frame, 'No File', (1600, 10), 0.75)
    
    if cut_filedate != 'No File':
        drawText('left', 'bottom', frame, cut_filedate, (1600, 100), 0.75)
    else:
        drawText('left', 'bottom', frame, 'No File', (1600, 100), 0.75)

def add_caption_to_frame(frame: np.ndarray, resolution: Tuple[int, int], fps: int, project_name: str,
                         text_ts_info: List[str], total_frame_number: int, text_cut_num: List[str],
                         text_cut_take: List[str], cut_status: List[str], cut_staff: List[str],
                         cut_filedate: str, local_frame_number: int, video_index: int) -> np.ndarray:
    """フレームにキャプション情報を追加する

    Args:
        frame (np.ndarray): 入力フレーム
        resolution (Tuple[int, int]): フレームの解像度 (width, height)
        fps (int): フレームレート
        project_name (str): プロジェクト名
        text_ts_info (List[str]): タイムスタンプ情報のリスト
        total_frame_number (int): 総フレーム数
        text_cut_num (List[str]): カット番号のリスト
        text_cut_take (List[str]): テイク番号のリスト
        cut_status (List[str]): カットステータスのリスト
        cut_staff (List[str]): スタッフ情報のリスト
        cut_filedate (str): ファイルの日付
        local_frame_number (int): 現在のフレーム番号
        video_index (int): 動画のインデックス

    Returns:
        np.ndarray: キャプションが追加されたフレーム
    """
    width, height = resolution
    
    # タイムコード関連の情報生成
    total_text_tc, text_tc, text_ts, text_local_frame = generate_timecode_info(
        local_frame_number, total_frame_number, fps
    )
    
    # プロジェクト情報の描画
    draw_project_info(frame, project_name, text_ts_info[video_index], width)
    
    # カット情報の描画
    draw_cut_info(frame, text_cut_num[video_index], text_cut_take[video_index],
                 cut_status[video_index])
    
    # 中央のタイムコード表示
    drawText('center', 'center', frame, total_text_tc, (width/2, 90), 2)
    
    # スタッフ情報の描画
    draw_staff_info(frame, cut_staff[video_index], cut_filedate)
    
    # フレーム情報の描画
    text_cut_frameinfo = f"{text_tc} - {text_ts} - {text_local_frame}"
    drawText('center', 'bottom', frame, text_cut_frameinfo, (width/2, height + 190), 1.5)
    
    return frame