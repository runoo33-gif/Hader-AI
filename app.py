import streamlit as st
import cv2
from PIL import Image
import numpy as np
import os
import pandas as pd
from datetime import datetime

# إعدادات الصفحة الرئيسية
st.set_page_config(page_title="حاضر AI | Hader AI", page_icon="🎓", layout="centered")

# تحميل خوارزمية اكتشاف الوجوه (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# -------------------------------------------------------------
# قاعدة البيانات المحدثة بالسجلات اليومية والتواريخ
# -------------------------------------------------------------
mock_students = {
    "raneem": {
        "المادة": ["الشبكات العصبية الاصطناعية ANN", "الشبكات العصبية الاصطناعية ANN", "أمن الشبكات والمعلومات (سيبراني)", "أمن الشبكات والمعلومات (سيبراني)"],
        "اليوم": ["الاثنين", "الاثنين", "الخميس", "الخميس"],
        "التاريخ": ["2026-06-22", "2026-06-29", "2026-06-25", "2026-07-02"],
        "الوقت": ["03:00 PM", "03:00 PM", "04:00 PM", "04:00 PM"],
        "أستاذ المادة": ["د. محمد الشهري", "د. محمد الشهري", "د. محمد الشهري", "د. محمد الشهري"],
        "الحالة": ["حاضر", "غائب", "حاضر", "حاضر"]
    },
    "njood": {
        "المادة": ["الشبكات العصبية الاصطناعية ANN", "الشبكات العصبية الاصطناعية ANN", "أمن الشبكات والمعلومات (سيبراني)", "أمن الشبكات والمعلومات (سيبراني)"],
        "اليوم": ["الاثنين", "الاثنين", "الخميس", "الخميس"],
        "التاريخ": ["2026-06-22", "2026-06-29", "2026-06-25", "2026-07-02"],
        "الوقت": ["03:00 PM", "03:00 PM", "04:00 PM", "04:00 PM"],
        "أستاذ المادة": ["د. محمد الشهري", "د. محمد الشهري", "د. محمد الشهري", "د. محمد الشهري"],
        "الحالة": ["حاضر", "حاضر", "غائب", "حاضر"]
    },
    "sara": {
        "المادة": ["الشبكات العصبية الاصطناعية ANN", "الشبكات العصبية الاصطناعية ANN", "أمن الشبكات والمعلومات (سيبراني)", "أمن الشبكات والمعلومات (سيبراني)"],
        "اليوم": ["الاثنين", "الاثنين", "الخميس", "الخميس"],
        "التاريخ": ["2026-06-22", "2026-06-29", "2026-06-25", "2026-07-02"],
        "الوقت": ["03:00 PM", "03:00 PM", "04:00 PM", "04:00 PM"],
        "أستاذ المادة": ["د. محمد الشهري", "د. محمد الشهري", "د. محمد الشهري", "د. محمد الشهري"],
        "الحالة": ["غائب", "حاضر", "حاضر", "حاضر"]
    }
}

# دالة مطابقة الوجه
def verify_face(captured_face, knowledge_base_dir):
    captured_gray = cv2.cvtColor(captured_face, cv2.COLOR_RGB2GRAY)
    captured_gray = cv2.resize(captured_gray, (200, 200))
    for file_name in os.listdir(knowledge_base_dir):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(knowledge_base_dir, file_name)
            known_img = cv2.imread(img_path)
            known_gray = cv2.cvtColor(known_img, cv2.COLOR_BGR2GRAY)
            known_faces = face_cascade.detectMultiScale(known_gray, 1.1, 5)
            if len(known_faces) > 0:
                (x, y, w, h) = known_faces[0]
                known_face_crop = known_gray[y:y+h, x:x+w]
                known_face_crop = cv2.resize(known_face_crop, (200, 200))
                error = np.sum((captured_gray.astype("float") - known_face_crop.astype("float")) ** 2)
                error /= float(captured_gray.shape[0] * captured_gray.shape[1])
                if error < 1500:  
                    return True, os.path.splitext(file_name)[0]
    return False, None

# -------------------------------------------------------------
# القائمة الجانبية للتنقل (Navigation Sidebar)
# -------------------------------------------------------------
st.sidebar.title("🎮 لوحة التحكم والتنقل")
page = st.sidebar.radio("اختر الواجهة الحالية:", ["👤 بوابة الطالب", "👨‍🏫 لوحة تحكم الدكتور"])

# =============================================================
# 1. صفحة الطالب
# =============================================================
if page == "👤 بوابة الطالب":
    st.title("🎓 حاضر AI - بوابة الطالب الأكاديمية")
    st.subheader("حضور موثوق… بذكاء اصطناعي")
    st.write("---")
    
    st.info("مرحباً بكِ في صفحة التحقق الذكي لدفعة الحوسبة والذكاء الاصطناعي")
    student_name = st.text_input("الرجاء إدخال اسمك باللغة الإنجليزية (raneem أو njood أو sara للتجربة):")

    if student_name:
        st.success(f"أهلاً بكِ يا {student_name}. يرجى تفعيل الكاميرا للتحقق التلقائي من الحضور.")
        picture = st.camera_input("التقط صورة واضحة لوجهك")
        
        if picture:
            st.write("🔍 جاري فحص البصمة الحيوية ومطابقة الملامح...")
            img = Image.open(picture)
            img_array = np.array(img)
            gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray_img, 1.1, 5)
            
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    captured_face_crop = img_array[y:y+h, x:x+w]
                    is_matched, matched_name = verify_face(captured_face_crop, "knowledge_base")
                    
                    if is_matched and matched_name.lower() in student_name.lower():
                        cv2.rectangle(img_array, (x, y), (x+w, y+h), (0, 255, 0), 5)
                        st.image(img_array, use_container_width=True)
                        st.balloons()
                        st.success(f"✅ تم التحقق بنجاح وتثبيت حضورك للمحاضرة الحالية يا {student_name}!")
                    else:
                        cv2.rectangle(img_array, (x, y), (x+w, y+h), (255, 0, 0), 5)
                        st.image(img_array, use_container_width=True)
                        st.error("❌ فشل التحقق! الوجه لا يطابق ملامح الطالب المسجلة في هذا الحساب.")
            else:
                st.error("❌ لم يتم رصد وجه في الإطار الحركي. يرجى تعديل الإضاءة والوقوف أمام الكاميرا.")
                
        # لوحة بيانات الطالب
        st.write("---")
        st.header(f"📊 السجل الأكاديمي التفصيلي للطالبة: {student_name}")
        
        name_key = "other"
        for key in mock_students.keys():
            if key in student_name.lower():
                name_key = key
                break
        
        if name_key in mock_students:
            df = pd.DataFrame(mock_students[name_key])
            
            # حساب الإحصائيات العامة للطالبة
            total_lectures = len(df)
            total_att = len(df[df["الحالة"] == "حاضر"])
            total_abs = len(df[df["الحالة"] == "غائب"])
            overall_pct = round((total_att / total_lectures) * 100, 1) if total_lectures > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="حضورك الإجمالي", value=f"{total_att} محاضرات")
            col2.metric(label="رصيد الغياب الكلي", value=f"{total_abs} أيام", delta=f"-{total_abs}", delta_color="inverse")
            col3.metric(label="معدل الالتزام العام", value=f"{overall_pct}%")
            
            st.write("### 📝 تفاصيل الحضور اليومي بالتواريخ:")
            st.dataframe(df[["المادة", "اليوم", "التاريخ", "الوقت", "أستاذ المادة", "الحالة"]], use_container_width=True)
        else:
            st.warning("الرجاء إدخال اسم صحيح لاستعراض جدول التواريخ.")

# =============================================================
# 2. صفحة الدكتور محمد الشهري (التصفية بالمادة والتاريخ واليوم)
# =============================================================
elif page == "👨‍🏫 لوحة تحكم الدكتور":
    st.title("👨‍🏫 لوحة تحكم أعضاء هيئة التدريس والمحاضرين")
    st.write("---")
    
    password = st.text_input("الرجاء إدخال الرقم السري لدخول لوحة التحكم الإدارية:", type="password")
    
    if password == "1234":
        st.success("🔓 مرحباً بك سعادة الدكتور محمد الشهري. تم تسجيل دخولك بنجاح للوحة الإشراف الأكاديمي.")
        
        tab1, tab2 = st.tabs(["📊 كشف حضور الشعب الأكاديمية", "📩 مراجعة الأعذار المستلمة"])
        
        with tab1:
            st.write("### 🔍 استعراض حضور وغياب الطلاب بالتاريخ واليوم:")
            
            # 1. اختيار المادة
            selected_course = st.selectbox(
                "1. اختر المادة التعليمية:",
                ["الشبكات العصبية الاصطناعية ANN", "أمن الشبكات والمعلومات (سيبراني)"]
            )
            
            # تجميع التواريخ المتاحة للمادة المحددة لتظهر في القائمة
            available_dates = set()
            date_to_day_map = {}
            for s_name, data in mock_students.items():
                for i in range(len(data["المادة"])):
                    if data["المادة"][i] == selected_course and data["أستاذ المادة"][i] == "د. محمد الشهري":
                        available_dates.add(data["التاريخ"][i])
                        date_to_day_map[data["التاريخ"][i]] = data["اليوم"][i]
            
            sorted_dates = sorted(list(available_dates))
            
            if sorted_dates:
                # 2. اختيار التاريخ
                selected_date = st.selectbox("2. اختر تاريخ المحاضرة المراد تفتيشها:", sorted_dates)
                corresponding_day = date_to_day_map[selected_date]
                
                st.info(f"📅 يوم المحاضرة المتوافق مع التاريخ المحدد: **{corresponding_day}**")
                
                # بناء جدول الطلاب لهذه المادة وهذا التاريخ بالتحديد
                course_data = []
                for s_name, data in mock_students.items():
                    for i in range(len(data["المادة"])):
                        if (data["المادة"][i] == selected_course and 
                            data["التاريخ"][i] == selected_date and 
                            data["أستاذ المادة"][i] == "د. محمد الشهري"):
                            
                            course_data.append({
                                "اسم الطالبة": s_name.upper(),
                                "المقرر الدراسي": data["المادة"][i],
                                "اليوم": data["اليوم"][i],
                                "التاريخ": data["التاريخ"][i],
                                "توقيت المحاضرة": data["الوقت"][i],
                                "حالة الحضور": data["الحالة"][i]
                            })
                
                if course_data:
                    df_filtered = pd.DataFrame(course_data)
                    st.write(f"📋 **كشف أسماء الطالبات ليوم {corresponding_day} تاريخ {selected_date}:**")
                    st.dataframe(df_filtered, use_container_width=True)
                    
                    # إحصائية سريعة لليوم المحدد
                    att_count = len(df_filtered[df_filtered["حالة الحضور"] == "حاضر"])
                    abs_count = len(df_filtered[df_filtered["حالة الحضور"] == "غائب"])
                    st.caption(f"📊 إحصائية سريعة لهذه المحاضرة 👈 عدد الحاضرات: {att_count} | عدد الغائبات: {abs_count}")
            else:
                st.warning("لا توجد تواريخ مسجلة لهذه المادة حالياً.")
            
        with tab2:
            st.write("### 📥 طلبات الأعذار المستلمة لمقرراتك:")
            st.warning("⚠️ عذر طبي جديد مستلم من الطالبة: **RANEEM**")
            st.info("**المادة:** الشبكات العصبية الاصطناعية ANN \n\n**السبب المكتوب:** تغيبت بسبب وعكة صحية طارئة ومرفق التقرير الطبي من المستشفى.")
            col_acc, col_rej = st.columns(2)
            if col_acc.button("✅ اعتماد العذر وتعديل الغياب"):
                st.success("تم اعتماد عذر الطالبة رنيم بنجاح وتحديث السجل تلقائياً.")
            if col_rej.button("❌ رفض وثيقة العذر"):
                st.error("تم رفض طلب العذر.")
                
    elif password != "":
        st.error("🛑 الرقم السري غير صحيح! ليس لديك