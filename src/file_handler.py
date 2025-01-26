import os
import csv
import datetime
from typing import List, Tuple

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

def initialize_project_settings(project_csv_path: str, csv_path: str) -> Tuple[str, int, int, int, List[str], List[str], List[str], List[str], List[str], List[str], List[str]]:
    """プロジェクトの設定を初期化する

    Args:
        project_csv_path (str): プロジェクト情報CSVファイルのパス
        csv_path (str): カット情報CSVファイルのパス

    Returns:
        Tuple[str, int, int, int, List[str], List[str], List[str], List[str], List[str], List[str], List[str]]:
            (プロジェクト名, 幅, 高さ, FPS, カット番号リスト, タイムスタンプ情報リスト, ステータスリスト, テイクリスト, スタッフリスト, 秒数リスト, フレーム数リスト)
    """
    project_name, width, height, fps = read_project_info(project_csv_path)
    print(f'SettingImported! size = ({width}{height}) fps = {fps}')
    
    cut_num, cut_length_second, cut_length_frame, cut_status, cut_take, cut_staff = read_cut_info(csv_path)
    text_ts_info = [f"{s} + {f}" for s, f in zip(cut_length_second, cut_length_frame)]
    
    return project_name, width, height, fps, cut_num, text_ts_info, cut_status, cut_take, cut_staff, cut_length_second, cut_length_frame