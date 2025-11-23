import cv2
import os
import numpy as np
import yaml
import torch
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from  collections import deque
import math
def process_result(result):
    try:
        detection_results = []
        for landmark in result.landmark:
            detection_results.append([landmark.x,landmark.y,landmark.z,landmark.visibility])
        return detection_results
    except:
        return
def get_root_dir():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    root_dir = os.path.dirname(script_dir)
    return root_dir
root = get_root_dir()
print(get_root_dir())
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)
model = face_mesh
mp_hands = mp.solutions.hands
hand_model = mp_hands.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
)
mp_drawing = mp.solutions.drawing_utils

# print(os.path.join(get_root_dir(),"attention.yaml"))
# print(os.path.join(get_root_dir(),"data\csv.csv"))
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
def landmark_to_np(landmark,w,h):
    return np.array([landmark.x*w,landmark.y*h,landmark.z*w])
def get_axes(left,right,top,bottom,front):
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
cap = cv2.VideoCapture(1)
cap.set(3,1280)
cap.set(4,720)
while cap.isOpened():
    ret,frame = cap.read()
    if not ret:
        break
    h,w,_ = frame.shape
    rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = model.process(rgb)
    hand_result = hand_model.process(rgb)
    if hand_result.q:
        for hand_landmarks in hand_result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style()
            )
            processed_result = torch.tensor(process_result(hand_landmarks))
            print(processed_result.shape)
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0].landmark
        landmarks_frame = np.zeros_like(frame)
        
        outline_pts = []
        
        for i,landmark in enumerate(face_landmarks):
            pt = landmark_to_np(landmark,w,h)
            x,y = int(pt[0]),int(pt[1])
            if 0 <=x < w and 0 <=y < h:
                color = (155,155,155) if i in FACE_OUTLINE_INDICES else (255,25,10)
                color = (10,25,255) if i in IRIS_LANDMARK else (255,25,10)
                cv2.circle(landmarks_frame,(x,y),1,color,-1)
                frame[y,x] = (255,255,255)
                
                
        key_points = {}
        for name,idx in LANDMARKS.items():
            pt = landmark_to_np(face_landmarks[idx],w,h)
            key_points[name] = pt
            x,y = int(pt[0]), int(pt[1])
            cv2.circle(frame,(x,y),4,(0,0,0),-1)
        liris_points = {}
        for name,idx in LEFT_EYE_REFERENCE.items():
            pt = landmark_to_np(face_landmarks[idx],w,h)
            liris_points[name] = pt
            x,y = int(pt[0]), int(pt[1])
            cv2.circle(frame,(x,y),4,(0,0,0),-1)
        riris_points = {}
        for name,idx in RIGHT_EYE_REFERENCE.items():
            pt = landmark_to_np(face_landmarks[idx],w,h)
            riris_points[name] = pt
            x,y = int(pt[0]), int(pt[1])
            cv2.circle(frame,(x,y),4,(0,0,0),-1)
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
        cv2.circle(frame,project(eye_center),2,(0,0,0),-1)
        cv2.circle(frame,project(liris_center),2,(255,255,255),-1)
        cv2.putText(frame,f"left EAR: ({LEFT_EAR})",(0,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
        #cv2.putText(frame,f"distant from eye center: ({liris_center[0]-eye_center[0]},{liris_center[1]-eye_center[1]})",(0,70),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
        liris_hort_angle,liris_vert_angle = get_eye_angles(liris_center,liris_left,liris_right,liris_top,liris_bottom)
        cv2.putText(frame,f"angles: ({liris_hort_angle},{liris_vert_angle})",(0,70),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
        hx,vy = math.radians(liris_hort_angle), math.radians(liris_vert_angle)
        dx,dy = 100* math.sin(hx) , 100*math.sin(vy)
        end_point = (int(liris_center[0]+dx),int(liris_center[1]+dy))
        cv2.line(frame,project(eye_center),end_point,(94,194,99),2)
        cv2.putText(frame,f"left iris rotation:({liris_hort_angle},{liris_vert_angle})",(0,140),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
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
        hx,vy = math.radians(riris_hort_angle), math.radians(riris_vert_angle)
        dx,dy = 100* math.sin(hx) , 100*math.sin(vy)
        end_point = (int(riris_center[0]+dx),int(riris_center[1]+dy))
        cv2.line(frame,project(eye_center),end_point,(94,194,99),2)
        cv2.putText(frame,f"right iris rotation:({riris_hort_angle},{riris_vert_angle})",(0,170),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2,cv2.LINE_AA)
        # face points
        left = key_points['left']
        right = key_points['right']
        top = key_points['top']
        bottom = key_points['bottom']
        front = key_points['front']
        right_axis,up_axis,forward_axis = get_axes(left,right,top,bottom,front)
        center = (left+right+bottom+top+front)/5
        
        half_width = np.linalg.norm(right-left)/2
        half_height = np.linalg.norm(top-bottom)/2
        half_depth = 80
        
        def corner(x_sign,y_sign,z_sign):
            return (center
                    + x_sign*half_width*right_axis
                    + y_sign*half_height*up_axis
                    + z_sign*half_width*forward_axis
                    )

        cube_corners = [
            corner(-1, 1, -1),   # top-left-front
            corner(1, 1, -1),    # top-right-front
            corner(1, -1, -1),   # bottom-right-front
            corner(-1, -1, -1),  # bottom-left-front
            corner(-1, 1, 1),    # top-left-back
            corner(1, 1, 1),     # top-right-back
            corner(1, -1, 1),    # bottom-right-back
            corner(-1, -1, 1)    # bottom-left-back
        ]
        
        
        cube_corners_2d = [project(pt) for pt in cube_corners]
        edges = [
            (0,1),(1,2),(2,3),(3,0), # front face
            (4,5),(5,6),(6,7),(7,4), # back face
            (0,4),(1,5),(2,6),(3,7) # sides
        ]
        for i,j in edges:
            cv2.line(frame,cube_corners_2d[i],cube_corners_2d[j],(255,125,35),2)

        # Update soomthing buffers
        ray_origins.append(center)
        ray_directions.append(forward_axis)
        
        avg_origin = np.mean(ray_origins,axis=0)
        avg_direction = np.mean(ray_directions,axis=0)
        avg_direction /= np.linalg.norm(avg_direction) 
        
        reference_forward = np.array([0, 0, -1])  # Z-axis into the screen

        # Horizontal (yaw) angle from reference (project onto XZ plane)
        xz_proj = np.array([avg_direction[0], 0, avg_direction[2]])
        xz_proj /= np.linalg.norm(xz_proj)
        yaw_rad = math.acos(np.clip(np.dot(reference_forward, xz_proj), -1.0, 1.0))
        if avg_direction[0] < 0:
            yaw_rad = -yaw_rad  # left is negative

        # Vertical (pitch) angle from reference (project onto YZ plane)
        yz_proj = np.array([0, avg_direction[1], avg_direction[2]])
        yz_proj /= np.linalg.norm(yz_proj)
        pitch_rad = math.acos(np.clip(np.dot(reference_forward, yz_proj), -1.0, 1.0))
        if avg_direction[1] > 0:
            pitch_rad = -pitch_rad  # up is positive

        #Specify 

        # Convert to degrees and re-center around 0
        yaw_deg = np.degrees(yaw_rad)
        pitch_deg = np.degrees(pitch_rad)

        #this results in the center being 180, +10 left = -170, +10 right = +170

        #convert left rotations to 0-180
        if yaw_deg < 0:
            yaw_deg = abs(yaw_deg)
        elif yaw_deg < 180:
            yaw_deg = 360 - yaw_deg

        if pitch_deg < 0:
            pitch_deg = 360 + pitch_deg
        
        # if yaw_deg < 0:
        #     yaw_deg = abs(yaw_deg)
        # elif yaw_deg < 180:
        #     yaw_deg = 360-yaw_deg
        
        # if pitch_deg < 0 :
        #     pitch_deg = 360+pitch_deg
        ray_length = 2.5*half_depth
        ray_end = avg_origin - avg_direction*ray_length
        cv2.line(frame,project(avg_origin),project(ray_end),(15,255,0),3)
        cv2.line(landmarks_frame,project(avg_origin),project(ray_end),(15,255,0),3)
        #print(f" Angles: ({yaw_deg},{pitch_deg})")
        cv2.imshow("Head-aligned cube",frame)
        cv2.imshow("Facial Landmarks",landmarks_frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                break
                
        
        
cv2.destroyAllWindows()