import unittest
import cv2
import numpy as np
import os
import tempfile
import csv
from datetime import datetime
from rush_generator import (
    drawText,
    create_blank_frame,
    resize_and_add_padding,
    add_caption_to_frame,
    merge_videos_with_frame_numbers,
    calculate_timecode,
    format_timecode,
    calculate_timestamp,
    calculate_text_position,
    read_project_info,
    read_cut_info,
    get_media_file_info,
    process_media_file
)

class TestRushGenerator(unittest.TestCase):
    def setUp(self):
        """テストで使用する共通の値を設定"""
        self.width = 1920
        self.height = 1080
        self.padding = 100
        self.fps = 30

    def test_calculate_timecode(self):
        """calculate_timecode関数のテスト"""
        # 通常のケース
        result = calculate_timecode(90, 30)  # 3秒分のフレーム
        self.assertEqual(result, {
            "hours": 0,
            "minutes": 0,
            "seconds": 3,
            "frames": 0
        })

        # 1時間以上のケース
        result = calculate_timecode(3600 * 30, 30)  # 1時間分のフレーム
        self.assertEqual(result, {
            "hours": 1,
            "minutes": 0,
            "seconds": 0,
            "frames": 0
        })

        # フレーム数のみのケース
        result = calculate_timecode(15, 30)
        self.assertEqual(result, {
            "hours": 0,
            "minutes": 0,
            "seconds": 0,
            "frames": 15
        })

    def test_format_timecode(self):
        """format_timecode関数のテスト"""
        tc_dict = {
            "hours": 1,
            "minutes": 30,
            "seconds": 45,
            "frames": 15
        }
        self.assertEqual(format_timecode(tc_dict), "01:30:45:15")

        # ゼロパディングのテスト
        tc_dict = {
            "hours": 0,
            "minutes": 5,
            "seconds": 7,
            "frames": 9
        }
        self.assertEqual(format_timecode(tc_dict), "00:05:07:09")

    def test_calculate_timestamp(self):
        """calculate_timestamp関数のテスト"""
        # 通常のケース
        seconds, frames = calculate_timestamp(89, 30)  # 2.9666...秒
        self.assertEqual(seconds, 3)
        self.assertEqual(frames, 0)

        # フレーム数のみのケース
        seconds, frames = calculate_timestamp(14, 30)
        self.assertEqual(seconds, 0)
        self.assertEqual(frames, 15)

    def test_calculate_text_position(self):
        """calculate_text_position関数のテスト"""
        text = "Test"
        font_scale = 1.0
        thickness = 2
        position = (100, 100)

        # 左上配置
        pos = calculate_text_position('left', 'top', text, position, font_scale, thickness)
        self.assertEqual(pos[0], 100)  # X座標は変更なし
        self.assertEqual(pos[1], 100)  # Y座標は変更なし

        # 中央配置
        pos = calculate_text_position('center', 'center', text, position, font_scale, thickness)
        self.assertLess(pos[0], 100)  # X座標は左にオフセット
        self.assertLess(pos[1], 100)  # Y座標は上にオフセット

        # 右下配置
        pos = calculate_text_position('right', 'bottom', text, position, font_scale, thickness)
        self.assertLess(pos[0], 100)  # X座標は左にオフセット
        self.assertLess(pos[1], 100)  # Y座標は上にオフセット

    def test_create_blank_frame(self):
        """create_blank_frame関数のテスト"""
        # 基本的なケース
        frame = create_blank_frame(self.width, self.height, self.padding)
        self.assertEqual(frame.shape, (self.height + 2 * self.padding, self.width, 3))
        self.assertTrue(np.all(frame == 0))  # デフォルトの黒色を確認

        # カスタム色のケース
        custom_color = (255, 0, 0)  # 青色
        frame = create_blank_frame(self.width, self.height, self.padding, color=custom_color)
        self.assertTrue(np.all(frame[:, :] == custom_color))

        # 最小サイズのケース
        min_frame = create_blank_frame(1, 1, 0)
        self.assertEqual(min_frame.shape, (1, 1, 3))

    def test_drawText(self):
        """drawText関数のテスト"""
        frame = create_blank_frame(self.width, self.height, self.padding)
        test_text = "Test Text"
        
        # 左上配置のテスト
        drawText('left', 'top', frame, test_text, (50, 50), 1.0)
        self.assertFalse(np.all(frame == 0))

        # 中央配置のテスト
        frame = create_blank_frame(self.width, self.height, self.padding)
        drawText('center', 'center', frame, test_text, (self.width//2, self.height//2), 1.0)
        self.assertFalse(np.all(frame == 0))

        # 日本語テキストのテスト
        frame = create_blank_frame(self.width, self.height, self.padding)
        drawText('left', 'top', frame, "テストテキスト", (50, 50), 1.0)
        self.assertFalse(np.all(frame == 0))

    def test_resize_and_add_padding(self):
        """resize_and_add_padding関数のテスト"""
        # 標準的なケース
        input_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        input_frame[:] = (255, 255, 255)  # 白色フレーム
        target_resolution = (1920, 1080)
        result = resize_and_add_padding(input_frame, target_resolution, self.padding)
        expected_height = target_resolution[1] + 2 * self.padding
        self.assertEqual(result.shape, (expected_height, target_resolution[0], 3))
        self.assertTrue(np.all(result[:self.padding] == 0))  # 上部パディング
        self.assertTrue(np.all(result[-self.padding:] == 0))  # 下部パディング

        # 小さい解像度へのリサイズ
        target_resolution = (640, 360)
        result = resize_and_add_padding(input_frame, target_resolution, self.padding)
        expected_height = target_resolution[1] + 2 * self.padding
        self.assertEqual(result.shape, (expected_height, target_resolution[0], 3))

    def test_read_project_info(self):
        """read_project_info関数のテスト"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Project Name", "Width", "Height", "FPS"])
            writer.writerow(["Test Project", "1920", "1080", "30"])
            csv_path = f.name

        try:
            project_name, width, height, fps = read_project_info(csv_path)
            self.assertEqual(project_name, "Test Project")
            self.assertEqual(width, 1920)
            self.assertEqual(height, 1080)
            self.assertEqual(fps, 30)
        finally:
            os.unlink(csv_path)

    def test_read_cut_info(self):
        """read_cut_info関数のテスト"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Cut Number", "Seconds", "Frames", "Status", "Take", "Staff"])
            writer.writerow(["A0001", "1", "15", "OK", "Take1", "Staff A"])
            writer.writerow(["A0002", "2", "0", "NG", "Take2", "Staff B"])
            csv_path = f.name

        try:
            cut_num, cut_length_second, cut_length_frame, cut_status, cut_take, cut_staff = read_cut_info(csv_path)
            self.assertEqual(cut_num, ["A0001", "A0002"])
            self.assertEqual(cut_length_second, ["1", "2"])
            self.assertEqual(cut_length_frame, ["15", "0"])
            self.assertEqual(cut_status, ["OK", "NG"])
            self.assertEqual(cut_take, ["Take1", "Take2"])
            self.assertEqual(cut_staff, ["Staff A", "Staff B"])
        finally:
            os.unlink(csv_path)

    def test_get_media_file_info(self):
        """get_media_file_info関数のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 空ディレクトリのケース
            file_name, updated_dt = get_media_file_info(temp_dir)
            self.assertEqual(file_name, "No File")
            self.assertEqual(updated_dt.year, 1970)

            # ファイルがある場合
            test_file = os.path.join(temp_dir, "test.mp4")
            with open(test_file, 'w') as f:
                f.write("dummy")
            
            file_name, updated_dt = get_media_file_info(temp_dir)
            self.assertEqual(file_name, "test.mp4")
            self.assertGreater(updated_dt.year, 1970)

    def test_add_caption_to_frame(self):
        """add_caption_to_frame関数のテスト"""
        frame = create_blank_frame(self.width, self.height, self.padding)
        resolution = (self.width, self.height)
        project_name = "Test Project"
        text_ts_info = ["1:00 + 15"]
        total_frame_number = 30
        text_cut_num = ["A0001"]
        text_cut_take = ["Take1"]
        cut_status = ["OK"]
        cut_staff = ["Staff A"]
        cut_filedate = "20250123"
        local_frame_number = 0
        video_index = 0

        result = add_caption_to_frame(
            frame, resolution, self.fps, project_name,
            text_ts_info, total_frame_number, text_cut_num,
            text_cut_take, cut_status, cut_staff,
            cut_filedate, local_frame_number, video_index
        )

        # キャプションが追加されたことを確認
        self.assertFalse(np.all(result == 0))

        # Noneの値を含むケース
        cut_status = [None]
        cut_staff = [None]
        result = add_caption_to_frame(
            frame, resolution, self.fps, project_name,
            text_ts_info, total_frame_number, text_cut_num,
            text_cut_take, cut_status, cut_staff,
            'No File', local_frame_number, video_index
        )
        self.assertFalse(np.all(result == 0))

    def test_merge_videos_with_frame_numbers_empty_directory(self):
        """merge_videos_with_frame_numbers関数の空ディレクトリケースのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # プロジェクト情報CSVの作成
            project_csv_path = os.path.join(temp_dir, "project_info.csv")
            with open(project_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Project Name", "Width", "Height", "FPS"])
                writer.writerow(["Test Project", "1920", "1080", "30"])

            # カット情報CSVの作成
            cut_csv_path = os.path.join(temp_dir, "cut_info.csv")
            with open(cut_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Cut Number", "Seconds", "Frames", "Status", "Take", "Staff"])
                writer.writerow(["A0001", "1", "0", "OK", "Take1", "Staff A"])

            # 出力ファイルパス
            output_path = os.path.join(temp_dir, "output.mp4")

            # videosディレクトリの作成
            os.makedirs(os.path.join(temp_dir, "videos"))

            # 関数の実行
            merge_videos_with_frame_numbers(
                temp_dir,
                project_csv_path,
                cut_csv_path,
                output_path,
                self.padding
            )

            # 出力ファイルが作成されたことを確認
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)

    def test_read_project_info_error(self):
        """read_project_info関数のエラーケースのテスト"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Project Name", "Width", "Height", "FPS"])
            csv_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                read_project_info(csv_path)
            self.assertEqual(str(context.exception), "Project info not found in CSV")
        finally:
            os.unlink(csv_path)

    def test_process_media_file_image(self):
        """process_media_file関数の画像処理テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の画像を作成
            img_path = os.path.join(temp_dir, "test.png")
            img = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.imwrite(img_path, img)

            frames, frame_count = process_media_file(
                img_path, 1920, 1080, 100, 30,
                "Test Project", ["1:00 + 15"], 0,
                ["A0001"], ["Take1"], ["OK"],
                ["Staff A"], "20250123", 0,
                duration=30
            )

            self.assertEqual(len(frames), 30)
            self.assertEqual(frame_count, 30)

    def test_process_media_file_image_no_duration(self):
        """process_media_file関数の画像処理エラーケースのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            img_path = os.path.join(temp_dir, "test.png")
            img = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.imwrite(img_path, img)

            with self.assertRaises(ValueError) as context:
                process_media_file(
                    img_path, 1920, 1080, 100, 30,
                    "Test Project", ["1:00 + 15"], 0,
                    ["A0001"], ["Take1"], ["OK"],
                    ["Staff A"], "20250123", 0
                )
            self.assertEqual(str(context.exception), "Duration is required for image files")

    def test_merge_videos_with_frame_numbers_with_files(self):
        """merge_videos_with_frame_numbers関数のファイルありケースのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # プロジェクト情報CSVの作成
            project_csv_path = os.path.join(temp_dir, "project_info.csv")
            with open(project_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Project Name", "Width", "Height", "FPS"])
                writer.writerow(["Test Project", "1920", "1080", "30"])

            # カット情報CSVの作成
            cut_csv_path = os.path.join(temp_dir, "cut_info.csv")
            with open(cut_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Cut Number", "Seconds", "Frames", "Status", "Take", "Staff"])
                writer.writerow(["A0001", "1", "0", "OK", "Take1", "Staff A"])

            # テスト用の動画ディレクトリとファイルを作成
            videos_dir = os.path.join(temp_dir, "videos", "A0001")
            os.makedirs(videos_dir)
            img_path = os.path.join(videos_dir, "test.png")
            img = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.imwrite(img_path, img)

            # 出力ファイルパス
            output_path = os.path.join(temp_dir, "output.mp4")

            # 関数の実行
            merge_videos_with_frame_numbers(
                temp_dir,
                project_csv_path,
                cut_csv_path,
                output_path,
                100
            )

            # 出力ファイルが作成されたことを確認
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)

    def test_process_media_file_video(self):
        """process_media_file関数の動画処理テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # テスト用の動画を作成
            video_path = os.path.join(temp_dir, "test.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_path, fourcc, 30, (1280, 720))
            
            # 3フレームの動画を作成
            for _ in range(3):
                frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                out.write(frame)
            out.release()

            frames, frame_count = process_media_file(
                video_path, 1920, 1080, 100, 30,
                "Test Project", ["1:00 + 15"], 0,
                ["A0001"], ["Take1"], ["OK"],
                ["Staff A"], "20250123", 0
            )

            self.assertEqual(len(frames), 3)
            self.assertEqual(frame_count, 3)

    def test_merge_videos_with_frame_numbers_empty_directory_with_duration(self):
        """merge_videos_with_frame_numbers関数の空ディレクトリ処理テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # プロジェクト情報CSVの作成
            project_csv_path = os.path.join(temp_dir, "project_info.csv")
            with open(project_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Project Name", "Width", "Height", "FPS"])
                writer.writerow(["Test Project", "1920", "1080", "30"])

            # カット情報CSVの作成
            cut_csv_path = os.path.join(temp_dir, "cut_info.csv")
            with open(cut_csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Cut Number", "Seconds", "Frames", "Status", "Take", "Staff"])
                writer.writerow(["A0001", "1", "0", "OK", "Take1", "Staff A"])

            # 空のディレクトリを作成
            videos_dir = os.path.join(temp_dir, "videos", "A0001")
            os.makedirs(videos_dir)

            # 出力ファイルパス
            output_path = os.path.join(temp_dir, "output.mp4")

            # 関数の実行
            merge_videos_with_frame_numbers(
                temp_dir,
                project_csv_path,
                cut_csv_path,
                output_path,
                100
            )

            # 出力ファイルが作成されたことを確認
            self.assertTrue(os.path.exists(output_path))
            self.assertTrue(os.path.getsize(output_path) > 0)

if __name__ == '__main__':
    unittest.main()