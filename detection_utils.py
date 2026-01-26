"""
🏍️ PRECISION HELMET DETECTION ENGINE
Industry-Standard Implementation
Strict Rules: Motorcycle Riders Only | No Helmet = Violation | One Clear Plate Image
"""
import cv2
import time
import csv
import os
import numpy as np
import streamlit as st
from app_config import (
    RIDER_ID, NO_HELMET_ID, PLATE_ID, HELMET_ID,
    COLOR_RIDER, COLOR_NO_HELMET, COLOR_PLATE,
    CSV_FILE, DUPLICATE_WINDOW, CLASS_NAMES
)
from datetime import datetime

# Production mode - clean output
DEBUG_MODE = False  # Set True for debugging

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_center(box):
    """Calculate center point of bounding box"""
    x1, y1, x2, y2 = box
    return int((x1 + x2) / 2), int((y1 + y2) / 2)

def calculate_iou(box1, box2):
    """Calculate Intersection over Union for spatial relationship"""
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    x_left = max(x1_1, x1_2)
    y_top = max(y1_1, y1_2)
    x_right = min(x2_1, x2_2)
    y_bottom = min(y2_1, y2_2)
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection = (x_right - x_left) * (y_bottom - y_top)
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0

def is_inside(inner_box, outer_box, tolerance=0):
    """Check if inner box center is within outer box"""
    cx, cy = get_center(inner_box)
    ox1, oy1, ox2, oy2 = outer_box
    return (ox1 - tolerance < cx < ox2 + tolerance) and (oy1 - tolerance < cy < oy2 + tolerance)

def enhance_plate_image(plate_crop):
    """
    Enhance plate image for maximum clarity
    Applied: Upscaling, Denoising, Sharpening, Contrast Enhancement
    """
    try:
        if plate_crop is None or plate_crop.size == 0:
            return plate_crop
        
        h, w = plate_crop.shape[:2]
        
        # 1. Upscale 3x for better quality
        upscaled = cv2.resize(plate_crop, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)
        
        # 2. Denoise
        denoised = cv2.fastNlMeansDenoisingColored(upscaled, None, 10, 10, 7, 21)
        
        # 3. Convert to LAB color space for better processing
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # 4. Apply CLAHE to L channel (contrast enhancement)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # 5. Merge and convert back
        enhanced_lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # 6. Sharpen
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
        
    except Exception as e:
        print(f"Enhancement error: {e}")
        return plate_crop

def is_duplicate_plate(plate_box, now):
    """
    Check if this plate was already captured (location-based)
    Prevents multiple captures of same bike
    """
    if "recent_plates" not in st.session_state:
        st.session_state.recent_plates = []
    
    px, py = get_center(plate_box)
    
    # Clean up old entries
    st.session_state.recent_plates = [
        (x, y, t) for x, y, t in st.session_state.recent_plates
        if now - t < DUPLICATE_WINDOW
    ]
    
    # Check spatial proximity
    for x, y, t in st.session_state.recent_plates:
        distance = ((px - x)**2 + (py - y)**2)**0.5
        if distance < 150:  # Same plate if within 150 pixels
            return True
    
    # Register new plate
    st.session_state.recent_plates.append((px, py, now))
    return False

# ==========================================
# MAIN DETECTION ENGINE
# ==========================================

def process_frame(frame, results, **kwargs):
    """
    PRECISION DETECTION PIPELINE
    
    Rules:
    1. Only process RIDERS (people on motorcycles)
    2. Check if rider has HELMET → Skip if yes
    3. Check if rider has NO_HELMET → Violation if yes
    4. Find best PLATE image → Save ONE clear image per bike
    """
    
    # === STEP 1: Collect Detections ===
    riders = []
    helmets = []
    no_helmets = []
    plates = []
    
    for box in results.boxes:
        try:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            detection = (x1, y1, x2, y2, conf)
            
            if cls == RIDER_ID:
                riders.append(detection)
            elif cls == HELMET_ID:
                helmets.append(detection)
            elif cls == NO_HELMET_ID:
                no_helmets.append(detection)
            elif cls == PLATE_ID:
                plates.append(detection)
                
        except Exception as e:
            continue
    
    # === STEP 2: Process Each Rider (Motorcycle Only) ===
    violation_count = 0
    
    for rider_data in riders:
        rx1, ry1, rx2, ry2, r_conf = rider_data
        rider_box = (rx1, ry1, rx2, ry2)
        
        # === CHECK 1: Does rider have HELMET? ===
        has_helmet = False
        
        for helmet_data in helmets:
            hx1, hy1, hx2, hy2, h_conf = helmet_data
            helmet_box = (hx1, hy1, hx2, hy2)
            
            # Helmet must be inside or significantly overlap rider
            iou = calculate_iou(helmet_box, rider_box)
            inside = is_inside(helmet_box, rider_box, tolerance=50)
            
            if inside or iou > 0.15:
                has_helmet = True
                if DEBUG_MODE:
                    cv2.rectangle(frame, (hx1, hy1), (hx2, hy2), (0, 255, 0), 2)
                    cv2.putText(frame, "SAFE", (hx1, hy1-5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                break
        
        # SKIP if rider has helmet (SAFE)
        if has_helmet:
            continue
        
        # === CHECK 2: Does rider have NO_HELMET? ===
        has_no_helmet = False
        best_no_helmet = None
        best_nh_iou = 0.0
        
        for nh_data in no_helmets:
            nx1, ny1, nx2, ny2, nh_conf = nh_data
            nh_box = (nx1, ny1, nx2, ny2)
            
            iou = calculate_iou(nh_box, rider_box)
            inside = is_inside(nh_box, rider_box, tolerance=50)
            
            if (inside or iou > 0.1) and iou > best_nh_iou:
                has_no_helmet = True
                best_nh_iou = iou
                best_no_helmet = nh_data
        
        # SKIP if no clear NO_HELMET detection
        if not has_no_helmet or not best_no_helmet:
            continue
        
        # === VIOLATION CONFIRMED ===
        violation_count += 1
        
        nx1, ny1, nx2, ny2, nh_conf = best_no_helmet
        
        # Draw violation annotations
        cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), COLOR_RIDER, 3)
        cv2.rectangle(frame, (nx1, ny1), (nx2, ny2), COLOR_NO_HELMET, 3)
        
        # Violation badge
        cv2.rectangle(frame, (rx1, ry1-40), (rx1+200, ry1), (0, 0, 0), -1)
        cv2.putText(frame, f"VIOLATION #{violation_count}", (rx1+5, ry1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # === CHECK 3: Find BEST Plate for This Rider ===
        best_plate = None
        best_plate_score = 0.0
        
        for pl_data in plates:
            px1, py1, px2, py2, pl_conf = pl_data
            plate_box = (px1, py1, px2, py2)
            
            # Expand rider box downward (plates at bottom of bike)
            expanded_rider = (rx1, ry1, rx2, ry2 + 250)
            
            # Calculate plate quality score
            # Factors: confidence, size, position
            plate_area = (px2 - px1) * (py2 - py1)
            
            if is_inside(plate_box, expanded_rider, tolerance=80):
                # Quality score: confidence * size * position_weight
                position_score = 1.0 if py1 > ry2 else 0.5  # Prefer plates below rider
                quality_score = pl_conf * (plate_area / 1000.0) * position_score
                
                if quality_score > best_plate_score:
                    best_plate_score = quality_score
                    best_plate = pl_data
        
        # === SAVE BEST PLATE IMAGE ===
        if best_plate:
            px1, py1, px2, py2, pl_conf = best_plate
            
            # Check for duplicates
            now = time.time()
            plate_box = (px1, py1, px2, py2)
            
            if not is_duplicate_plate(plate_box, now):
                # Draw plate box
                cv2.rectangle(frame, (px1, py1), (px2, py2), COLOR_PLATE, 3)
                
                # Visual connection
                nh_center = get_center((nx1, ny1, nx2, ny2))
                plate_center = get_center(plate_box)
                cv2.line(frame, nh_center, plate_center, (0, 255, 0), 2)
                
                # Extract and enhance plate
                try:
                    # Add padding for better capture
                    pad = 10
                    crop_y1 = max(0, py1 - pad)
                    crop_y2 = min(frame.shape[0], py2 + pad)
                    crop_x1 = max(0, px1 - pad)
                    crop_x2 = min(frame.shape[1], px2 + pad)
                    
                    plate_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2].copy()
                    
                    if plate_crop.size > 0:
                        # Enhance for clarity
                        enhanced_plate = enhance_plate_image(plate_crop)
                        
                        # Save with timestamp
                        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        plate_filename = f"plate_{timestamp_str}_{int(now*1000)%10000}_conf{int(pl_conf*100)}.jpg"
                        plate_path = os.path.join("violations", plate_filename)
                        
                        # Save enhanced image
                        cv2.imwrite(plate_path, enhanced_plate, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        
                        # Log to database
                        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            csv.writer(f).writerow([
                                timestamp,
                                "",  # To be filled manually
                                f"{pl_conf:.3f}",
                                "Video",
                                plate_filename
                            ])
                        
                        # Visual feedback
                        cv2.putText(frame, f"PLATE SAVED ({pl_conf:.2f})", (px1, py2+25),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_PLATE, 2)
                        
                        if DEBUG_MODE:
                            print(f"✅ SAVED: {plate_filename} | Confidence: {pl_conf:.2f}")
                
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"❌ Plate save error: {e}")
        
        else:
            # Violation but no plate
            cv2.putText(frame, "NO PLATE DETECTED", (rx1, ry2+25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # === Status overlay ===
    if violation_count > 0:
        cv2.rectangle(frame, (10, 10), (300, 60), (0, 0, 0), -1)
        cv2.putText(frame, f"VIOLATIONS: {violation_count}", (20, 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
    
    return frame

def initialize_csv():
    """Initialize database with correct schema"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "Time",
                "Plate_Number",
                "Detection_Confidence",
                "Source",
                "Image_File"
            ])
