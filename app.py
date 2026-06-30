import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os
import random

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="نظام حاضر AI", page_icon="🎓", layout="wide")

# مسار مجلد الصور المرجعية
DB_PATH = "knowledge_base"

# قائمة المواد الدراسية المتاحة في النظام
SUBJECTS = [
    "الذكاء الاصطناعي (AI)",
    "معالجة الصور الرقمية (Digital Image Processing)",
    "الأمن السيبراني (Cybersecurity)",
    "هندسة البرمجيات (Software Engineering)",
    "تنقيب البيانات (Data Mining)"
]

# قاعدة بيانات تجريبية مبسطة لربط الأرقام الجامعية بالأسماء (محاكاة)
STUDENTS_DB = {
    "441001": "رنيم حسن",
    "441002": "نجود حسن",
    "441003": "سارة أحمد",
    "441004": "أروى حسن"
}

# دالة محاكاة التحقق من الوجه
def verify_attendance(uploaded_image, db_path, student_id):
    if not os.path.exists(db_path):
        return False, "مجلد الصور المرجعية غير موجود."
    
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_img, 1.1, 4)
    
    if len(faces) == 0:
        return False, "لم يتم رصد أي وجه في الصورة. يرجى توجيه وجهكِ بالكامل للكاميرا."
    
    return True, None

# دالة ذكية لقراءة ملف السجل بأمان وتجنب خطأ KeyError
def load_attendance_log(file_path):
    required_columns = ["الرقم الجامعي", "اسم الطالبة", "المادة الدراسية", "التاريخ", "الوقت", "الحالة", "كشف الحيوية"]
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # التحقق من وجود جميع الأعمدة المطلوبة لتفادي تضارب الملف القديم
            if all(col in df.columns for col in required_columns):
                return df
        except:
            pass
    # في حال عدم وجود الملف أو نقص الأعمدة، يتم بناء جدول جديد تماماً
    df = pd.DataFrame(columns=required_columns)
    df.to_csv(file_path, index=False)
    return df

# واجهة المستخدم والتنقل
st.title("🎓 نظام تحضير الطالبات الذكي - حاضر AI")
st.markdown("---")

menu = ["بوابة الطالبة (تسجيل دخول)", "تسجيل الحضور الذكي", "لوحة تحكم الإدارة (الدكتور)"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

LOG_FILE = "attendance_log.csv"

# --- 1️⃣ بوابة الطالبة (ملف الحضور والغياب) ---
if choice == "بوابة الطالبة (تسجيل دخول)":
    st.header("🔐 بوابة الطالبة الإلكترونية")
    st.subheader("يرجى تسجيل الدخول للاطلاع على سجل الحضور والغياب")
    
    student_id = st.text_input("أدخلي الرقم الجامعي الخاص بكِ:", key="student_login")
    
    if student_id:
        if student_id in STUDENTS_DB:
            student_name = STUDENTS_DB[student_id]
            st.success(f"أهلاً بكِ يا {student_name} (الرقم الجامعي: {student_id})")
            
            # قراءة السجل بأمان باستخدام الدالة المحدثة
            log_df = load_attendance_log(LOG_FILE)
            
            # تصفية السجلات بأمان وتجنب الأخطاء البرمجية
            if not log_df.empty:
                log_df["الرقم الجامعي"] = log_df["الرقم الجامعي"].astype(str)
                student_records = log_df[log_df["الرقم الجامعي"] == str(student_id)]
            else:
                student_records = pd.DataFrame()
            
            st.markdown("### 📊 ملخص حالتكِ الأكاديمية في كل المواد")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="✅ إجمالي عدد أيام الحضور المسجلة", value=len(student_records))
            with col2:
                st.metric(label="❌ إجمالي عدد أيام الغياب (التقديري)", value=max(0, 3 - len(student_records)))
            
            st.markdown("---")
            st.subheader("📅 سجل حضوركِ بالتفصيل:")
            if not student_records.empty:
                st.dataframe(student_records[["المادة الدراسية", "التاريخ", "الوقت", "الحالة", "كشف الحيوية"]], use_container_width=True)
            else:
                st.info("لم يتم تسجيل أي حالة حضور لكِ في النظام حتى الآن. يرجى التوجه لخانة 'تسجيل الحضور الذكي' عند بدء المحاضرة.")
        else:
            st.error("الرقم الجامعي غير مسجل في النظام! (جربي الأرقام التجريبية المتاحة مثل: 441001 أو 441002)")

# --- 2️⃣ واجهة تسجيل الحضور بالكاميرا واختبار الحيوية ---
elif choice == "تسجيل الحضور الذكي":
    st.header("📸 التحقق الآلي من الهوية واختبار الحيوية")
    
    st.subheader("📚 خطوة 1: البيانات الأساسية والمادة")
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("أدخلي رقمكِ الجامعي للتحضير:")
    with col2:
        selected_subject = st.selectbox("اختارِ المادة المراد تحضيركِ فيها:", SUBJECTS)
        
    if student_id:
        if student_id in STUDENTS_DB:
            student_name = STUDENTS_DB[student_id]
            st.markdown(f"**الطالبة المحددة:** {student_name}")
            
            st.markdown("---")
            st.subheader("🔒 خطوة 2: اختبار الأمان وكشف الحيوية")
            
            if 'liveness_challenge' not in st.session_state:
                challenges = [
                    {"text": "الرجاء الابتسام بشكل واضح أمام الكاميرا 😊", "icon": "😊"},
                    {"text": "الرجاء رمش العينين مرتين متتاليتين 😉", "icon": "😉"},
                    {"text": "الرجاء إمالة الرأس قليلاً نحو اليمين أو اليسار 📍", "icon": "📍"},
                    {"text": "الرجاء رفع اليد أمام الكاميرا للإشارة 🖐️", "icon": "🖐️"}
                ]
                st.session_state.liveness_challenge = random.choice(challenges)
            
            st.info(f"🔒 **اختبار الأمان الحركي (Liveness Detection):** {st.session_state.liveness_challenge['text']}")
            
            input_method = st.radio("اختر طريقة التحقق المتاحة:", ["📸 التقاط صورة حية فورية", "📁 رفع صورة من الجهاز"])
            
            uploaded_file = None
            if input_method == "📸 التقاط صورة حية فورية":
                uploaded_file = st.camera_input(f"قم بتنفيذ الحركة {st.session_state.liveness_challenge['icon']} ثم التقط الصورة")
            else:
                uploaded_file = st.file_uploader("الرجاء رفع صورة الطالبة الشخصية", type=["jpg", "jpeg", "png"])
            
            if uploaded_file is not None:
                if st.button("تأكيد تسجيل الحضور الذكي"):
                    with st.spinner("جاري معالجة الصورة ومطابقة القياسات الحيوية..."):
                        success, error_msg = verify_attendance(uploaded_file, DB_PATH, student_id)
                        
                        if error_msg:
                            st.error(error_msg)
                        else:
                            st.success(f"✅ تم التحقق بنجاح واجتياز اختبار الحيوية!")
                            st.balloons()
                            
                            # قراءة وقيد البيانات بأمان
                            log_df = load_attendance_log(LOG_FILE)
                            
                            now = datetime.now()
                            current_date = now.strftime("%Y-%m-%d")
                            current_time = now.strftime("%H:%M:%S")
                            
                            new_row = pd.DataFrame([{
                                "الرقم الجامعي": str(student_id),
                                "اسم الطالبة": student_name, 
                                "المادة الدراسية": selected_subject,
                                "التاريخ": current_date, 
                                "الوقت": current_time, 
                                "الحالة": "حاضر",
                                "كشف الحيوية": f"ناجح ({st.session_state.liveness_challenge['text'][:15]}...)"
                            }])
                            log_df = pd.concat([log_df, new_row], ignore_index=True)
                            log_df.to_csv(LOG_FILE, index=False)
                            st.toast("تم تسجيل حضوركِ بنجاح وتحديث ملفكِ الشخصي!")
                            
                            del st.session_state.liveness_challenge
        else:
            st.error("رقم الطالبة غير مسجل في قاعدة البيانات الكلية.")

# --- 3️⃣ لوحة تحكم الإدارة (الدكتور) ---
elif choice == "لوحة تحكم الإدارة (الدكتور)":
    st.header("📊 لوحة تحكم الإدارة ومتابعة السجلات الكلية")
    
    password = st.text_input("الرجاء إدخال الرقم السري للوصول", type="password")
    if password == "admin123":
        st.success("تم تسجيل الدخول بنجاح")
        
        log_df = load_attendance_log(LOG_FILE)
        
        if not log_df.empty:
            st.subheader("🔍 فلاتر تصفية البيانات وعمليات المراجعة الذكية")
            col1, col2, col3 = st.columns(3)
            with col1:
                search_name = st.text_input("البحث باسم الطالبة أو رقمها الجامعي")
            with col2:
                available_subjects = ["الكل"] + SUBJECTS
                selected_sub = st.selectbox("تصفية حسب المادة الدراسية", available_subjects)
            with col3:
                available_dates = ["الكل"] + list(log_df["التاريخ"].unique())
                selected_date = st.selectbox("تصفية حسب التاريخ", available_dates)
            
            filtered_df = log_df.copy()
            if search_name:
                filtered_df = filtered_df[
                    (filtered_df["اسم الطالبة"].str.contains(search_name, na=False)) | 
                    (filtered_df["الرقم الجامعي"].astype(str).str.contains(search_name, na=False))
                ]
            if selected_sub != "الكل":
                filtered_df = filtered_df[filtered_df["المادة الدراسية"] == selected_sub]
            if selected_date != "الكل":
                filtered_df = filtered_df[filtered_df["التاريخ"] == selected_date]
                
            st.dataframe(filtered_df, use_container_width=True)
            
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل سجل الحضور المصفى كملف Excel/CSV",
                data=csv,
                file_name=f"Hader_AI_Master_Report.csv",
                mime="text/csv",
            )
        else:
            st.info("السجل العام فارغ حالياً، لم يتم رصد عمليات تحضير بعد.")
    elif password != "":
        st.error("الرقم السري غير صحيح!")
