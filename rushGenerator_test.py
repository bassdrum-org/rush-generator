import cv2
import os

width, height = 1920, 1080
fps = 24
current = os.path.dirname(__file__)
output_video_path = current + '/out/rush_test.mp4'
print(output_video_path)
padding = 100
out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height + (padding*2)))
videoindex = 0
# 黒いフレームを作成する関数（背景色指定可能）
def create_blank_frame(_width, _height, _padding, color=(0, 0, 0)):
    blank_height = _height + (2 * _padding)
    blank_frame = cv2.UMat(blank_height, _width, cv2.CV_8UC3).get()
    blank_frame[:, :] = color  # フレーム全体に背景色を設定
    # print(blank_height)
    return blank_frame


# 修正版：resize_and_add_padding関数
def resize_and_add_padding(frame, target_resolution, padding, color=(0, 0, 0)):
    # フレームを指定の解像度にリサイズ
    resized_frame = cv2.resize(frame, target_resolution)

    # 黒い背景フレームを作成
    padded_height = target_resolution[1] + 2 * padding
    padded_frame = create_blank_frame(target_resolution[0], target_resolution[1], padding, color)

    # リサイズしたフレームを背景フレームの中央に配置
    padded_frame[padding:padding + target_resolution[1], :, :] = resized_frame
    return padded_frame


if not out.isOpened():
    print("VideoWriterが開けませんでした。コーデックかパスを確認してください。")

assetsPath = current + '/videos/'
dirs = sorted(os.listdir(assetsPath))
videoindex = 0
for dir in dirs:
        
    dirPath = os.path.join(assetsPath , dir)
    files = sorted(os.listdir(dirPath))
    if len(os.listdir(dirPath)) != 0:
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.jpg', '.png', '.jpeg']:
                print(str(videoindex) + ' :img') 
                #画像ファイルの場合
                img = cv2.imread(dirPath + '/' + file)
                duration =  (int(5) * fps)
                local_frame_number = 0
                for _ in range(duration):
                    out.write(resize_and_add_padding(img,(width,height),padding))
                    local_frame_number+=1
                    continue
            elif ext in ['.mp4', '.avi', '.mov']:
                print(str(videoindex) + ' :video') 
                video = cv2.VideoCapture(dirPath + '/' + file)
                if video.isOpened():
                        #動画ファイルの場合 
                    local_frame_number = 0
                    while video.isOpened():
                        ret, frame = video.read()
                        if not ret:
                            break
                        resize_frame = resize_and_add_padding(frame,(width,height), padding)
                        out.write(resize_frame)
                        local_frame_number += 1
                    video.release()    
    else:
        #なにもなかった場合
        print(str(videoindex) + ' :blank') 
        duration =  (int(5) * fps)
        local_frame_number = 0
        for _ in range(duration):
                blank_frame = create_blank_frame(width, height, padding, color=(0, 0, 0))
                out.write(blank_frame)
                local_frame_number += 1
    videoindex += 1




out.release()
cv2.destroyAllWindows()
print('おわり')