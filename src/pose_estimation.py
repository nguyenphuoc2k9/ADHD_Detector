import mediapipe as mp
import cv2
import numpy as np
import json
import os
from utils.detection_result_processor import process_result
from utils.image_visualizer import draw_landmarks_on_image

class pose_estimation_model:
    def __init__(self,model_path):
        # Mediapipe config
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        # Model options
        options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model_path))
        # detector
        self.detector = PoseLandmarker.create_from_options(options)
    def __call__(self,frame):
        result = self.detector.detect(frame)
        annotated_image = draw_landmarks_on_image(frame.numpy_view(),result)
        
        return result,annotated_image
        
        