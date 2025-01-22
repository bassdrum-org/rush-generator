import cv2
import os
import glob
import datetime
import csv
import time
import random
import numpy as np
from typing import List, Tuple, Optional, Dict

# タイムコード関連の関数
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

# テキスト描画関連の関数
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

def drawText(_anchorX: str, _anchorY: str, _frame: np.ndarray, _text: str, 
             _position: Tuple[int, int], _font_scale: float, font_color: Tuple[int, int, int] = (255, 255, 255)):
    """フレームにテキストを描画する

    Args:
        _anchorX (str): X軸のアンカーポイント ('left', 'center', 'right')
        _anchorY (str): Y軸のアンカーポイント ('top', 'center', 'bottom')
        _frame (np.ndarray): 描画対象のフレーム
        _text (str): 描画するテキスト
        _position (Tuple[int, int]): テキストの基準位置 (x, y)
        _font_scale (float): フォントスケール
        font_color (Tuple[int, int, int], optional): フォントの色 (B,G,R). デフォルト値は白 (255,255,255)
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 2
    pos = calculate_text_position(_anchorX, _anchorY, _text, _position, _font_scale, thickness)
    cv2.putText(_frame, _text, pos, font, _font_scale, font_color, thickness)

# フレーム生成関連の関数
def create_blank_frame(_width: int, _height: int, _padding: int, color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """指定したサイズの空のフレームを作成する

    Args:
        _width (int): フレームの幅
        _height (int): フレームの高さ
        _padding (int): パディングのサイズ
        color (Tuple[int, int, int], optional): フレームの背景色 (B,G,R). デフォルト値は黒 (0,0,0)

    Returns:
        np.ndarray: 作成された空のフレーム
    """
    blank_height = _height + (2 * _padding)
    blank_frame = cv2.UMat(blank_height, _width, cv2.CV_8UC3).get()
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

# ファイル操作関連の関数
def read_project_info(csv_path: str) -> Tuple[str, int, int, int]:
    """プロジェクト情報CSVファイルを読み込む

    Args:
        csv_path (str): プロジェクト情報CSVファイルのパス

    Returns:
        Tuple[str, int, int, int]: (プロジェクト名, 幅, 高さ, FPS)

    Raises:
        ValueError: CSVファイルにプロジェクト情報が見つからない場合
    """
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # ヘッダーをスキップ
        for line_number, row in enumerate(reader, start=0):
            if line_number == 0:
                return row[0], int(row[1]), int(row[2]), int(row[3])
    raise ValueError("Project info not found in CSV")

def read_cut_info(csv_path: str) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[str]]:
    """カット情報CSVファイルを読み込む

    Args:
        csv_path (str): カット情報CSVファイルのパス

    Returns:
        Tuple[List[str], List[str], List[str], List[str], List[str], List[str]]: 
            (カット番号リスト, 秒数リスト, フレーム数リスト, ステータスリスト, テイクリスト, スタッフリスト)
    """
    cut_num, cut_length_second, cut_length_frame = [], [], []
    cut_status, cut_take, cut_staff = [], [], []
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            cut_num.append(row[0])
            cut_length_second.append(row[1])
            cut_length_frame.append(row[2])
            cut_status.append(row[3])
            cut_take.append(row[4])
            cut_staff.append(row[5])
    
    return cut_num, cut_length_second, cut_length_frame, cut_status, cut_take, cut_staff

def get_media_file_info(dir_path: str) -> Tuple[str, datetime.datetime]:
    """指定ディレクトリ内のメディアファイル情報を取得する

    Args:
        dir_path (str): メディアファイルが格納されているディレクトリのパス

    Returns:
        Tuple[str, datetime.datetime]: (ファイル名, 更新日時)
            ファイルが存在しない場合は ('NoFile', 1970-01-01 00:00:00) を返す
    """
    files = [f for f in os.listdir(dir_path) if f != '.DS_Store']
    if not files:
        return 'NoFile', datetime.datetime(1970, 1, 1)
    
    file = files[0]
    updated_time = os.path.getmtime(os.path.join(dir_path, file))
    updated_dt = datetime.datetime.fromtimestamp(updated_time)
    return file, updated_dt

# キャプション関連の関数
def generate_timecode_info(_local_frame_number: int, _total_frame_number: int, _fps: int) -> Tuple[str, str, str, str]:
    """タイムコード関連の情報を生成する

    Args:
        _local_frame_number (int): 現在のフレーム番号
        _total_frame_number (int): 総フレーム数
        _fps (int): フレームレート

    Returns:
        Tuple[str, str, str, str]: (総タイムコード, TCテキスト, TSテキスト, フレーム番号テキスト)
    """
    total_tc = calculate_timecode(_total_frame_number, _fps)
    total_text_tc = format_timecode(total_tc)
    
    local_tc = calculate_timecode(_local_frame_number, _fps)
    text_tc = f"TC {format_timecode(local_tc)}"
    
    ts_seconds, ts_frames = calculate_timestamp(_local_frame_number, _fps)
    text_ts = f"TS ({ts_seconds}:{ts_frames:02})"
    
    text_local_frame = f"{(_local_frame_number + 1):04}"
    
    return total_text_tc, text_tc, text_ts, text_local_frame

def draw_project_info(_frame: np.ndarray, _project_name: str, _text_ts_info: str,
                     _width: int) -> None:
    """プロジェクト情報を描画する

    Args:
        _frame (np.ndarray): 入力フレーム
        _project_name (str): プロジェクト名
        _text_ts_info (str): タイムスタンプ情報
        _width (int): フレームの幅
    """
    drawText('left', 'top', _frame, _project_name, (50, 35), 1)
    drawText('left', 'bottom', _frame, _text_ts_info, (50, 100), 0.75)
    
def draw_cut_info(_frame: np.ndarray, _cut_num: str, _cut_take: str,
                  _cut_status: Optional[str]) -> None:
    """カット情報を描画する

    Args:
        _frame (np.ndarray): 入力フレーム
        _cut_num (str): カット番号
        _cut_take (str): テイク番号
        _cut_status (Optional[str]): カットステータス
    """
    drawText('left', 'top', _frame, _cut_num, (400, 30), 0.75)
    drawText('left', 'center', _frame, _cut_take, (400, 65), 0.75)
    
    if _cut_status is not None:
        drawText('left', 'bottom', _frame, _cut_status, (400, 100), 0.75)
    else:
        drawText('left', 'bottom', _frame, 'NoFile', (200, 100), 0.75)

def draw_staff_info(_frame: np.ndarray, _cut_staff: Optional[str],
                    _cut_filedate: str) -> None:
    """スタッフ情報を描画する

    Args:
        _frame (np.ndarray): 入力フレーム
        _cut_staff (Optional[str]): スタッフ情報
        _cut_filedate (str): ファイルの日付
    """
    if _cut_staff is not None:
        drawText('left', 'top', _frame, _cut_staff, (1600, 30), 0.75)
    else:
        drawText('left', 'top', _frame, 'NoFile', (1600, 10), 0.75)
    
    if _cut_filedate != 'NoFile':
        drawText('left', 'bottom', _frame, _cut_filedate, (1600, 100), 0.75)
    else:
        drawText('left', 'bottom', _frame, 'NoFile', (1600, 100), 0.75)

def add_caption_to_frame(_frame: np.ndarray, _resolution: Tuple[int, int], _fps: int, _project_name: str,
                         _text_ts_info: List[str], _total_frame_number: int, _text_cut_num: List[str],
                         _text_cut_take: List[str], _cut_status: List[str], _cut_staff: List[str],
                         _cut_filedate: str, _local_frame_number: int, _video_index: int) -> np.ndarray:
    """フレームにキャプション情報を追加する

    Args:
        _frame (np.ndarray): 入力フレーム
        _resolution (Tuple[int, int]): フレームの解像度 (width, height)
        _fps (int): フレームレート
        _project_name (str): プロジェクト名
        _text_ts_info (List[str]): タイムスタンプ情報のリスト
        _total_frame_number (int): 総フレーム数
        _text_cut_num (List[str]): カット番号のリスト
        _text_cut_take (List[str]): テイク番号のリスト
        _cut_status (List[str]): カットステータスのリスト
        _cut_staff (List[str]): スタッフ情報のリスト
        _cut_filedate (str): ファイルの日付
        _local_frame_number (int): 現在のフレーム番号
        _video_index (int): 動画のインデックス

    Returns:
        np.ndarray: キャプションが追加されたフレーム
    """
    _width, _height = _resolution
    
    # タイムコード関連の情報生成
    total_text_tc, text_tc, text_ts, text_local_frame = generate_timecode_info(
        _local_frame_number, _total_frame_number, _fps
    )
    
    # プロジェクト情報の描画
    draw_project_info(_frame, _project_name, _text_ts_info[_video_index], _width)
    
    # カット情報の描画
    draw_cut_info(_frame, _text_cut_num[_video_index], _text_cut_take[_video_index],
                 _cut_status[_video_index])
    
    # 中央のタイムコード表示
    drawText('center', 'center', _frame, total_text_tc, (_width/2, 90), 2)
    
    # スタッフ情報の描画
    draw_staff_info(_frame, _cut_staff[_video_index], _cut_filedate)
    
    # フレーム情報の描画
    text_cut_frameinfo = f"{text_tc} - {text_ts} - {text_local_frame}"
    drawText('center', 'bottom', _frame, text_cut_frameinfo, (_width/2, _height + 190), 1.5)
    
    return _frame

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
    if ext in ['.jpg', '.png', '.jpeg']:
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
            
    elif ext in ['.mp4', '.avi', '.mov']:
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

def initialize_project_settings(_project_csv_path: str, _csv_path: str) -> Tuple[str, int, int, int, List[str], List[str]]:
    """プロジェクトの設定を初期化する

    Args:
        _project_csv_path (str): プロジェクト情報CSVファイルのパス
        _csv_path (str): カット情報CSVファイルのパス

    Returns:
        Tuple[str, int, int, int, List[str], List[str]]:
            (プロジェクト名, 幅, 高さ, FPS, カット番号リスト, タイムスタンプ情報リスト)
    """
    project_name, width, height, fps = read_project_info(_project_csv_path)
    print(f'SettingImported! size = ({width}{height}) fps = {fps}')
    
    cut_num, cut_length_second, cut_length_frame, cut_status, cut_take, cut_staff = read_cut_info(_csv_path)
    text_ts_info = [f"{s} + {f}" for s, f in zip(cut_length_second, cut_length_frame)]
    
    return project_name, width, height, fps, cut_num, text_ts_info, cut_status, cut_take, cut_staff, cut_length_second, cut_length_frame

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
    """
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, int(fourcc), fps, (width, height + (padding*2)))
    
    if not out.isOpened():
        raise RuntimeError("VideoWriterを開けませんでした。コーデックやパスを見直してください。")
    
    return out

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
    random_color = tuple(random.randint(150, 255) for _ in range(3))
    for local_frame_number in range(duration):
        blank_frame = create_blank_frame(width, height, padding)
        cv2.rectangle(blank_frame, (0, padding), (width, height + padding), random_color, -1)
        add_caption_blank_frame = add_caption_to_frame(
            blank_frame, (width, height), fps, project_name,
            text_ts_info, total_frame_number, cut_num,
            cut_take, cut_status, cut_staff, 'NoFile',
            local_frame_number, video_index
        )
        drawText('center', 'center', add_caption_blank_frame, 'No File',
                (width/2, height/2 + padding+40), 2, font_color=(0, 0, 0))
        frames.append(add_caption_blank_frame)
    return frames, duration

def merge_videos_with_frame_numbers(_current_path: str, _project_csv_path: str, _csv_path: str,
                                   output_path: str, _padding: int):
    """複数の動画/画像ファイルを結合し、フレーム番号とキャプションを追加する

    Args:
        _current_path (str): 現在のディレクトリパス
        _project_csv_path (str): プロジェクト情報CSVファイルのパス
        _csv_path (str): カット情報CSVファイルのパス
        output_path (str): 出力動画ファイルのパス
        _padding (int): パディングのサイズ
    """
    # プロジェクト設定の初期化
    project_name, width, height, fps, cut_num, text_ts_info, cut_status, cut_take, cut_staff, cut_length_second, cut_length_frame = initialize_project_settings(_project_csv_path, _csv_path)
    
    # 出力動画の設定
    out = setup_video_writer(output_path, width, height, fps, _padding)
    
    # 素材ディレクトリの処理
    total_frame_number = 0
    assets_path = os.path.join(_current_path, 'videos')
    dirs = sorted([f for f in os.listdir(assets_path) if os.path.isdir(os.path.join(assets_path, f))])
    print(dirs)
    print(cut_num)
    
    for video_index, cut in enumerate(cut_num):
        found_cut = False
        for dir_name in dirs:
            if cut == dir_name:
                found_cut = True
                dir_path = os.path.join(assets_path, dir_name)
                duration = (int(cut_length_second[video_index]) * fps) + int(cut_length_frame[video_index])
                
                if os.listdir(dir_path):
                    print(f'StartProcess>>cut_{video_index} :media')
                    file_name, updated_dt = get_media_file_info(dir_path)
                    if file_name != 'NoFile':
                        file_path = os.path.join(dir_path, file_name)
                        frames, frame_count = process_media_file(
                            file_path, width, height, _padding, fps,
                            project_name, text_ts_info, total_frame_number,
                            cut_num, cut_take, cut_status, cut_staff,
                            updated_dt.strftime('%Y%m%d'), video_index,
                            duration if file_name.lower().endswith(('.jpg', '.png', '.jpeg')) else None
                        )
                else:
                    print(f'StartProcess>>cut_{video_index} :blank')
                    frames, frame_count = process_empty_directory(
                        width, height, _padding, fps, project_name,
                        text_ts_info, total_frame_number, cut_num,
                        cut_take, cut_status, cut_staff, duration,
                        video_index
                    )
                
                for frame in frames:
                    out.write(frame)
                total_frame_number += frame_count
                print('EndProcess')
                
        if not found_cut:
            print("not found cut directory")
    
    out.release()
    cv2.destroyAllWindows()
    print('Done!')

# メイン処理
if __name__ == "__main__":
    current = os.path.dirname(__file__)
    csv_path_project = os.path.join(current, "project_info.csv")
    csv_path_cut = os.path.join(current, "cut_info.csv")
    
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = now.strftime('%Y%m%d%H%M')
    output_video_path = os.path.join(current, 'out', f'rush_{d}.mp4')
    
    start_time = time.time()
    print("Start")
    
    merge_videos_with_frame_numbers(current, csv_path_project, csv_path_cut, output_video_path, 100)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"EndExport. Processing time{elapsed_time:.2f}seconds")