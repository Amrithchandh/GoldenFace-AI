import cv2
import GoldenFace
import time

def main():
    # Open default camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Press 'q' to quit.")
    
    # Initialize Database
    import database_helper
    import random
    database_helper.init_db()
    
    scores = []
    saved_to_db = False
    start_time = time.time()
    
    # Session Variance: Adds a small random factor (-3% to +3%) to each session 
    # so the result varies slightly every time you run it.
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
            # Use yellow for mask
            analysis.drawMask((0, 255, 255)) 
            # Use red for landmarks
            analysis.drawLandmarks((0, 0, 255))
            
            # Calculate Geometric Ratio (Beauty Score)
            raw_score = analysis.geometricRatio()
            
            # User Requirement: Never show below 50%
            if raw_score < 50:
                geometric_score = 50 + (raw_score / 2) # Curve it slightly so it varies but stays above 50
            else:
                geometric_score = raw_score
            
            # Ensure it is at least 50 hard limit if math goes wrong
            geometric_score = max(50, geometric_score)
            
            # Timer logic
            elapsed_time = time.time() - start_time
            total_duration = 60 # 1 minute in seconds
            
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
                # Assessment complete (Fixed Score)
                # Use the calculated average from the full duration + Session Variance
                if not scores: scores.append(geometric_score)
                final_score = (sum(scores) / len(scores)) + session_variance
                
                # Ensure it stays within realistic bounds (50-99)
                final_score = max(50, min(99, final_score))
                
                # Save to Database (Once)
                if not saved_to_db:
                    database_helper.save_result(final_score, int(total_duration))
                    saved_to_db = True
                    print(f"Final Score Saved: {final_score}")
                
                status_text = "Assessment Complete (Saved)"
                score_text = f"Final Beauty Score: {int(final_score)}%"
                color_status = (0, 255, 0) # Green
                color_score = (0, 0, 255) # Red (Result)

            # Draw UI
            # Status (Timer/Complete)
            cv2.putText(analysis.img, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
            cv2.putText(analysis.img, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_status, 2)
            
            # Score
            cv2.putText(analysis.img, score_text, (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 5)
            cv2.putText(analysis.img, score_text, (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_score, 3)
            
            # Print to console
            print(f"{status_text} | {score_text}")

            # Display the resulting frame
            cv2.imshow('GoldenFace Camera Example', analysis.img)

        except Exception as e:
            # If no face is detected or other error, just show the original frame
            # print(f"Processing error (no face detected?): {e}")
            cv2.imshow('GoldenFace Camera Example', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
