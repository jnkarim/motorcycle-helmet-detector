"""
🏍️ INTELLIGENT HELMET VIOLATION DETECTION SYSTEM
Premium Edition - International Expo Version
Bangladesh Traffic Enforcement AI
"""
import streamlit as st
import cv2
import tempfile
import os
import pandas as pd
from datetime import datetime
from ultralytics import YOLO
from pathlib import Path

from app_config import MODEL_PATH, CSV_FILE, SAVE_DIR
from detection_utils import process_frame, initialize_csv

# ================= PREMIUM UI CONFIGURATION =================
st.set_page_config(
    page_title="Traffic AI - Helmet Detection",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.traffic.gov.bd',
        'Report a bug': None,
        'About': "AI-Based Helmet Compliance Detection System"
    }
)

# ================= PREMIUM STYLING =================
st.markdown("""
<style>
    /* Main Theme - Red, Black, White */
    :root {
        --primary-red: #DC143C;
        --dark-bg: #1a1a1a;
        --card-bg: #2d2d2d;
        --text-white: #ffffff;
        --border-color: #404040;
        --success-green: #00ff41;
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    /* Main Container */
    .main {
        background-color: transparent;
    }
    
    /* Premium Header */
    .premium-header {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(220, 20, 60, 0.3);
        text-align: center;
    }
    
    .premium-title {
        font-size: 48px;
        font-weight: 900;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin: 0;
        letter-spacing: 2px;
    }
    
    .premium-subtitle {
        font-size: 20px;
        color: #f0f0f0;
        margin-top: 10px;
        font-weight: 300;
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #DC143C;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(220, 20, 60, 0.4);
    }
    
    .stat-number {
        font-size: 48px;
        font-weight: 900;
        color: #DC143C;
        margin: 0;
    }
    
    .stat-label {
        font-size: 16px;
        color: #cccccc;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 10px;
    }
    
    /* Control Panel */
    .control-panel {
        background: #2d2d2d;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #404040;
        margin-bottom: 25px;
    }
    
    /* Video Frame */
    .video-container {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #DC143C;
        box-shadow: 0 0 30px rgba(220, 20, 60, 0.3);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px 35px;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(220, 20, 60, 0.6);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #1a1a1a;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #DC143C;
        font-size: 32px;
        font-weight: 900;
    }
    
    /* Success/Info Messages */
    .stSuccess {
        background: rgba(0, 255, 65, 0.1);
        border: 1px solid #00ff41;
        border-radius: 10px;
    }
    
    .stInfo {
        background: rgba(220, 20, 60, 0.1);
        border: 1px solid #DC143C;
        border-radius: 10px;
    }
    
    /* Data Table */
    .dataframe {
        background: #2d2d2d !important;
        color: white !important;
        border: 1px solid #404040 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #1a1a1a;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2d2d2d;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
    }
    
    /* Logo Badge */
    .logo-badge {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #DC143C;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(220, 20, 60, 0.5);
        z-index: 999;
    }
    
    /* Navigation Notice Box */
    .nav-notice {
        background: linear-gradient(135deg, #DC143C 15%, #8B0000 100%);
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        border: 2px solid rgba(220, 20, 60, 0.5);
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.3);
    }
    
    .nav-notice h4 {
        color: white;
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 700;
    }
    
    .nav-notice p {
        color: #f5f5f5;
        margin: 0;
        font-size: 13px;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ================= LOAD MODEL =================
@st.cache_resource
def load_model():
    """Load YOLO model with caching"""
    try:
        model = YOLO(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"❌ Model Loading Failed: {str(e)}")
        return None

# ================= HEADER =================
st.markdown("""
<div class="premium-header">
    <h1 class="premium-title">AI-Based Helmet Compliance Detection System</h1>
    <p class="premium-subtitle">Intelligent Helmet Violation Detection | Bangladesh Traffic Authority</p>
</div>
""", unsafe_allow_html=True)

# Initialize
initialize_csv()
model = load_model()

if not model:
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM CONTROLS")
    st.markdown("---")
    
    # Settings
    conf_threshold = st.slider(
        "🎯 Detection Confidence",
        0.1, 0.9, 0.5, 0.05,
        help="Higher = More strict detection"
    )
    
    frame_skip = st.slider(
        "⚡ Processing Speed",
        1, 10, 2,
        help="Process every Nth frame (higher = faster)"
    )
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📊 SYSTEM STATUS")
    
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.markdown("**Model:**")
        st.success("✅ Active")
    with status_col2:
        st.markdown("**Storage:**")
        st.success("✅ Ready")
    
    st.markdown("---")
    
    # Navigation Notice - NEW ADDITION
    st.markdown("""
    <div class="nav-notice">
        <h4>📄 Generate Fines</h4>
        <p>After detecting violations, use the <strong>Fine Generation</strong> page (above in sidebar) to review violations and create PDF fine documents.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🔧 QUICK ACTIONS")
    
    if st.button("🗑️ Clear All Data", use_container_width=True):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            initialize_csv()
            st.success("✅ Database Cleared")
            st.rerun()
    
    if st.button("📊 View Analytics", use_container_width=True):
        st.info("Switch to 'Analytics' tab")
    
    st.markdown("---")
    st.markdown("### 📍 DEPLOYMENT INFO")
    st.caption(f"📁 Storage: `{SAVE_DIR}/`")
    st.caption(f"💾 Database: `{CSV_FILE}`")
    st.caption(f"🕒 Session: {datetime.now().strftime('%H:%M:%S')}")

# ================= MAIN TABS =================
tab1, tab2, tab3 = st.tabs(["🎥 LIVE DETECTION", "📊 ANALYTICS", "⚙️ SYSTEM"])

# ================= TAB 1: DETECTION =================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📹 VIDEO PROCESSING")
        
        video_file = st.file_uploader(
            "Upload Traffic Video",
            type=["mp4", "avi", "mov"],
            help="Supported: MP4, AVI, MOV"
        )
        
        if video_file:
            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file.read())
                video_path = tmp.name
            
            # Video info
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            duration = total_frames / fps if fps > 0 else 0
            
            # Info cards
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.metric("📹 Total Frames", f"{total_frames:,}")
            with info_col2:
                st.metric("⚡ FPS", f"{fps}")
            with info_col3:
                st.metric("⏱️ Duration", f"{duration:.1f}s")
            
            st.markdown("---")
            
            # Process button
            if st.button("▶️ START PROCESSING", use_container_width=True):
                st.markdown('<div class="video-container">', unsafe_allow_html=True)
                
                video_placeholder = st.empty()
                progress_bar = st.progress(0)
                stats_placeholder = st.empty()
                
                frame_count = 0
                violations_detected = 0
                plates_saved = 0
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    frame_count += 1
                    progress_bar.progress(frame_count / total_frames)
                    
                    # Skip frames for speed
                    if frame_count % frame_skip != 0:
                        continue
                    
                    # Process frame
                    results = model(frame, conf=conf_threshold)[0]
                    output_frame = process_frame(frame.copy(), results)
                    
                    # Display
                    video_placeholder.image(
                        output_frame,
                        channels="BGR",
                        use_container_width=True
                    )
                    
                    # Update stats
                    stats_placeholder.markdown(f"""
                    **Processing:** Frame {frame_count}/{total_frames} 
                    | **Violations:** {violations_detected} 
                    | **Plates Saved:** {plates_saved}
                    """)
                
                cap.release()
                st.markdown('</div>', unsafe_allow_html=True)
                st.success(f"✅ Processing Complete! {violations_detected} violations detected.")
                
                # Next step notice
                if violations_detected > 0:
                    st.info("📄 **Next:** Go to 'Fine Generation' page in the sidebar to review violations and create fines!")
                
                # Cleanup
                os.unlink(video_path)
    
    with col2:
        st.markdown("### 📈 LIVE STATISTICS")
        
        # Load current violations
        if os.path.exists(CSV_FILE):
            try:
                df = pd.read_csv(CSV_FILE)
                
                # Today's stats
                today = datetime.now().strftime('%Y-%m-%d')
                today_violations = len(df[df['Time'].str.contains(today, na=False)])
                total_violations = len(df)
                pending_review = len(df[df['Plate_Number'].isna() | (df['Plate_Number'] == '')])
                
                # Display stats
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{today_violations}</div>
                    <div class="stat-label">Today's Violations</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{total_violations}</div>
                    <div class="stat-label">Total Violations</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{pending_review}</div>
                    <div class="stat-label">Pending Review</div>
                </div>
                """, unsafe_allow_html=True)
                
            except:
                st.info("📊 No data available yet")
        else:
            st.info("📊 Upload a video to start")
        
        st.markdown("---")
        
        # System Info
        st.markdown("### 🎯 DETECTION INFO")
        st.info("""
        **Active Detection Rules:**
        - ✅ Riders on motorcycles only
        - ✅ Helmet presence verified
        - ✅ Clear plate capture
        - ✅ No duplicate logging
        """)

# ================= TAB 2: ANALYTICS =================
with tab2:
    st.markdown("### 📊 VIOLATION ANALYTICS")
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            
            if len(df) > 0:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📈 Total Cases", len(df))
                with col2:
                    reviewed = len(df[df['Plate_Number'].notna() & (df['Plate_Number'] != '')])
                    st.metric("✅ Reviewed", reviewed)
                with col3:
                    pending = len(df) - reviewed
                    st.metric("⏳ Pending", pending)
                with col4:
                    today = datetime.now().strftime('%Y-%m-%d')
                    today_count = len(df[df['Time'].str.contains(today, na=False)])
                    st.metric("📅 Today", today_count)
                
                st.markdown("---")
                
                # Data table
                st.markdown("### 📋 RECENT VIOLATIONS")
                st.dataframe(
                    df.tail(10)[['Time', 'Plate_Number', 'Detection_Confidence', 'Source']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                
                # Export
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Full Report",
                        csv_data,
                        f"violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("🔄 Refresh Data", use_container_width=True):
                        st.rerun()
            
            else:
                st.info("📊 No violations recorded yet")
        
        except Exception as e:
            st.error(f"❌ Error loading analytics: {e}")
    else:
        st.info("📊 No data available. Process videos to generate analytics.")

# ================= TAB 3: SYSTEM =================
with tab3:
    st.markdown("### ⚙️ SYSTEM CONFIGURATION")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 Detection Settings")
        st.code(f"""
Model: {MODEL_PATH}
Confidence: {conf_threshold}
Frame Skip: {frame_skip}
        """)
        
        st.markdown("#### 📁 Storage")
        st.code(f"""
Database: {CSV_FILE}
Images: {SAVE_DIR}/
        """)
    
    with col2:
        st.markdown("#### 🎯 Detection Classes")
        st.code("""
0: Helmet (Safe)
1: No-Helmet (Violation)
2: License Plate
3: Rider
        """)
        
        st.markdown("#### 📊 System Health")
        st.success("✅ All Systems Operational")

# ================= FOOTER =================
st.markdown("""
<div class="logo-badge">
    🚔 Traffic AI v2.0
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p><strong>INTELLIGENT TRAFFIC ENFORCEMENT SYSTEM</strong></p>
    <p style='font-size: 12px;'>© 2026 Traffic AI. International Expo Edition.</p>
</div>
""", unsafe_allow_html=True)