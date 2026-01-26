"""
🚔 PREMIUM VIOLATION REVIEW & FINE GENERATION SYSTEM
Professional Interface with PDF Generation
Bangladesh Traffic Authority Standard
"""
import streamlit as st
import pandas as pd
import cv2
import os
from datetime import datetime, timedelta
from pdf_generator import TrafficFinePDF

CSV_FILE = "violations.csv"
VIOLATIONS_DIR = "violations"
FINES_DIR = "fines"

st.set_page_config(
    page_title="Traffic Fine System",
    page_icon="🚔",
    layout="wide"
)

# ================= PREMIUM STYLING =================
st.markdown("""
<style>
    /* Premium Red-Black-White Theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    
    /* Header */
    .review-header {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(220, 20, 60, 0.5);
        margin-bottom: 30px;
    }
    
    .review-title {
        font-size: 42px;
        font-weight: 900;
        color: white;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.6);
        letter-spacing: 2px;
    }
    
    .review-subtitle {
        font-size: 18px;
        color: #f5f5f5;
        margin-top: 10px;
        font-weight: 300;
    }
    
    /* Violation Cards */
    .violation-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        border: 3px solid #404040;
        border-radius: 18px;
        padding: 30px;
        margin: 25px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.6);
        transition: all 0.4s ease;
    }
    
    .violation-card:hover {
        border-color: #DC143C;
        box-shadow: 0 12px 40px rgba(220, 20, 60, 0.4);
        transform: translateY(-5px);
    }
    
    .reviewed-card {
        border-color: #00ff41;
        background: linear-gradient(135deg, #2d2d2d 0%, #1a3d1a 100%);
    }
    
    .pending-card {
        border-color: #ffa500;
        background: linear-gradient(135deg, #2d2d2d 0%, #3d2a1a 100%);
    }
    
    /* Image Container */
    .plate-image {
        border: 4px solid #DC143C;
        border-radius: 15px;
        padding: 15px;
        background: #0a0a0a;
        box-shadow: 0 0 25px rgba(220, 20, 60, 0.4);
    }
    
    /* Stats Cards */
    .stat-box {
        background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(220, 20, 60, 0.5);
        transition: transform 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-3px);
    }
    
    .stat-number {
        font-size: 48px;
        font-weight: 900;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .stat-label {
        font-size: 15px;
        color: #f5f5f5;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* Input Fields */
    .stTextInput input {
        background: #0a0a0a;
        color: white;
        border: 3px solid #404040;
        border-radius: 10px;
        padding: 18px;
        font-size: 19px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #DC143C;
        box-shadow: 0 0 20px rgba(220, 20, 60, 0.4);
        background: #1a1a1a;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px 35px;
        font-size: 17px;
        font-weight: 800;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.5);
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(220, 20, 60, 0.7);
    }
    
    /* Info Badges */
    .info-badge {
        background: #404040;
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 700;
        display: inline-block;
        margin: 5px;
        border: 2px solid #555;
    }
    
    /* Section Headers */
    .section-header {
        color: #DC143C;
        font-size: 24px;
        font-weight: 900;
        margin: 20px 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Progress */
    .stProgress > div > div {
        background: linear-gradient(90deg, #DC143C 0%, #8B0000 100%);
    }
    
    /* Success Message */
    .success-box {
        background: linear-gradient(135deg, #00ff41 0%, #00b82e 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 5px 20px rgba(0, 255, 65, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def load_violations():
    """Load violations with error recovery"""
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Time", "Plate_Number", "Detection_Confidence", "Source", "Image_File"])
    
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔧 Auto Repair", use_container_width=True):
                try:
                    df = pd.read_csv(CSV_FILE, encoding='utf-8', on_bad_lines='skip')
                    st.success(f"✅ Recovered {len(df)} records")
                    return df
                except:
                    st.error("Repair failed")
        
        with col2:
            if st.button("🗑️ Reset Database", use_container_width=True):
                backup = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                os.rename(CSV_FILE, backup)
                st.success(f"✅ Reset! Backup: {backup}")
                st.rerun()
        
        return pd.DataFrame(columns=["Time", "Plate_Number", "Detection_Confidence", "Source", "Image_File"])

def save_violations(df):
    """Save to database"""
    df.to_csv(CSV_FILE, index=False, encoding='utf-8')

def update_plate(index, plate_number, df):
    """Update plate number"""
    df.at[index, 'Plate_Number'] = plate_number
    save_violations(df)
    return df

def delete_violation(index, df):
    """Delete violation and image"""
    if 'Image_File' in df.columns and pd.notna(df.at[index, 'Image_File']):
        img_file = df.at[index, 'Image_File']
        if img_file != "NO_PLATE":
            img_path = os.path.join(VIOLATIONS_DIR, img_file)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except:
                    pass
    
    df = df.drop(index).reset_index(drop=True)
    save_violations(df)
    return df

def generate_case_id():
    """Generate unique case ID"""
    return f"10{datetime.now().strftime('%y%m%d%H%M%S')}"

def generate_trace_no():
    """Generate trace number"""
    return datetime.now().strftime('%m%d%H')

# ================= MAIN APP =================

st.markdown("""
<div class="review-header">
    <h1 class="review-title">🚔 TRAFFIC FINE GENERATION SYSTEM</h1>
    <p class="review-subtitle">Violation Review & Official Document Generation</p>
</div>
""", unsafe_allow_html=True)

# Initialize PDF generator
pdf_generator = TrafficFinePDF(output_folder=FINES_DIR)

# Load data
df = load_violations()

if df.empty:
    st.info("📭 No violations recorded. Process videos in the main system first.")
    st.stop()

# ================= STATISTICS =================

st.markdown('<p class="section-header">📊 SYSTEM STATISTICS</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

total = len(df)
reviewed = len(df[df['Plate_Number'].notna() & (df['Plate_Number'] != '')])
pending = total - reviewed
today = datetime.now().strftime('%Y-%m-%d')
today_count = len(df[df['Time'].str.contains(today, na=False)])

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{total}</div>
        <div class="stat-label">Total Cases</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-box" style="background: linear-gradient(135deg, #00ff41 0%, #00b82e 100%);">
        <div class="stat-number">{reviewed}</div>
        <div class="stat-label">Completed</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-box" style="background: linear-gradient(135deg, #ffa500 0%, #ff6b00 100%);">
        <div class="stat-number">{pending}</div>
        <div class="stat-label">Pending</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-box" style="background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);">
        <div class="stat-number">{today_count}</div>
        <div class="stat-label">Today</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= FILTERS =================

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    filter_mode = st.selectbox(
        "🔍 Filter Violations",
        ["⏳ Pending Review", "✅ Completed", "📋 All Violations"],
        index=0
    )

with col2:
    search = st.text_input("🔎 Search Plate Number", "")

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Apply filters
filtered_df = df.copy()

if "Pending" in filter_mode:
    filtered_df = filtered_df[filtered_df['Plate_Number'].isna() | (filtered_df['Plate_Number'] == '')]
elif "Completed" in filter_mode:
    filtered_df = filtered_df[filtered_df['Plate_Number'].notna() & (filtered_df['Plate_Number'] != '')]

if search:
    filtered_df = filtered_df[filtered_df['Plate_Number'].str.contains(search, case=False, na=False)]

st.markdown("---")
st.markdown('<p class="section-header">📋 VIOLATION PROCESSING</p>', unsafe_allow_html=True)

# ================= VIOLATIONS DISPLAY =================

if filtered_df.empty:
    st.info("No violations match your filters.")
else:
    for idx, row in filtered_df.iterrows():
        is_reviewed = pd.notna(row['Plate_Number']) and row['Plate_Number'] != ''
        card_class = "reviewed-card" if is_reviewed else "pending-card"
        
        with st.container():
            st.markdown(f'<div class="violation-card {card_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Plate Image
                st.markdown('<div class="plate-image">', unsafe_allow_html=True)
                
                img_path = None
                if 'Image_File' in row and pd.notna(row['Image_File']) and row['Image_File'] != "NO_PLATE":
                    img_path = os.path.join(VIOLATIONS_DIR, row['Image_File'])
                    if os.path.exists(img_path):
                        image = cv2.imread(img_path)
                        if image is not None:
                            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            st.image(image, use_container_width=True, caption="License Plate Evidence")
                        else:
                            st.error("⚠️ Image Load Error")
                            img_path = None
                    else:
                        st.warning(f"⚠️ File Not Found")
                        img_path = None
                else:
                    st.warning("⚠️ No Image Captured")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Violation Info
                st.markdown(f"""
                <span class="info-badge">🕒 {row['Time']}</span>
                <span class="info-badge">📊 Conf: {row.get('Detection_Confidence', 'N/A')}</span>
                <span class="info-badge">📹 {row.get('Source', 'Video')}</span>
                """, unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                if is_reviewed:
                    # Already reviewed - Show plate and generate PDF option
                    st.markdown("### ✅ PLATE NUMBER RECORDED")
                    st.markdown(f"### `{row['Plate_Number']}`")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # PDF Generation Form
                    with st.expander("📄 GENERATE OFFICIAL FINE DOCUMENT", expanded=False):
                        with st.form(key=f"pdf_form_{idx}"):
                            st.markdown("**Fill Case Details:**")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                accused_person = st.text_input("Accused Person", key=f"accused_{idx}")
                                father_spouse = st.text_input("Father/Spouse", key=f"father_{idx}")
                                cell_number = st.text_input("Cell Number", key=f"cell_{idx}")
                                address = st.text_input("Address", key=f"address_{idx}")
                            
                            with col_b:
                                offence = st.selectbox("Offence", 
                                    ["Driving Without Helmet", "No Helmet - Passenger", "Expired License", "No License"],
                                    key=f"offence_{idx}")
                                section = st.text_input("Section", value="122", key=f"section_{idx}")
                                seized_docs = st.text_input("Seized Docs", value="T/T", key=f"seized_{idx}")
                                witness = st.text_input("Witness", key=f"witness_{idx}")
                            
                            fine_amount = st.selectbox("Fine Amount (TK)", 
                                ["1,000.00", "500.00", "2,000.00", "5,000.00"],
                                key=f"fine_{idx}")
                            
                            payment_days = st.slider("Payment Days", 7, 90, 21, key=f"days_{idx}")
                            
                            # Submit button inside form
                            submitted = st.form_submit_button("📄 GENERATE PDF FINE", use_container_width=True)
                        
                        # Handle submission OUTSIDE form
                        if submitted:
                            if not accused_person or not cell_number:
                                st.error("⚠️ Please fill required fields: Accused Person, Cell Number")
                            else:
                                # Prepare data
                                violation_data = {
                                    'trace_no': generate_trace_no(),
                                    'case_id': generate_case_id(),
                                    'accused_person': accused_person,
                                    'father_spouse': father_spouse or 'N/A',
                                    'cell_number': cell_number,
                                    'address': address or 'N/A',
                                    'vehicle_reg_no': row['Plate_Number'],
                                    'offence': offence,
                                    'section': section,
                                    'seized_docs': seized_docs,
                                    'occurrence_date': row['Time'],
                                    'payment_last_date': (datetime.now() + timedelta(days=payment_days)).strftime('%Y-%m-%d'),
                                    'witness': witness or 'N/A',
                                    'fine_amount': fine_amount,
                                    'officer_id': '9623252925',
                                    'division': 'Tejgaon - TRAFFIC',
                                    'location': 'DHAKA METROPOLITAN POLICE',
                                    'plate_image_path': img_path
                                }
                                
                                try:
                                    pdf_path = pdf_generator.generate_fine(violation_data)
                                    
                                    st.markdown(f"""
                                    <div class="success-box">
                                        ✅ FINE DOCUMENT GENERATED SUCCESSFULLY!
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.balloons()
                                    
                                    # Download button OUTSIDE form
                                    with open(pdf_path, "rb") as pdf_file:
                                        st.download_button(
                                            "⬇️ DOWNLOAD PDF FINE",
                                            pdf_file,
                                            file_name=os.path.basename(pdf_path),
                                            mime="application/pdf",
                                            use_container_width=True
                                        )
                                except Exception as e:
                                    st.error(f"❌ PDF Generation Error: {e}")
                    
                    # Edit/Delete options
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("✏️ Edit Plate", key=f"edit_{idx}", use_container_width=True):
                            st.session_state[f'editing_{idx}'] = True
                            st.rerun()
                    
                    with col_b:
                        if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True):
                            df = delete_violation(idx, df)
                            st.success("✅ Deleted")
                            st.rerun()
                    
                    # Edit mode
                    if st.session_state.get(f'editing_{idx}', False):
                        with st.form(key=f"edit_form_{idx}"):
                            new_plate = st.text_input(
                                "New Plate Number",
                                value=row['Plate_Number'],
                                key=f"edit_input_{idx}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            
                            if col_save.form_submit_button("💾 Save", use_container_width=True):
                                df = update_plate(idx, new_plate, df)
                                st.session_state[f'editing_{idx}'] = False
                                st.success(f"✅ Updated: {new_plate}")
                                st.rerun()
                            
                            if col_cancel.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f'editing_{idx}'] = False
                                st.rerun()
                
                else:
                    # Pending - Enter plate
                    st.markdown("### ⏳ ENTER PLATE NUMBER")
                    
                    with st.form(key=f"form_{idx}"):
                        plate_input = st.text_input(
                            "License Plate Number",
                            key=f"plate_{idx}",
                            placeholder="e.g., Dhaka Metro LA 45-6093 or ঢাকা মেট্রো ঢ ৬৫-৯৯৯৯",
                            help="Type the exact plate number visible in the image above"
                        )
                        
                        col_submit, col_skip = st.columns(2)
                        
                        submitted = col_submit.form_submit_button("✅ SUBMIT & CONTINUE", use_container_width=True)
                        skipped = col_skip.form_submit_button("⏭️ SKIP THIS", use_container_width=True)
                        
                        if submitted and plate_input:
                            df = update_plate(idx, plate_input, df)
                            st.markdown(f"""
                            <div class="success-box">
                                ✅ SAVED: {plate_input}
                            </div>
                            """, unsafe_allow_html=True)
                            st.rerun()
                        elif submitted:
                            st.warning("⚠️ Please enter a plate number")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

# ================= SIDEBAR =================

with st.sidebar:
    st.markdown("### 📥 EXPORT OPTIONS")
    
    if st.button("📊 Export All Data", use_container_width=True):
        csv_data = df.to_csv(index=False, encoding='utf-8')
        st.download_button(
            "⬇️ Download Complete CSV",
            csv_data,
            f"violations_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    if st.button("✅ Export Completed Only", use_container_width=True):
        reviewed_df = df[df['Plate_Number'].notna() & (df['Plate_Number'] != '')]
        if not reviewed_df.empty:
            csv_data = reviewed_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                "⬇️ Download Completed CSV",
                csv_data,
                f"completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("No completed violations")
    
    st.markdown("---")
    st.markdown("### 📁 FILE MANAGEMENT")
    
    # Count PDF files
    if os.path.exists(FINES_DIR):
        pdf_count = len([f for f in os.listdir(FINES_DIR) if f.endswith('.pdf')])
        st.metric("Generated PDFs", pdf_count)
    
    if st.button("📂 Open Fines Folder", use_container_width=True):
        os.makedirs(FINES_DIR, exist_ok=True)
        st.info(f"📁 Location: {os.path.abspath(FINES_DIR)}")
    
    st.markdown("---")
    st.markdown("### ⚡ BULK ACTIONS")
    
    if st.button("🗑️ Clear All Pending", use_container_width=True):
        if st.checkbox("⚠️ Confirm Delete"):
            pending_indices = df[df['Plate_Number'].isna() | (df['Plate_Number'] == '')].index
            for idx in pending_indices:
                if 'Image_File' in df.columns and pd.notna(df.at[idx, 'Image_File']):
                    img_file = df.at[idx, 'Image_File']
                    if img_file != "NO_PLATE":
                        img_path = os.path.join(VIOLATIONS_DIR, img_file)
                        if os.path.exists(img_path):
                            try:
                                os.remove(img_path)
                            except:
                                pass
            
            df = df[df['Plate_Number'].notna() & (df['Plate_Number'] != '')]
            save_violations(df)
            st.success("✅ Cleared!")
            st.rerun()
    
    # Progress
    if pending > 0:
        st.markdown("---")
        st.markdown("### 📊 PROGRESS TRACKING")
        progress = reviewed / total
        st.progress(progress)
        st.markdown(f"**{reviewed}/{total}** processed")
        st.markdown(f"**{progress*100:.1f}%** complete")
        st.markdown(f"**{pending}** remaining")
    else:
        st.markdown("---")
        st.success("🎉 ALL VIOLATIONS PROCESSED!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p style='font-size: 18px; font-weight: 700;'><strong>TRAFFIC AI FINE GENERATION SYSTEM</strong></p>
    <p>Official Document Generation for Traffic Violations</p>
    <p style='font-size: 12px;'>© 2026 Bangladesh Traffic Authority | Powered by AI Technology</p>
</div>
""", unsafe_allow_html=True)