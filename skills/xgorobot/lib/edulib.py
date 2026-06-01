'''
xgo图形化python库  edu库
'''
import cv2
import numpy as np
import math
import os,sys,time,json,base64
import spidev as SPI
import xgoscreen.LCD_2inch as LCD_2inch
import RPi.GPIO as GPIO
from PIL import Image,ImageDraw,ImageFont
import json
import threading
from picamera2 import Picamera2
from libcamera import Transform
# from xgolib import XGO
# from keras.preprocessing import image
# import _thread  使用_thread会报错，坑！


__versinon__ = '1.3.6'
__last_modified__ = '2023/9/5'

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

camera_still=False
import subprocess

'''
人脸检测
'''
def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)),8)  
    return frameOpencvDnn, bboxes

'''
手势识别函数
'''
def hand_pos(angle):
    """
    手势识别函数 - 优化版本
    根据手指角度判断手势，增加容错性和准确性
    """
    if not angle or len(angle) != 5:
        return None
        
    pos = None
    # 手指角度阈值优化 - 增加容错范围
    thumb_threshold = 55   # 大拇指阈值调整
    finger_threshold = 55  # 其他手指阈值调整
    
    # 手指角度
    f1 = angle[0]  # 大拇指角度
    f2 = angle[1]  # 食指角度  
    f3 = angle[2]  # 中指角度
    f4 = angle[3]  # 无名指角度
    f5 = angle[4]  # 小拇指角度
    
    # 手指状态判断（优化后的阈值）
    thumb_up = f1 < thumb_threshold
    index_up = f2 < finger_threshold
    middle_up = f3 < finger_threshold  
    ring_up = f4 < finger_threshold
    pinky_up = f5 < finger_threshold
    
    thumb_down = f1 >= thumb_threshold
    index_down = f2 >= finger_threshold
    middle_down = f3 >= finger_threshold
    ring_down = f4 >= finger_threshold  
    pinky_down = f5 >= finger_threshold
    
    # 手势识别逻辑优化（按优先级排序）
    
    # 1. 五指张开 - 最容易识别
    if thumb_up and index_up and middle_up and ring_up and pinky_up:
        pos = '5'
    
    # 2. 拳头 - 全部手指弯曲
    elif thumb_down and index_down and middle_down and ring_down and pinky_down:
        pos = 'Stone'
    
    # 3. 特殊手势 - 按特征优先级
    elif thumb_up and index_down and middle_down and ring_down and pinky_down:
        pos = 'Good'  # 站起大拇指
    
    elif thumb_up and index_down and middle_up and ring_up and pinky_down:
        pos = 'Rock'  # 摇滚手势
    
    elif thumb_up and index_down and middle_up and ring_up and pinky_up:
        pos = 'Ok'    # OK手势（近似）
    
    # 4. 数字手势 - 按伸出手指数量
    elif thumb_down and index_up and middle_down and ring_down and pinky_down:
        pos = '1'     # 一根手指
    
    elif thumb_down and index_up and middle_up and ring_down and pinky_down:
        pos = '2'     # 两根手指
    
    elif thumb_down and index_up and middle_up and ring_up and pinky_down:
        pos = '3'     # 三根手指
    
    elif thumb_down and index_up and middle_up and ring_up and pinky_up:
        pos = '4'     # 四根手指
    
    # 5. 有歧义的情况 - 添加容错判断
    # 如果上述所有条件都不符合，尝试放宽条件
    elif not pos:
        # 放宽阈值重新判断
        relaxed_threshold = 70
        
        # 重新计算手指状态
        t_up = f1 < relaxed_threshold
        i_up = f2 < relaxed_threshold
        m_up = f3 < relaxed_threshold
        r_up = f4 < relaxed_threshold  
        p_up = f5 < relaxed_threshold
        
        if t_up and not i_up and not m_up and not r_up and not p_up:
            pos = 'Good'
        elif not t_up and i_up and not m_up and not r_up and not p_up:
            pos = '1'
        elif not t_up and i_up and m_up and not r_up and not p_up:
            pos = '2'
        elif t_up and i_up and m_up and r_up and p_up:
            pos = '5'
        elif not t_up and not i_up and not m_up and not r_up and not p_up:
            pos = 'Stone'
    
    return pos
def color(value):
  digit = list(map(str, range(10))) + list("ABCDEF")
  value = value.upper()
  if isinstance(value, tuple):
    string = '#'
    for i in value:
      a1 = i // 16
      a2 = i % 16
      string += digit[a1] + digit[a2]
    return string
  elif isinstance(value, str):
    a1 = digit.index(value[1]) * 16 + digit.index(value[2])
    a2 = digit.index(value[3]) * 16 + digit.index(value[4])
    a3 = digit.index(value[5]) * 16 + digit.index(value[6])
    return (a3, a2, a1)



class XGOEDU():
    def __init__(self, display_init=True):
        self.display_enabled = display_init
        if display_init:
            self.display = LCD_2inch.LCD_2inch()
            self.display.Init()
            self.display.clear()
            self.splash = Image.new("RGB",(320,240),"black")
            self.display.ShowImage(self.splash)
            self.draw = ImageDraw.Draw(self.splash)
            self.font = ImageFont.truetype("/home/pi/model/msyh.ttc",15)
        else:
            self.display = None
            self.splash = None
            self.draw = None
            self.font = None
        self.key1=17
        self.key2=22
        self.key3=23
        self.key4=24
        self.cap=None
        self.hand=None
        self.yolo=None
        self.face=None
        self.face_classifier=None
        self.classifier=None
        self.agesexmark=None
        self.camera_still=False
        self.picam2 = None
        self.camera_config = None
        os.system("sudo pinctrl set 24 ip")
        os.system("sudo pinctrl set 23 ip")
        os.system("sudo pinctrl set 17 ip")
        os.system("sudo pinctrl set 22 ip")
        
    def open_camera(self):
        if self.picam2 is None:
            self.picam2 = Picamera2()
            self.camera_config = self.picam2.create_preview_configuration(
                main={"size": (320, 240), "format": "RGB888"},  # 强制指定RGB格式
                transform=Transform(hflip=1, vflip=0)
            )
            self.picam2.configure(self.camera_config)
            self.picam2.start()
            time.sleep(1)





    #绘画直线
    '''
    x1,y1为初始点坐标,x2,y2为终止点坐标
    '''
    def lcd_line(self,x1,y1,x2,y2,color="WHITE",width=2):
        self.draw.line([(x1,y1),(x2,y2)],fill=color ,width=width)
        self.display.ShowImage(self.splash)
    #绘画圆
    '''
    x1,y1,x2,y2为定义给定边框的两个点,angle0为初始角度,angle1为终止角度
    '''
    def lcd_circle(self,x1,y1,x2,y2,angle0,angle1,color="WHITE",width=2):
        self.draw.arc((x1,y1,x2,y2),angle0,angle1,fill=color ,width=width)
        self.display.ShowImage(self.splash)

    #绘画圆弧
    '''
    x1,y1,x2,y2为定义边界框的两个点
    angle0为初始角度，三点钟方向为起始点，顺时针增加
    angle1为终止角度
    color为圆弧颜色，默认为白色
    width为圆弧宽度，默认为2
    '''
    def lcd_arc(self,x1,y1,x2,y2,angle0,angle1,color=(255,255,255),width=2):
        self.draw.arc((x1,y1,x2,y2),angle0,angle1,fill=color,width=width)
        self.display.ShowImage(self.splash)

    #绘画圆:  根据圆形点和半径画圆
    '''
    center_x, center_y 圆心点坐标
    radius 圆半径长度 mm
    
    '''
    def lcd_round(self,center_x, center_y, radius, color, width=2):
        # Calculate the bounding box for the circle
        x1 = center_x - radius
        y1 = center_y - radius
        x2 = center_x + radius
        y2 = center_y + radius
    
        # Call lcd_circle() function to draw the circle
        self.lcd_circle(x1, y1, x2, y2, 0, 360, color=color, width=width)
  

    
    #绘画矩形
    '''
    x1,y1为初始点坐标,x2,y2为对角线终止点坐标
    '''
    def lcd_rectangle(self,x1,y1,x2,y2,fill=None,outline="WHITE",width=2):
        self.draw.rectangle((x1,y1,x2,y2),fill=fill,outline=outline,width=width)
        self.display.ShowImage(self.splash)
    #清除屏幕
    def lcd_clear(self):
        self.splash = Image.new("RGB",(320,240),"black")
        self.draw = ImageDraw.Draw(self.splash)
        self.display.ShowImage(self.splash)
    #显示图片
    '''
    图片的大小为320*240,jpg格式
    '''
    def lcd_picture(self,filename,x=0,y=0):
        path="/home/pi/xgoPictures/"
        image = Image.open(path+filename)
        self.splash.paste(image,(x,y))
        self.display.ShowImage(self.splash)
    #显示文字
    '''
    x1,y1为初始点坐标,content为内容
    '''
    def lcd_text(self,x,y,content,color="WHITE",fontsize=15):
        if fontsize!=15:
            self.font = ImageFont.truetype("/home/pi/model/msyh.ttc",fontsize)
        self.draw.text((x,y),content,fill=color,font=self.font)
        self.display.ShowImage(self.splash)
    #流式显示所有文字
    '''
    x1,y1为初始点坐标,content为内容
    遇到回车符自动换行，遇到边缘换行，一页满了自动清屏，2,2开始继续显示
    '''
    def display_text_on_screen(self, content, color, start_x=2, start_y=2, font_size=20, screen_width=320, screen_height=240):
        # 计算每行可显示字符的数量和行数
        char_width = font_size +1  #// 2
        chars_per_line = screen_width // char_width
        lines = screen_height // char_width
    
        # 拆分内容为逐个字符的列表
        chars = list(content)
     
        # 处理换行符
        line_break_indices = [i for i, char in enumerate(chars) if char == '\n']
    
    
        # 计算总行数和页数
        total_lines = len(chars) // chars_per_line + 1
        total_pages = (total_lines - 1+len(line_break_indices)) // lines + 1
    
        # 清屏
        self.display.clear()
    
        # 逐行显示文字
        current_page = 1
        current_line = 1
        current_char = 0
    
        while current_page <= total_pages or  current_char < len(chars) :
            self.display.clear()
            # 计算当前页要显示的行数
            if current_page < total_pages or  current_char < len(chars) :
                lines_to_display = lines
            else:
                lines_to_display = (total_lines - 1) % lines + 1
    
            current_line = 1
            # 显示当前页的内容
            for line in range(lines_to_display):
                current_x = start_x
                current_y = start_y + current_line * char_width # font_size
                current_line +=1
                if current_line >= lines:
                    break
    
                # 显示当前行的文字
                for _ in range(chars_per_line):
                    # 检查是否所有字符都已显示完毕
                    if current_char >= len(chars):
                        break
    
                    char = chars[current_char]
                    if char == '\n':
                        current_x = start_x
                        current_y = start_y + current_line * char_width # font_size
                        current_line +=1
                       
                        self.lcd_text(current_x, current_y, char, color, font_size)
                        current_char += 1
                        break  # continue
    
                    self.lcd_text(current_x, current_y, char, color, font_size)
                    current_x += char_width
                    current_char += 1
    
                # 检查是否所有字符都已显示完毕
                if current_char >= len(chars):
                    break
    
            # 更新当前页和当前行
            current_page += 1
            current_line += lines_to_display
    
            # 等待显示时间或手动触发翻页
            # 这里可以根据需要添加适当的延时代码或触发翻页的机制
    
        # 如果内容超过一屏幕，则清屏
        # if total_lines > lines:
        if current_page < total_pages:
            self.display.clear()
    
    #key_value
    '''
    a左上按键
    b右上按键
    c左下按键
    d右下按键
    返回值 0未按下,1按下
    '''
    def xgoButton(self, button):
        if button == "d":
            result = subprocess.run(["sudo", "pinctrl", "level", "24"], capture_output=True, text=True).stdout
            if result[0] == "1":
                last_state = True
            else:
                last_state = False
            time.sleep(0.02)
            return not last_state
        elif button == "c":
            result = subprocess.run(["sudo", "pinctrl", "level", "23"], capture_output=True, text=True).stdout
            if result[0] == "1":
                last_state = True
            else:
                last_state = False
            time.sleep(0.02)
            return not last_state
        elif button == "a":
            result = subprocess.run(["sudo", "pinctrl", "level", "17"], capture_output=True, text=True).stdout
            if result[0] == "1":
                last_state = True
            else:
                last_state = False
            time.sleep(0.02)
            return not last_state
        elif button == "b":
            result = subprocess.run(["sudo", "pinctrl", "level", "22"], capture_output=True, text=True).stdout
            if result[0] == "1":
                last_state = True
            else:
                last_state = False
            time.sleep(0.02)
            return not last_state
    #speaker
    '''
    filename 文件名 字符串
    '''
    def xgoSpeaker(self,filename):
        path="/home/pi/xgoMusic/"
        os.system("mplayer"+" "+path+filename)

    def xgoVideoAudio(self,filename):
        path="/home/pi/xgoVideos/"
        time.sleep(0.2)  #音画速度同步了 但是时间轴可能不同步 这里调试一下
        cmd="sudo mplayer "+path+filename+" -novideo"
        os.system(cmd)

    def xgoVideo(self,filename):
        path="/home/pi/xgoVideos/"
        x=threading.Thread(target=self.xgoVideoAudio,args=(filename,))
        x.start()
        global counter
        video=cv2.VideoCapture(path+filename)
        print(path+filename)
        fps = video.get(cv2.CAP_PROP_FPS) 
        print(fps)
        init_time=time.time()
        counter=0
        while True:
            grabbed, dst = video.read()
            try:
                b,g,r = cv2.split(dst)
                dst = cv2.merge((r,g,b))
            except:
                pass
            try:
                imgok = Image.fromarray(dst)
            except:
                break
            self.display.ShowImage(imgok)
            #强制卡帧数 实测帧数不要超过20贞 否则显示跟不上 但是20贞转换经常有问题 所以建议直接15贞
            counter += 1
            ctime=time.time()- init_time
            if ctime != 0:
                qtime=counter/fps-ctime
                #print(qtime)
                if qtime>0:
                    time.sleep(qtime)
            if not grabbed:
                break
        
    #audio_record
    '''
    filename 文件名 字符串
    seconds 录制时间S 字符串
    '''
    def xgoAudioRecord(self,filename="record",seconds=5):
        path="/home/pi/xgoMusic/"
        # 如果文件夹不存在则创建
        if not os.path.exists(path):
            os.makedirs(path)
        command1 = "sudo arecord -d"
        command2 = "-f S32_LE -r 8000 -c 1 -t wav"
        cmd=command1+" "+str(seconds)+" "+command2+" "+path+filename
        print(cmd)
        os.system(cmd)

    def xgoCamera(self,switch):
        global camera_still
        if switch:
            self.open_camera()
            self.camera_still=True
            if self.display_enabled:
                t = threading.Thread(target=self.camera_mode)  
                t.start() 
        else:
            self.camera_still=False
            time.sleep(0.5)
            if self.display_enabled:
                splash = Image.new("RGB",(320,240),"black")
                self.display.ShowImage(splash)

    def camera_mode(self):
        self.camera_still = True
        while self.camera_still:
            # 使用Picamera2捕获帧
            image = self.picam2.capture_array()
            # 转换颜色空间 BGR -> RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # 转换为PIL Image并显示
            imgok = Image.fromarray(image)
            self.display.ShowImage(imgok)
            time.sleep(0.033)  # 约30fps
  #这里的seconds基本上相当于视频的两倍时长
    def xgoVideoRecord(self, filename="record", seconds=5):
        path = "/home/pi/xgoVideos/"
        # 如果文件夹不存在则创建
        if not os.path.exists(path):
            os.makedirs(path)
        self.camera_still = False
        time.sleep(0.6)
        
        if self.picam2 is None:
            self.open_camera()
        
        # 创建视频写入器
        FPS = 10
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_path = path + filename
        video_writer = cv2.VideoWriter(video_path, fourcc, FPS, (320, 240))
        
        start_time = time.time()
        while time.time() - start_time < seconds:
            print('recording...')
            # 捕获帧
            image = self.picam2.capture_array()
            # 写入视频
            video_writer.write(image)
            # 显示预览
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            imgok = Image.fromarray(image)
            self.display.ShowImage(imgok)
        
        print('recording done')
        video_writer.release()

    def xgoTakePhoto(self, filename="photo"):
        path = "/home/pi/xgoPictures/"
        self.camera_still = False
        time.sleep(0.6)
        
        if self.picam2 is None:
            self.open_camera()
        
        # 使用Picamera2捕获图像
        image = self.picam2.capture_array()
        # 保存为JPEG
        cv2.imwrite(path + filename , image)
        
        # 显示预览
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imgok = Image.fromarray(image)
        if self.display_enabled: self.display.ShowImage(imgok)
        print('photo writed!')
        time.sleep(0.7)


    '''
    开启摄像头  A键拍照 B键录像 C键退出
    '''
    def camera(self, filename="camera"):
        import time
        import cv2
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        
        # 1. 初始化配置
        font = ImageFont.truetype("/home/pi/model/msyh.ttc", 20)
        video_fps = 15
        preview_size = (320, 240)
        photo_path = f"/home/pi/xgoPictures/{filename}.jpg"
        video_path = f"/home/pi/xgoVideos/{filename}.mp4"
        
        # 2. 确保之前相机已关闭
        def safe_camera_shutdown():
            if hasattr(self, 'picam2') and self.picam2 is not None:
                try:
                    if hasattr(self.picam2, '_preview'):
                        self.picam2.stop_preview()
                    self.picam2.stop()
                    self.picam2.close()
                except:
                    pass
                finally:
                    self.picam2 = None
        
        safe_camera_shutdown()
        time.sleep(1)  #

        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": preview_size, "format": "RGB888"},
                buffer_count=4)
            self.picam2.configure(config)
            self.picam2.start()
            time.sleep(2)  
            
    
            recording = False
            video_writer = None
            last_button_time = 0
            
            while True:
                current_time = time.time()
                
                try:
                   
                    frame = self.picam2.capture_array("main")
                    if frame is None or frame.size == 0:
                        continue
                        
                    # 6. 标准化图像
                    frame = frame.astype(np.uint8)
                    if len(frame.shape) == 2:
                        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                    else:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                 
                    img = Image.fromarray(frame)
                    draw = ImageDraw.Draw(img)
                    status = "录像中" if recording else "就绪"
                    draw.text((5, 5), f"A:拍照 B:{'停止' if recording else '开始'} C:退出 | {status}", 
                             fill=(255,255,0), font=font)
                    self.display.ShowImage(img)
                    
    
                    if recording and video_writer is not None:
                        video_writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    

                    if current_time - last_button_time > 0.1:
                        if XGOEDU.xgoButton(self, "a"):  # 拍照
                            cv2.imwrite(photo_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                            # 显示拍照反馈
                            feedback = Image.new("RGB", preview_size, (0,0,0))
                            draw = ImageDraw.Draw(feedback)
                            draw.text((50, 100), "照片已保存!", fill=(0,255,0), font=font)
                            self.display.ShowImage(feedback)
                            time.sleep(1)
                            last_button_time = current_time
                            
                        elif XGOEDU.xgoButton(self, "b"):  # 录像控制
                            recording = not recording
                            if recording:
                                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                                video_writer = cv2.VideoWriter(video_path, fourcc, video_fps, preview_size)
                            elif video_writer is not None:
                                video_writer.release()
                                video_writer = None
                                # 显示录像反馈
                                feedback = Image.new("RGB", preview_size, (0,0,0))
                                draw = ImageDraw.Draw(feedback)
                                draw.text((40, 100), "视频已保存!", fill=(0,255,0), font=font)
                                self.display.ShowImage(feedback)
                                time.sleep(1)
                            last_button_time = current_time
                            
                        elif XGOEDU.xgoButton(self, "c"):  
                            break
                            
                except Exception as e:
                    print(f"帧处理异常: {str(e)}")
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"相机初始化失败: {str(e)}")
        finally:
            # 10. 安全释放资源
            try:
                if video_writer is not None:
                    video_writer.release()
            except:
                pass
                
            safe_camera_shutdown()
            XGOEDU.lcd_clear(self)
            print("相机应用已安全退出")
    '''
    骨骼识别
    '''
    def posenetRecognition(self, target="camera"):
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        ges = ''
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        joint_list = [[24,26,28], [23,25,27], [14,12,24], [13,11,23]]  # leg&arm
        
        # 图像采集（关键修改点）
        if target == "camera":
            self.open_camera()
            image = self.picam2.capture_array()  # Picamera2默认输出BGR
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # MediaPipe需要RGB
        else:
            image = np.array(Image.open(target).convert('RGB'))  # 确保RGB格式
    
        with mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as pose:
                
            # 姿势识别（关键修改：删除冗余颜色转换）
            image.flags.writeable = False
            results = pose.process(image)  # 直接使用RGB图像
            
            # 绘制结果
            image.flags.writeable = True
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            # 角度计算
            angellist = []
            if results.pose_landmarks:
                RHL = results.pose_landmarks
                for joint in joint_list:
                    a = np.array([RHL.landmark[joint[0]].x, RHL.landmark[joint[0]].y])
                    b = np.array([RHL.landmark[joint[1]].x, RHL.landmark[joint[1]].y])
                    c = np.array([RHL.landmark[joint[2]].x, RHL.landmark[joint[2]].y])
                    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                    angle = np.abs(radians * 180.0 / np.pi)
                    angellist.append(angle if angle <= 180 else 360-angle)
            
            # 显示处理（关键修改：保持RGB格式）
            image = cv2.flip(image, 1)
            if angellist:
                ges = '|'.join(str(int(a)) for a in angellist[:4])
                cv2.putText(image, ges, (10,220), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                           (255,255,255), 2, cv2.LINE_AA)
            
            imgok = Image.fromarray(image)  # PIL需要RGB格式
            self.display.ShowImage(imgok)
        
        return angellist if angellist else None
    '''
    手势识别
    '''
    def gestureRecognition(self, target="camera"):
        ges = ''
        # 优化手势识别参数，提高检测精度
        if self.hand is None:
            self.hand = hands(1, 2, 0.7, 0.7)  # 提高检测和跟踪置信度
        
        # 图像采集优化
        if target == "camera":
            self.open_camera()
            time.sleep(0.5)  # 给摄像头稳定时间
            # 多帧采集，提高稳定性
            stable_image = None
            for _ in range(3):
                frame = self.picam2.capture_array()
                if stable_image is None:
                    stable_image = frame
                time.sleep(0.1)
            image = cv2.cvtColor(stable_image, cv2.COLOR_BGR2RGB)
        else:
            path = "/home/pi/xgoPictures/" if not target.startswith('/') else ""
            image = np.array(Image.open(path + target).convert('RGB'))
        
        # 图像预处理优化 - 提高识别准确性
        # 1. 降噪处理
        image = cv2.bilateralFilter(image, 9, 75, 75)
        # 2. 对比度增强
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        image = cv2.merge([l, a, b])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2RGB)
        
        # 水平镜像（自拍模式）
        image = cv2.flip(image, 1)
        
        # 手势识别优化 - 多次检测取最稳定结果
        best_data = None
        best_confidence = 0
        
        # 尝试3次检测，选择最佳结果
        for attempt in range(3):
            try:
                # 轻微变换图像角度提高检测率
                if attempt == 1:
                    # 轻微旋转
                    rows, cols = image.shape[:2]
                    M = cv2.getRotationMatrix2D((cols/2, rows/2), 2, 1)
                    test_image = cv2.warpAffine(image, M, (cols, rows))
                elif attempt == 2:
                    # 轻微缩放
                    test_image = cv2.resize(image, None, fx=1.1, fy=1.1)
                    test_image = cv2.resize(test_image, (image.shape[1], image.shape[0]))
                else:
                    test_image = image.copy()
                
                datas = self.hand.run(cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR))
                
                if datas:
                    for data in datas:
                        # 计算手势置信度（基于手部区域大小和关键点质量）
                        rect = data['rect']
                        dlandmark = data['dlandmark']
                        
                        # 手部区域大小合理性检查
                        area = rect[2] * rect[3]
                        if area < 1000 or area > 50000:  # 过小或过大的区域可能不准确
                            continue
                            
                        # 关键点质量检查
                        if len(dlandmark) < 20:  # MediaPipe手部模型有21个关键点
                            continue
                            
                        # 计算手势角度的稳定性
                        hand_angle = data['hand_angle']
                        if not hand_angle or len(hand_angle) != 5:
                            continue
                            
                        # 简单的置信度评分
                        confidence = area / 10000.0  # 基于区域大小
                        confidence += len(dlandmark) / 21.0  # 基于关键点完整性
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_data = data
                            
            except Exception as e:
                continue
        
        # 使用最佳检测结果进行绘制
        if best_data:
            data = best_data
            rect = data['rect']
            right_left = data['right_left']
            center = data['center']
            dlandmark = data['dlandmark']
            hand_angle = data['hand_angle']
            
            # 手势角度后处理 - 平滑化处理
            smoothed_angles = []
            for angle in hand_angle:
                # 角度范围限制和平滑
                if angle < 0:
                    angle = 0
                elif angle > 180:
                    angle = 180
                smoothed_angles.append(angle)
            
            # 绘制手部区域
            cv2.rectangle(image, 
                         (rect[0], rect[1]),
                         (rect[0]+rect[2], rect[1]+rect[3]),
                         (51, 204, 0), 2)  # RGB格式的绿色
            
            # 显示手势结果
            ges = hand_pos(smoothed_angles)
            if ges:  # 只有识别到有效手势才显示
                text_pos = (180, 80) if right_left == 'L' else (50, 80)
                color = (51, 204, 0) if right_left == 'L' else (255, 0, 0)
                cv2.putText(image, ges, text_pos,
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # 显示置信度
                conf_text = f"Conf: {best_confidence:.2f}"
                cv2.putText(image, conf_text, (text_pos[0], text_pos[1] + 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # 绘制关键点（只绘制重要的关键点）
            important_points = [0, 4, 8, 12, 16, 20]  # 指尖和手腕
            for i, point in enumerate(dlandmark):
                if i in important_points:
                    cv2.circle(image, (int(point[0]), int(point[1])),
                              4, (255, 153, 0), -1)  # RGB格式的橙色
                else:
                    cv2.circle(image, (int(point[0]), int(point[1])),
                              2, (255, 204, 153), -1)  # 淡橙色
        
        # 显示结果
        imgok = Image.fromarray(image)  # PIL需要RGB格式
        if self.display is not None:
            self.display.ShowImage(imgok)
        
        return (ges, center) if ges else None
    '''
    yolo
    '''
    def yoloFast(self,target="camera"):
        ret=''
        self.open_camera()
        if self.yolo==None:
            self.yolo = yoloXgo('/home/pi/model/Model.onnx',
            ['person','bicycle','car','motorbike','aeroplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','sofa','pottedplant','bed','diningtable','toilet','tvmonitor','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush'],
            [352,352],0.66)
        if target=="camera":
            self.open_camera()
            image = self.picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 如果需要RGB格式
        else:
            image=np.array(Image.open(target))
        datas = self.yolo.run(image)
        b,g,r = cv2.split(image)
        image = cv2.merge((r,g,b))
        image = cv2.flip(image,1)
        if datas:
            for data in datas:
                XGOEDU.rectangle(self,image,data['xywh'],"#33cc00",2)
                xy= (data['xywh'][0], data['xywh'][1])
                XGOEDU.text(self,image,data['classes'],xy,1,"#ff0000",2)
                value_yolo = data['classes']
                ret=(value_yolo,xy)
        imgok = Image.fromarray(image)
        self.display.ShowImage(imgok)
        if ret=='':
            return None
        else:
            return ret

    '''
    人脸坐标点检测
    '''
    def face_detect(self,target="camera"):
        ret=''
        if self.face==None:
            self.face = face_detection(0.7)
        if target=="camera":
            self.open_camera()
            image = self.picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 如果需要RGB格式    
        else:
            image=np.array(Image.open(target))
        image = cv2.flip(image,1)
        datas = self.face.run(image)
        for data in datas:
            lefteye = str(data['left_eye'])
            righteye = str(data['right_eye'])
            nose = str(data['nose'])
            mouth = str(data['mouth'])
            leftear = str(data['left_ear'])
            rightear = str(data['right_ear'])
            cv2.putText(image,'lefteye',(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)
            cv2.putText(image,lefteye,(100,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)
            cv2.putText(image,'righteye',(10,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
            cv2.putText(image,righteye,(100,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
            cv2.putText(image,'nose',(10,70),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.putText(image,nose,(100,70),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.putText(image,'leftear',(10,90),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2)
            cv2.putText(image,leftear,(100,90),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2)
            cv2.putText(image,'rightear',(10,110),cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,0,200),2)
            cv2.putText(image,rightear,(100,110),cv2.FONT_HERSHEY_SIMPLEX,0.7,(200,0,200),2)
            XGOEDU.rectangle(self,image,data['rect'],"#33cc00",2)
            ret=data['rect']
        imgok = Image.fromarray(image)
        self.display.ShowImage(imgok)
        if ret=='':
            return None
        else:
            return ret

    '''
    情绪识别
    '''
    def emotion(self, target="camera"):
        ret = ''
        if self.classifier == None:
            from keras.models import load_model
            self.face_classifier = cv2.CascadeClassifier('/home/pi/model/haarcascade_frontalface_default.xml')
            self.classifier = load_model('/home/pi/model/EmotionDetectionModel.h5')
        
        class_labels = ['Angry', 'Happy', 'Neutral', 'Sad', 'Surprise']
        
        if target == "camera":
            self.open_camera()
            image = self.picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = np.array(Image.open(target))
        
        labels = []
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)
        label = ''
        
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
            
            if np.sum([roi_gray]) != 0:
                from tensorflow.keras.utils import img_to_array
                roi = roi_gray.astype('float')/255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
    
                preds = self.classifier.predict(roi, verbose=0)[0]
                label = class_labels[preds.argmax()]
                label_position = (x, y)
                ret = (label, (x, y))
            else:
                label = 'No Face Found'
            
            try:
                cv2.putText(image, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            except:
                pass
        
        image = cv2.flip(image, 1)
        imgok = Image.fromarray(image)
        self.display.ShowImage(imgok)
        
        if ret == '':
            return None
        else:
            return ret
    '''
    年纪及性别检测
    '''
    def agesex(self, target="camera"):
        ret = ''
        MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        genderList = ['Male', 'Female']
        padding = 20
        
        if target == "camera":
            self.open_camera()
            image = self.picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = np.array(Image.open(target))
        
        if self.agesexmark == None:
            faceProto = "/home/pi/model/opencv_face_detector.pbtxt"
            faceModel = "/home/pi/model/opencv_face_detector_uint8.pb"
            ageProto = "/home/pi/model/age_deploy.prototxt"
            ageModel = "/home/pi/model/age_net.caffemodel"
            genderProto = "/home/pi/model/gender_deploy.prototxt"
            genderModel = "/home/pi/model/gender_net.caffemodel"
            self.ageNet = cv2.dnn.readNet(ageModel, ageProto)
            self.genderNet = cv2.dnn.readNet(genderModel, genderProto)
            self.faceNet = cv2.dnn.readNet(faceModel, faceProto)
            self.agesexmark = True
    
        image = cv2.flip(image, 1)
        frameFace, bboxes = getFaceBox(self.faceNet, image)
        gender = ''
        age = ''
        
        for bbox in bboxes:
            face = image[max(0, bbox[1]-padding):min(bbox[3]+padding, image.shape[0]-1),
                        max(0, bbox[0]-padding):min(bbox[2]+padding, image.shape[1]-1)]
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            
            self.genderNet.setInput(blob)
            genderPreds = self.genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            
            self.ageNet.setInput(blob)
            agePreds = self.ageNet.forward()
            age = ageList[agePreds[0].argmax()]
            
            label = "{},{}".format(gender, age)
            cv2.putText(frameFace, label, (bbox[0], bbox[1]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
            ret = (gender, age, (bbox[0], bbox[1]))
        
        imgok = Image.fromarray(frameFace)
        self.display.ShowImage(imgok)
        
        if ret == '':
            return None
        else:
            return ret

    
    def rectangle(self,frame,z,colors,size):
        frame=cv2.rectangle(frame,(int(z[0]),int(z[1])),(int(z[0]+z[2]),int(z[1]+z[3])),color(colors),size)
        return frame
        
    def circle(self,frame,xy,rad,colors,tk):
        frame=cv2.circle(frame,xy,rad,color(colors),tk)
        return frame
    
    def text(self,frame,text,xy,font_size,colors,size):
        frame=cv2.putText(frame,text,xy,cv2.FONT_HERSHEY_SIMPLEX,font_size,color(colors),size)
        return frame   


    def cv2AddChineseText(self,img, text, position, textColor=(0, 255, 0), textSize=30):
        if (isinstance(img, np.ndarray)):  
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        fontStyle = ImageFont.truetype(
            "/home/pi/model/msyh.ttc", textSize, encoding="utf-8")
        draw.text(position, text, textColor, font=fontStyle)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    
    def AprilTagRecognition(self, target="camera"):
        """
        AprilTag码识别（使用OpenCV aruco模块）
        返回: 识别到的第一个Tag ID，没有则返回None
        """
        if target == "camera":
            self.open_camera()
            image = self.picam2.capture_array()
            # 摄像头配置了hflip=1，AprilTag检测需要原始方向，先翻转回来
            image = cv2.flip(image, 1)
        else:
            path = "/home/pi/xgoPictures/"
            image = np.array(Image.open(path + target).convert('RGB'))
        
        # 转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 支持多种AprilTag字典
        apriltag_dicts = [
            cv2.aruco.DICT_APRILTAG_36h11,
            cv2.aruco.DICT_APRILTAG_25h9,
            cv2.aruco.DICT_APRILTAG_16h5,
            cv2.aruco.DICT_APRILTAG_36h10
        ]
        
        # 创建检测参数
        parameters = cv2.aruco.DetectorParameters()
        
        result = None
        for dict_type in apriltag_dicts:
            aruco_dict = cv2.aruco.getPredefinedDictionary(dict_type)
            corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
            if ids is not None:
                for i, corner in enumerate(corners):
                    tag_id = ids[i][0]
                    pts = corner[0].astype(int)
                    
                    # 绘制边框
                    for j in range(4):
                        pt1 = tuple(pts[j])
                        pt2 = tuple(pts[(j + 1) % 4])
                        cv2.line(image, pt1, pt2, (0, 255, 0), 2)
                    
                    # 绘制中心点
                    center = pts.mean(axis=0).astype(int)
                    cv2.circle(image, tuple(center), 5, (255, 0, 0), -1)
                    cv2.putText(image, f"ID:{tag_id}", (center[0] - 20, center[1] - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    
                    if result is None:
                        result = tag_id
                break  # 找到就退出
        
        # 显示时翻转回来，保持与用户视角一致
        image = cv2.flip(image, 1)
        imgok = Image.fromarray(image)
        self.display.ShowImage(imgok)
        
        return result

    def QRRecognition(self, target="camera"):
        import pyzbar.pyzbar as pyzbar
        
        # 图像采集（统一使用image变量）
        if target == "camera":
            self.open_camera()
            image = self.picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 转换为RGB
        else:
            path = "/home/pi/xgoPictures/"
            image = np.array(Image.open(path + target))  # 统一使用image变量
        
        # QR码识别（使用正确的变量名）
        barcodes = pyzbar.decode(image)  # 关键修改：使用image而不是img
        
        # 结果处理
        result = []
        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            result.append(barcodeData)
            text = "{} ({})".format(barcodeData, barcodeType)
            image = self.cv2AddChineseText(image, text, (10, 30), (0, 255, 0), 30)
        
        # 显示处理（保持RGB格式）
        imgok = Image.fromarray(image)  # 直接使用RGB格式
        self.display.ShowImage(imgok)
        
        return result if result else []

    def ColorRecognition(self, target="camera", mode='R'):
        color_x = 0
        color_y = 0
        color_radius = 0
    
        # 颜色阈值设置
        if mode == 'R':  # red
            color_lower = np.array([0, 43, 46])
            color_upper = np.array([10, 255, 255])
        elif mode == 'G':  # green
            color_lower = np.array([35, 43, 46])
            color_upper = np.array([77, 255, 255])
        elif mode == 'B':  # blue
            color_lower = np.array([100, 43, 46])
            color_upper = np.array([124, 255, 255])
        elif mode == 'Y':  # yellow
            color_lower = np.array([26, 43, 46])
            color_upper = np.array([34, 255, 255])
    
        # 图像采集（统一使用frame变量）
        if target == "camera":
            self.open_camera()
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换为RGB
        else:
            path = "/home/pi/xgoPictures/"
            frame = np.array(Image.open(path + target).convert('RGB'))
    
        # 图像处理
        frame_ = cv2.GaussianBlur(frame, (5,5), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)  # 注意是RGB2HSV
        mask = cv2.inRange(hsv, color_lower, color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        mask = cv2.GaussianBlur(mask, (3,3), 0)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
        # 目标检测
        if len(cnts) > 0:
            cnt = max(cnts, key=cv2.contourArea)
            (color_x, color_y), color_radius = cv2.minEnclosingCircle(cnt)
            cv2.circle(frame, (int(color_x), int(color_y)), int(color_radius), (255,0,255), 2)
        
        # 显示坐标
        cv2.putText(frame, f"X:{int(color_x)}, Y:{int(color_y)}", 
                   (40,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
    
        # 显示处理（直接使用RGB格式）
        imgok = Image.fromarray(frame)
        self.display.ShowImage(imgok)
    
        return ((color_x, color_y), color_radius)

    def LineRecognition(self, target="camera", mode='K'):
        """
        巡线识别函数 - 文章五步法版本
        
        核心算法：灰度化 → 动态二值化 → 开运算去噪 → 轮廓提取 → 逐列扫描+多项式拟合
        
        参数:
            target: 图像来源，"camera"表示摄像头，其他为图片文件名
            mode: 颜色模式，'K'(黑色), 'W'(白色), 'R'(红), 'G'(绿), 'B'(蓝), 'Y'(黄)
        
        返回:
            {
                'x': 线的x坐标 (0-320, 160为中心; -1表示未检测到),
                'angle': 线的方向角度(度数，-90到90，0表示竖直，正值向右倾斜)
            }
        """
        SCREEN_WIDTH = 320
        SCREEN_HEIGHT = 240
        
        # ========== 第零步：图像采集 ==========
        if target == "camera":
            self.open_camera()
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            path = "/home/pi/xgoPictures/"
            frame = np.array(Image.open(path + target).convert('RGB'))
        
        orig_height, orig_width = frame.shape[:2]
        result = {'x': -1, 'angle': 0}
        
        # ROI区域：底部80-120行（文章推荐），这里取底部1/3
        roi_top = int(orig_height * 2 / 3)
        roi = frame[roi_top:, :]
        roi_height, roi_width = roi.shape[:2]
        
        # ========== 第一步：灰度化 ==========
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        
        # ========== 第二步：二值化（动态阈值） ==========
        # 使用自适应阈值，适应光照变化
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        if mode == 'K':  # 黑线
            # 自适应阈值：局部区域均值法
            binary = cv2.adaptiveThreshold(
                gray_blur, 255, 
                cv2.ADAPTIVE_THRESH_MEAN_C,  # 局部均值
                cv2.THRESH_BINARY_INV,       # 黑线变白
                blockSize=25,                # 局部区域大小
                C=10                         # 常数偏移
            )
        elif mode == 'W':  # 白线
            binary = cv2.adaptiveThreshold(
                gray_blur, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                blockSize=25, C=10
            )
        else:
            # 彩色线使用HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
            if mode == 'R':
                mask1 = cv2.inRange(hsv, np.array([0, 100, 50]), np.array([10, 255, 255]))
                mask2 = cv2.inRange(hsv, np.array([170, 100, 50]), np.array([180, 255, 255]))
                binary = cv2.bitwise_or(mask1, mask2)
            elif mode == 'G':
                binary = cv2.inRange(hsv, np.array([35, 100, 50]), np.array([85, 255, 255]))
            elif mode == 'B':
                binary = cv2.inRange(hsv, np.array([100, 100, 50]), np.array([130, 255, 255]))
            elif mode == 'Y':
                binary = cv2.inRange(hsv, np.array([20, 100, 50]), np.array([35, 255, 255]))
            else:
                binary = cv2.adaptiveThreshold(
                    gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                    cv2.THRESH_BINARY_INV, 25, 10
                )
        
        # ========== 第三步：形态学处理（开运算去噪） ==========
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # 先腐蚀后膨胀，去噪
        
        # ========== 第四步：轮廓提取（筛选最大轮廓） ==========
        cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 筛选面积最大的轮廓
        valid_cnts = [c for c in cnts if cv2.contourArea(c) > 100]
        if not valid_cnts:
            # 没有检测到有效轮廓
            display_frame = frame.copy()
            cv2.line(display_frame, (0, roi_top), (orig_width, roi_top), (100, 100, 100), 1)
            cv2.putText(display_frame, "No line detected", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            imgok = Image.fromarray(display_frame)
            self.display.ShowImage(imgok)
            return result
        
        # 取最大轮廓
        best_cnt = max(valid_cnts, key=cv2.contourArea)
        
        # 创建只包含最大轮廓的掩码
        line_mask = np.zeros_like(binary)
        cv2.drawContours(line_mask, [best_cnt], -1, 255, -1)
        
        # ========== 第五步：逐列扫描 + 中心线拟合 ==========
        centroid_x = []  # 列坐标
        centroid_y = []  # 该列黑色像素的垂直中点
        
        # 逐列扫描
        for x in range(roi_width):
            col_pixels = np.where(line_mask[:, x] > 0)[0]  # 该列的白色像素（即黑线）
            if len(col_pixels) > 0:
                # 计算该列像素的垂直中点
                y_center = int(np.mean(col_pixels))
                centroid_x.append(x)
                centroid_y.append(y_center)
        
        if len(centroid_x) < 5:
            # 采样点太少，无法拟合
            display_frame = frame.copy()
            cv2.line(display_frame, (0, roi_top), (orig_width, roi_top), (100, 100, 100), 1)
            cv2.putText(display_frame, "Too few points", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            imgok = Image.fromarray(display_frame)
            self.display.ShowImage(imgok)
            return result
        
        centroid_x = np.array(centroid_x)
        centroid_y = np.array(centroid_y)
        
        # 用顶部20%和底部20%区域的平均x来计算角度（更稳定）
        y_min, y_max = centroid_y.min(), centroid_y.max()
        y_range = y_max - y_min
        
        if y_range > 5:
            # 取顶部20%的点的平均x坐标
            top_threshold = y_min + y_range * 0.2
            top_mask = centroid_y <= top_threshold
            top_x = centroid_x[top_mask].mean() if top_mask.any() else centroid_x.mean()
            
            # 取底部20%的点的平均x坐标
            bottom_threshold = y_max - y_range * 0.2
            bottom_mask = centroid_y >= bottom_threshold
            bottom_x = centroid_x[bottom_mask].mean() if bottom_mask.any() else centroid_x.mean()
            
            # 计算角度
            dx = top_x - bottom_x
            line_angle = math.degrees(math.atan2(dx, y_range))
        else:
            # 线太短，无法计算角度
            line_angle = 0
            bottom_x = centroid_x.mean()
        
        # 角度归一化到 [-90, 90]
        if line_angle > 90:
            line_angle -= 180
        elif line_angle < -90:
            line_angle += 180
        
        result['x'] = int(bottom_x * SCREEN_WIDTH / orig_width)
        result['angle'] = int(line_angle)
        
        # 保存底部点y坐标用于绘制
        bottom_y_draw = int(y_max)
        
        # ========== 绘制结果 ==========
        display_frame = frame.copy()
        
        # 绘制ROI分界线
        cv2.line(display_frame, (0, roi_top), (orig_width, roi_top), (100, 100, 100), 1)
        
        # 绘制轮廓
        shifted_cnt = best_cnt.copy()
        shifted_cnt[:, 0, 1] += roi_top
        cv2.drawContours(display_frame, [shifted_cnt], -1, (0, 255, 0), 2)
        
        # 绘制拟合曲线上的点
        for i in range(0, len(centroid_x), 3):  # 每3个点画一个
            px = centroid_x[i]
            py = centroid_y[i] + roi_top
            cv2.circle(display_frame, (int(px), int(py)), 3, (255, 255, 0), -1)
        
        # 绘制底部检测点
        draw_cx = int(bottom_x)
        draw_cy = bottom_y_draw + roi_top
        cv2.circle(display_frame, (draw_cx, draw_cy), 8, (255, 0, 255), -1)
        
        # 绘制方向线
        angle_rad = math.radians(result['angle'])
        line_len = 40
        dx = int(line_len * math.sin(angle_rad))
        dy = int(line_len * math.cos(angle_rad))
        cv2.line(display_frame, (draw_cx, draw_cy), (draw_cx + dx, draw_cy - dy), (255, 0, 0), 3)
        
        # 显示信息
        offset = result['x'] - SCREEN_WIDTH // 2
        info_text = f"X:{result['x']} Off:{offset} Ang:{result['angle']}"
        cv2.putText(display_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(display_frame, f"Pts:{len(centroid_x)}", (200, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        imgok = Image.fromarray(display_frame)
        self.display.ShowImage(imgok)
        
        return result

    def cap_color_mask(self, position=None, scale=25, h_error=20, s_limit=[90, 255], v_limit=[90, 230]):
        if position is None:
            position = [160, 100]
        count = 0
        self.open_camera()
        
        while True:
            if self.xgoButton("c"):   
                break
                
            # 图像采集（统一使用image变量）
            image = self.picam2.capture_array()  # Picamera2默认输出BGR
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 转为RGB用于显示
            
            # 颜色空间处理（保持BGR用于HSV转换）
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # 颜色采样
            color = np.mean(h[position[1]:position[1] + scale, position[0]:position[0] + scale])
            
            if self.xgoButton("b") and count == 0:
                count += 1
                color_lower = [max(color - h_error, 0), s_limit[0], v_limit[0]]
                color_upper = [min(color + h_error, 255), s_limit[1], v_limit[1]]
                return [color_lower, color_upper]
    
            # 绘制界面（使用RGB图像）
            if count == 0:
                cv2.rectangle(image_rgb, 
                             (position[0], position[1]), 
                             (position[0] + scale, position[1] + scale),
                             (255, 255, 255), 2)
                cv2.putText(image_rgb, 'press button B', 
                           (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (255, 0, 0), 2)  # RGB格式的红色
            
            # 显示（直接使用RGB）
            imgok = Image.fromarray(image_rgb)
            self.display.ShowImage(imgok)
    
    def filter_img(self,frame,color):
        b,g,r = cv2.split(frame)
        frame_bgr = cv2.merge((r,g,b))
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        if isinstance(color, list):
            color_lower = np.array(color[0])
            color_upper = np.array(color[1])
        else:
            color_upper, color_lower = get_color_mask(color)
        mask = cv2.inRange(hsv, color_lower, color_upper)
        img_mask = cv2.bitwise_and(frame, frame, mask=mask)
        return img_mask

    def BallRecognition(self,color_mask,target="camera",p1=36, p2=15, minR=6, maxR=35):
        x=y=ra=0
        if target=="camera":
            self.open_camera()
            image = self.picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # 如果需要RGB格式
        else:
            path="/home/pi/xgoPictures/"
            image=np.array(Image.open(path+target))

        frame_mask=self.filter_img(image, color_mask)
        
        img = cv2.medianBlur(frame_mask, 5)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1=p1, param2=p2, minRadius=minR,maxRadius=maxR)
        b,g,r = cv2.split(image)
        image = cv2.merge((r,g,b))
        if circles is not None and len(circles[0]) == 1:
            param = circles[0][0]
            x, y, ra = int(param[0]), int(param[1]), int(param[2])
            cv2.circle(image, (x, y), ra, (255, 255, 255), 2)
            cv2.circle(image, (x, y), 2, (255, 255, 255), 2)
        imgok = Image.fromarray(image)
        self.display.ShowImage(imgok)
        return x,y,ra





class DemoError(Exception):
    pass

class hands():
    def __init__(self,model_complexity,max_num_hands,min_detection_confidence,min_tracking_confidence):
        import mediapipe as mp
        self.model_complexity = model_complexity
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )
    
    def run(self,cv_img):
        import copy
        image = cv_img
        debug_image = copy.deepcopy(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)
        hf=[]
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                # 手的重心计算
                cx, cy = self.calc_palm_moment(debug_image, hand_landmarks)
                # 手的外接矩形计算
                rect = self.calc_bounding_rect(debug_image, hand_landmarks)
                # 手的个关键点
                dlandmark = self.dlandmarks(debug_image,hand_landmarks,handedness)

                hf.append({'center':(cx,cy),'rect':rect,'dlandmark':dlandmark[0],'hand_angle':self.hand_angle(dlandmark[0]),'right_left':dlandmark[1]})
        return hf

    def calc_palm_moment(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]
        palm_array = np.empty((0, 2), int)
        for index, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point = [np.array((landmark_x, landmark_y))]
            if index == 0:  # 手首1
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 1:  # 手首2
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 5:  # 人差指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 9:  # 中指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 13:  # 薬指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
            if index == 17:  # 小指：付け根
                palm_array = np.append(palm_array, landmark_point, axis=0)
        M = cv2.moments(palm_array)
        cx, cy = 0, 0
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
        return cx, cy

    def calc_bounding_rect(self, image, landmarks):
        image_width, image_height = image.shape[1], image.shape[0]
        landmark_array = np.empty((0, 2), int)
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point = [np.array((landmark_x, landmark_y))]
            landmark_array = np.append(landmark_array, landmark_point, axis=0)
        x, y, w, h = cv2.boundingRect(landmark_array)
        return [x, y, w, h]

    def dlandmarks(self,image, landmarks, handedness):
        image_width, image_height = image.shape[1], image.shape[0]
        landmark_point = []
        for index, landmark in enumerate(landmarks.landmark):
            if landmark.visibility < 0 or landmark.presence < 0:
                continue
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point.append((landmark_x, landmark_y))
        return landmark_point,handedness.classification[0].label[0]

    def vector_2d_angle(self, v1, v2):
        v1_x = v1[0]
        v1_y = v1[1]
        v2_x = v2[0]
        v2_y = v2[1]
        try:
            angle_= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
        except:
            angle_ = 180
        return angle_

    def hand_angle(self,hand_):
        angle_list = []
        # thumb 大拇指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
            ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
            )
        angle_list.append(angle_)
        # index 食指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
            ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
            )
        angle_list.append(angle_)
        # middle 中指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
            ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
            )
        angle_list.append(angle_)
        # ring 無名指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
            ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
            )
        angle_list.append(angle_)
        # pink 小拇指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
            ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
            )
        angle_list.append(angle_)
        return angle_list
    
class yoloXgo():
    def __init__(self,model,classes,inputwh,thresh):
        import onnxruntime 
        self.session = onnxruntime.InferenceSession(model)
        self.input_width=inputwh[0]
        self.input_height=inputwh[1]
        self.thresh=thresh
        self.classes=classes
        
    def sigmoid(self,x):
        return 1. / (1 + np.exp(-x))

    # tanh函数
    def tanh(self,x):
        return 2. / (1 + np.exp(-2 * x)) - 1

    # 数据预处理
    def preprocess(self,src_img, size):
        output = cv2.resize(src_img,(size[0], size[1]),interpolation=cv2.INTER_AREA)
        output = output.transpose(2,0,1)
        output = output.reshape((1, 3, size[1], size[0])) / 255
        return output.astype('float32') 

    # nms算法
    def nms(self,dets,thresh=0.45):
        # dets:N*M,N是bbox的个数，M的前4位是对应的（x1,y1,x2,y2），第5位是对应的分数
        # #thresh:0.3,0.5....
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        scores = dets[:, 4]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)  # 求每个bbox的面积
        order = scores.argsort()[::-1]  # 对分数进行倒排序
        keep = []  # 用来保存最后留下来的bboxx下标

        while order.size > 0:
            i = order[0]  # 无条件保留每次迭代中置信度最高的bbox
            keep.append(i)

            # 计算置信度最高的bbox和其他剩下bbox之间的交叉区域
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            # 计算置信度高的bbox和其他剩下bbox之间交叉区域的面积
            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h

            # 求交叉区域的面积占两者（置信度高的bbox和其他bbox）面积和的必烈
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            # 保留ovr小于thresh的bbox，进入下一次迭代。
            inds = np.where(ovr <= thresh)[0]

            # 因为ovr中的索引不包括order[0]所以要向后移动一位
            order = order[inds + 1]
        
        output = []
        for i in keep:
            output.append(dets[i].tolist())

        return output

    def run(self, img,):
        pred = []

        # 输入图像的原始宽高
        H, W, _ = img.shape

        # 数据预处理: resize, 1/255
        data = self.preprocess(img, [self.input_width, self.input_height])

        # 模型推理
        input_name = self.session.get_inputs()[0].name
        feature_map = self.session.run([], {input_name: data})[0][0]

        # 输出特征图转置: CHW, HWC
        feature_map = feature_map.transpose(1, 2, 0)
        # 输出特征图的宽高
        feature_map_height = feature_map.shape[0]
        feature_map_width = feature_map.shape[1]

        # 特征图后处理
        for h in range(feature_map_height):
            for w in range(feature_map_width):
                data = feature_map[h][w]

                # 解析检测框置信度
                obj_score, cls_score = data[0], data[5:].max()
                score = (obj_score ** 0.6) * (cls_score ** 0.4)

                # 阈值筛选
                if score > self.thresh:
                    # 检测框类别
                    cls_index = np.argmax(data[5:])
                    # 检测框中心点偏移
                    x_offset, y_offset = self.tanh(data[1]), self.tanh(data[2])
                    # 检测框归一化后的宽高
                    box_width, box_height = self.sigmoid(data[3]), self.sigmoid(data[4])
                    # 检测框归一化后中心点
                    box_cx = (w + x_offset) / feature_map_width
                    box_cy = (h + y_offset) / feature_map_height
                    
                    # cx,cy,w,h => x1, y1, x2, y2
                    x1, y1 = box_cx - 0.5 * box_width, box_cy - 0.5 * box_height
                    x2, y2 = box_cx + 0.5 * box_width, box_cy + 0.5 * box_height
                    x1, y1, x2, y2 = int(x1 * W), int(y1 * H), int(x2 * W), int(y2 * H)

                    pred.append([x1, y1, x2, y2, score, cls_index])
        datas=np.array(pred)
        data=[]
        if len(datas)>0:
            boxes=self.nms(datas)
            for b in boxes:
                obj_score, cls_index = b[4], int(b[5])
                x1, y1, x2, y2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
                s={'classes':self.classes[cls_index],'score':'%.2f' % obj_score,'xywh':[x1,y1,x2-x1,y2-y1],}
                data.append(s)
            return data
        else:
            return False

class face_detection():
    def __init__(self,min_detection_confidence):
        import mediapipe as mp
        self.model_selection = 0
        self.min_detection_confidence =min_detection_confidence
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=self.min_detection_confidence,
        )

    def run(self,cv_img):
        image = cv_img
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(cv_img)
        face=[]
        if results.detections is not None:
            for detection in results.detections:
                data =self.draw_detection(image,detection) 
                face.append(data)
        return face
    def draw_detection(self, image, detection):
        image_width, image_height = image.shape[1], image.shape[0]
        bbox = detection.location_data.relative_bounding_box
        bbox.xmin = int(bbox.xmin * image_width)
        bbox.ymin = int(bbox.ymin * image_height)
        bbox.width = int(bbox.width * image_width)
        bbox.height = int(bbox.height * image_height)


        # 位置：右目
        keypoint0 = detection.location_data.relative_keypoints[0]
        keypoint0.x = int(keypoint0.x * image_width)
        keypoint0.y = int(keypoint0.y * image_height)


        # 位置：左目
        keypoint1 = detection.location_data.relative_keypoints[1]
        keypoint1.x = int(keypoint1.x * image_width)
        keypoint1.y = int(keypoint1.y * image_height)


        # 位置：鼻
        keypoint2 = detection.location_data.relative_keypoints[2]
        keypoint2.x = int(keypoint2.x * image_width)
        keypoint2.y = int(keypoint2.y * image_height)


        # 位置：口
        keypoint3 = detection.location_data.relative_keypoints[3]
        keypoint3.x = int(keypoint3.x * image_width)
        keypoint3.y = int(keypoint3.y * image_height)

        # 位置：右耳
        keypoint4 = detection.location_data.relative_keypoints[4]
        keypoint4.x = int(keypoint4.x * image_width)
        keypoint4.y = int(keypoint4.y * image_height)

        # 位置：左耳
        keypoint5 = detection.location_data.relative_keypoints[5]
        keypoint5.x = int(keypoint5.x * image_width)
        keypoint5.y = int(keypoint5.y * image_height)

        data={'id':detection.label_id[0],
            'score':round(detection.score[0], 3),
            'rect':[int(bbox.xmin),int(bbox.ymin),int(bbox.width),int(bbox.height)],
            'right_eye':(int(keypoint0.x),int(keypoint0.y)),
            'left_eye':(int(keypoint1.x),int(keypoint1.y)),
            'nose':(int(keypoint2.x),int(keypoint2.y)),
            'mouth':(int(keypoint3.x),int(keypoint3.y)),
            'right_ear':(int(keypoint4.x),int(keypoint4.y)),
            'left_ear':(int(keypoint5.x),int(keypoint5.y)),
            }
        return data
