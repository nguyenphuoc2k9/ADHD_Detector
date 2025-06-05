import mediapipe as mp
import cv2
import torch
import torch.nn as nn
import numpy as np
from utils.detection_result_processor import process_result
from utils.image_visualizer import draw_landmarks_on_image
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
model = "./model/pose_landmarker_lite.task"

options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),)
class ClassificationModel(nn.Module):
    def __init__(self):
        self.model = nn.Sequential(
            
        )
def run_detection():
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    frame = 0
    detector = PoseLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(0)
    detection_results = []
    cap.set(cv2.CAP_PROP_FPS,16)
    while cap.isOpened():
            _,frame=  cap.read()
            image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            image = np.array(image,dtype=np.uint8)
            image = mp.Image(image_format=mp.ImageFormat.SRGB,data=image)
            result = detector.detect(image)
            
            annotated_image = draw_landmarks_on_image(image.numpy_view(),result)
            cv2.imshow("Pose Estimation",cv2.cvtColor(annotated_image,cv2.COLOR_RGB2BGR))
            # frame +=1
            # detection_results.append(process_result(result))
            cv2.waitKey(10)

run_detection()