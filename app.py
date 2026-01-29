"""
🏍️ SAFEGUARD VISION - INTELLIGENT HELMET VIOLATION DETECTION SYSTEM
Enhanced Edition with Improved PDF Management
Bangladesh Traffic Enforcement AI
"""
import streamlit as st
import cv2
import tempfile
import os
import pandas as pd
from datetime import datetime, timedelta
from ultralytics import YOLO
from pathlib import Path
import glob
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # For Streamlit compatibility

from app_config import MODEL_PATH, CSV_FILE, SAVE_DIR
from detection_utils import process_frame, initialize_csv
from pdf_generator import TrafficFinePDF

# ================= PREMIUM UI CONFIGURATION =================
st.set_page_config(
    page_title="Safeguard Vision - Traffic AI",
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
    
    /* Case Card */
    .case-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #DC143C;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    
    .case-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(220, 20, 60, 0.4);
    }
    
    .case-header {
        font-size: 18px;
        font-weight: 700;
        color: #DC143C;
        margin-bottom: 10px;
    }
    
    .case-detail {
        font-size: 14px;
        color: #cccccc;
        margin: 5px 0;
    }
    
    .case-detail strong {
        color: #ffffff;
    }
    
    /* PDF Card */
    .pdf-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #DC143C;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .pdf-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(220, 20, 60, 0.4);
        transition: all 0.3s ease;
    }
    
    .pdf-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }
    
    .pdf-meta {
        font-size: 12px;
        color: #999999;
        margin: 5px 0;
    }
    
    .pdf-icon {
        font-size: 48px;
        margin-bottom: 15px;
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
    
    /* Download Button Special */
    .stDownloadButton>button {
        background: linear-gradient(90deg, #00ff41 0%, #00cc33 100%);
        color: #000000;
        font-weight: 800;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(90deg, #00cc33 0%, #00aa2a 100%);
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
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #FFC107;
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
    
    /* Search Box */
    .stTextInput>div>div>input {
        background: #2d2d2d;
        color: white;
        border: 2px solid #404040;
        border-radius: 8px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #DC143C;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
        padding: 15px 20px;
        border-radius: 10px;
        margin: 20px 0 15px 0;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.3);
    }
    
    .section-header h3 {
        color: white;
        margin: 0;
        font-weight: 700;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        background: #2d2d2d;
        border-radius: 15px;
        border: 2px dashed #404040;
    }
    
    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 20px;
        opacity: 0.5;
    }
    
    .empty-state-text {
        color: #999999;
        font-size: 18px;
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
    <div class="premium-title">🛡️ SAFEGUARD VISION</div>
    <div class="premium-subtitle">AI-Powered Helmet Violation Detection & Case Management System</div>
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM CONTROLS")
    
    # Settings
    conf_threshold = st.slider(
        "🎯 Detection Confidence",
        0.1, 1.0, 0.45, 0.05,
        help="Minimum confidence for detections"
    )
    
    frame_skip = st.slider(
        "⏩ Frame Skip",
        1, 10, 3, 1,
        help="Process every Nth frame (higher = faster)"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 QUICK STATS")
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            today = datetime.now().strftime('%Y-%m-%d')
            today_count = len(df[df['Time'].str.contains(today, na=False)])
            total_count = len(df)
            
            st.metric("Today's Cases", today_count)
            st.metric("Total Cases", total_count)
            
            # PDF count
            pdf_files = glob.glob("fines/FINE_*.pdf")
            st.metric("Generated PDFs", len(pdf_files))
        except:
            st.info("No data yet")
    else:
        st.info("No data yet")
    
    st.markdown("---")
    st.caption(f"🕒 Session: {datetime.now().strftime('%H:%M:%S')}")

# ================= INITIALIZE =================
model = load_model()
initialize_csv()

# Create directories
os.makedirs("violations", exist_ok=True)
os.makedirs("fines", exist_ok=True)

# ================= MAIN TABS =================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎥 DETECTION", 
    "📋 CASE MANAGEMENT", 
    "📄 PDF DOCUMENTS",
    "📊 ANALYTICS", 
    "⚙️ SYSTEM"
])

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
                    | **Progress:** {(frame_count/total_frames)*100:.1f}%
                    """)
                
                cap.release()
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Count actual violations
                if os.path.exists(CSV_FILE):
                    df = pd.read_csv(CSV_FILE)
                    violations_detected = len(df)
                
                st.success(f"✅ Processing Complete! {violations_detected} violations detected.")
                
                # Next step notice
                if violations_detected > 0:
                    st.info("📋 **Next Step:** Go to 'CASE MANAGEMENT' tab to review violations and generate fine documents!")
                
                # Cleanup
                os.unlink(video_path)
    
    with col2:
    
        
        # System Info
        st.markdown("### 🎯 DETECTION INFO")
        st.info("""
        **Active Detection Rules:**
        - ✅ Riders on motorcycles only
        - ✅ Helmet presence verified
        - ✅ Clear plate capture
        - ✅ No duplicate logging
        """)

# ================= TAB 2: CASE MANAGEMENT =================
with tab2:
    st.markdown('<div class="section-header"><h3>📋 CASE MANAGEMENT & FINE GENERATION</h3></div>', unsafe_allow_html=True)
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            
            if len(df) > 0:
                # Search and filter
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    search_query = st.text_input("🔍 Search by Plate Number", placeholder="Enter plate number...")
                with col2:
                    date_filter = st.date_input("📅 Filter by Date", datetime.now())
                with col3:
                    status_filter = st.selectbox("📊 Status", ["All", "Pending", "Reviewed"])
                
                # Apply filters
                filtered_df = df.copy()
                
                if search_query:
                    filtered_df = filtered_df[filtered_df['Plate_Number'].str.contains(search_query, case=False, na=False)]
                
                if date_filter:
                    date_str = date_filter.strftime('%Y-%m-%d')
                    filtered_df = filtered_df[filtered_df['Time'].str.contains(date_str, na=False)]
                
                if status_filter == "Pending":
                    filtered_df = filtered_df[filtered_df['Plate_Number'].isna() | (filtered_df['Plate_Number'] == '')]
                elif status_filter == "Reviewed":
                    filtered_df = filtered_df[filtered_df['Plate_Number'].notna() & (filtered_df['Plate_Number'] != '')]
                
                st.markdown(f"### Found {len(filtered_df)} cases")
                st.markdown("---")
                
                # Display cases
                if len(filtered_df) > 0:
                    # Reverse to show newest first
                    for idx in reversed(filtered_df.index):
                        row = filtered_df.loc[idx]
                        
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                # Case card
                                plate_status = "✅ Reviewed" if pd.notna(row['Plate_Number']) and row['Plate_Number'] != '' else "⏳ Pending"
                                
                                st.markdown(f"""
                                <div class="case-card">
                                    <div class="case-header">Case #{idx + 1} - {plate_status}</div>
                                    <div class="case-detail"><strong>Time:</strong> {row['Time']}</div>
                                    <div class="case-detail"><strong>Plate:</strong> {row['Plate_Number'] if pd.notna(row['Plate_Number']) else 'Not Set'}</div>
                                    <div class="case-detail"><strong>Confidence:</strong> {row['Detection_Confidence']}</div>
                                    <div class="case-detail"><strong>Image:</strong> {row['Image_File']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                # Show plate image if available
                                img_path = os.path.join("violations", row['Image_File'])
                                if os.path.exists(img_path):
                                    st.image(img_path, caption="License Plate", use_container_width=True)
                                else:
                                    st.warning("Image not found")
                        
                        # Generate fine form section - FULL WIDTH BELOW
                        with st.expander(f"📄 Generate Fine for Case #{idx+1}", expanded=False):
                            with st.form(key=f"fine_form_{idx}"):
                                st.markdown("### 📋 Fine Details")
                                
                                # Left side form - Personal details
                                st.markdown("#### Personal Information")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    accused = st.text_input("Accused Person*", key=f"accused_{idx}", placeholder="Enter full name")
                                    father = st.text_input("Father/Spouse Name*", key=f"father_{idx}", placeholder="Enter father/spouse name")
                                    
                                with col_b:
                                    cell = st.text_input("Cell Number*", key=f"cell_{idx}", placeholder="e.g., 01858051852")
                                    address = st.text_area("Address*", key=f"address_{idx}", placeholder="Enter full address", height=100)
                                
                                st.markdown("---")
                                
                                # Vehicle & Offence details
                                st.markdown("#### Vehicle & Offence Information")
                                col_c, col_d = st.columns(2)
                                with col_c:
                                    vehicle_reg = st.text_input("Vehicle Reg No*", value=row['Plate_Number'] if pd.notna(row['Plate_Number']) else "", key=f"vehicle_{idx}", placeholder="e.g., Dhaka Metro LA 45-6093")
                                    offence = st.selectbox("Offence*", [
                                        "Driving Without Helmet",
                                        "Riding Without Helmet",
                                        "Passenger Without Helmet"
                                    ], key=f"offence_{idx}")
                                
                                with col_d:
                                    section = st.text_input("Section*", value="122", key=f"section_{idx}")
                                    fine_amount = st.text_input("Fine Amount (TK)*", value="1,000.00", key=f"amount_{idx}")
                                
                                st.markdown("---")
                                
                                # Officer details
                                st.markdown("#### Officer & Location Details")
                                col_e, col_f = st.columns(2)
                                with col_e:
                                    witness = st.text_input("Witness", value="Traffic Officer", key=f"witness_{idx}")
                                    division = st.text_input("Division", value="Tejgaon", key=f"div_{idx}")
                                
                                with col_f:
                                    officer_id = st.text_input("Officer ID", value="9623252925", key=f"officer_{idx}")
                                    location = st.text_input("Location", value="DHAKA METRO", key=f"loc_{idx}")
                                
                                st.markdown("---")
                                
                                submitted = st.form_submit_button("✅ Generate Fine PDF", use_container_width=True, type="primary")
                            
                            # Handle form submission OUTSIDE the form
                            if submitted:
                                if all([accused, father, cell, address, vehicle_reg]):
                                    # Generate case ID
                                    case_id = f"100{idx:07d}"
                                    trace_no = f"{idx:06d}"
                                    
                                    # Prepare data
                                    violation_data = {
                                        'trace_no': trace_no,
                                        'case_id': case_id,
                                        'accused_person': accused,
                                        'father_spouse': father,
                                        'cell_number': cell,
                                        'address': address,
                                        'vehicle_reg_no': vehicle_reg,
                                        'offence': offence,
                                        'section': section,
                                        'seized_docs': 'T/T',
                                        'occurrence_date': row['Time'],
                                        'payment_last_date': (datetime.strptime(row['Time'], '%Y-%m-%d %H:%M:%S') + timedelta(days=21)).strftime('%Y-%m-%d'),
                                        'witness': witness,
                                        'fine_amount': fine_amount,
                                        'officer_id': officer_id,
                                        'officer_name': 'Traffic Officer',
                                        'division': division,
                                        'location': location,
                                        'plate_image_path': img_path if os.path.exists(img_path) else None
                                    }
                                    
                                    # Generate PDF
                                    try:
                                        pdf_gen = TrafficFinePDF()
                                        pdf_path = pdf_gen.generate_fine(violation_data)
                                        
                                        st.success(f"✅ Fine PDF generated successfully!")
                                        
                                        # Provide immediate download OUTSIDE form
                                        with open(pdf_path, 'rb') as f:
                                            pdf_data = f.read()
                                            st.download_button(
                                                label="⬇️ Download Fine PDF",
                                                data=pdf_data,
                                                file_name=os.path.basename(pdf_path),
                                                mime="application/pdf",
                                                key=f"download_new_{idx}",
                                                use_container_width=True
                                            )
                                        
                                        st.info(f"📁 PDF saved to: `{pdf_path}`")
                                        st.info(f"📄 You can also find this PDF in the 'PDF DOCUMENTS' tab")
                                        
                                        # Update plate number if not set
                                        if pd.isna(row['Plate_Number']) or row['Plate_Number'] == '':
                                            df.at[idx, 'Plate_Number'] = vehicle_reg
                                            df.to_csv(CSV_FILE, index=False)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Error generating PDF: {str(e)}")
                                        import traceback
                                        st.code(traceback.format_exc())
                                else:
                                    st.error("❌ Please fill all required fields marked with *")
                        
                        st.markdown("---")
                else:
                    st.markdown("""
                    <div class="empty-state">
                        <div class="empty-state-icon">🔍</div>
                        <div class="empty-state-text">No cases found matching your filters</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <div class="empty-state-text">No cases recorded yet. Process a video to start.</div>
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error loading cases: {e}")
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div class="empty-state-text">No database found. Process a video to create cases.</div>
        </div>
        """, unsafe_allow_html=True)

# ================= TAB 3: PDF DOCUMENTS =================
with tab3:
    st.markdown('<div class="section-header"><h3>📄 GENERATED FINE DOCUMENTS</h3></div>', unsafe_allow_html=True)
    
    # Get all PDF files
    pdf_files = sorted(glob.glob("fines/FINE_*.pdf"), key=os.path.getmtime, reverse=True)
    
    if pdf_files:
        st.markdown(f"### 📚 {len(pdf_files)} Fine Documents Available")
        
        # Search box
        search_pdf = st.text_input("🔍 Search PDFs by Case ID or Date", placeholder="Enter case ID or date...")
        
        # Filter PDFs
        if search_pdf:
            pdf_files = [f for f in pdf_files if search_pdf.lower() in f.lower()]
        
        st.markdown("---")
        
        # Display PDFs in grid
        cols_per_row = 3
        for i in range(0, len(pdf_files), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(pdf_files):
                    pdf_path = pdf_files[idx]
                    pdf_name = os.path.basename(pdf_path)
                    
                    # Extract case ID from filename
                    case_id = pdf_name.split('_')[1] if len(pdf_name.split('_')) > 1 else "Unknown"
                    
                    # Get file info
                    file_size = os.path.getsize(pdf_path) / 1024  # KB
                    file_time = datetime.fromtimestamp(os.path.getmtime(pdf_path))
                    
                    with col:
                        st.markdown(f"""
                        <div class="pdf-card">
                            <div class="pdf-icon">📄</div>
                            <div class="pdf-title">Case #{case_id}</div>
                            <div class="pdf-meta">📅 {file_time.strftime('%Y-%m-%d %H:%M')}</div>
                            <div class="pdf-meta">💾 {file_size:.1f} KB</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Download button
                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=f.read(),
                                file_name=pdf_name,
                                mime="application/pdf",
                                key=f"download_{idx}",
                                use_container_width=True
                            )
                        
                        # Delete button
                        if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                            try:
                                os.remove(pdf_path)
                                st.success("Deleted!")
                                st.rerun()
                            except:
                                st.error("Delete failed")
        
        st.markdown("---")
        
        # Bulk actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh List", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📂 Open Fines Folder", use_container_width=True):
                st.info("📁 PDFs are stored in: `fines/` folder")
    
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📄</div>
            <div class="empty-state-text">No fine documents generated yet.<br>Go to 'CASE MANAGEMENT' to generate fines.</div>
        </div>
        """, unsafe_allow_html=True)

# ================= TAB 4: ANALYTICS =================
with tab4:
    st.markdown("### 📊 INTERACTIVE ANALYTICS DASHBOARD")
    
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            
            if len(df) > 0:
                # ============ TOP ANIMATED METRICS ============
                st.markdown("#### 🎯 Real-Time Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total = len(df)
                    st.markdown(f"""
                    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 2px solid #DC143C;'>
                        <div style='font-size: 40px; margin-bottom: 10px;'>🚨</div>
                        <h1 style='color: #DC143C; font-size: 48px; margin: 0; font-weight: 900;'>{total}</h1>
                        <p style='color: #ccc; margin: 10px 0; font-size: 13px; letter-spacing: 1px;'>TOTAL VIOLATIONS</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    today = datetime.now().strftime('%Y-%m-%d')
                    today_count = len(df[df['Time'].str.contains(today, na=False)])
                    st.markdown(f"""
                    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 2px solid #4CAF50;'>
                        <div style='font-size: 40px; margin-bottom: 10px;'>📅</div>
                        <h1 style='color: #4CAF50; font-size: 48px; margin: 0; font-weight: 900;'>{today_count}</h1>
                        <p style='color: #ccc; margin: 10px 0; font-size: 13px; letter-spacing: 1px;'>TODAY'S CASES</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_conf = df['Detection_Confidence'].mean()
                    st.markdown(f"""
                    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 2px solid #2196F3;'>
                        <div style='font-size: 40px; margin-bottom: 10px;'>🎯</div>
                        <h1 style='color: #2196F3; font-size: 48px; margin: 0; font-weight: 900;'>{avg_conf:.1f}%</h1>
                        <p style='color: #ccc; margin: 10px 0; font-size: 13px; letter-spacing: 1px;'>AVG CONFIDENCE</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    reviewed = len(df[df['Plate_Number'].notna() & (df['Plate_Number'] != '')])
                    st.markdown(f"""
                    <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 2px solid #FF9800;'>
                        <div style='font-size: 40px; margin-bottom: 10px;'>✅</div>
                        <h1 style='color: #FF9800; font-size: 48px; margin: 0; font-weight: 900;'>{reviewed}</h1>
                        <p style='color: #ccc; margin: 10px 0; font-size: 13px; letter-spacing: 1px;'>REVIEWED</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Set dark style for all charts
                plt.style.use('dark_background')
                
                # ============ CHARTS ROW 1 ============
                st.markdown("#### 📈 Violation Trends & Patterns")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 📅 Daily Violation Trend")
                    df['Date'] = pd.to_datetime(df['Time']).dt.date
                    time_data = df.groupby('Date').size().reset_index(name='Count')
                    
                    fig1, ax1 = plt.subplots(figsize=(10, 5))
                    ax1.plot(time_data['Date'], time_data['Count'], 
                            color='#DC143C', linewidth=2.5, marker='o', markersize=6, markerfacecolor='#DC143C', markeredgecolor='white', markeredgewidth=1.5)
                    ax1.fill_between(time_data['Date'], time_data['Count'], alpha=0.2, color='#DC143C')
                    ax1.set_xlabel('Date', fontsize=11, color='#ccc')
                    ax1.set_ylabel('Violations', fontsize=11, color='#ccc')
                    ax1.set_title('Violations Over Time', fontsize=13, fontweight='bold', color='white', pad=15)
                    ax1.grid(True, alpha=0.2, linestyle='--')
                    ax1.tick_params(colors='#ccc', labelsize=9)
                    ax1.set_facecolor('#1a1a1a')
                    fig1.patch.set_facecolor('#1a1a1a')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig1)
                    plt.close()
                
                with col2:
                    st.markdown("##### ⏰ Hourly Distribution")
                    df['Hour'] = pd.to_datetime(df['Time']).dt.hour
                    hour_data = df.groupby('Hour').size().reset_index(name='Count')
                    
                    fig2, ax2 = plt.subplots(figsize=(10, 5))
                    bars = ax2.bar(hour_data['Hour'], hour_data['Count'], 
                                   color='#2196F3', edgecolor='#64B5F6', linewidth=1.5, alpha=0.9)
                    ax2.set_xlabel('Hour (24h)', fontsize=11, color='#ccc')
                    ax2.set_ylabel('Violations', fontsize=11, color='#ccc')
                    ax2.set_title('Violations by Hour of Day', fontsize=13, fontweight='bold', color='white', pad=15)
                    ax2.grid(True, alpha=0.2, axis='y', linestyle='--')
                    ax2.tick_params(colors='#ccc', labelsize=9)
                    ax2.set_facecolor('#1a1a1a')
                    fig2.patch.set_facecolor('#1a1a1a')
                    plt.tight_layout()
                    st.pyplot(fig2)
                    plt.close()
                
                # ============ CHARTS ROW 2 ============
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown("##### 🎯 AI Confidence Distribution")
                    fig3, ax3 = plt.subplots(figsize=(10, 5))
                    ax3.hist(df['Detection_Confidence'], bins=20, 
                            color='#4CAF50', edgecolor='#81C784', linewidth=1.5, alpha=0.9)
                    ax3.set_xlabel('Confidence %', fontsize=11, color='#ccc')
                    ax3.set_ylabel('Number of Cases', fontsize=11, color='#ccc')
                    ax3.set_title('Detection Confidence Scores', fontsize=13, fontweight='bold', color='white', pad=15)
                    ax3.grid(True, alpha=0.2, axis='y', linestyle='--')
                    ax3.tick_params(colors='#ccc', labelsize=9)
                    ax3.set_facecolor('#1a1a1a')
                    fig3.patch.set_facecolor('#1a1a1a')
                    plt.tight_layout()
                    st.pyplot(fig3)
                    plt.close()
                
                with col4:
                    st.markdown("##### 📊 Case Status Distribution")
                    reviewed_count = len(df[df['Plate_Number'].notna() & (df['Plate_Number'] != '')])
                    pending_count = len(df) - reviewed_count
                    
                    fig4, ax4 = plt.subplots(figsize=(8, 8))
                    colors_pie = ['#4CAF50', '#FF9800']
                    wedges, texts, autotexts = ax4.pie(
                        [reviewed_count, pending_count],
                        labels=['Reviewed', 'Pending'],
                        colors=colors_pie,
                        autopct='%1.1f%%',
                        startangle=90,
                        textprops={'color': 'white', 'fontsize': 12, 'fontweight': 'bold'},
                        wedgeprops={'edgecolor': '#1a1a1a', 'linewidth': 2}
                    )
                    ax4.set_title('Case Review Status', fontsize=13, fontweight='bold', color='white', pad=20)
                    ax4.set_facecolor('#1a1a1a')
                    fig4.patch.set_facecolor('#1a1a1a')
                    # Make percentage text white
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    plt.tight_layout()
                    st.pyplot(fig4)
                    plt.close()
                
                # ============ WEEKLY COMPARISON ============
                st.markdown("#### 📆 Weekly Performance Comparison")
                df['Week'] = pd.to_datetime(df['Time']).dt.isocalendar().week
                df['Weekday'] = pd.to_datetime(df['Time']).dt.day_name()
                
                weekday_data = df.groupby('Weekday').size().reset_index(name='Count')
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_data['Weekday'] = pd.Categorical(weekday_data['Weekday'], categories=day_order, ordered=True)
                weekday_data = weekday_data.sort_values('Weekday')
                
                fig5, ax5 = plt.subplots(figsize=(12, 5))
                bars = ax5.bar(weekday_data['Weekday'], weekday_data['Count'], 
                              color='#FF9800', edgecolor='#FFB74D', linewidth=2, alpha=0.9)
                ax5.set_xlabel('Day of Week', fontsize=11, color='#ccc')
                ax5.set_ylabel('Violations', fontsize=11, color='#ccc')
                ax5.set_title('Violations by Day of Week', fontsize=13, fontweight='bold', color='white', pad=15)
                ax5.grid(True, alpha=0.2, axis='y', linestyle='--')
                ax5.tick_params(colors='#ccc', labelsize=9)
                ax5.set_facecolor('#1a1a1a')
                fig5.patch.set_facecolor('#1a1a1a')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax5.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', color='white', fontweight='bold', fontsize=10)
                
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig5)
                plt.close()
                
                # ============ KEY INSIGHTS ============
                st.markdown("#### 💡 Key Insights")
                
                # Calculate insights
                max_day = weekday_data.loc[weekday_data['Count'].idxmax(), 'Weekday']
                max_hour = hour_data.loc[hour_data['Count'].idxmax(), 'Hour']
                high_conf = len(df[df['Detection_Confidence'] > 80])
                high_conf_pct = (high_conf / len(df)) * 100
                
                col_i1, col_i2, col_i3 = st.columns(3)
                
                with col_i1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid #DC143C;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                            <span style='font-size: 32px; margin-right: 15px;'>📊</span>
                            <h4 style='color: #DC143C; margin: 0;'>Peak Day</h4>
                        </div>
                        <p style='color: white; font-size: 24px; margin: 10px 0; font-weight: bold;'>{max_day}</p>
                        <p style='color: #999; font-size: 12px; margin: 0;'>Most violations occur on this day</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_i2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid #2196F3;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                            <span style='font-size: 32px; margin-right: 15px;'>⏰</span>
                            <h4 style='color: #2196F3; margin: 0;'>Peak Hour</h4>
                        </div>
                        <p style='color: white; font-size: 24px; margin: 10px 0; font-weight: bold;'>{max_hour}:00</p>
                        <p style='color: #999; font-size: 12px; margin: 0;'>Rush hour violations</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_i3:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                            <span style='font-size: 32px; margin-right: 15px;'>🤖</span>
                            <h4 style='color: #4CAF50; margin: 0;'>AI Reliability</h4>
                        </div>
                        <p style='color: white; font-size: 24px; margin: 10px 0; font-weight: bold;'>{high_conf_pct:.1f}%</p>
                        <p style='color: #999; font-size: 12px; margin: 0;'>Detections with >80% confidence</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # ============ DATA TABLE ============
                st.markdown("### 📋 RECENT VIOLATIONS")
                st.dataframe(
                    df.tail(20)[['Time', 'Plate_Number', 'Detection_Confidence', 'Source', 'Image_File']],
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                
                # ============ EXPORT OPTIONS ============
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Full Report (CSV)",
                        csv_data,
                        f"violations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("🔄 Refresh Dashboard", use_container_width=True):
                        st.rerun()
            
            else:
                st.info("📊 No violations recorded yet. Process a video to see analytics!")
        
        except Exception as e:
            st.error(f"❌ Error loading analytics: {e}")
    else:
        st.info("📊 No data available. Process videos to generate analytics.")

# ================= TAB 5: SYSTEM =================
with tab5:
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
Images: violations/
PDFs: fines/
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
        
        # System stats
        violation_images = len(glob.glob("violations/*.jpg"))
        pdf_count = len(glob.glob("fines/FINE_*.pdf"))
        
        st.info(f"""
        **Storage:**
        - {violation_images} violation images
        - {pdf_count} PDF documents
        """)

# ================= FOOTER =================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p><strong>SAFEGUARD VISION - INTELLIGENT TRAFFIC ENFORCEMENT SYSTEM</strong></p>
    <p style='font-size: 12px;'>© 2026 Safeguard Vision. Enhanced Case Management Edition.</p>
</div>
""", unsafe_allow_html=True)