## Import
import cv2
import csv
import yaml
import numpy as np
import os
import math
import random
import mediapipe as mp
from pose_estimation import pose_estimation_model
from utils.detection_result_processor import process_result
from utils.get_root_dir import get_root_dir
## utils
def label_dict_from_config_file(file):
    with open(file,"r") as f:
        label_tag = yaml.full_load(f)["attention"]
    return label_tag
class DatasetWriter:
    def __init__(self,file):
        self.csv_file = open(file,"a")
        self.csv_writer = csv.writer(self.csv_file,delimiter=",",quotechar="|",quoting=csv.QUOTE_MINIMAL)
    def add(self,landmark,label):
        print(landmark,label)
        self.csv_writer.writerow([label,*np.array(landmark).flatten().tolist()])
    def close(self):
        self.csv_file.close()
## main code
def run(data_path,detection_model=None,split="train",resolution=(1280,720)):
    
    
    # video_list = os.listdir(data_path)
    # while True:
    #     path = os.path.join(data_path,video_list[0])
    #     cap = cv2.VideoCapture(path)
    #     delay = 10
    #     while cap.isOpened():
    #         _,frame = cap.read()
        
    #         cv2.imshow("Video",frame)
        
    #         key = cv2.waitKey(delay) & 0xFF
    #         if(key == ord("f")):
    #             delay-=1
    #         elif key == ord("s"):
    #             delay+=1
            
            
    PoseModel = pose_estimation_model(detection_model)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS,16)
    cap.set(3,resolution[0])
    cap.set(4,resolution[1])
    
    os.makedirs(data_path,exist_ok=True)
    
    dataset_path = os.path.join(os.path.join(data_path,f"landmark_{split}.csv"))
    dataset = DatasetWriter(dataset_path)
    time_frame = 0
    while cap.isOpened():
        _,frame = cap.read()
        
        image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        image = np.array(image,dtype=np.uint8)
        image = mp.Image(image_format=mp.ImageFormat.SRGB,data=image)
        result,annotated_image = PoseModel(image)
        result = process_result(result)
        annotated_image = cv2.cvtColor(annotated_image,cv2.COLOR_RGB2BGR)
        key = cv2.waitKey(10) & 0xFF
        
        cv2.imshow("Data Collector",annotated_image)
        if key == ord("r"):
            key = int(cv2.waitKey(0) & 0xFF)
            if key <=51:
                dataset.add(result,key-48)
        elif key==ord("q"):
            break
        
        time_frame+=1
    cv2.destroyAllWindows()
    dataset.close()


if __name__=="__main__":
    ## Config
    root = os.path.dirname(get_root_dir())
    print(root)
    model = os.path.join(root,"model\pose_landmarker_heavy.task")
    config_file = os.path.join(root,"attention.yaml")
    data_path = os.path.join(root,"data")
    
    LABEL_TAG = label_dict_from_config_file(config_file)
    # run
    run(data_path,model,"train",resolution=(1280,720))
    run(data_path,model,"val",resolution=(1280,720))
    run(data_path,model,"test",resolution=(1280,720))
    