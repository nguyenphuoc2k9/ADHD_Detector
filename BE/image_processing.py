import cv2
import base64
import numpy as np
import mediapipe as mp
import math
import os
import json
def decode_base64_image(base64_img):
    img_bytes = base64.b64decode(base64_img.split(",")[1])
    img_np = np.frombuffer(img_bytes,np.uint8)
    return cv2.imdecode(img_np,cv2.IMREAD_COLOR)
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
def compute_focus_score(yaw,pitch,avg_dir,gaze_history,blink_history):
    MAX_YAW = 20
    MAX_PITCH = 20
    yaw_norm = max(0,1-abs(yaw)/MAX_YAW)
    pitch_norm = max(0,1-abs(pitch)/MAX_PITCH)
    GazeCenterScore = (yaw_norm+pitch_norm)/2
    
    if(len(gaze_history)) >= 40:
        gaze_std = np.std(gaze_history,axis=0)
        instability = np.linalg.norm(gaze_std)
        instability_clamped = min(instability/0.15,1.0)
        GazeStabilityScore = 1- instability_clamped
    else:
        
        GazeStabilityScore = 1.0
    if len(blink_history) >= 40:
        blink_rate = sum(blink_history) / len(blink_history)
    else:
        blink_rate = 0
    if blink_rate < 0.05:
        BlinkAttentionScore = 1.0
    elif blink_rate < 0.15:
        BlinkAttentionScore = 0.7
    else:
        blink_rate = 0.4
    w1,w2,w3 = 0.55,0.40,0.05
    FocusScore = (
        w1*GazeCenterScore +
        w2*GazeStabilityScore +
        w3*BlinkAttentionScore
    )
    return max(0,min(FocusScore,1))
def compute_and_draw_coordinate_box(frame, face_landmarks, indices,
                                    ref_matrix_container, color=(0,255,0), size=80):
    h,w,_ = frame.shape
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