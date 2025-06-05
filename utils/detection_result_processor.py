def process_result(result):
    detection_results = []
    for landmark in result.pose_landmarks[0]:
        detection_results.append([landmark.x,landmark.y,landmark.z,landmark.visibility])
    return detection_results