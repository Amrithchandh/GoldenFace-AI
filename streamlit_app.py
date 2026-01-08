import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
import os

# Clean import for GoldenFace (folder must be named GoldenFace)
try:
    import GoldenFace
except ImportError:
    # Local fallback in case of path issues
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        import GoldenFace
    except ImportError:
        st.error("### ❌ GoldenFace library not found!")
        st.info("The folder 'GoldenFace' must be in your repository root.")
        st.stop()

st.set_page_config(page_title="GoldenFace AI", layout="centered")

st.title("🔬 GoldenFace – Facial Beauty Analyzer")
st.markdown("Assess facial geometric ratios using your camera or by uploading a portrait.")

# Sidebar for options
st.sidebar.title("Options")
input_mode = st.sidebar.radio("Choose Input Mode", ["Upload Image", "Take a Photo"])

uploaded_file = None
if input_mode == "Upload Image":
    uploaded_file = st.file_uploader("Choose a portrait image (jpg/png)", type=["jpg", "jpeg", "png"])
else:
    uploaded_file = st.camera_input("Smile for the AI!")

if uploaded_file is not None:
    try:
        # Correctly read image data from bytes
        file_bytes = np.asarray(bytearray(uploaded_file.getvalue()), dtype=np.uint8)
        bgr_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if bgr_image is None:
            st.error("Could not decode image. Please try a different format or file.")
        else:
            with st.spinner("Analyzing face..."):
                analysis = GoldenFace.goldenFace(bgr_image)
                
                # Check if faces were detected
                if not hasattr(analysis, 'faceBorders') or analysis.faceBorders is None:
                    st.warning("No face detected in the image. Please try again with a clear portrait.")
                else:
                    # Draw visualizations
                    analysis.drawFaceCover((0, 255, 255))  # yellow mask
                    analysis.drawLandmarks((0, 0, 255))    # red dots
                    
                    # Compute score
                    raw_score = analysis.geometricRatio()
                    # Normalized Beauty Score (50-99%)
                    geometric_score = 50 + raw_score / 2 if raw_score < 50 else raw_score
                    geometric_score = max(50, min(99, geometric_score))

                    # Convert result for display
                    rgb_image = cv2.cvtColor(analysis.img, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb_image)

                    # Layout for results
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.image(pil_img, caption="Analyzed Result", use_column_width=True)
                    with col2:
                        st.subheader("Results")
                        st.metric(label="Beauty Score", value=f"{int(geometric_score)}%")
                        st.write("The score is based on facial geometric ratios.")
    
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
else:
    st.info("Waiting for image input...")
