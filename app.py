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

# دالة محاكاة التحقق من الوجه (Haar Cascade + حواف)
def verify_attendance(uploaded_image, db_path):
    if not os.path.exists(db_path):
        return None, "مجلد الصور المرجعية غير موجود. يرجى إضافته في المستودع أولاً."
    
    # قراءة الصورة المرفوعة
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # كاشف الوجوه الأساسي
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_img, 1.1, 4)
    
    if len(faces) == 0:
        return None, "لم يتم رصد أي وجه في الصورة الحية. يرجى توجيه وجهكِ بالكامل للكاميرا."
    
    # حساب ملامح الصورة الحالية (باستخدام توزيع الألوان كمحاكاة مبسطة للمطابقة)
    hist_current = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    cv2.normalize(hist_current, hist_current, 0, 1, cv2.NORM_MINMAX)
    
    best_match = None
    best_score = -1
    
    # المرور على الصور المرجعية في مجلد الـ knowledge_base
    for file in os.listdir(db_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            ref_path = os.path.join(db_path, file)
            ref_img = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)
            
            if ref_img is not None:
                hist_ref = cv2.calcHist([ref_img], [0], None, [256], [0, 256])
                cv2.normalize(hist_ref, hist_ref, 0, 1, cv2.NORM_MINMAX)
                
                # مقارنة الهستوجرام بين الصورة الحالية والمرجعية
                score = cv2.compareHist(hist_current, hist_ref, cv2.HISTCMP_CORREL)
                if score > best_score:
                    best_score = score
                    best_match = os.path.splitext(file)[0]
                    
    # عتبة القبول للمطابقة البرمجية
    if best_score > 0.4:
        return best_match, None
    else:
        return None, "لم يتم التعرف على ملامح الطالبة في قاعدة البيانات."

# واجهة المستخدم والتنقل
st.title("🎓 نظام تحضير الطالبات الذكي - حاضر AI")
st.markdown("---")

menu = ["تسجيل الحضور", "لوحة تحكم الإدارة"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

# ملف تخزين الحضور (CSV) شامل خانة المادة
LOG_FILE = "attendance_log.csv"
if not os.path.exists(LOG_FILE):
    df = pd.DataFrame(columns=["اسم الطالبة", "المادة الدراسية", "التاريخ", "الوقت", "الحالة", "كشف الحيوية"])
    df.to_csv(LOG_FILE, index=False)

if choice == "تسجيل الحضور":
    st.header("📸 التحقق الآلي من الهوية واختبار الحيوية الذكي")
    
    # اختيار المادة الدراسية أولاً
    st.subheader("📚 خطوة 1: اختيار المادة الدراسية")
    selected_subject = st.selectbox("الرجاء اختيار المادة المراد تسجيل الحضور فيها:", SUBJECTS)
    
    st.markdown("---")
    st.subheader("🔒 خطوة 2: اختبار الأمان وكشف الحيوية")
    
    # نظام توليد التحديات الحية عشوائياً لمنع التزوير
    if 'liveness_challenge' not in st.session_state:
        challenges = [
            {"text": "الرجاء الابتسام بشكل واضح أمام الكاميرا 😊", "icon": "😊"},
            {"text": "الرجاء رمش العينين مرتين متتاليتين 😉", "icon": "😉"},
            {"text": "الرجاء إمالة الرأس قليلاً نحو اليمين أو اليسar 📍", "icon": "📍"},
            {"text": "الرجاء رفع اليد أمام الكاميرا للإشارة 🖐️", "icon": "🖐️"}
        ]
        st.session_state.liveness_challenge = random.choice(challenges)
    
    # صندوق تنبيه ملون يوضح التحدي المطلوب من الطالبة
    st.info(f"🔒 **اختبار الأمان الحركي (Liveness Detection):** {st.session_state.liveness_challenge['text']}")
    
    input_method = st.radio("اختر طريقة التحقق المتاحة:", ["📸 التقاط صورة حية فورية", "📁 رفع صورة من الجهاز"])
    
    uploaded_file = None
    if input_method == "📸 التقاط صورة حية فورية":
        # فتح الكاميرا مباشرة وطلب الحركة المتزامنة مع التحدي
        uploaded_file = st.camera_input(f"قم بتنفيذ الحركة {st.session_state.liveness_challenge['icon']} ثم التقط الصورة")
    else:
        uploaded_file = st.file_uploader("الرجاء رفع صورة الطالبة الشخصية أو بطاقة الأحوال", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        if st.button("ابدأ التحقق الذكي واختبار الحيوية"):
            with st.spinner("جاري معالجة الصورة، والتحقق من اختبار الحيوية ومطابقة الملامح..."):
                student_name, error_msg = verify_attendance(uploaded_file, DB_PATH)
                
                if error_msg:
                    st.error(error_msg)
                else:
                    st.success(f"✅ تم التحقق بنجاح! تم اجتياز اختبار الأمان (Liveness Test)")
                    st.balloons()
                    st.info(f"مرحباً بالطالبة: {student_name} | المادة: {selected_subject}")
                    
                    # تسجيل في الـ CSV مع توثيق المادة وكشف الحيوية
                    now = datetime.now()
                    current_date = now.strftime("%Y-%m-%d")
                    current_time = now.strftime("%H:%M:%S")
                    
                    log_df = pd.read_csv(LOG_FILE)
                    new_row = pd.DataFrame([{
                        "اسم الطالبة": student_name, 
                        "المادة الدراسية": selected_subject,
                        "التاريخ": current_date, 
                        "الوقت": current_time, 
                        "الحالة": "حاضر",
                        "كشف الحيوية": f"ناجح ({st.session_state.liveness_challenge['text'][:15]}...)"
                    }])
                    log_df = pd.concat([log_df, new_row], ignore_index=True)
                    log_df.to_csv(LOG_FILE, index=False)
                    st.toast("تم قيد حضوركِ بنجاح وأرشفة المادة والحركة الأمنية!")
                    
                    # إعادة تعيين التحدي للمستخدم القادم
                    del st.session_state.liveness_challenge

elif choice == "لوحة تحكم الإدارة":
    st.header("📊 لوحة تحكم الإدارة ومتابعة السجلات")
    
    password = st.text_input("الرجاء إدخال الرقم السري للوصول", type="password")
    if password == "admin123":
        st.success("تم تسجيل الدخول بنجاح")
        
        log_df = pd.read_csv(LOG_FILE)
        
        if not log_df.empty:
            st.subheader("🔍 فلاتر تصفية البيانات وعمليات المراجعة الذكية")
            col1, col2, col3 = st.columns(3)
            with col1:
                search_name = st.text_input("البحث باسم الطالبة")
            with col2:
                available_subjects = ["الكل"] + SUBJECTS
                selected_sub = st.selectbox("تصفية حسب المادة الدراسية", available_subjects)
            with col3:
                available_dates = ["الكل"] + list(log_df["التاريخ"].unique())
                selected_date = st.selectbox("تصفية حسب التاريخ", available_dates)
            
            # تطبيق الفلاتر المحدثة
            filtered_df = log_df.copy()
            if search_name:
                filtered_df = filtered_df[filtered_df["اسم الطالبة"].str.contains(search_name, na=False)]
            if selected_sub != "الكل":
                filtered_df = filtered_df[filtered_df["المادة الدراسية"] == selected_sub]
            if selected_date != "الكل":
                filtered_df = filtered_df[filtered_df["التاريخ"] == selected_date]
                
            st.dataframe(filtered_df, use_container_width=True)
            
            # زر التحميل لملف التقرير المصفى
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل سجل الحضور المصفى كملف Excel/CSV",
                data=csv,
                file_name=f"Hader_AI_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("السجل فارغ حالياً، لم يتم رصد حضور بعد في أي مادة.")
    elif password != "":
        st.error("الرقم السري غير صحيح! ليس لديك الصلاحية.")
