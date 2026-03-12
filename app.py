import streamlit as st
import cv2
import numpy as np
import pandas as pd
import io
import datetime

st.set_page_config(layout="wide")
st.title("Smart Attendance System 📝")
st.write("Upload the Master List and the Photo to generate attendance.")

col1, col2, col3 = st.columns(3)
with col1:
    uploaded_image = st.file_uploader("1. Upload Attendance Photo", type=["jpg", "jpeg", "png"])
with col2:
    uploaded_excel = st.file_uploader("2. Upload Master List", type=["xlsx", "csv"])
with col3:
    attendance_date = st.date_input("3. Select Attendance Date", datetime.date.today())

if uploaded_image is not None and uploaded_excel is not None:
    
    try:
        if uploaded_excel.name.endswith('.csv'):
            df = pd.read_csv(uploaded_excel)
        else:
            df = pd.read_excel(uploaded_excel)
            
        num_students = len(df)
        st.success(f"Master List loaded! Found exactly {num_students} students.")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1) 
    
    st.markdown("### Step 4: Frame the Column (CRITICAL STEP)")
    st.warning("Make the **GREEN BOX** narrow! It should ONLY cover one single column for the selected date. Do NOT include the header rows.")
    
    height, width, _ = image.shape
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        top_crop = st.slider("Crop Top (%)", 0, 50, 15)
    with c2:
        bottom_crop = st.slider("Crop Bottom (%)", 0, 50, 10)
    with c3:
        left_crop = st.slider("Crop Left (%)", 0, 95, 45)
    with c4:
        right_crop = st.slider("Crop Right (%)", 0, 95, 45)

    y1 = int(height * (top_crop / 100))
    y2 = int(height * (1 - (bottom_crop / 100)))
    x1 = int(width * (left_crop / 100))
    x2 = int(width * (1 - (right_crop / 100)))

    img_preview = image.copy()
    cv2.rectangle(img_preview, (x1, y1), (x2, y2), (0, 255, 0), 3)
    
    if y2 > y1 and x2 > x1 and num_students > 0:
        sig_column = image[y1:y2, x1:x2]
        
        # Red Filter Masking
        hsv = cv2.cvtColor(sig_column, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2 
        
        gray = cv2.cvtColor(sig_column, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        thresh[red_mask > 0] = 0
        
        img_col1, img_col2 = st.columns([3, 1])
        with img_col1:
            st.image(img_preview, channels="BGR", caption="Adjust sliders to frame ONLY the signatures")
        with img_col2:
            st.image(thresh, caption="System View (Red Ink is Erased!)")

        # --- EXTREME INNER BOX METHOD ---
        slice_height = (y2 - y1) / num_students
        ink_counts = []
        
        for i in range(num_students):
            start_y = int(i * slice_height)
            end_y = int((i + 1) * slice_height)
            
            full_box = thresh[start_y:end_y, :]
            box_h, box_w = full_box.shape
            
            # We shave off a massive 30% from the Top, Bottom, Left, and Right. 
            # This looks ONLY at the dead-center of the box, ignoring all grid lines.
            crop_y1 = int(box_h * 0.30)
            crop_y2 = int(box_h * 0.70)
            crop_x1 = int(box_w * 0.30)
            crop_x2 = int(box_w * 0.70)
            
            if crop_y2 > crop_y1 and crop_x2 > crop_x1:
                inner_box = full_box[crop_y1:crop_y2, crop_x1:crop_x2]
                ink_pixels = cv2.countNonZero(inner_box)
            else:
                ink_pixels = 0
                
            ink_counts.append(ink_pixels)

        # --- THE VISUAL CHART LOGIC (FIXED ALTAIR ERROR) ---
        st.markdown("### Step 5: Visual Ink Analysis")
        st.info("Look at the chart below. Tall bars = Signatures. Short bars = Empty/Noise. Adjust the slider to sit right between them!")
        
        # Safely get labels for the chart without crashing Altair
        try:
            name_col = [col for col in df.columns if 'name' in col.lower()][0]
            chart_labels = df[name_col].astype(str) # Force it to be text
        except:
            chart_labels = df.index.astype(str)
            
        # Create a clean DataFrame and explicitly set X and Y axes
        chart_data = pd.DataFrame({
            "Student": chart_labels, 
            "Ink Pixels": ink_counts
        })
        st.bar_chart(chart_data, x="Student", y="Ink Pixels")

        # Intelligent Slider
        max_ink = max(ink_counts) if ink_counts else 500
        min_ink = min(ink_counts) if ink_counts else 0
        default_thresh = int((max_ink + min_ink) / 2)
        
        manual_threshold = st.slider("Drag this to separate the tall bars from the short bars:", 0, max_ink + 50, default_thresh)

        statuses = []
        for ink in ink_counts:
            if ink > manual_threshold:  
                statuses.append("Present")
            else:
                statuses.append("Absent")
                
        date_str = attendance_date.strftime("%d-%b-%Y")
        df["Ink Pixels (Debug)"] = ink_counts
        df[date_str] = statuses
        
        st.markdown(f"### 📋 Final Attendance Record for {date_str}")
        st.dataframe(df)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.drop(columns=["Ink Pixels (Debug)"]).to_excel(writer, index=False, sheet_name='Attendance')
        
        st.download_button(
            label="📥 Download Updated Attendance Excel",
            data=buffer.getvalue(),
            file_name=f"Attendance_{date_str}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.error("Invalid crop area.")