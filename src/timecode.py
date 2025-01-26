from typing import Dict, Tuple

def calculate_timecode(frame_number: int, fps: int) -> Dict[str, int]:
    """フレーム番号からタイムコードを計算する

    Args:
        frame_number (int): フレーム番号
        fps (int): フレームレート（1秒あたりのフレーム数）

    Returns:
        Dict[str, int]: タイムコードを表す辞書
            - hours (int): 時間
            - minutes (int): 分
            - seconds (int): 秒
            - frames (int): フレーム
    """
    hours = frame_number // (fps * 3600)
    minutes = (frame_number % (fps * 3600)) // (fps * 60)
    seconds = (frame_number % (fps * 60)) // fps
    frames = frame_number % fps
    return {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "frames": frames
    }

def format_timecode(tc_dict: Dict[str, int]) -> str:
    """タイムコードを文字列形式にフォーマットする

    Args:
        tc_dict (Dict[str, int]): タイムコードを表す辞書
            - hours (int): 時間
            - minutes (int): 分
            - seconds (int): 秒
            - frames (int): フレーム

    Returns:
        str: "HH:MM:SS:FF"形式のタイムコード文字列
    """
    return f"{tc_dict['hours']:02}:{tc_dict['minutes']:02}:{tc_dict['seconds']:02}:{tc_dict['frames']:02}"

def calculate_timestamp(frame_number: int, fps: int) -> Tuple[int, int]:
    """フレーム番号からタイムスタンプを計算する

    Args:
        frame_number (int): フレーム番号
        fps (int): フレームレート（1秒あたりのフレーム数）

    Returns:
        Tuple[int, int]: (秒, フレーム)のタプル
    """
    seconds = (frame_number + 1) // fps
    frames = ((frame_number + 1) % fps)
    return seconds, frames