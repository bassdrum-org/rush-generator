import unittest
import cv2
import numpy as np
from rush_generator import (
    drawText,
    create_blank_frame,
    resize_and_add_padding,
    add_caption_to_frame,
    merge_videos_with_frame_numbers
)

class TestRushGenerator(unittest.TestCase):
    def setUp(self):
        # テストで使用する共通の値を設定
        self.width = 1920
        self.height = 1080
        self.padding = 100
        self.fps = 30

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

    def test_drawText(self):
        """drawText関数のテスト"""
        frame = create_blank_frame(self.width, self.height, self.padding)
        test_text = "Test Text"
        
        # 左上配置のテスト
        drawText('left', 'top', frame, test_text, (50, 50), 1.0)
        # テキストが描画されたことを確認（完全なテキスト検証は難しいため、
        # フレームが変更されたことを確認）
        self.assertFalse(np.all(frame == 0))

        # 中央配置のテスト
        frame = create_blank_frame(self.width, self.height, self.padding)
        drawText('center', 'center', frame, test_text, (self.width//2, self.height//2), 1.0)
        self.assertFalse(np.all(frame == 0))

    def test_resize_and_add_padding(self):
        """resize_and_add_padding関数のテスト"""
        # テスト用の入力フレーム作成
        input_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        input_frame[:] = (255, 255, 255)  # 白色フレーム

        # リサイズとパディング処理
        target_resolution = (1920, 1080)
        result = resize_and_add_padding(input_frame, target_resolution, self.padding)

        # 出力サイズの検証
        expected_height = target_resolution[1] + 2 * self.padding
        self.assertEqual(result.shape, (expected_height, target_resolution[0], 3))

        # パディング部分が黒であることを確認
        self.assertTrue(np.all(result[:self.padding] == 0))  # 上部パディング
        self.assertTrue(np.all(result[-self.padding:] == 0))  # 下部パディング

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

    def test_merge_videos_with_frame_numbers_empty_directory(self):
        """merge_videos_with_frame_numbers関数の空ディレクトリケースのテスト"""
        import os
        import tempfile
        import csv

        # テスト用の一時ディレクトリとファイルを作成
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

if __name__ == '__main__':
    unittest.main()