import cv2
import numpy as np
import mediapipe as mp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from collections import deque
import time
from AI_chat import ask_AI
from DB_utils import create_timestamp,find_timestamp_this_month,find_timestamp_this_year,find_timestamp_today,create_goal,edit_goal_progress,find_timestamp_this_week,get_goals,delete_goal
from image_processing import compute_and_draw_coordinate_box, compute_focus_score, compute_scale, convert_gaze_to_screen_coordinates, decode_base64_image, normalize
app = FastAPI(
    title="Vercel + FastAPI",
    description="Vercel + FastAPI",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # React frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
FPS=10
LEFT_IRIS, RIGHT_IRIS = 468, 473
gaze_history = deque(maxlen=FPS*5)
blink_history = deque(maxlen=FPS*5)
# === Configuration ===
filter_length = 10       # smoothing window for gaze vector
# --- Reference matrices for rotation stabilization ---
R_ref_nose = [None]
calibration_nose_scale = None

# === Initialize MediaPipe FaceMesh ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
# === Initialize MediaPipe hand landmarker ===
mp_hand_mesh = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
nose_indices = [4, 45, 275, 220, 440, 1, 5, 51, 281, 44, 274, 241,
                461, 125, 354, 218, 438, 195, 167, 393, 165, 391,
                3, 248]

combined_gaze_directions = deque(maxlen=filter_length)

# --- Eye sphere calibration ---
left_sphere_locked = False
right_sphere_locked = False
left_sphere_local_offset = None
right_sphere_local_offset = None
left_calibration_nose_scale = None
right_calibration_nose_scale = None
# class
class Frame(BaseModel):
    image:str
class FocusScore(BaseModel):
    userid:str
    focus_score:int
class Goal(BaseModel):
    title:str
    desc:str
    userid:str
    deadline:str
class TimeStamp(BaseModel):
    userid:str
    avg_focus_score:int
class NewProgress(BaseModel):
    new_progress:int
    id: str = Field(alias="_id")
class DeleteProgress(BaseModel):
    id: str = Field(alias="_id")
class UserInfo(BaseModel):
    userid:str
class AI_REQUEST(BaseModel):
    userid:str
    user_chat:str
@app.post('/create_goal')
def createGoal(payload:Goal):
    create_goal(payload)
@app.put("/edit_goal_progress")
def editgoalProgress(payload:NewProgress):
    edit_goal_progress(payload)
@app.post('/get_goals')
def getGoals(payload: UserInfo):
    return get_goals(payload)
@app.delete("/delete_goal")
def deleteGoal(payload:DeleteProgress):
    delete_goal(payload)
@app.post("/create_timestamp")
def createTimestamp(payload:TimeStamp):
    create_timestamp(payload)
    return {'status':1}
@app.post("/get_timestamp_today")
def getTimeStampToday(payload:UserInfo):
    return find_timestamp_today(payload)
@app.post("/get_timestamp_month")
def getTimeStampThisMonth(payload:UserInfo):
    return find_timestamp_this_month(payload)
@app.post("/get_timestamp_week")
def getTimeStampThisWeek(payload:UserInfo):
    return find_timestamp_this_week(payload)
@app.post("/get_timestamp_year")
def getTimeStampThisYear(payload:UserInfo):
    return find_timestamp_this_year(payload)
@app.post("/call_ai")
def call_AI(payload:AI_REQUEST):
    new_info = UserInfo(userid=payload.userid)
    focus_history = find_timestamp_this_week(new_info)
    return ask_AI(payload.user_chat,focus_history,'week')
@app.post("/calibrate")
def calibrate(frame: Frame):
    global left_calibration_nose_scale
    global left_sphere_locked
    global left_sphere_local_offset
    global right_calibration_nose_scale
    global right_sphere_locked
    global right_sphere_local_offset
    global face_mesh
    global nose_indices
    global R_ref_nose
    base_radius = 20
    left_sphere_local_offset = None
    camera_dir_local = None
    left_sphere_local_offset = None
    left_calibration_nose_scale = None
    left_sphere_locked = None
    right_sphere_local_offset = None
    right_sphere_local_offset = None
    right_calibration_nose_scale = None
    right_sphere_locked = None
    gaze_history.clear()
    blink_history.clear()
    frame = decode_base64_image(frame.image)
    h,w,_ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    print(results)
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0].landmark
        
        head_center, R_final, nose_points_3d = compute_and_draw_coordinate_box(
            frame, face_landmarks, nose_indices, R_ref_nose,
            color=(0,255,0),size=80
        )
        current_nose_scale = compute_scale(nose_points_3d)
        left_iris = np.array([face_landmarks[LEFT_IRIS].x * w,
                              face_landmarks[LEFT_IRIS].y * h,
                              face_landmarks[LEFT_IRIS].z * w])
        right_iris = np.array([face_landmarks[RIGHT_IRIS].x * w,
                               face_landmarks[RIGHT_IRIS].y * h,
                               face_landmarks[RIGHT_IRIS].z * w])
        print(left_iris,right_iris)
        left_sphere_local_offset = R_final.T @ (left_iris - head_center)
        camera_dir_local = R_final.T @ np.array([0, 0, 1])
        left_sphere_local_offset += base_radius * camera_dir_local
        left_calibration_nose_scale = current_nose_scale
        left_sphere_locked = True
        right_sphere_local_offset = R_final.T @ (right_iris - head_center)
        right_sphere_local_offset += base_radius * camera_dir_local
        right_calibration_nose_scale = current_nose_scale
        right_sphere_locked = True
        return {'state':'done'}
@app.post("/process")
def process_image(frame: Frame):
    global face_mesh
    global nose_indices
    global R_ref_nose
    global combined_gaze_directions
    global gaze_history
    global blink_history
    global left_calibration_nose_scale
    global left_sphere_local_offset
    global right_calibration_nose_scale
    global right_sphere_local_offset
    frame = decode_base64_image(frame.image)
    h,w,_ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0].landmark

        # --- Compute head coordinate system ---
        head_center, R_final, nose_points_3d = compute_and_draw_coordinate_box(
            frame, face_landmarks, nose_indices, R_ref_nose,
            color=(0, 255, 0), size=80
        )

        current_nose_scale = compute_scale(nose_points_3d)

        # --- Iris centers (in pixel units) ---
        left_iris = np.array([face_landmarks[LEFT_IRIS].x * w,
                              face_landmarks[LEFT_IRIS].y * h,
                              face_landmarks[LEFT_IRIS].z * w])
        right_iris = np.array([face_landmarks[RIGHT_IRIS].x * w,
                               face_landmarks[RIGHT_IRIS].y * h,
                               face_landmarks[RIGHT_IRIS].z * w])

        # --- Eye sphere calibration (first time 'c' pressed) ---
        # --- Draw iris and compute gaze if calibrated ---
        if left_sphere_locked and right_sphere_locked:
            # Recompute scale ratio (for distance compensation)
            scale_ratio_l = current_nose_scale / left_calibration_nose_scale
            scale_ratio_r = current_nose_scale / right_calibration_nose_scale

            sphere_world_l = head_center + R_final @ (left_sphere_local_offset * scale_ratio_l)
            sphere_world_r = head_center + R_final @ (right_sphere_local_offset * scale_ratio_r)

            # Individual gaze directions
            left_gaze_dir = normalize(left_iris - sphere_world_l)
            right_gaze_dir = normalize(right_iris - sphere_world_r)

            # Combined, smoothed direction
            raw_combined = normalize((left_gaze_dir + right_gaze_dir) / 2)
            combined_gaze_directions.append(raw_combined)
            avg_dir = normalize(np.mean(combined_gaze_directions, axis=0))



            # Convert to yaw/pitch
            gaze_history.append(avg_dir)
            isblink = np.isnan(left_iris[0]) or np.isnan(right_iris[0])
            blink_history.append(1 if isblink else 0)
            yaw,pitch = convert_gaze_to_screen_coordinates(avg_dir)
            focus_score = compute_focus_score(yaw,pitch,avg_dir,gaze_history,blink_history)
            return {'focus_score':focus_score}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5001, reload=True)