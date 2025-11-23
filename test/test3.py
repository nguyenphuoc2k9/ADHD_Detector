import cv2
import numpy as np
import mediapipe as mp
import math
from scipy.spatial.transform import Rotation as Rscipy
from collections import deque
import os
import json
def get_root_dir():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    root_dir = os.path.dirname(script_dir)
    return root_dir
# === Configuration ===
filter_length = 10       # smoothing window for gaze vector
gaze_length = 300        # line length for visualization

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
hand_model  = mp_hand_mesh.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
)
mp_drawing = mp.solutions.drawing_utils



# === Open Webcam ===
FPS = 16
cap = cv2.VideoCapture(0)
cap_2 = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FPS,FPS)
cap_2.set(cv2.CAP_PROP_FPS,FPS)
w_2 = int(cap_2.get(cv2.CAP_PROP_FRAME_WIDTH))
h_2 = int(cap_2.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# === Video Writer ===
fourcc = cv2.VideoWriter_fourcc(*"MJPG")
video_folder_path = os.path.join(get_root_dir(),"record_data")
video_filename_list = os.listdir(video_folder_path)
video_id = 0
if len(video_filename_list) > 0:
    video_id = int(video_filename_list[-1].split(".")[0].split("_")[-1])+1
video_hand_filename = os.path.join(video_folder_path,"hand",video_id)
video_face_filename = os.path.join(video_folder_path,"face",video_id)
out_hand= cv2.VideoWriter(video_hand_filename,fourcc,FPS,(w_2,h_2))
out_face= cv2.VideoWriter(video_face_filename,fourcc,FPS,(w,h))
# === Nose landmark indices for stable head orientation ===
nose_indices = [4, 45, 275, 220, 440, 1, 5, 51, 281, 44, 274, 241,
                461, 125, 354, 218, 438, 195, 167, 393, 165, 391,
                3, 248]

# === Iris landmark indices ===
LEFT_IRIS, RIGHT_IRIS = 468, 473

# --- Utility functions ---

def draw_hand_landmark(frame,hand_landmarks):
    global mp_hand_mesh
    mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hand_mesh.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style()
    )
def convert_gaze_to_screen_coordinates(combined_gaze_direction):
    """
    Convert 3D gaze direction vector to 2D screen coordinates
    This function is adapted from the old script's vector-to-screen mapping logic
    """
    # Reference forward direction (camera looking straight ahead)
    reference_forward = np.array([0, 0, -1])  # Z-axis into the screen

    # Normalize the gaze direction
    avg_direction = combined_gaze_direction / np.linalg.norm(combined_gaze_direction)

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

    # Convert to degrees and re-center around 0
    yaw_deg = np.degrees(yaw_rad)
    pitch_deg = np.degrees(pitch_rad)

    # Convert left rotations to 0-180 (from old script logic)
    if yaw_deg < 0:
        yaw_deg = -(yaw_deg)
    elif yaw_deg > 0:
        yaw_deg = - yaw_deg

    #yaw is now converted to -90 (looking directly left) to +90 (looking directly right), wrt camera
    #pitch is now converted to +90 (looking straight up) and -90 (looking straight down), wrt camera
    
    raw_yaw_deg = yaw_deg
    raw_pitch_deg = pitch_deg

    return  raw_yaw_deg, raw_pitch_deg

def normalize(v):
    v = np.array(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def compute_scale(points_3d):
    # Average pairwise distance (for scale stability)
    n = len(points_3d)
    total, count = 0, 0
    for i in range(n):
        for j in range(i + 1, n):
            total += np.linalg.norm(points_3d[i] - points_3d[j])
            count += 1
    return total / count if count > 0 else 1.0

def draw_wireframe_cube(frame, center, R, size=80):
    right = R[:, 0]
    up = -R[:, 1]
    forward = -R[:, 2]
    hw = hh = hd = size

    def corner(x, y, z):
        return (center + x*hw*right + y*hh*up + z*hd*forward)

    corners = [corner(x, y, z)
               for x in [-1, 1] for y in [1, -1] for z in [-1, 1]]
    projected = [(int(pt[0]), int(pt[1])) for pt in corners]
    edges = [
        (0,1),(1,3),(3,2),(2,0),
        (4,5),(5,7),(7,6),(6,4),
        (0,4),(1,5),(2,6),(3,7)
    ]
    for i, j in edges:
        cv2.line(frame, projected[i], projected[j], (255, 128, 0), 1)

def compute_and_draw_coordinate_box(frame, face_landmarks, indices,
                                    ref_matrix_container, color=(0,255,0), size=80):
    points_3d = np.array([
        [face_landmarks[i].x * w,
         face_landmarks[i].y * h,
         face_landmarks[i].z * w]
        for i in indices
    ])
    center = np.mean(points_3d, axis=0)

    # PCA orientation
    centered = points_3d - center
    cov = np.cov(centered.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    eigvecs = eigvecs[:, np.argsort(-eigvals)]
    if np.linalg.det(eigvecs) < 0:
        eigvecs[:, 2] *= -1

    R_final = eigvecs.copy()

    # Stabilize eigenvector flips
    if ref_matrix_container[0] is None:
        ref_matrix_container[0] = R_final.copy()
    else:
        R_ref = ref_matrix_container[0]
        for i in range(3):
            if np.dot(R_final[:, i], R_ref[:, i]) < 0:
                R_final[:, i] *= -1

    draw_wireframe_cube(frame, center, R_final, size)
    return center, R_final, points_3d

# --- Buffers ---
combined_gaze_directions = deque(maxlen=filter_length)

# --- Eye sphere calibration ---
left_sphere_locked = False
right_sphere_locked = False
left_sphere_local_offset = None
right_sphere_local_offset = None
left_calibration_nose_scale = None
right_calibration_nose_scale = None

# === Main loop ===
video_duration = 15
frame_limit = video_duration*FPS
frame_cnt = 0
data = []
hand_data = []
face_data = []
while cap.isOpened() and cap_2.isOpened():
    ret1, frame = cap.read()
    ret2, hand_frame = cap_2.read()
    recored_face_frame = frame.copy()
    recored_hand_frame = hand_frame.copy()
    if not ret1 or not ret2:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_rgb = cv2.cvtColor(hand_frame,cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    hand_results = hand_model.process(hand_rgb)
    
    if hand_results.multi_hand_landmarks:
        hand_row = []
        cnt_hand = 0
            
        for hand_landmark in hand_results.multi_hand_landmarks:
            draw_hand_landmark(hand_frame,hand_landmark)
            temp = []
            for landmark in hand_landmark.landmark:
                temp.append([landmark.x,landmark.y,landmark.z])
            hand_row.append(temp)
            cnt_hand+=1
        print(cnt_hand)
        if len(hand_row) < 2:
            hand_row = np.stack((np.zeros(1,21,3),np.array(hand_row)),axis=0).tolist()
    
    else:
        hand_row = np.zeros((2,21,3)).tolist()
    hand_data.append(hand_row)
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
        key = cv2.waitKey(1) & 0xFF
        if key == ord("c") and not (left_sphere_locked and right_sphere_locked):
            base_radius = 20
            left_sphere_local_offset = R_final.T @ (left_iris - head_center)
            camera_dir_local = R_final.T @ np.array([0, 0, 1])
            left_sphere_local_offset += base_radius * camera_dir_local
            left_calibration_nose_scale = current_nose_scale
            left_sphere_locked = True

            right_sphere_local_offset = R_final.T @ (right_iris - head_center)
            right_sphere_local_offset += base_radius * camera_dir_local
            right_calibration_nose_scale = current_nose_scale
            right_sphere_locked = True

            print("[Calibration] Eye spheres locked.")
            continue
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

            # Draw per-eye gaze
            for eye_center, gaze_dir, color in [
                (sphere_world_l, left_gaze_dir, (255, 255, 0)),
                (sphere_world_r, right_gaze_dir, (0, 255, 255))
            ]:
                start = (int(eye_center[0]), int(eye_center[1]))
                end = (int(eye_center[0] + gaze_dir[0]*gaze_length),
                       int(eye_center[1] + gaze_dir[1]*gaze_length))
                cv2.line(frame, start, end, color, 2)

            # Draw combined average gaze (green)
            origin = (sphere_world_l + sphere_world_r) / 2
            end = origin + avg_dir * gaze_length
            cv2.line(frame,
                     (int(origin[0]), int(origin[1])),
                     (int(end[0]), int(end[1])),
                     (0, 255, 0), 3)

            # Convert to yaw/pitch
            yaw,pitch = convert_gaze_to_screen_coordinates(avg_dir)
            cv2.putText(frame, f"Yaw: {yaw:+.1f}°", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Pitch: {pitch:+.1f}°", (30, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            face_row = [left_gaze_dir,right_gaze_dir]
            face_data.append(face_row)
            if frame_cnt == frame_limit:
                data = {
                    "face_data": face_data,
                    "hand_data":hand_data
                }
                face_data = []
                hand_data = []
                out_hand.release()
                out_face.release()
                frame_cnt = 0
                video_hand_filename = os.path.join(video_folder_path,"hand",f"_{video_id}.avi")
                video_face_filename = os.path.join(video_folder_path,"face",f"_{video_id}.avi")
                log_filename = os.path.join(video_folder_path,"log",f"_{video_id}.json")
                out_hand= cv2.VideoWriter(video_hand_filename,fourcc,FPS,(w_2,h_2))
                out_face= cv2.VideoWriter(video_face_filename,fourcc,FPS,(w,h))
                with open(log_filename,"w") as f:
                    json.dump(data,f,indent=4)
                frame_cnt +=1
                out_hand.write(recored_hand_frame)
                out_face.write(recored_face_frame)
    cv2.imshow("Accurate Eye Gaze Tracking (No Screen Mapping)", frame)
    cv2.imshow("hand camera",hand_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord("t"):
                break

cap.release()
cv2.destroyAllWindows()
