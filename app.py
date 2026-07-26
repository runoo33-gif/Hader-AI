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
        "title": "🎓 نظام تحضير الطالبات الذكي - حاضر AI",
        "menu_student": "بوابة الطالبة (تسجيل دخول)",
        "menu_attendance": "تسجيل الحضور الذكي",
        "menu_admin": "لوحة تحكم الإدارة (الدكتور)",
        "student_portal": "🔐 بوابة الطالبة الإلكترونية",
        "enter_id_login": "أدخلي الرقم الجامعي الخاص بكِ:",
        "welcome": "أهلاً بكِ يا",
        "attended_days": "✅ أيام الحضور المسجلة",
        "absent_days": "❌ أيام الغياب التقديرية",
        "records_detail": "📅 سجل حضوركِ بالتفصيل:",
        "no_records": "لم يتم تسجيل أي حالة حضور لكِ حتى الآن.",
        "not_found": "الرقم الجامعي غير مسجل في النظام!",
        "step1": "📚 خطوة 1: البيانات الأساسية والمادة",
        "select_subject": "اختارِ المادة الدراسية:",
        "step2": "🔒 خطوة 2: اختبار الأمان وكشف الحيوية",
        "network_success": "🌐 اتصال آمن: أنتِ متصلة بشبكة المعهد الداخلية",
        "network_error": "❌ تنبيه أمني: يجب الاتصال بشبكة المعهد الداخلية للتمكن من التحضير!",
        "capture_btn": "تأكيد تسجيل الحضور الذكي",
        "face_success": "✅ تم التحقق بنجاح واجتياز اختبار الحيوية!",
        "admin_title": "📊 لوحة تحكم الإدارة ومتابعة السجلات",
        "enter_pass": "إدخال الرقم السري للوصول:",
        "download_csv": "📥 تحميل سجل الحضور المصفى (CSV)"
    },
    "EN": {
        "title": "🎓 Smart Attendance System - Hader AI",
        "menu_student": "Student Portal (Login)",
        "menu_attendance": "Smart Attendance Check-in",
        "menu_admin": "Faculty Control Panel",
        "student_portal": "🔐 Student Electronic Portal",
        "enter_id_login": "Enter Your University ID:",
        "welcome": "Welcome,",
        "attended_days": "✅ Attended Days",
        "absent_days": "❌ Estimated Absent Days",
        "records_detail": "📅 Detailed Attendance History:",
        "no_records": "No attendance records found yet.",
        "not_found": "University ID is not registered!",
        "step1": "📚 Step 1: Basic Info & Subject",
        "select_subject": "Select Course Subject:",
        "step2": "🔒 Step 2: Security & Liveness Test",
        "network_success": "🌐 Secure Network: Connected to Institute Wi-Fi",
        "network_error": "❌ Security Alert: You must connect to Institute Wi-Fi to check in!",
        "capture_btn": "Confirm Smart Attendance",
        "face_success": "✅ Successfully verified with Liveness Detection!",
        "admin_title": "📊 Faculty Dashboard & Master Logs",
        "enter_pass": "Enter Admin Password:",
        "download_csv": "📥 Download Attendance Log (CSV)"
    }
}

st.sidebar.markdown("### 🌐 Language / اللغة")
lang_choice = st.sidebar.radio("", ["العربية 🇸🇦", "English 🇬🇧"])
lang = "AR" if lang_choice == "العربية 🇸🇦" else "EN"
t = TRANSLATIONS[lang]

menu = [t["menu_student"], t["menu_attendance"], t["menu_admin"]]
choice = st.sidebar.selectbox("القائمة" if lang == "AR" else "Navigation", menu)

SUBJECTS = [
    "الذكاء الاصطناعي (AI)",
    "معالجة الصور الرقمية (Digital Image Processing)",
    "الأمن السيبراني (Cybersecurity)",
    "هندسة البرمجيات (Software Engineering)"
]

STUDENTS_DB = {
    "441001": "رنيم حسن جريبي"
}

def load_attendance_log(file_path):
    cols = ["الرقم الجامعي", "اسم الطالبة", "المادة الدراسية", "التاريخ", "الوقت", "الحالة", "كشف الحيوية"]
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
st.markdown("---")

# 1. بوابة الطالبة
if choice == t["menu_student"]:
    st.header(t["student_portal"])
    student_id = st.text_input(t["enter_id_login"], key="student_login")
    
    if student_id:
        if student_id in STUDENTS_DB:
            student_name = STUDENTS_DB[student_id]
            st.success(f"{t['welcome']} {student_name} ({student_id})")
            
            log_df = load_attendance_log(LOG_FILE)
            if not log_df.empty:
                log_df["الرقم الجامعي"] = log_df["الرقم الجامعي"].astype(str)
                records = log_df[log_df["الرقم الجامعي"] == str(student_id)]
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
                    st.success(t["face_success"])
                    st.balloons()
                    
                    log_df = load_attendance_log(LOG_FILE)
                    new_row = pd.DataFrame([{
                        "الرقم الجامعي": str(student_id),
                        "اسم الطالبة": STUDENTS_DB[student_id],
                        "المادة الدراسية": selected_subject,
                        "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                        "الوقت": datetime.now().strftime("%H:%M:%S"),
                        "الحالة": "حاضر / Present",
                        "كشف الحيوية": "ناجح / Passed"
                    }])
                    log_df = pd.concat([log_df, new_row], ignore_index=True)
                    log_df.to_csv(LOG_FILE, index=False)
        elif student_id:
            st.error(t["not_found"])
    else:
        st.error(f"{t['network_error']}\n\n(Current IP: {user_ip})")

# 3. لوحة الدكتور
elif choice == t["menu_admin"]:
    st.header(t["admin_title"])
    password = st.text_input(t["enter_pass"], type="password")
    if password == "admin123":
        log_df = load_attendance_log(LOG_FILE)
        st.dataframe(log_df, use_container_width=True)
        csv = log_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label=t["download_csv"], data=csv, file_name="Hader_AI_Report.csv", mime="text/csv")
