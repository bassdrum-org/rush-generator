import os
import cv2
import datetime
import time
from src.file_handler import initialize_project_settings, get_media_file_info
from src.media_processor import process_media_file, process_empty_directory, setup_video_writer

def merge_videos_with_frame_numbers(current_path: str, project_csv_path: str, csv_path: str,
                                   output_path: str, padding: int):
    """複数の動画/画像ファイルを結合し、フレーム番号とキャプションを追加する

    Args:
        current_path (str): 現在のディレクトリパス
        project_csv_path (str): プロジェクト情報CSVファイルのパス
        csv_path (str): カット情報CSVファイルのパス
        output_path (str): 出力動画ファイルのパス
        padding (int): パディングのサイズ
    """
    # プロジェクト設定の初期化
    project_name, width, height, fps, cut_num, text_ts_info, cut_status, cut_take, cut_staff, cut_length_second, cut_length_frame = initialize_project_settings(project_csv_path, csv_path)
    
    # 出力動画の設定
    out = setup_video_writer(output_path, width, height, fps, padding)
    
    # 素材ディレクトリの処理
    total_frame_number = 0
    assets_path = os.path.join(current_path, 'videos')
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
                            file_path, width, height, padding, fps,
                            project_name, text_ts_info, total_frame_number,
                            cut_num, cut_take, cut_status, cut_staff,
                            updated_dt.strftime('%Y%m%d'), video_index,
                            duration if file_name.lower().endswith(('.jpg', '.png', '.jpeg')) else None
                        )
                else:
                    print(f'StartProcess>>cut_{video_index} :blank')
                    frames, frame_count = process_empty_directory(
                        width, height, padding, fps, project_name,
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