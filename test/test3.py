import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                  max_num_faces=1,
                                  refine_landmarks=True,
                                  min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)

# Define a simplified 3D face model (approx landmark coordinates in 3D)
# We only need a few stable points: nose, eyes, mouth corners
FACE_3D_POINTS = np.array([
    (0.0, 0.0, 0.0),    # Nose tip
    (0.0, -330.0, -65.0),  # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),  # Right eye right corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0, -150.0, -125.0)   # Right mouth corner
], dtype=np.float64)

# Corresponding Mediapipe landmarks (indices for nose, chin, eyes, mouth)
FACE_LANDMARK_IDS = [1, 152, 33, 263, 61, 291]

# Start webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    img_h, img_w = frame.shape[:2]

    # Convert to RGB for mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        # 2D landmarks in image plane
        face_2d = []
        for idx in FACE_LANDMARK_IDS:
            x = int(face_landmarks.landmark[idx].x * img_w)
            y = int(face_landmarks.landmark[idx].y * img_h)
            face_2d.append([x, y])

        face_2d = np.array(face_2d, dtype=np.float64)

        # Camera matrix
        focal_length = img_w
        cam_matrix = np.array([[focal_length, 0, img_w/2],
                               [0, focal_length, img_h/2],
                               [0, 0, 1]], dtype=np.float64)

        # Distortion coefficients (assume no distortion)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # SolvePnP to get rotation and translation
        success, rot_vec, trans_vec = cv2.solvePnP(FACE_3D_POINTS,
                                                   face_2d,
                                                   cam_matrix,
                                                   dist_coeffs)

        # Convert rotation vector to rotation matrix
        rmat, _ = cv2.Rodrigues(rot_vec)

        # Safe Euler extraction
        sy = math.sqrt(rmat[0, 0] * rmat[0, 0] + rmat[1, 0] * rmat[1, 0])

        singular = sy < 1e-6

        if not singular:
            pitch = math.atan2(rmat[2, 1], rmat[2, 2])
            yaw = math.atan2(-rmat[2, 0], sy)
            roll = math.atan2(rmat[1, 0], rmat[0, 0])
        else:
            pitch = math.atan2(-rmat[1, 2], rmat[1, 1])
            yaw = math.atan2(-rmat[2, 0], sy)
            roll = 0

        # Convert to degrees
        pitch = math.degrees(pitch)
        yaw = math.degrees(yaw)
        roll = math.degrees(roll)

        # Display
        cv2.putText(frame, f"Yaw: {int(yaw)} Pitch: {int(pitch)} Roll: {int(roll)}",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Head Pose Estimation (PnP)", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
