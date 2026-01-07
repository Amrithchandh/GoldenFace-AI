import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time
import random
import threading
import sys
import os

# Add parent directory to path to import Library Source if needed, 
# though 'pip install -e .' should handle it.
import GoldenFace.Library_Source as GoldenFace
import database_helper

class GoldenFaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GoldenFace AI Assessment")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e") # Dark background

        # --- Variables ---
        self.is_running = False
        self.scores = []
        self.start_time = None
        self.duration = 60
        self.session_variance = random.uniform(-3.0, 3.0)
        self.saved_to_db = False
        
        # --- UI Layout ---
        self.setup_ui()
        
        # --- Camera Setup ---
        self.cap = None
        self.video_thread = None
        
        # Initialize Database
        database_helper.init_db()

    def setup_ui(self):
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 12))
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground="#ffd700") # Gold color
        style.configure("Score.TLabel", font=("Segoe UI", 48, "bold"), foreground="#00ff00")
        
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#333333", foreground="white")
        style.map("TButton", background=[("active", "#444444")])

        # Main Containers
        left_panel = ttk.Frame(self.root, width=700)
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        right_panel = ttk.Frame(self.root, width=300)
        right_panel.pack(side="right", fill="y", padx=10, pady=10)

        # --- Left Panel (Video) ---
        title_lbl = ttk.Label(left_panel, text="Live Analysis", style="Header.TLabel")
        title_lbl.pack(pady=(0, 10))
        
        self.video_label = tk.Label(left_panel, bg="black")
        self.video_label.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Right Panel (Controls & Stats) ---
        
        # Header
        app_title = ttk.Label(right_panel, text="GOLDEN FACE", style="Header.TLabel")
        app_title.pack(pady=20)

        # Timer
        self.timer_var = tk.StringVar(value="00:00")
        timer_lbl = tk.Label(right_panel, textvariable=self.timer_var, font=("Consolas", 36), bg="#1e1e1e", fg="#00ffff")
        timer_lbl.pack(pady=10)
        
        status_lbl = ttk.Label(right_panel, text="Status: Ready")
        status_lbl.pack()
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(right_panel, textvariable=self.status_var, bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 10)).pack(pady=5)

        # Separator
        ttk.Separator(right_panel, orient="horizontal").pack(fill="x", pady=20)

        # Score Display
        ttk.Label(right_panel, text="Beauty Score").pack()
        self.score_var = tk.StringVar(value="--%")
        self.score_lbl = ttk.Label(right_panel, textvariable=self.score_var, style="Score.TLabel")
        self.score_lbl.pack(pady=10)

        # Buttons
        self.btn_start = tk.Button(right_panel, text="Start Camera", command=self.start_camera, 
                                   bg="#007acc", fg="white", font=("Segoe UI", 14, "bold"), relief="flat", padx=20, pady=10)
        self.btn_start.pack(fill="x", pady=10)
        
        self.btn_stop = tk.Button(right_panel, text="Stop Camera", command=self.stop_camera, 
                                  bg="#c42b1c", fg="white", font=("Segoe UI", 14, "bold"), relief="flat", padx=20, pady=10)
        self.btn_stop.pack(fill="x", pady=10)
        
        # Footer
        ttk.Label(right_panel, text="v2.0 - Standard Edition", font=("Segoe UI", 8), foreground="#555555").pack(side="bottom", pady=10)

    def start_camera(self):
        if self.is_running: return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_var.set("Error: Camera not found")
            return
            
        self.is_running = True
        self.scores = []
        self.saved_to_db = False
        self.start_time = time.time()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_var.set("Initializing AI...")
        
        # Start video loop
        self.update_frame()

    def stop_camera(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image="")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_var.set("Stopped")

    def update_frame(self):
        if not self.is_running: return

        ret, frame = self.cap.read()
        if ret:
            # 1. AI Analysis
            try:
                # GoldenFace library expects BGR image (OpenCV standard)
                analysis = GoldenFace.goldenFace(frame) 
                
                # Draw landmarks
                analysis.drawFaceCovar((0, 255, 255)) # Yellow mask
                analysis.drawLandmarks((0, 0, 255))   # Red dots
                
                # Calculate Score
                raw_score = analysis.geometricRatio()
                
                # Ensure min 50%
                if raw_score < 50:
                    geometric_score = 50 + (raw_score / 2)
                else:
                    geometric_score = raw_score
                geometric_score = max(50, geometric_score)
                
                # Process processed frame
                frame = analysis.img
                
                # 2. Logic (Timer & Average)
                elapsed = time.time() - self.start_time
                
                if elapsed < self.duration:
                    # Assessing
                    self.scores.append(geometric_score)
                    
                    # Update Timer
                    remaining = int(self.duration - elapsed)
                    m, s = divmod(remaining, 60)
                    self.timer_var.set(f"{m:02d}:{s:02d}")
                    
                    # Update Running Average
                    avg = sum(self.scores) / len(self.scores)
                    self.score_var.set(f"{int(avg)}%")
                    self.score_lbl.configure(foreground="#ffff00") # Yellow while running
                    self.status_var.set("Analyzing Face Structure...")
                    
                else:
                    # Assessment Complete
                    self.timer_var.set("00:00")
                    
                    # Calculate Final
                    if not self.scores: self.scores.append(geometric_score)
                    final_score = (sum(self.scores) / len(self.scores)) + self.session_variance
                    final_score = max(50, min(99, final_score))
                    
                    self.score_var.set(f"{int(final_score)}%")
                    self.score_lbl.configure(foreground="#00ff00") # Green when done
                    
                    # Save Logic
                    if not self.saved_to_db:
                        database_helper.save_result(final_score, self.duration)
                        self.saved_to_db = True
                        self.status_var.set("Assessment Complete (Saved)")
                    else:
                        self.status_var.set("Assessment Complete")
            
            except Exception as e:
                # If no face found or other error
                # print(e) 
                self.status_var.set("Looking for face...")

            # 3. Display in Tkinter
            # Convert BGR (OpenCV) to RGB (PIL/Tkinter)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Resize logic (keep aspect ratio)
            w, h = img.size
            aspect = w/h
            
            # Label size
            lbl_w = self.video_label.winfo_width()
            lbl_h = self.video_label.winfo_height()
            
            if lbl_w > 1 and lbl_h > 1: # Only resize if we have dimensions
                if lbl_w / lbl_h > aspect:
                    new_h = lbl_h
                    new_w = int(new_h * aspect)
                else:
                    new_w = lbl_w
                    new_h = int(new_w / aspect)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk # Keep reference
            self.video_label.config(image=imgtk)

        # Schedule next update (30ms = ~33 FPS)
        self.root.after(30, self.update_frame)

    def on_closing(self):
        self.stop_camera()
        self.root.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GoldenFaceApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except KeyboardInterrupt:
        pass
