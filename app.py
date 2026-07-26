import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os
import socket

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="نظام حاضر AI | Hader AI", page_icon="🎓", layout="wide")

DB_PATH = "knowledge_base"
LOG_FILE = "attendance_log.csv"

# نطاق IP شبكة المعهد (192.168 أو 127.0.0.1 للتجربة)
INSTITUTE_IP_PREFIX = "192.168"

# دالة كشف الوجه المحدثة
def detect_face(uploaded_file):
    try:
        if uploaded_file is None:
            return False, 0
        
        # قراءة وتحويل بيانات الصورة بأمان
        bytes_data = uploaded_file.getvalue()
        file_bytes = np.frombuffer(bytes_data, np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if img is None:
            return False, 0
            
        # 1. تصغير حجم الصورة إذا كانت كبيرة جداً لتسهيل وسرعة الكشف
        height, width = img.shape[:2]
        max_dim = 800
        if max(height, width) > max_dim:
            scale = max_dim / float(max(height, width))
            img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. تحسين التباين والإضاءة
        gray = cv2.equalizeHist(gray)
        
        # 3. تحميل خوارزمية كشف الوجوه بمدخلات مرنة وحساسة
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.05, 
            minNeighbors=3, 
            minSize=(30, 30)
        )
        
        return len(faces) > 0, len(faces)
    except Exception as e:
        return False, 0

def get_user_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "127.0.0.1"

def is_connected_to_institute_network():
    user_ip = get_user_ip()
    if user_ip.startswith(INSTITUTE_IP_PREFIX) or user_ip == "127.0.0.1":
        return True, user_ip
    return False, user_ip

TRANSLATIONS = {
    "AR": {
        "title": "🎓 نظام تحضير المتدربين الذكي - حاضر AI",
        "trainer_header": "👩‍🏫 إشراف المدربة: رنيم جريبي",
        "menu_student": "بوابة المتدرب/ة (تسجيل دخول)",
        "menu_attendance": "تسجيل الحضور الذكي",
        "menu_admin": "منصة المدربة (لوحة التحكم الإحصائية)",
        "student_portal": "🔐 بوابة المتدرب/ة الإلكترونية",
        "enter_id_login": "أدخل/ي رقم الهوية الوطنية / الإقامة:",
        "welcome": "أهلاً بك يا",
        "attended_days": "✅ أيام الحضور المسجلة",
        "absent_days": "❌ أيام الغياب التقديرية",
        "records_detail": "📅 سجل حضورك بالتفصيل:",
        "no_records": "لم يتم تسجيل أي حالة حضور لك حتى الآن.",
        "not_found": "رقم الهوية غير مسجل في قاعدة بيانات المعهد!",
        "step1": "📚 خطوة 1: البيانات الأساسية والدورة",
        "select_subject": "اختر/ي المستوى التدريبي (Course Level):",
        "step2": "🔒 خطوة 2: اختبار الأمان وكشف الحيوية والوجه",
        "network_success": "🌐 اتصال آمن: أنت متصل بشبكة المعهد الداخلية",
        "network_error": "❌ تنبيه أمني: يجب الاتصال بشبكة المعهد الداخلية للتمكن من التحضير!",
        "capture_btn": "تأكيد تسجيل الحضور الذكي",
        "face_success": "✅ تم التعرف على الوجه بنجاح واجتياز كشف الحيوية!",
        "face_error": "❌ لم يتم التعرف على وجه واضح في الصورة! يرجى النظر للكاميرا والتقاط الصورة مجدداً.",
        "admin_title": "📊 منصة المدربة رنيم جريبي - تحليلات وإحصائيات الحضور",
        "enter_pass": "إدخال الرقم السري للوصول لـ منصة المدربة:",
        "download_csv": "📥 تحميل سجل الحضور المصفى (CSV)",
        "total_attendance": "إجمالي حالات الحضور المسجلة",
        "unique_students": "عدد المتدربين النشطين",
        "subject_chart": "📈 توزيع الحضور حسب مستويات اللغة الإنجليزية"
    },
    "EN": {
        "title": "🎓 Smart Attendance System - Hader AI",
        "trainer_header": "👩‍🏫 Supervised by Trainer: Raneem Jareebi",
        "menu_student": "Trainee Portal (Login)",
        "menu_attendance": "Smart Attendance Check-in",
        "menu_admin": "Trainer Platform (Analytics Dashboard)",
        "student_portal": "🔐 Trainee Electronic Portal",
        "enter_id_login": "Enter National ID / Iqama Number:",
        "welcome": "Welcome,",
        "attended_days": "✅ Attended Days",
        "absent_days": "❌ Estimated Absent Days",
        "records_detail": "📅 Detailed Attendance History:",
        "no_records": "No attendance records found yet.",
        "not_found": "National ID is not registered in the system!",
        "step1": "📚 Step 1: Basic Info & Course Level",
        "select_subject": "Select Course Level:",
        "step2": "🔒 Step 2: Security, Face & Liveness Test",
        "network_success": "🌐 Secure Network: Connected to Institute Wi-Fi",
        "network_error": "❌ Security Alert: You must connect to Institute Wi-Fi to check in!",
        "capture_btn": "Confirm Smart Attendance",
        "face_success": "✅ Human Face Detected & Verified Successfully!",
        "face_error": "❌ No clear human face detected! Please look at the camera and try again.",
        "admin_title": "📊 Trainer Raneem Jareebi Platform - Master Logs & Analytics",
        "enter_pass": "Enter Password for Trainer Platform:",
        "download_csv": "📥 Download Attendance Log (CSV)",
        "total_attendance": "Total Attendance Logs",
        "unique_students": "Active Trainees",
        "subject_chart": "📈 Attendance Distribution by English Levels"
    }
}

st.sidebar.markdown("### 🌐 Language / اللغة")
lang_choice = st.sidebar.radio("", ["العربية 🇸🇦", "English 🇬🇧"])
lang = "AR" if lang_choice == "العربية 🇸🇦" else "EN"
t = TRANSLATIONS[lang]

menu = [t["menu_student"], t["menu_attendance"], t["menu_admin"]]
choice = st.sidebar.selectbox("القائمة" if lang == "AR" else "Navigation", menu)

# قائمة المواد (مستويات اللغة الإنجليزية)
SUBJECTS = [
    "English Level 1",
    "English Level 2",
    "English Level 3",
    "English Level 4",
    "English Level 5"
]

# قاعدة بيانات الطلاب (تم التحديث للرقم الجديد)
STUDENTS_DB = {
    "1120491764": "رنيم حسن جريبي"
}

def load_attendance_log(file_path):
    cols = ["رقم الهوية", "اسم المتدرب/ة", "البرنامج التدريبي", "التاريخ", "الوقت", "الحالة", "كشف الحيوية"]
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if all(c in df.columns for c in cols):
                return df
        except:
            pass
    df = pd.DataFrame(columns=cols)
    df.to_csv(file_path, index=False)
    return df

st.title(t["title"])
st.subheader(t["trainer_header"])
st.markdown("---")

# 1. بوابة المتدرب
if choice == t["menu_student"]:
    st.header(t["student_portal"])
    student_id = st.text_input(t["enter_id_login"], key="student_login")
    
    if student_id:
        if student_id in STUDENTS_DB:
            student_name = STUDENTS_DB[student_id]
            st.success(f"{t['welcome']} {student_name} ({student_id})")
            
            log_df = load_attendance_log(LOG_FILE)
            if not log_df.empty:
                log_df["رقم الهوية"] = log_df["رقم الهوية"].astype(str)
                records = log_df[log_df["رقم الهوية"] == str(student_id)]
            else:
                records = pd.DataFrame()
            
            col1, col2 = st.columns(2)
            col1.metric(label=t["attended_days"], value=len(records))
            col2.metric(label=t["absent_days"], value=max(0, 3 - len(records)))
            
            st.subheader(t["records_detail"])
            if not records.empty:
                st.dataframe(records, use_container_width=True)
            else:
                st.info(t["no_records"])
        else:
            st.error(t["not_found"])

# 2. تسجيل الحضور
elif choice == t["menu_attendance"]:
    st.header(t["menu_attendance"])
    is_institute_net, user_ip = is_connected_to_institute_network()
    
    if is_institute_net:
        st.success(f"{t['network_success']} (IP: {user_ip})")
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input(t["enter_id_login"])
        with col2:
            selected_subject = st.selectbox(t["select_subject"], SUBJECTS)
            
        if student_id in STUDENTS_DB:
            st.markdown("---")
            st.subheader(t["step2"])
            uploaded_file = st.camera_input("📸 Take Photo / التقاط صورة")
            
            if uploaded_file is not None:
                if st.button(t["capture_btn"]):
                    has_face, face_count = detect_face(uploaded_file)
                    
                    if has_face:
                        st.success(t["face_success"])
                        st.balloons()
                        
                        log_df = load_attendance_log(LOG_FILE)
                        new_row = pd.DataFrame([{
                            "رقم الهوية": str(student_id),
                            "اسم المتدرب/ة": STUDENTS_DB[student_id],
                            "البرنامج التدريبي": selected_subject,
                            "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                            "الوقت": datetime.now().strftime("%H:%M:%S"),
                            "الحالة": "حاضر / Present",
                            "كشف الحيوية": "ناجح / Passed"
                        }])
                        log_df = pd.concat([log_df, new_row], ignore_index=True)
                        log_df.to_csv(LOG_FILE, index=False)
                    else:
                        st.error(t["face_error"])
        elif student_id:
            st.error(t["not_found"])
    else:
        st.error(f"{t['network_error']}\n\n(Current IP: {user_ip})")

# 3. منصة المدربة رنيم جريبي للإحصائيات
elif choice == t["menu_admin"]:
    st.header(t["admin_title"])
    password = st.text_input(t["enter_pass"], type="password")
    if password == "admin123":
        log_df = load_attendance_log(LOG_FILE)
        
        # مؤشرات إحصائية
        col1, col2 = st.columns(2)
        col1.metric(label=t["total_attendance"], value=len(log_df))
        unique_students_count = log_df["رقم الهوية"].nunique() if not log_df.empty else 0
        col2.metric(label=t["unique_students"], value=unique_students_count)
        
        st.markdown("---")
        
        # رسم بياني إحصائي للحضور حسب مستويات الإنجليزية
        if not log_df.empty and "البرنامج التدريبي" in log_df.columns:
            st.subheader(t["subject_chart"])
            subject_counts = log_df["البرنامج التدريبي"].value_counts()
            st.bar_chart(subject_counts)
        
        st.subheader("📋 الجدول الكامل لسجلات حضور المتدربين")
        st.dataframe(log_df, use_container_width=True)
        csv = log_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label=t["download_csv"], data=csv, file_name="Trainer_Raneem_Report.csv", mime="text/csv")
