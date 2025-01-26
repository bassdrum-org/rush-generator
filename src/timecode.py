from typing import Dict, Tuple
from enum import Enum

# タイムコード関連の定数
class TimeConstants:
    # 時間の単位（秒）
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_MINUTE = 60

class TimecodeKeys(Enum):
    HOURS = 'hours'
    MINUTES = 'minutes'
    SECONDS = 'seconds'
    FRAMES = 'frames'

class TimecodeFormat:
    # タイムコードのフォーマット指定
    DIGIT_FORMAT = '02d'  # 2桁の数値として表示
    SEPARATOR = ':'

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
    hours = frame_number // (fps * TimeConstants.SECONDS_PER_HOUR)
    minutes = (frame_number % (fps * TimeConstants.SECONDS_PER_HOUR)) // (fps * TimeConstants.SECONDS_PER_MINUTE)
    seconds = (frame_number % (fps * TimeConstants.SECONDS_PER_MINUTE)) // fps
    frames = frame_number % fps
    return {
        TimecodeKeys.HOURS.value: hours,
        TimecodeKeys.MINUTES.value: minutes,
        TimecodeKeys.SECONDS.value: seconds,
        TimecodeKeys.FRAMES.value: frames
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
    format_str = f"{{:{TimecodeFormat.DIGIT_FORMAT}}}"
    return TimecodeFormat.SEPARATOR.join([
        format_str.format(tc_dict[TimecodeKeys.HOURS.value]),
        format_str.format(tc_dict[TimecodeKeys.MINUTES.value]),
        format_str.format(tc_dict[TimecodeKeys.SECONDS.value]),
        format_str.format(tc_dict[TimecodeKeys.FRAMES.value])
    ])

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