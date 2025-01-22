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
    """フレーム番号からタイムコードを計算"""
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
    """タイムコードを文字列にフォーマット"""
    return f"{tc_dict['hours']:02}:{tc_dict['minutes']:02}:{tc_dict['seconds']:02}:{tc_dict['frames']:02}"

def calculate_timestamp(frame_number: int, fps: int) -> Tuple[int, int]:
    """フレーム番号からタイムスタンプを計算"""
    seconds = (frame_number + 1) // fps
    frames = ((frame_number + 1) % fps)
    return seconds, frames

# テキスト描画関連の関数
def calculate_text_position(anchor_x: str, anchor_y: str, text: str, position: Tuple[int, int], 
                          font_scale: float, thickness: int = 2) -> Tuple[int, int]:
    """テキストの描画位置を計算"""
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
    """文字書き込み関数"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 2
    pos = calculate_text_position(_anchorX, _anchorY, _text, _position, _font_scale, thickness)
    cv2.putText(_frame, _text, pos, font, _font_scale, font_color, thickness)

# フレーム生成関連の関数
def create_blank_frame(_width: int, _height: int, _padding: int, color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """黒いフレームを作成する関数"""
    blank_height = _height + (2 * _padding)
    blank_frame = cv2.UMat(blank_height, _width, cv2.CV_8UC3).get()
    blank_frame[:, :] = color
    return blank_frame

def resize_and_add_padding(frame: np.ndarray, target_resolution: Tuple[int, int], 
                          padding: int, color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
    """フレームをリサイズしてパディングを追加"""
    resized_frame = cv2.resize(frame, target_resolution)
    padded_frame = create_blank_frame(target_resolution[0], target_resolution[1], padding, color)
    padded_frame[padding:padding + target_resolution[1], :, :] = resized_frame
    return padded_frame

# ファイル操作関連の関数
def read_project_info(csv_path: str) -> Tuple[str, int, int, int]:
    """プロジェクト情報CSVを読み込む"""
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # ヘッダーをスキップ
        for line_number, row in enumerate(reader, start=0):
            if line_number == 0:
                return row[0], int(row[1]), int(row[2]), int(row[3])
    raise ValueError("Project info not found in CSV")

def read_cut_info(csv_path: str) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[str]]:
    """カット情報CSVを読み込む"""
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
    """メディアファイルの情報を取得"""
    files = [f for f in os.listdir(dir_path) if f != '.DS_Store']
    if not files:
        return 'NoFile', datetime.datetime(1970, 1, 1)
    
    file = files[0]
    updated_time = os.path.getmtime(os.path.join(dir_path, file))
    updated_dt = datetime.datetime.fromtimestamp(updated_time)
    return file, updated_dt

# キャプション関連の関数
def add_caption_to_frame(_frame: np.ndarray, _resolution: Tuple[int, int], _fps: int, _project_name: str,
                        _text_ts_info: List[str], _total_frame_number: int, _text_cut_num: List[str],
                        _text_cut_take: List[str], _cut_status: List[str], _cut_staff: List[str],
                        _cut_filedate: str, _local_frame_number: int, _video_index: int) -> np.ndarray:
    """フレームを計算して字幕を追加する関数"""
    _width, _height = _resolution
    
    # タイムコードの計算
    total_tc = calculate_timecode(_total_frame_number, _fps)
    total_text_tc = format_timecode(total_tc)
    
    local_tc = calculate_timecode(_local_frame_number, _fps)
    text_tc = f"TC {format_timecode(local_tc)}"
    
    ts_seconds, ts_frames = calculate_timestamp(_local_frame_number, _fps)
    text_ts = f"TS ({ts_seconds}:{ts_frames:02})"
    
    # フレームに字幕を追加
    drawText('left', 'top', _frame, _project_name, (50, 35), 1)
    drawText('left', 'bottom', _frame, _text_ts_info[_video_index], (50, 100), 0.75)
    
    drawText('left', 'top', _frame, _text_cut_num[_video_index], (400, 30), 0.75)
    drawText('left', 'center', _frame, _text_cut_take[_video_index], (400, 65), 0.75)
    
    if _cut_status[_video_index] is not None:
        drawText('left', 'bottom', _frame, _cut_status[_video_index], (400, 100), 0.75)
    else:
        drawText('left', 'bottom', _frame, 'NoFile', (200, 100), 0.75)
    
    drawText('center', 'center', _frame, total_text_tc, (_width/2, 90), 2)
    
    if _cut_staff[_video_index] is not None:
        drawText('left', 'top', _frame, _cut_staff[_video_index], (1600, 30), 0.75)
    else:
        drawText('left', 'top', _frame, 'NoFile', (1600, 10), 0.75)
    
    if _cut_filedate != 'NoFile':
        drawText('left', 'bottom', _frame, _cut_filedate, (1600, 100), 0.75)
    else:
        drawText('left', 'bottom', _frame, 'NoFile', (1600, 100), 0.75)
    
    text_local_frame = f"{(_local_frame_number + 1):04}"
    text_cut_frameinfo = f"{text_tc} - {text_ts} - {text_local_frame}"
    
    drawText('center', 'bottom', _frame, text_cut_frameinfo, (_width/2, _height + 190), 1.5)
    return _frame

def process_media_file(file_path: str, width: int, height: int, padding: int, fps: int,
                      project_name: str, text_ts_info: List[str], total_frame_number: int,
                      text_cut_num: List[str], text_cut_take: List[str], cut_status: List[str],
                      cut_staff: List[str], cut_filedate: str, video_index: int,
                      duration: Optional[int] = None) -> Tuple[List[np.ndarray], int]:
    """メディアファイル（画像/動画）を処理"""
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

def merge_videos_with_frame_numbers(_current_path: str, _project_csv_path: str, _csv_path: str,
                                  output_path: str, _padding: int):
    """メインの動画書き出し関数"""
    # プロジェクト情報の読み込み
    project_name, width, height, fps = read_project_info(_project_csv_path)
    print(f'SettingImported! size = ({width}{height}) fps = {fps}')
    
    # カット情報の読み込み
    cut_num, cut_length_second, cut_length_frame, cut_status, cut_take, cut_staff = read_cut_info(_csv_path)
    text_ts_info = [f"{s} + {f}" for s, f in zip(cut_length_second, cut_length_frame)]
    
    # 出力動画の設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, int(fourcc), fps, (width, height + (_padding*2)))
    
    if not out.isOpened():
        print("VideoWriterを開けませんでした。コーデックやパスを見直してください。")
        return
    
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
                
                if os.listdir(dir_path):
                    print(f'StartProcess>>cut_{video_index} :media')
                    file_name, updated_dt = get_media_file_info(dir_path)
                    if file_name != 'NoFile':
                        file_path = os.path.join(dir_path, file_name)
                        duration = (int(cut_length_second[video_index]) * fps) + int(cut_length_frame[video_index])
                        frames, frame_count = process_media_file(
                            file_path, width, height, _padding, fps,
                            project_name, text_ts_info, total_frame_number,
                            cut_num, cut_take, cut_status, cut_staff,
                            updated_dt.strftime('%Y%m%d'), video_index,
                            duration if file_name.lower().endswith(('.jpg', '.png', '.jpeg')) else None
                        )
                        for frame in frames:
                            out.write(frame)
                        total_frame_number += frame_count
                else:
                    print(f'StartProcess>>cut_{video_index} :blank')
                    duration = (int(cut_length_second[video_index]) * fps) + int(cut_length_frame[video_index])
                    random_color = tuple(random.randint(150, 255) for _ in range(3))
                    for local_frame_number in range(duration):
                        blank_frame = create_blank_frame(width, height, _padding)
                        cv2.rectangle(blank_frame, (0, _padding), (width, height + _padding), random_color, -1)
                        add_caption_blank_frame = add_caption_to_frame(
                            blank_frame, (width, height), fps, project_name,
                            text_ts_info, total_frame_number, cut_num,
                            cut_take, cut_status, cut_staff, 'NoFile',
                            local_frame_number, video_index
                        )
                        drawText('center', 'center', add_caption_blank_frame, 'No File',
                               (width/2, height/2 + _padding+40), 2, font_color=(0, 0, 0))
                        out.write(add_caption_blank_frame)
                        total_frame_number += 1
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