import cv2
import numpy as np
import mediapipe as mp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel,Field
from collections import deque
import time
from AI_chat import ask_AI
from DB_utils import create_timestamp, create_user,find_timestamp_this_month,find_timestamp_this_year,find_timestamp_today,create_goal,edit_goal_progress,find_timestamp_this_week,get_goals,delete_goal, login
from image_processing import compute_and_draw_coordinate_box, compute_focus_score, compute_scale, convert_gaze_to_screen_coordinates, decode_base64_image, normalize
app = FastAPI(
    title="Vercel + FastAPI",
    description="Vercel + FastAPI",
    version="1.0.0",
)
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vercel + FastAPI</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background-color: #000000;
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }

            header {
                border-bottom: 1px solid #333333;
                padding: 0;
            }

            nav {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                padding: 1rem 2rem;
                gap: 2rem;
            }

            .logo {
                font-size: 1.25rem;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
            }

            .nav-links {
                display: flex;
                gap: 1.5rem;
                margin-left: auto;
            }

            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }

            .nav-links a:hover {
                color: #ffffff;
                background-color: #111111;
            }

            main {
                flex: 1;
                max-width: 1200px;
                margin: 0 auto;
                padding: 4rem 2rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }

            .hero {
                margin-bottom: 3rem;
            }

            .hero-code {
                margin-top: 2rem;
                width: 100%;
                max-width: 900px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }

            .hero-code pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: left;
                grid-column: 1 / -1;
            }

            h1 {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 1rem;
                background: linear-gradient(to right, #ffffff, #888888);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .subtitle {
                font-size: 1.25rem;
                color: #888888;
                margin-bottom: 2rem;
                max-width: 600px;
            }

            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                width: 100%;
                max-width: 900px;
            }

            .card {
                background-color: #111111;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                transition: all 0.2s ease;
                text-align: left;
            }

            .card:hover {
                border-color: #555555;
                transform: translateY(-2px);
            }

            .card h3 {
                font-size: 1.125rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #ffffff;
            }

            .card p {
                color: #888888;
                font-size: 0.875rem;
                margin-bottom: 1rem;
            }

            .card a {
                display: inline-flex;
                align-items: center;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.875rem;
                font-weight: 500;
                padding: 0.5rem 1rem;
                background-color: #222222;
                border-radius: 6px;
                border: 1px solid #333333;
                transition: all 0.2s ease;
            }

            .card a:hover {
                background-color: #333333;
                border-color: #555555;
            }

            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background-color: #0070f3;
                color: #ffffff;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 500;
                margin-bottom: 2rem;
            }

            .status-dot {
                width: 6px;
                height: 6px;
                background-color: #00ff88;
                border-radius: 50%;
            }

            pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 1rem;
                overflow-x: auto;
                margin: 0;
            }

            code {
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                font-size: 0.85rem;
                line-height: 1.5;
                color: #ffffff;
            }

            /* Syntax highlighting */
            .keyword {
                color: #ff79c6;
            }

            .string {
                color: #f1fa8c;
            }

            .function {
                color: #50fa7b;
            }

            .class {
                color: #8be9fd;
            }

            .module {
                color: #8be9fd;
            }

            .variable {
                color: #f8f8f2;
            }

            .decorator {
                color: #ffb86c;
            }

            @media (max-width: 768px) {
                nav {
                    padding: 1rem;
                    flex-direction: column;
                    gap: 1rem;
                }

                .nav-links {
                    margin-left: 0;
                }

                main {
                    padding: 2rem 1rem;
                }

                h1 {
                    font-size: 2rem;
                }

                .hero-code {
                    grid-template-columns: 1fr;
                }

                .cards {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">Vercel + FastAPI</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="/api/data">API</a>
                </div>
            </nav>
        </header>
        <main>
            <div class="hero">
                <h1>Vercel + FastAPI</h1>
                <div class="hero-code">
                    <pre><code><span class="keyword">from</span> <span class="module">fastapi</span> <span class="keyword">import</span> <span class="class">FastAPI</span>

<span class="variable">app</span> = <span class="class">FastAPI</span>()

<span class="decorator">@app.get</span>(<span class="string">"/"</span>)
<span class="keyword">def</span> <span class="function">read_root</span>():
    <span class="keyword">return</span> {<span class="string">"Python"</span>: <span class="string">"on Vercel"</span>}</code></pre>
                </div>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>Interactive API Docs</h3>
                    <p>Explore this API's endpoints with the interactive Swagger UI. Test requests and view response schemas in real-time.</p>
                    <a href="/docs">Open Swagger UI →</a>
                </div>

                <div class="card">
                    <h3>Sample Data</h3>
                    <p>Access sample JSON data through our REST API. Perfect for testing and development purposes.</p>
                    <a href="/api/data">Get Data →</a>
                </div>

            </div>
        </main>
    </body>
    </html>
    """
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # React frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
FPS=10
LEFT_IRIS, RIGHT_IRIS = 468, 473
gaze_history = deque(maxlen=FPS*4)
blink_history = deque(maxlen=FPS*2)
# === Configuration ===
filter_length = 10       # smoothing window for gaze vector
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
mp_drawing = mp.solutions.drawing_utils
nose_indices = [4, 45, 275, 220, 440, 1, 5, 51, 281, 44, 274, 241,
                461, 125, 354, 218, 438, 195, 167, 393, 165, 391,
                3, 248]

combined_gaze_directions = deque(maxlen=filter_length)

# --- Eye sphere calibration ---
left_sphere_locked = False
right_sphere_locked = False
left_sphere_local_offset = None
right_sphere_local_offset = None
left_calibration_nose_scale = None
right_calibration_nose_scale = None
# class
class Frame(BaseModel):
    image:str
class FocusScore(BaseModel):
    userid:str
    focus_score:int
class Goal(BaseModel):
    title:str
    desc:str
    userid:str
    deadline:str
class TimeStamp(BaseModel):
    userid:str
    avgfocus_score:int
class NewProgress(BaseModel):
    new_progress:int
    id: str = Field(alias="_id")
class DeleteProgress(BaseModel):
    id: str = Field(alias="_id")
class UserInfo(BaseModel):
    userid:str
class AI_REQUEST(BaseModel):
    userid:str
    user_chat:str
class Register(BaseModel):
    email: str
    fullName: str
    password:str
class Login(BaseModel):
    email:str
    password:str
@app.post("/create_user")
def createUser(payload:Register):
    create_user(payload)
def Login(payload:Login):
    login(payload)
@app.post('/create_goal')
def createGoal(payload:Goal):
    create_goal(payload)
@app.put("/edit_goal_progress")
def editgoalProgress(payload:NewProgress):
    edit_goal_progress(payload)
@app.post('/get_goals')
def getGoals(payload: UserInfo):
    return get_goals(payload)
@app.delete("/delete_goal")
def deleteGoal(payload:DeleteProgress):
    delete_goal(payload)
@app.post("/create_timestamp")
def createTimestamp(payload:TimeStamp):
    create_timestamp(payload)
    return {'status':1}
@app.post("/get_timestamp_today")
def getTimeStampToday(payload:UserInfo):
    return find_timestamp_today(payload)
@app.post("/get_timestamp_month")
def getTimeStampThisMonth(payload:UserInfo):
    return find_timestamp_this_month(payload)
@app.post("/get_timestamp_week")
def getTimeStampThisWeek(payload:UserInfo):
    return find_timestamp_this_week(payload)
@app.post("/get_timestamp_year")
def getTimeStampThisYear(payload:UserInfo):
    return find_timestamp_this_year(payload)
@app.post("/call_ai")
def call_AI(payload:AI_REQUEST):
    new_info = UserInfo(userid=payload.userid)
    focus_history = find_timestamp_this_week(new_info)
    return ask_AI(payload.user_chat,focus_history,'week')
@app.post("/calibrate")
def calibrate(frame: Frame):
    global left_calibration_nose_scale
    global left_sphere_locked
    global left_sphere_local_offset
    global right_calibration_nose_scale
    global right_sphere_locked
    global right_sphere_local_offset
    global face_mesh
    global nose_indices
    global R_ref_nose
    base_radius = 20
    left_sphere_local_offset = None
    camera_dir_local = None
    left_sphere_local_offset = None
    left_calibration_nose_scale = None
    left_sphere_locked = None
    right_sphere_local_offset = None
    right_sphere_local_offset = None
    right_calibration_nose_scale = None
    right_sphere_locked = None
    gaze_history.clear()
    blink_history.clear()
    frame = decode_base64_image(frame.image)
    h,w,_ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    print(results)
    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0].landmark
        
        head_center, R_final, nose_points_3d = compute_and_draw_coordinate_box(
            frame, face_landmarks, nose_indices, R_ref_nose,
            color=(0,255,0),size=80
        )
        current_nose_scale = compute_scale(nose_points_3d)
        left_iris = np.array([face_landmarks[LEFT_IRIS].x * w,
                              face_landmarks[LEFT_IRIS].y * h,
                              face_landmarks[LEFT_IRIS].z * w])
        right_iris = np.array([face_landmarks[RIGHT_IRIS].x * w,
                               face_landmarks[RIGHT_IRIS].y * h,
                               face_landmarks[RIGHT_IRIS].z * w])
        print(left_iris,right_iris)
        left_sphere_local_offset = R_final.T @ (left_iris - head_center)
        camera_dir_local = R_final.T @ np.array([0, 0, 1])
        left_sphere_local_offset += base_radius * camera_dir_local
        left_calibration_nose_scale = current_nose_scale
        left_sphere_locked = True
        right_sphere_local_offset = R_final.T @ (right_iris - head_center)
        right_sphere_local_offset += base_radius * camera_dir_local
        right_calibration_nose_scale = current_nose_scale
        right_sphere_locked = True
        return {'state':'done'}
@app.post("/process")
def process_image(frame: Frame):
    global face_mesh
    global nose_indices
    global R_ref_nose
    global combined_gaze_directions
    global gaze_history
    global blink_history
    global left_calibration_nose_scale
    global left_sphere_local_offset
    global right_calibration_nose_scale
    global right_sphere_local_offset
    frame = decode_base64_image(frame.image)
    h,w,_ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
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



            # Convert to yaw/pitch
            gaze_history.append(avg_dir)
            isblink = np.isnan(left_iris[0]) or np.isnan(right_iris[0])
            blink_history.append(1 if isblink else 0)
            yaw,pitch = convert_gaze_to_screen_coordinates(avg_dir)
            focus_score = compute_focus_score(yaw,pitch,avg_dir,gaze_history,blink_history)
            return {'focus_score':focus_score}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=False)