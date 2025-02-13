import os
import cv2
import datetime
import time
from tqdm import tqdm
from src.file_handler import initialize_project_settings, get_media_file_info
from src.media_processor import process_media_file, process_empty_directory, setup_video_writer

def format_time(seconds):
    """秒数を時間:分:秒の形式に変換する"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def merge_videos_with_frame_numbers(current_path: str, project_csv_path: str, csv_path: str,
                                 output_path: str, padding: int):
    """複数の動画/画像ファイルを結合し、フレーム番号とキャプションを追加する

    Args:
        current_path (str): ビデオディレクトリのパス（絶対パスまたは相対パス）
        project_csv_path (str): プロジェクト情報CSVファイルのパス
        csv_path (str): カット情報CSVファイルのパス
        output_path (str): 出力動画ファイルのパス
        padding (int): パディングのサイズ

    Raises:
        ValueError: ビデオディレクトリまたはCSVファイルが存在しない場合
    """
    # Validate paths
    if not os.path.isdir(current_path):
        raise ValueError(f"Video directory not found: {current_path}")
    if not os.path.isfile(project_csv_path):
        raise ValueError(f"Project info CSV file not found: {project_csv_path}")
    if not os.path.isfile(csv_path):
        raise ValueError(f"Cut info CSV file not found: {csv_path}")
    # プロジェクト設定の初期化
    project_name, width, height, fps, cut_num, text_ts_info, cut_status, cut_take, cut_staff, cut_length_second, cut_length_frame = initialize_project_settings(project_csv_path, csv_path)
    
    # プロジェクト情報の表示
    print("\nProject Information:")
    print("-" * 50)
    print(f"Project Name: {project_name}")
    print(f"Resolution: {width}x{height}")
    print(f"Frame Rate: {fps}fps")
    print("-" * 50)
    
    # Display cut information
    print("\nCut Information Summary:")
    print("-" * 50)
    print(f"{'Cut No.':<10}{'Dur(s)':<8}{'Dur(F)':<8}{'Status':<12}{'Take':<10}{'Staff'}")
    print("-" * 50)
    for i in range(len(cut_num)):
        print(f"{cut_num[i]:<10}{cut_length_second[i]:<8}{cut_length_frame[i]:<8}{cut_status[i]:<12}{cut_take[i]:<10}{cut_staff[i]}")
    print("-" * 50)
    print(f"Total Cuts: {len(cut_num)}")
    total_seconds = sum(int(sec) for sec in cut_length_second)
    total_frames = sum((int(sec) * fps + int(frame)) for sec, frame in zip(cut_length_second, cut_length_frame))
    print(f"Total Duration: {format_time(total_seconds)} ({total_frames} frames)")
    print("-" * 50 + "\n")
    
    # 出力動画の設定
    out = setup_video_writer(output_path, width, height, fps, padding)
    
    # 素材ディレクトリの処理
    total_frame_number = 0
    assets_path = os.path.join(current_path, 'videos')
    
    # 総フレーム数を計算
    total_frames = sum((int(cut_length_second[i]) * fps + int(cut_length_frame[i])) for i in range(len(cut_num)))
    
    # プログレスバーの初期化
    progress_bar = tqdm(total=total_frames, unit='frames', desc='Total Progress')
    
    start_time = time.time()
    processed_frames = 0
    
    for video_index, cut in enumerate(cut_num):
        dir_path = os.path.join(assets_path, cut)
        if os.path.isdir(dir_path):
            duration = (int(cut_length_second[video_index]) * fps) + int(cut_length_frame[video_index])
            
            # カット情報の表示
            cut_info = f"\nProcessing Cut: {cut} ({video_index + 1}/{len(cut_num)})"
            cut_info += f"\nStatus: {cut_status[video_index]}"
            cut_info += f"\nTake: {cut_take[video_index]}"
            cut_info += f"\nStaff: {cut_staff[video_index]}"
            cut_info += f"\nDuration: {format_time(duration/fps)}"
            print(cut_info)
            
            if os.listdir(dir_path):
                file_name, updated_dt = get_media_file_info(dir_path)
                if file_name != 'No File':
                    file_ext = os.path.splitext(file_name)[1].lower()
                    media_type = 'image' if file_ext in ['.jpg', '.png', '.jpeg'] else 'video' if file_ext in ['.mp4', '.avi', '.mov'] else 'media'
                    print(f'Media Type: {media_type.upper()}')
                    print(f'File: {file_name}')
                    print(f'Last Updated: {updated_dt.strftime("%Y-%m-%d %H:%M:%S")}')
                        
                    file_path = os.path.join(dir_path, file_name)
                    frames, frame_count = process_media_file(
                        file_path, width, height, padding, fps,
                        project_name, text_ts_info, total_frame_number,
                        cut_num, cut_take, cut_status, cut_staff,
                        updated_dt.strftime('%Y%m%d'), video_index,
                        duration if file_name.lower().endswith(('.jpg', '.png', '.jpeg')) else None
                    )
            else:
                print(f'Media Type: BLANK')
                frames, frame_count = process_empty_directory(
                    width, height, padding, fps, project_name,
                    text_ts_info, total_frame_number, cut_num,
                    cut_take, cut_status, cut_staff, duration,
                    video_index
                )
                
            # フレーム処理とプログレス更新
            frame_progress = tqdm(frames, total=frame_count, unit='frames', desc='Cut Progress', leave=False)
            for frame in frame_progress:
                out.write(frame)
                processed_frames += 1
                progress_bar.update(1)
                
                # 処理速度と残り時間の計算
                elapsed_time = time.time() - start_time
                fps_rate = processed_frames / elapsed_time
                remaining_frames = total_frames - processed_frames
                eta = remaining_frames / fps_rate if fps_rate > 0 else 0
                
                # ステータス行の更新
                progress_bar.set_postfix({
                    'FPS': f'{fps_rate:.2f}',
                    'ETA': format_time(eta)
                })
            
            total_frame_number += frame_count
            print(f'Cut {cut} completed\n')
        else:
            print(f"\nWarning: Cut directory {cut} not found")
            print(f'Media Type: BLANK (Directory not found)')
            duration = (int(cut_length_second[video_index]) * fps) + int(cut_length_frame[video_index])
            frames, frame_count = process_empty_directory(
                width, height, padding, fps, project_name,
                text_ts_info, total_frame_number, cut_num,
                cut_take, cut_status, cut_staff, duration,
                video_index
            )
            
            # フレーム処理とプログレス更新
            frame_progress = tqdm(frames, total=frame_count, unit='frames', desc='Cut Progress', leave=False)
            for frame in frame_progress:
                out.write(frame)
                processed_frames += 1
                progress_bar.update(1)
                
                # 処理速度と残り時間の計算
                elapsed_time = time.time() - start_time
                fps_rate = processed_frames / elapsed_time
                remaining_frames = total_frames - processed_frames
                eta = remaining_frames / fps_rate if fps_rate > 0 else 0
                
                # ステータス行の更新
                progress_bar.set_postfix({
                    'FPS': f'{fps_rate:.2f}',
                    'ETA': format_time(eta)
                })
            
            total_frame_number += frame_count
            print(f'Cut {cut} completed\n')
    
    progress_bar.close()
    out.release()
    cv2.destroyAllWindows()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nExport completed!")
    print(f"Total processing time: {format_time(elapsed_time)}")
    print(f"Average processing speed: {processed_frames / elapsed_time:.2f} FPS")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Rush Generator - Generate preview videos with timecode and metadata')
    parser.add_argument('--videos-dir', type=str, default='videos',
                      help='Directory containing the video files (default: videos)')
    parser.add_argument('--project-csv', type=str, default='project_info.csv',
                      help='Path to project info CSV file (default: project_info.csv)')
    parser.add_argument('--cut-csv', type=str, default='cut_info.csv',
                      help='Path to cut info CSV file (default: cut_info.csv)')
    args = parser.parse_args()
    
    current = os.path.dirname(__file__)
    
    # Convert relative paths to absolute if needed
    videos_dir = os.path.abspath(args.videos_dir)
    project_csv_path = os.path.abspath(args.project_csv)
    cut_csv_path = os.path.abspath(args.cut_csv)
    
    # Validate that CSV files exist
    if not os.path.isfile(project_csv_path):
        raise ValueError(f"Project info CSV file not found: {project_csv_path}")
    if not os.path.isfile(cut_csv_path):
        raise ValueError(f"Cut info CSV file not found: {cut_csv_path}")
    
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = now.strftime('%Y%m%d%H%M')
    output_video_path = os.path.join(current, 'out', f'rush_{d}.mp4')
    
    print("\nRush Generator Starting...")
    print(f"Videos Directory: {videos_dir}")
    print(f"Project Info CSV: {project_csv_path}")
    print(f"Cut Info CSV: {cut_csv_path}")
    print(f"Output: {output_video_path}")
    print("-" * 50)
    
    merge_videos_with_frame_numbers(videos_dir, project_csv_path, cut_csv_path, output_video_path, 100)
