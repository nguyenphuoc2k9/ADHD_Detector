import mediapipe as mp
import cv2
import torch
import torch.nn as nn
import numpy as np
import json
import os
from utils.detection_result_processor import process_result
from utils.image_visualizer import draw_landmarks_on_image
training_data_dir = "./training_data"
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
model = "./model/pose_landmarker_heavy.task"

options = PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),)
class ClassificationModel(nn.Module):
    def __init__(self):
        self.model = nn.Sequential(
            
        )
        # class 0: focus; 1: rotated > 45 degree; 2: hand_unsual_movement; 3: undefined
def run_detection():
    frame = 0
    detector = PoseLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(0)
    dataset = []
    cap.set(cv2.CAP_PROP_FPS,16)
    while cap.isOpened():
            _,frame=  cap.read()
            image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            image = np.array(image,dtype=np.uint8)
            image = mp.Image(image_format=mp.ImageFormat.SRGB,data=image)
            result = detector.detect(image)
            
            annotated_image = draw_landmarks_on_image(image.numpy_view(),result)
            cv2.imshow("Pose Estimation",cv2.cvtColor(annotated_image,cv2.COLOR_RGB2BGR))
            
            key = cv2.waitKey(10) & 0xFF
            if key == ord("r"):
                key = cv2.waitKey(0) & 0xFF
                data = {
                    "landmarks": process_result(result),
                    "class": 0
                }
                if key == ord("0") :
                    dataset.append(data)
                elif key == ord("1"):
                    data['class'] = 1
                    dataset.append(data)
                elif key ==ord("2"):
                    data['class'] = 2
                    dataset.append(data)
                else:
                    print("undefined class")
            elif key == ord("q"):
                list_file = os.listdir(training_data_dir)
                if len(list_file) == 0:
                    last_num = 1
                else:
                    last_num = int(list_file[-1].split(".")[0].split("_")[-1])+1
                
                with open(f"./training_data/data_{last_num}","w") as f:
                    json.dump(dataset,f,indent=2)
                    dataset = []
                break
    cv2.destroyAllWindows()
run_detection()