def process_result(result):
    try:
        detection_results = []
        for landmark in result.landmark:
            detection_results.append([landmark.x,landmark.y,landmark.z,landmark.visibility])
        return detection_results
    except:
        return