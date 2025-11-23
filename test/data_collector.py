import cv2
import os
import numpy as np
import yaml
import json
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from  collections import deque
import math
def get_root_dir():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    root_dir = os.path.dirname(script_dir)
    return root_dir
root = get_root_dir()
print(root)
data_path = os.path.join(root,"json")
json_files = os.listdir(data_path)
mp_face_mesh = mp.solutions.face_mesh
model = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
mp_hand_mesh = mp.solutions.hands
hand_model  = mp_hand_mesh.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
)
mp_drawing = mp.solutions.drawing_utils
LANDMARKS = {
    "left": 234,
    "right": 454,
    "top": 10,
    "bottom": 152,
    "front": 1,
}

LEFT_IRIS = {
    "left":474,
    "right":476,
    "top":475,
    "bottom":477,
    "front":473
}
RIGHT_IRIS = {
    "left":471,
    "right":469,
    "top":470,
    "bottom":472,
    "front":468
}
LEFT_EYE_REFERENCE = {
    "left":263, # p1
    "right":362, # p4
    "top":386, # p2
    "bottom":374, # p5
    "p3":385, 
    "p6":380
}
RIGHT_EYE_REFERENCE = {
    "left":33, # p1
    "right":133, # p4
    "top":159, # p2
    "bottom":145, # p5
    "p3":160,
    "p6":144
}
IRIS_LANDMARK = {
    474,475,476,477,469,470,471,472,468,473
}
FACE_OUTLINE_INDICES = {
    10, 338, 297, 332, 284, 251, 389, 356,
    454, 323, 361, 288, 397, 365, 379, 378,
    400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21,
    54, 103, 67, 109
}
filter_length = 8
ray_origins = deque(maxlen=filter_length)
ray_directions = deque(maxlen=filter_length)
liris_ray_origins = deque(maxlen=filter_length)
liris_ray_directions = deque(maxlen=filter_length)
riris_ray_origins = deque(maxlen=filter_length)
riris_ray_directions = deque(maxlen=filter_length)
def draw_hand_landmark(frame,hand_landmarks):
    global mp_hand_mesh
    mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hand_mesh.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style()
    )
def landmark_to_np(landmark,w,h):
    return np.array([landmark.x*w,landmark.y*h,landmark.z*w])
def get_axes(left,right,top,bottom):
    right_axis = (right-left)
    right_axis/=np.linalg.norm(right_axis)
    
    up_axis = (top-bottom)
    up_axis /= np.linalg.norm(up_axis)
    
    forward_axis = np.cross(right_axis,up_axis)
    forward_axis /= np.linalg.norm(forward_axis)
    forward_axis = -forward_axis
    
    return right_axis,up_axis,forward_axis
def get_eye_angles(iris_center,left,right,top,bottom):
    eye_center = (left+right+top+bottom)/4
    
    eye_width = abs(right[0]-left[0])
    eye_height = abs(bottom[1]-top[1])
    
    dx = (iris_center[0] - eye_center[0]) / (eye_width/2)
    dy =  (iris_center[1]- eye_center[1]) / (eye_height/2)
    
    horizontal_angle = dx*30
    vertical_angle  = dy*20
    return horizontal_angle, vertical_angle
def project(pt3d):
    return int(pt3d[0]),int(pt3d[1])
def cal_EAR(p1,p2,p3,p4,p5,p6):
    return (np.linalg.norm(p2-p6)+np.linalg.norm(p3-p5))/(2*np.linalg.norm(p1-p4))
video_folder_path = os.path.join(root,"video_data")
video_paths = os.listdir(video_folder_path)
data = []
for video_path in video_paths:
    video_path = os.path.join(video_folder_path,video_path)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    speed =1
    label = 0
    face_row = []
    hand_row = []
    frame_count = 0
    frame_limit = fps*30
    while cap.isOpened():
        ret,frame = cap.read()
        if not ret:
            break
        h,w,_ = frame.shape
        
        hand_frame = frame[:,:1280,:]
        face_frame = frame[:480,1281:,:]
        hand_rgb = cv2.cvtColor(hand_frame,cv2.COLOR_BGR2RGB)
        face_rgb = cv2.cvtColor(face_frame,cv2.COLOR_BGR2RGB)
        cv2.waitKey(1)
        face_results = model.process(face_rgb)
        hand_results = hand_model.process(hand_rgb)
        if hand_results.multi_hand_landmarks:
            temp = []
            for hand_landmark in hand_results.multi_hand_landmarks:
                draw_hand_landmark(hand_frame,hand_landmark)
                for landmark in hand_landmark.landmark:
                    temp.append(landmark.x)
                    temp.append(landmark.y)
                    temp.append(landmark.z)
            hand_row.append(temp)
            cv2.imshow("hand",hand_frame)
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0].landmark
            key_points = {}
            for name,idx in LANDMARKS.items():
                pt = landmark_to_np(face_landmarks[idx],w,h)
                key_points[name] = pt
            liris_points = {}
            for name,idx in LEFT_EYE_REFERENCE.items():
                pt = landmark_to_np(face_landmarks[idx],w,h)
                liris_points[name] = pt
            riris_points = {}
            for name,idx in RIGHT_EYE_REFERENCE.items():
                pt = landmark_to_np(face_landmarks[idx],w,h)
                riris_points[name] = pt
            reference_forward = np.array([0,0,-1])
            # left iris points
            liris_left = liris_points['left']
            liris_right = liris_points['right']
            liris_top = liris_points['top']
            liris_bottom = liris_points['bottom']
            liris_center = np.array([0.0,0.0,0.0])
            LEFT_EAR = cal_EAR(
                p1= liris_left,
                p2=liris_top,
                p3 = liris_points['p3'],
                p4 = liris_right,
                p5 = liris_bottom,
                p6= liris_points['p6']
            )
            for name,idx in LEFT_IRIS.items():
                pt = landmark_to_np(face_landmarks[idx],w,h)
                liris_center+= pt
            liris_center /= 5
            
            eye_center = (liris_left + liris_right + liris_top + liris_bottom)/4
            liris_hort_angle,liris_vert_angle = get_eye_angles(liris_center,liris_left,liris_right,liris_top,liris_bottom)
            # right iris points
            riris_left = riris_points['left']
            riris_right = riris_points['right']
            riris_top = riris_points['top']
            riris_bottom = riris_points['bottom']
            RIGHT_EAR = cal_EAR(
                p1= riris_left,
                p2=riris_top,
                p3 = riris_points['p3'],
                p4 = riris_right,
                p5 = riris_bottom,
                p6= riris_points['p6']
            )
            riris_center = np.array([0.0,0.0,0.0])
            for name,idx in RIGHT_IRIS.items():
                pt = landmark_to_np(face_landmarks[idx],w,h)
                riris_center += pt
            riris_center/=5
            eye_center = (riris_left + riris_right + riris_top + riris_bottom)/4
            riris_hort_angle,riris_vert_angle = get_eye_angles(riris_center,riris_left,riris_right,riris_top,riris_bottom)
            # face points
            left = key_points['left']
            right = key_points['right']
            top = key_points['top']
            bottom = key_points['bottom']
            front = key_points['front']
            right_axis,up_axis,forward_axis = get_axes(left,right,top,bottom)
            center = (left+right+bottom+top+front)/5
            
            half_width = np.linalg.norm(right-left)/2
            half_height = np.linalg.norm(top-bottom)/2
            half_depth = 80
            # Update soomthing buffers
            ray_origins.append(center)
            ray_directions.append(forward_axis)
            
            avg_origin = np.mean(ray_origins,axis=0)
            avg_direction = np.mean(ray_directions,axis=0)
            avg_direction /= np.linalg.norm(avg_direction) 
            
            xz_proj = np.array([avg_direction[0],0,avg_direction[2]])
            xz_proj /= np.linalg.norm(xz_proj)
            yaw_rad = math.acos(np.clip(np.dot(reference_forward,xz_proj),-1.0,1.0))
            if avg_direction[0] < 0:
                yaw_rad = -yaw_rad
            yz_proj = np.array([0,avg_direction[1],avg_direction[2]])
            yz_proj /= np.linalg.norm(yz_proj)
            pitch_rad = math.acos(np.clip(np.dot(reference_forward,yz_proj),-1.0,1.0))
            if avg_direction[1] > 0:
                pitch_rad = -pitch_rad
                
            yaw_deg = np.degrees(yaw_rad)
            pitch_deg = np.degrees(pitch_rad)
            
            if yaw_deg < 0:
                yaw_deg = abs(yaw_deg)
            elif yaw_deg < 180:
                yaw_deg = 360-yaw_deg
            
            if pitch_deg < 0 :
                pitch_deg = 360+pitch_deg
            yaw_deg-=180
            pitch_deg -= 180
            cv2.putText(frame,f"seconds:{len(face_row)}",(0,20),1,1,(0,0,0),1)
            cv2.imshow("Head-aligned cube",face_frame)  
            face_row.append([LEFT_EAR,liris_hort_angle,liris_vert_angle,RIGHT_EAR,riris_hort_angle,riris_vert_angle,yaw_deg,pitch_deg])
        if frame_count == frame_limit:
            key = cv2.waitKey(0) & 0xFF
            if key == ord("0"):
                label = 0
            elif key == ord("1"):
                label = 1
            data.append({
                'face_features':face_row,
                'hand_features':hand_row,
                'label':label
            })
            face_row = []
            hand_row = []
            frame_count = 0
        key = cv2.waitKey(10) & 0xFF
        if key == ord("e"):
            speed -=1 
        elif key == ord("r"):
            speed+=1
        
        frame_count+=1
if len(json_files) == 0:
    file_path = os.path.join(data_path,"log_1.json")
    with open(file_path,"w") as f:
        json.dump(data,f,indent=4)
else:
    log_num = int(json_files[-1].split("_")[-1].split(".")[0])+1
    file_path = os.path.join(data_path,f"log_{log_num}.json")
    with open(file_path,"w") as f:
        json.dump(data,f,indent=4)
cv2.destroyAllWindows()
    