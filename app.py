import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import tempfile
import time
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Helmet Detection System",
    page_icon="🏍️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for violations
if 'violations' not in st.session_state:
    st.session_state.violations = []

# Load model
@st.cache_resource
def load_model(model_path):
    """Load YOLOv8 model"""
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

def detect_violations(results, conf_threshold=0.5):
    """
    Detect helmet violations
    Returns: list of violations with bounding boxes
    """
    violations = []
    
    for result in results:
        boxes = result.boxes
        
        has_no_helmet = False
        no_helmet_box = None
        number_plate_box = None
        
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = result.names[cls]
            
            if conf >= conf_threshold:
                if class_name == 'no_helmet':
                    has_no_helmet = True
                    no_helmet_box = box.xyxy[0].cpu().numpy()
                elif class_name == 'number_plate':
                    number_plate_box = box.xyxy[0].cpu().numpy()
        
        # If no helmet detected, record violation
        if has_no_helmet:
            violations.append({
                'no_helmet_box': no_helmet_box,
                'plate_box': number_plate_box,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return violations

def draw_detections(image, results, conf_threshold=0.5):
    """
    Draw bounding boxes on image
    """
    img = image.copy()
    
    for result in results:
        boxes = result.boxes
        
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = result.names[cls]
            
            if conf >= conf_threshold:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                
                # Set color based on class
                if class_name == 'helmet':
                    color = (0, 255, 0)  # Green for helmet
                elif class_name == 'no_helmet':
                    color = (0, 0, 255)  # Red for no helmet
                elif class_name == 'number_plate':
                    color = (255, 255, 0)  # Yellow for plate
                else:  # rider
                    color = (255, 165, 0)  # Orange for rider
                
                # Draw rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name}: {conf:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
                )
                cv2.rectangle(
                    img,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width, y1),
                    color,
                    -1
                )
                cv2.putText(
                    img,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )
    
    return img

def process_image(image, model, conf_threshold):
    """Process a single image"""
    # Convert PIL to numpy array
    img_array = np.array(image)
    
    # Run detection
    results = model(img_array, conf=conf_threshold)
    
    # Draw detections
    img_with_boxes = draw_detections(img_array, results, conf_threshold)
    
    # Detect violations
    violations = detect_violations(results, conf_threshold)
    
    return img_with_boxes, results, violations

def process_video(video_path, model, conf_threshold, progress_bar, status_text):
    """Process video file"""
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create temporary output file
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    video_violations = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run detection
        results = model(frame, conf=conf_threshold)
        
        # Draw detections
        frame_with_boxes = draw_detections(frame, results, conf_threshold)
        
        # Detect violations
        violations = detect_violations(results, conf_threshold)
        if violations:
            video_violations.extend(violations)
        
        # Write frame
        out.write(frame_with_boxes)
        
        # Update progress
        frame_count += 1
        progress = frame_count / total_frames
        progress_bar.progress(progress)
        status_text.text(f"Processing frame {frame_count}/{total_frames}")
    
    cap.release()
    out.release()
    
    return output_path, video_violations

# Main app
def main():
    st.title("🏍️ Helmet Detection & License Plate Recognition System")
    st.markdown("### Detect riders without helmets and identify license plates")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    # Model path input
    model_path = st.sidebar.text_input(
        "Model Path",
        value="helmet_best.pt",
        help="Path to your trained YOLOv8 model"
    )
    
    # Load model
    model = load_model(model_path)
    
    if model is None:
        st.error("❌ Failed to load model. Please check the model path.")
        st.stop()
    
    st.sidebar.success("✅ Model loaded successfully!")
    
    # Confidence threshold
    conf_threshold = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Minimum confidence for detections"
    )
    
    # Input method selection
    st.sidebar.header("📥 Input Method")
    input_method = st.sidebar.radio(
        "Choose input type:",
        ["Upload Image", "Upload Video", "Webcam (Coming Soon)"]
    )
    
    # Main content area
    if input_method == "Upload Image":
        st.header("📷 Image Detection")
        
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["jpg", "jpeg", "png"],
            help="Upload an image to detect helmets and license plates"
        )
        
        if uploaded_file is not None:
            # Load image
            image = Image.open(uploaded_file)
            
            # Create columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original Image")
                st.image(image, use_container_width=True)
            
            # Process button
            if st.button("🔍 Detect", type="primary"):
                with st.spinner("Processing image..."):
                    # Process image
                    img_with_boxes, results, violations = process_image(
                        image, model, conf_threshold
                    )
                    
                    with col2:
                        st.subheader("Detection Results")
                        st.image(img_with_boxes, use_container_width=True)
                    
                    # Display results
                    st.subheader("📊 Detection Summary")
                    
                    # Count detections
                    detection_counts = {
                        'helmet': 0,
                        'no_helmet': 0,
                        'number_plate': 0,
                        'rider': 0
                    }
                    
                    for result in results:
                        for box in result.boxes:
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])
                            if conf >= conf_threshold:
                                class_name = result.names[cls]
                                detection_counts[class_name] += 1
                    
                    # Display metrics
                    metrics_cols = st.columns(4)
                    metrics_cols[0].metric("✅ With Helmet", detection_counts['helmet'])
                    metrics_cols[1].metric("❌ No Helmet", detection_counts['no_helmet'])
                    metrics_cols[2].metric("🔢 License Plates", detection_counts['number_plate'])
                    metrics_cols[3].metric("👤 Riders", detection_counts['rider'])
                    
                    # Violations
                    if violations:
                        st.error(f"⚠️ {len(violations)} Violation(s) Detected!")
                        for i, violation in enumerate(violations, 1):
                            if violation['plate_box'] is not None:
                                st.warning(f"Violation #{i}: No helmet detected with license plate visible")
                            else:
                                st.warning(f"Violation #{i}: No helmet detected (license plate not visible)")
                    else:
                        st.success("✅ No violations detected!")
    
    elif input_method == "Upload Video":
        st.header("🎥 Video Detection")
        
        uploaded_video = st.file_uploader(
            "Choose a video...",
            type=["mp4", "avi", "mov", "mkv"],
            help="Upload a video to detect helmets and license plates"
        )
        
        if uploaded_video is not None:
            # Save uploaded video to temp file
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_video.read())
            video_path = tfile.name
            
            # Display original video
            st.subheader("Original Video")
            st.video(video_path)
            
            # Process button
            if st.button("🔍 Process Video", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("Processing video..."):
                    # Process video
                    output_path, violations = process_video(
                        video_path, model, conf_threshold, progress_bar, status_text
                    )
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display processed video
                    st.subheader("Processed Video")
                    st.video(output_path)
                    
                    # Display violations
                    st.subheader("📊 Violation Summary")
                    if violations:
                        st.error(f"⚠️ {len(violations)} Total Violation(s) Detected!")
                        
                        # Create violations dataframe
                        violations_df = pd.DataFrame([
                            {
                                'Violation #': i + 1,
                                'Timestamp': v['timestamp'],
                                'License Plate Visible': 'Yes' if v['plate_box'] is not None else 'No'
                            }
                            for i, v in enumerate(violations)
                        ])
                        
                        st.dataframe(violations_df, use_container_width=True)
                        
                        # Download option
                        st.download_button(
                            label="📥 Download Processed Video",
                            data=open(output_path, 'rb'),
                            file_name="processed_video.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.success("✅ No violations detected in the video!")
    
    else:  # Webcam
        st.header("📹 Webcam Detection")
        st.info("🚧 Webcam feature coming soon!")
        st.markdown("""
        This feature will allow you to:
        - Use your computer's webcam for real-time detection
        - Capture and save violations automatically
        - View live detection results
        """)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Class Information")
    st.sidebar.markdown("""
    - 🟢 **Helmet**: Rider wearing helmet
    - 🔴 **No Helmet**: Rider without helmet
    - 🟡 **Number Plate**: License plate
    - 🟠 **Rider**: Person on motorcycle
    """)

if __name__ == "__main__":
    main()