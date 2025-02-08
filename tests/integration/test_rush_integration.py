import unittest
import cv2
import os
import shutil
import numpy as np
from pathlib import Path

class TestRushIntegration(unittest.TestCase):
    def setUp(self):
        """テストの前準備"""
        self.width = 1920
        self.height = 1080
        self.fps = 24
        self.padding = 100
        
        # テスト用のディレクトリ構造を作成
        self.test_dir = Path(os.path.dirname(__file__)) / 'test_data'
        self.videos_dir = self.test_dir / 'videos'
        self.out_dir = self.test_dir / 'out'
        
        # テストディレクトリをクリーンな状態で作成
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)
        self.videos_dir.mkdir()
        self.out_dir.mkdir()
        
        self.output_video_path = str(self.out_dir / 'rush_test.mp4')
        self.out = cv2.VideoWriter(
            self.output_video_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.fps,
            (self.width, self.height + (self.padding*2))
        )

    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.out.release()
        cv2.destroyAllWindows()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def create_blank_frame(self, _width, _height, _padding, color=(0, 0, 0)):
        """黒いフレームを作成する関数(背景色指定可能)"""
        blank_height = _height + (2 * _padding)
        blank_frame = cv2.UMat(blank_height, _width, cv2.CV_8UC3).get()
        blank_frame[:, :] = color  # フレーム全体に背景色を設定
        return blank_frame

    def resize_and_add_padding(self, frame, target_resolution, padding, color=(0, 0, 0)):
        """フレームをリサイズしてパディングを追加する関数"""
        resized_frame = cv2.resize(frame, target_resolution)
        padded_height = target_resolution[1] + 2 * padding
        padded_frame = self.create_blank_frame(
            target_resolution[0],
            target_resolution[1],
            padding,
            color
        )
        padded_frame[padding:padding + target_resolution[1], :, :] = resized_frame
        return padded_frame

    def test_video_processing(self):
        """動画処理の統合テスト"""
        # テスト用の動画ディレクトリを作成
        test_video_dir = self.videos_dir / 'test001'
        test_video_dir.mkdir()

        # テスト用の画像を作成
        test_image_path = str(test_video_dir / 'test.png')
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.imwrite(test_image_path, test_frame)

        # ビデオ処理のテスト
        dirs = sorted(os.listdir(str(self.videos_dir)))
        videoindex = 0
        
        for dir in dirs:
            dir_path = os.path.join(str(self.videos_dir), dir)
            files = sorted(os.listdir(dir_path))
            
            if len(files) != 0:
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.jpg', '.png', '.jpeg']:
                        img = cv2.imread(os.path.join(dir_path, file))
                        duration = int(5) * self.fps
                        for _ in range(duration):
                            self.out.write(self.resize_and_add_padding(
                                img,
                                (self.width, self.height),
                                self.padding
                            ))
            else:
                # 空のディレクトリの場合
                duration = int(5) * self.fps
                for _ in range(duration):
                    blank_frame = self.create_blank_frame(
                        self.width,
                        self.height,
                        self.padding,
                        color=(0, 0, 0)
                    )
                    self.out.write(blank_frame)
            
            videoindex += 1

        # 出力ファイルが正しく作成されたことを確認
        self.assertTrue(os.path.exists(self.output_video_path))
        self.assertTrue(os.path.getsize(self.output_video_path) > 0)

if __name__ == '__main__':
    unittest.main()