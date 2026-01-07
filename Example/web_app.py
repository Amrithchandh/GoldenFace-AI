from flask import Flask, render_template, Response
import cv2
import time
import random
import sys
import os

# Import GoldenFace library
import GoldenFace
import database_helper

app = Flask(__name__)

# Global State
class AppState:
    def __init__(self):
        self.scores = []
        self.start_time = None
        self.duration = 60
        self.is_running = False
        self.saved_to_db = False
        self.session_variance = random.uniform(-3.0, 3.0)
        self.final_score = 0
        self.current_score = 0
        self.status = "Ready"
        self.timer_text = "00:00"

state = AppState()

# Initialize Database
database_helper.init_db()

def generate_frames():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    state.start_time = time.time()
    state.is_running = True
    state.scores = []
    state.saved_to_db = False
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        try:
            # 1. Analysis
            analysis = GoldenFace.goldenFace(frame)
            analysis.drawFaceCovar((0, 255, 255))
            analysis.drawLandmarks((0, 0, 255))
            
            raw_score = analysis.geometricRatio()
             # Ensure min 50%
            if raw_score < 50:
                geometric_score = 50 + (raw_score / 2)
            else:
                geometric_score = raw_score
            geometric_score = max(50, geometric_score)
            
            # 2. Logic
            elapsed = time.time() - state.start_time
            
            if elapsed < state.duration:
                # Assessing
                state.scores.append(geometric_score)
                state.current_score = sum(state.scores) / len(state.scores)
                
                remaining = int(state.duration - elapsed)
                m, s = divmod(remaining, 60)
                state.timer_text = f"{m:02d}:{s:02d}"
                state.status = "Analyzing..."
                
                # Draw Info on Frame
                cv2.putText(analysis.img, f"Status: {state.status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                cv2.putText(analysis.img, f"Time: {state.timer_text}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(analysis.img, f"Score: {int(state.current_score)}%", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
            else:
                # Done
                state.timer_text = "00:00"
                if not state.scores: state.scores.append(geometric_score)
                
                if not state.saved_to_db:
                    final_val = (sum(state.scores) / len(state.scores)) + state.session_variance
                    state.final_score = max(50, min(99, final_val))
                    database_helper.save_result(state.final_score, state.duration)
                    state.saved_to_db = True
                    state.status = "Completed"
                
                # Draw Info
                cv2.putText(analysis.img, "Assessment Complete", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(analysis.img, f"FINAL SCORE: {int(state.final_score)}%", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            processed_frame = analysis.img
            
        except Exception:
            # Fallback if no face
            processed_frame = frame
            cv2.putText(processed_frame, "Face Not Found", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Encode
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("Starting Flask Server...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
