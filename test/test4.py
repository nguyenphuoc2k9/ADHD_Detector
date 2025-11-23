import cv2
import time

def record_video_session(cap, filename, duration_sec=10):
    # 1. Get properties (can be done once outside if camera is constant)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    limited_frame = duration_sec*fps
    # 2. DEFINE and CREATE the VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))

    print(f"Recording '{filename}' for {duration_sec} seconds...")
    frame_cnt = 0
    # 3. Recording Loop
    while cap.isOpened() and frame_cnt != limited_frame:
        ret, frame = cap.read()

        if ret:
            out.write(frame)
            cv2.imshow('Recording...', frame)
            frame_cnt+=1
            # Check for a quick exit ('q' key)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # 4. CLEANUP (CRITICAL for each file)
    out.release()
    print(f"Finished recording '{filename}'.")


# --- Main Execution ---

# Initialize the camera ONCE
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Record the first file for 5 seconds
record_video_session(cap, 'video_part_1.avi', 5)
time.sleep(1) # Wait briefly before the next session

# Record the second file for 8 seconds
record_video_session(cap, 'video_part_2.avi', 8)

# Final Cleanup (release the camera itself)
cap.release()
cv2.destroyAllWindows()