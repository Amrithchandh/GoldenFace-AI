import cv2
import time
import sys
import os

# Clean import for GoldenFace
try:
    import GoldenFace
except ImportError:
    # Local fallback
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import GoldenFace

import database_helper
import random

def main():
    # Open default camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Press 'q' to quit.")
    
    database_helper.init_db()
    
    scores = []
    saved_to_db = False
    start_time = time.time()
    session_variance = random.uniform(-3.0, 3.0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        try:
            # Initialize GoldenFace with the current frame
            analysis = GoldenFace.goldenFace(frame)

            # Draw golden ratio mask and landmarks
            analysis.drawMask((0, 255, 255)) 
            analysis.drawLandmarks((0, 0, 255))
            
            # Calculate Geometric Ratio (Beauty Score)
            raw_score = analysis.geometricRatio()
            
            # Normalized Beauty Score (50-99%)
            geometric_score = 50 + (raw_score / 2) if raw_score < 50 else raw_score
            geometric_score = max(50, min(99, geometric_score))
            
            # Timer logic
            elapsed_time = time.time() - start_time
            total_duration = 60 # 1 minute
            
            if elapsed_time < total_duration:
                # Assessment in progress
                scores.append(geometric_score)
                avg_score = sum(scores) / len(scores)
                
                remaining_time = int(total_duration - elapsed_time)
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                
                status_text = f"Analyzing... {minutes:02d}:{seconds:02d}"
                score_text = f"Current Avg: {int(avg_score)}%"
                color_status = (0, 255, 255) # Yellow
                color_score = (255, 255, 255) # White
                
            else:
                # Assessment complete
                if not scores: scores.append(geometric_score)
                final_score = (sum(scores) / len(scores)) + session_variance
                final_score = max(50, min(99, final_score))
                
                if not saved_to_db:
                    database_helper.save_result(final_score, int(total_duration))
                    saved_to_db = True
                    print(f"Final Score Saved: {final_score}")
                
                status_text = "Assessment Complete (Saved)"
                score_text = f"Final Beauty Score: {int(final_score)}%"
                color_status = (0, 255, 0) # Green
                color_score = (0, 0, 255) # Red
                
            # Draw UI
            cv2.putText(analysis.img, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
            cv2.putText(analysis.img, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_status, 2)
            cv2.putText(analysis.img, score_text, (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 5)
            cv2.putText(analysis.img, score_text, (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_score, 3)
            
            # Display
            cv2.imshow('GoldenFace Live Demo', analysis.img)

        except Exception as e:
            cv2.imshow('GoldenFace Live Demo', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
