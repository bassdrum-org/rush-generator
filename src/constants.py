from enum import Enum
import cv2

# テキストアンカーポイントの定義
class HorizontalAnchor(Enum):
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'

class VerticalAnchor(Enum):
    TOP = 'top'
    CENTER = 'center'
    BOTTOM = 'bottom'

# フォント設定の定数
class FontConstants:
    DEFAULT_FONT = cv2.FONT_HERSHEY_SIMPLEX
    DEFAULT_THICKNESS = 2
    DEFAULT_COLOR = (255, 255, 255)  # 白色 (B,G,R)
    BLACK_COLOR = (0, 0, 0)  # 黒色 (B,G,R)

# フォントスケールの定数
class FontScale:
    SMALL = 0.75
    MEDIUM = 1.0
    LARGE = 1.5
    EXTRA_LARGE = 2.0

# フレーム関連の定数
class FrameConstants:
    DEFAULT_BACKGROUND_COLOR = (0, 0, 0)  # 黒色 (B,G,R)
    FRAME_FORMAT = cv2.CV_8UC3  # 8-bit、unsigned、3チャンネル

# メディアファイル関連の定数
class MediaConstants:
    # 対応する画像ファイル拡張子
    IMAGE_EXTENSIONS = {'.jpg', '.png', '.jpeg'}
    # 対応する動画ファイル拡張子
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov'}
    # 動画出力設定
    VIDEO_CODEC = 'mp4v'
    # 共通テキスト
    NO_FILE_TEXT = 'No File'
