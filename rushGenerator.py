import cv2
import os
import glob
import datetime
import csv


#文字書き込み関数 
def drawText(_anchorX,_anchorY,_frame,_text,_position,_font_scale):
    #文字のスタイル
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_color = (255, 255, 255)  # 白
    thickness = 5
    size= cv2.getTextSize(_text,font,_font_scale,thickness)[0]
    pos_x = _position[0]
    pos_y = _position[1]
    if _anchorX == 'left':
        offsetX = 0
    elif _anchorX == 'center':
        offsetX = -(size[0] / 2)
    elif _anchorX == 'right':
        offsetX = -size[0]

    if _anchorY == 'top':
        offsetY = 0
    elif _anchorY == 'center':
        offsetY = -(size[1] / 2)
    elif _anchorY == 'bottom':
        offsetY = -size[1]

    pos_x += offsetX
    pos_y += offsetY
    pos = [int(pos_x), int(pos_y)]
    cv2.putText(_frame, _text,pos, font, _font_scale, font_color)
    
# 黒いフレームを作成する関数（背景色指定可能）
def create_blank_frame(_width, _height, _padding, color=(0, 0, 0)):
    blank_height = _height + (2 * _padding)
    blank_frame = cv2.UMat(blank_height, _width, cv2.CV_8UC3).get()
    blank_frame[:, :] = color  # フレーム全体に背景色を設定
    # print(blank_height)
    return blank_frame


#
def resize_and_add_padding(frame, target_resolution, padding, color=(0, 0, 0)):
    # フレームを指定の解像度にリサイズ
    resized_frame = cv2.resize(frame, target_resolution)

    # 黒い背景フレームを作成
    padded_height = target_resolution[1] + 2 * padding
    # print(target_resolution[1] + 2 * padding)
    padded_frame = create_blank_frame(target_resolution[0], target_resolution[1], padding, color)

    # リサイズしたフレームを背景フレームの中央に配置
    padded_frame[padding:padding + target_resolution[1], :, :] = resized_frame
    return padded_frame

#フレームを計算して字幕を追加する関数
def add_caption_to_frame(_frame,_resolution,_fps,_project_name,_text_ts_info,_total_frame_number,_text_cut_num,_text_cut_take,_cut_status,_cut_staff,_cut_filedate,_local_frame_number,_video_index):
    _width = _resolution[0]
    _height = _resolution[1]
    # 時間、フレームの計算
    total_tc_hours = _total_frame_number // (_fps * 3600)
    total_tc_minutes = (_total_frame_number % (_fps * 3600)) // (_fps * 60)
    total_tc_seconds = (_total_frame_number % (_fps * 60)) // _fps
    total_tc_frames = (_total_frame_number % _fps) + 1  
    total_text_tc = f"{total_tc_hours:02}:{total_tc_minutes:02}:{total_tc_seconds:02}:{total_tc_frames:02}"


    tc_hours = _local_frame_number // (_fps * 3600)
    tc_minutes = (_local_frame_number % (_fps * 3600)) // (_fps * 60)
    tc_seconds = (_local_frame_number % (_fps * 60)) // _fps
    tc_frames = (_local_frame_number % _fps) + 1  
    text_tc = f"TC {tc_hours:02}:{tc_minutes:02}:{tc_seconds:02}:{tc_frames:02}"


    ts_seconds = _local_frame_number // _fps
    ts_frames = (_local_frame_number % _fps) + 1
    text_ts = f"TS ({ts_seconds}:{ts_frames:02})"
    # フレームに字幕を追加
    #上部情報
    drawText('left','center',_frame,_project_name,(50,50),2)
    drawText('left','center',_frame,_text_ts_info[_video_index],(50,75),0.75)

    drawText('left','center',_frame,_text_cut_num[_video_index],(200,50),2)
    drawText('left','center',_frame,_text_cut_take[_video_index],(300,50),1)
            
    if _cut_status[_video_index] != None:
        drawText('left','center',_frame,_cut_status[_video_index],(200,100),0.75)
    else:
        drawText('left','center',_frame,'NoFile',(200,100),0.75)
            
    drawText('center','center',_frame,total_text_tc,(_width/2,50),2)
            
    if _cut_staff[_video_index] != None:
        drawText('left','center',_frame,_cut_staff[_video_index],(1600,50),0.75)
    else:
        drawText('left','center',_frame,'NoFile',(1600,50),0.75)
            
    if _cut_filedate != 'NoFile':
        drawText('left','center',_frame,_cut_filedate,(1600,100),0.5)
    else:
        drawText('left','center',_frame,'NoFile',(1600,100),0.5)

            

    text_local_frame = f"{_local_frame_number:04}"
    text_cut_frameinfo = text_tc + " - " + text_ts + " - " + text_local_frame
    
    drawText('center','center',_frame,text_cut_frameinfo,(_width/2,_height/2),2)
    return _frame

#メインの動画書き出し関数
def merge_videos_with_frame_numbers(_current_path,_csv_path, output_path, _padding):
    text_cut_length_frame =[]
    text_cut_length_second =[]
    text_cut_ts_info = []
    text_cut_num = []
    text_cut_status = []
    text_cut_take = []
    text_cut_staff = []
    text_cut_filedate = []
    #CSVファイルの読み込み
    with open(_csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 最初の行（ヘッダー）をスキップ
        for line_number,row in enumerate(reader, start=0):
            text_cut_num.append(row[4])
            text_cut_length_second.append(row[5])
            text_cut_length_frame.append(row[6])
            text_cut_ts_info.append(f"{row[5]} + {row[6]}")
            text_cut_status.append(row[7])
            text_cut_take.append(row[8])
            text_cut_staff.append(row[9])
            if line_number == 0:
                text_project_name = row[0]
                width = int(row[1])
                height = int(row[2])
                fps = int(row[3])
        print('SettingImported! size = (' + str(width) + ',' + str(height) + ') fps = ' + str(fps) )
    # 出力動画を設定
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, int(fourcc), fps, (width, height + (_padding*2)))
  
    # print(height + _padding*2)
    if not out.isOpened():
        print("VideoWriterを開けませんでした。コーデックやパスを見直してください。")

    #素材ディレクトリごとに処理する
    total_frame_number = 0
    video_index = 0
    
    assetsPath = _current_path + '/videos/'
    dirs = sorted(os.listdir(assetsPath))
    for dir in dirs:
        
        dirPath = os.path.join(assetsPath , dir)
        files = sorted(os.listdir(dirPath))
        if len(os.listdir(dirPath)) != 0:
            print('here file')
            for file in files:
                #ファイルの更新日時
                if os.listdir(dirPath):
                    updated_time = os.path.getmtime(dirPath + '/' + file)
                    updated_dt = datetime.datetime.fromtimestamp(updated_time)
                else:
                    updated_dt = datetime.datetime(1970, 1, 1)  # デフォルト日時
                text_cut_filedate =updated_dt.strftime('%Y%m%d')

                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.png', '.jpeg']:
                    print('StartProcess>>cut_' + str(video_index) + ' :image') 
                    #画像ファイルの場合
                    img = cv2.imread(dirPath + '/' + file)
                    print('loaded ' + file)
                    duration =  (int(text_cut_length_second[video_index]) * fps) + int(text_cut_length_frame[video_index])
                    local_frame_number = 0
                    for _ in range(duration):
                        resize_img_frame = resize_and_add_padding(img, (width,height), _padding)
                        add_caption_img_frame = add_caption_to_frame(resize_img_frame,(width,height),fps,text_project_name,text_cut_ts_info,total_frame_number,text_cut_num,text_cut_take,text_cut_status,text_cut_staff,text_cut_filedate,local_frame_number,video_index)
                        out.write(add_caption_img_frame)
                        total_frame_number += 1
                        local_frame_number+=1
                        continue
                    print('EndProcess')
                elif ext in ['.mp4', '.avi', '.mov']:
                    print('StartProcess>>cut_' + str(video_index) + ' :video') 
                    video = cv2.VideoCapture(dirPath + '/' + file)
                    print('loaded ' + file)
                    if video.isOpened():
                        #動画ファイルの場合 
                        local_frame_number = 0
                        while video.isOpened():
                            ret, frame = video.read()
                            if not ret:
                                break
                            resize_frame = resize_and_add_padding(frame,(width,height), _padding)
                            add_caption_frame = add_caption_to_frame(resize_frame,(width,height),fps,text_project_name,text_cut_ts_info,total_frame_number,text_cut_num,text_cut_take,text_cut_status,text_cut_staff,text_cut_filedate,local_frame_number,video_index)
                            out.write(add_caption_frame)
                            total_frame_number += 1
                            local_frame_number += 1
                        video.release()
                    print('EndProcess')    
        else:
            #なにもなかった場合
            print('StartProcess>>cut_' + str(video_index) + ' :blank') 
            text_cut_filedate ='NoFile'
            duration =  (int(text_cut_length_second[video_index]) * fps) + int(text_cut_length_frame[video_index])
            local_frame_number = 0
            for _ in range(duration):
                blank_frame = create_blank_frame(width, height, _padding, color=(0, 0, 0))
                add_caption_blank_frame = add_caption_to_frame(blank_frame, (width, height), fps, text_project_name,text_cut_ts_info, total_frame_number, text_cut_num,text_cut_take, text_cut_status, text_cut_staff,text_cut_filedate, local_frame_number, video_index)
                out.write(add_caption_blank_frame)
                total_frame_number += 1
                local_frame_number += 1
            print('EndProcess')
        video_index += 1

    out.release()
    cv2.destroyAllWindows()
    print('Done!')






#以下出力実行------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
current = os.path.dirname(__file__)#現在のファイルのパス
#csvのパス
csv_path = current + "/RushInfo.csv"

# 時刻を取得してアウトプットファイル名に
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)
d = now.strftime('%Y%m%d%H%M')
output_video_path = current + '/out/rush_' + d + '.mp4'
merge_videos_with_frame_numbers(current,csv_path,output_video_path,100)
