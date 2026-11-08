"""
app.py
الواجهة الرئيسية لنظام التقارير العلاجي الذكي
"""
import streamlit as st
from data_manager import (
    init_data, login, logout,
    add_user, delete_user, get_all_users, get_specialists_list,
    add_patient, delete_patient, update_patient_assignment,
    get_all_patients, get_specialist_patients, get_patient_by_id,
    add_template, get_all_templates, get_active_template, delete_template,
    get_template_categories,
    add_session
)

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام التقارير الذكي",
    page_icon="🏥",
    layout="wide"
)
init_data()

# ============================================
# شاشة تسجيل الدخول
# ============================================
if "user" not in st.session_state:
    st.title("🏥 نظام التقارير العلاجي الذكي")
    st.markdown("### 🔐 تسجيل الدخول")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("اسم المستخدم")
    with col2:
        password = st.text_input("كلمة المرور", type="password")
    
    if st.button("🚀 دخول", type="primary", use_container_width=True):
        user_data = login(username, password)
        if user_data:
            st.session_state["user"] = {"username": username, **user_data}
            st.rerun()
        else:
            st.error("❌ بيانات الدخول غير صحيحة")
    
    st.markdown("---")
    st.info("""
    **الحساب الافتراضي:**
    - 👑 Admin: `admin` / `admin123`
    
    💡 بعد تسجيل الدخول، الأدمن يقدر يضيف كل المختصين من شاشة "إدارة المستخدمين"
    """)
    st.stop()

# ============================================
# الشريط الجانبي
# ============================================
user = st.session_state["user"]

st.sidebar.title(f"👋 {user['name']}")
st.sidebar.write(f"**الدور**: {'👑 مدير' if user['role'] == 'admin' else '👨‍⚕️ مختص'}")
if user.get("specialty"):
    st.sidebar.write(f"**التخصص**: {user['specialty']}")

st.sidebar.markdown("---")

# قائمة التنقل حسب الدور
if user["role"] == "admin":
    page = st.sidebar.radio(
        "📋 القائمة",
        ["🏠 الرئيسية", "👥 إدارة المستخدمين", "🧑 إدارة المرضى", "📋 إدارة القوالب"]
    )
else:
    page = st.sidebar.radio(
        "📋 القائمة",
        ["🏠 حالاتي", "📝 جلسة جديدة", "📊 تقارير مرضاي"]
    )

if st.sidebar.button("🚪 تسجيل خروج", use_container_width=True):
    logout()
    st.rerun()

# ============================================
# صفحات الأدمن
# ============================================
if user["role"] == "admin":
    
    # --- الصفحة الرئيسية ---
    if page == "🏠 الرئيسية":
        st.title("🏠 لوحة تحكم المدير")
        
        users = get_all_users()
        patients = get_all_patients()
        templates = get_all_templates()
        specialists = [u for u in users.values() if u["role"] == "specialist"]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 المستخدمين", len(users))
        c2.metric("👨‍⚕️ المختصين", len(specialists))
        c3.metric("🧑 المرضى", len(patients))
        c4.metric("📋 القوالب", len(templates))
        
        st.markdown("---")
        st.success("✅ استخدم القائمة الجانبية للتنقل بين الأقسام.")
    
    # --- إدارة المستخدمين ---
    elif page == "👥 إدارة المستخدمين":
        st.title("👥 إدارة المستخدمين")
        
        tab1, tab2 = st.tabs(["➕ إضافة مستخدم جديد", "📋 قائمة المستخدمين"])
        
        with tab1:
            st.markdown("### ➕ إضافة مستخدم جديد")
            
            with st.form("add_user_form"):
                new_username = st.text_input("اسم المستخدم (إنجليزي بدون مسافات)", placeholder="dr_khaled")
                new_password = st.text_input("كلمة المرور", placeholder="khaled123")
                new_name = st.text_input("الاسم الكامل", placeholder="د. خالد محمود")
                new_role = st.selectbox(
                    "الدور", 
                    ["specialist", "admin"],
                    format_func=lambda x: "👨‍⚕️ مختص" if x == "specialist" else "👑 مدير"
                )
                
                new_specialty = None
                if new_role == "specialist":
                    new_specialty = st.selectbox(
                        "التخصص",
                        ["تخاطب أطفال", "تأهيل حركي (كبار سن)", "دعم نفسي", "تخاطب كبار سن"]
                    )
                
                if st.form_submit_button("💾 حفظ المستخدم", type="primary", use_container_width=True):
                    if new_username and new_password and new_name:
                        success, msg = add_user(new_username, new_password, new_name, new_role, new_specialty)
                        if success:
                            st.success(f"✅ {msg}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.warning("⚠️ الرجاء ملء جميع الحقول")
        
        with tab2:
            st.markdown("### 📋 المستخدمين الحاليين")
            users = get_all_users()
            
            if len(users) == 1:
                st.warning("⚠️ لا يوجد مختصين. اذهبي لتاب 'إضافة مستخدم جديد'.")
            
            for uid, udata in users.items():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    
                    c1.markdown(f"**👤 {udata['name']}**")
                    if udata.get("specialty"):
                        c1.caption(f"🏷️ {udata['specialty']}")
                    
                    c2.write(f"🔑 `{uid}`")
                    
                    role_icon = "👑 مدير" if udata["role"] == "admin" else "👨‍⚕️ مختص"
                    c3.write(role_icon)
                    
                    if uid == "admin":
                        c4.caption("🔒 أساسي")
                    else:
                        if c4.button("🗑️", key=f"del_{uid}"):
                            st.session_state[f"confirm_del_{uid}"] = True
                    
                    if st.session_state.get(f"confirm_del_{uid}"):
                        st.warning(f"⚠️ حذف {udata['name']}؟")
                        c1, c2, _ = st.columns([1, 1, 4])
                        if c1.button("✅ نعم", key=f"yes_{uid}"):
                            delete_user(uid)
                            st.session_state[f"confirm_del_{uid}"] = False
                            st.rerun()
                        if c2.button("❌ إلغاء", key=f"no_{uid}"):
                            st.session_state[f"confirm_del_{uid}"] = False
                            st.rerun()
    
    # --- إدارة المرضى ---
    elif page == "🧑 إدارة المرضى":
        st.title("🧑 إدارة المرضى")
        
        tab1, tab2 = st.tabs(["➕ إضافة مريض جديد", "📋 قائمة المرضى"])
        
        with tab1:
            st.markdown("### ➕ إضافة مريض جديد")
            specialists = get_specialists_list()
            
            if not specialists:
                st.warning("⚠️ يجب إضافة مختصين أولاً من 'إدارة المستخدمين'")
            else:
                with st.form("add_patient_form"):
                    p_name = st.text_input("اسم المريض")
                    p_age = st.number_input("العمر", 0, 120, 5)
                    p_phone = st.text_input("رقم الهاتف")
                    p_specialist = st.selectbox(
                        "المختص المسؤول",
                        options=list(specialists.keys()),
                        format_func=lambda x: specialists[x]
                    )
                    
                    if st.form_submit_button("💾 حفظ المريض", type="primary"):
                        if p_name and p_phone:
                            success, pid = add_patient(p_name, int(p_age), p_phone, p_specialist)
                            st.success(f"✅ تمت الإضافة برقم: {pid}")
                            st.rerun()
                        else:
                            st.warning("⚠️ الرجاء ملء الاسم ورقم الهاتف")
        
        with tab2:
            st.markdown("### 📋 المرضى الحاليين")
            patients = get_all_patients()
            specialists = get_specialists_list()
            
            if not patients:
                st.info("📭 لا يوجد مرضى.")
            else:
                for pid, pdata in patients.items():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 1])
                        c1.markdown(f"### 🧑 {pdata['name']}")
                        c2.write(f"**الرقم**: {pid}")
                        c2.write(f"**العمر**: {pdata['age']} سنة")
                        c2.write(f"**📞**: {pdata['phone']}")
                        c2.write(f"**📝 الجلسات**: {len(pdata['sessions'])}")
                        
                        if specialists:
                            current_spec = pdata["assigned_to"]
                            spec_keys = list(specialists.keys())
                            default_idx = spec_keys.index(current_spec) if current_spec in spec_keys else 0
                            
                            new_spec = c3.selectbox(
                                "المختص",
                                options=spec_keys,
                                format_func=lambda x: specialists[x],
                                index=default_idx,
                                key=f"spec_{pid}"
                            )
                            if new_spec != current_spec:
                                update_patient_assignment(pid, new_spec)
                                st.rerun()
                        
                        if c3.button("🗑️ حذف", key=f"delp_{pid}"):
                            delete_patient(pid)
                            st.rerun()
    
    # --- إدارة القوالب ---
    elif page == "📋 إدارة القوالب":
        st.title("📋 إدارة القوالب")
        st.info("💡 من هنا تحددين شكل التقارير اللي هيمشي عليها الذكاء الاصطناعي")
        
        tab1, tab2 = st.tabs(["➕ إضافة قالب جديد", "📋 القوالب الحالية"])
        
        with tab1:
            st.markdown("### ➕ إضافة قالب جديد")
            
            with st.form("add_template_form"):
                template_name = st.text_input("اسم القالب", placeholder="تقرير جلسة تخاطب أطفال")
                template_category = st.text_input("فئة القالب", placeholder="تخاطب أطفال")
                
                st.markdown("---")
                st.markdown("### 📝 حقول التقرير")
                
                num_fields = st.number_input("عدد الحقول", 1, 20, 5, step=1)
                
                fields = []
                for i in range(int(num_fields)):
                    st.markdown(f"**الحقل {i+1}**")
                    fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
                    
                    with fc1:
                        field_name = st.text_input("الاسم (إنجليزي)", key=f"fname_{i}", placeholder="mood")
                    with fc2:
                        field_label = st.text_input("التسمية (عربي)", key=f"flabel_{i}", placeholder="الحالة المزاجية")
                    with fc3:
                        field_type = st.selectbox(
                            "النوع", 
                            ["text", "number", "enum", "textarea"],
                            key=f"ftype_{i}"
                        )
                    with fc4:
                        field_required = st.checkbox("مطلوب", key=f"freq_{i}", value=True)
                    
                    field_options = []
                    if field_type == "enum":
                        options_text = st.text_input(
                            "الخيارات (مفصولة بفاصلة)",
                            key=f"fopt_{i}",
                            placeholder="متعاون, غير متعاون, عدواني"
                        )
                        field_options = [opt.strip() for opt in options_text.split(",") if opt.strip()]
                    
                    fields.append({
                        "name": field_name,
                        "label": field_label,
                        "type": field_type,
                        "options": field_options,
                        "required": field_required
                    })
                
                if st.form_submit_button("💾 حفظ القالب", type="primary", use_container_width=True):
                    if template_name and template_category:
                        valid_fields = [f for f in fields if f["name"] and f["label"]]
                        if valid_fields:
                            success, tid = add_template(template_name, template_category, valid_fields)
                            if success:
                                st.success(f"✅ تم حفظ القالب برقم: {tid}")
                                st.balloons()
                                st.rerun()
                        else:
                            st.warning("⚠️ الرجاء ملء اسم وتسمية لكل حقل")
                    else:
                        st.warning("⚠️ الرجاء ملء اسم القالب والفئة")
        
        with tab2:
            st.markdown("### 📋 القوالب الحالية")
            templates = get_all_templates()
            
            if not templates:
                st.info("📭 لا توجد قوالب.")
            else:
                for tid, tdata in templates.items():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 2, 1])
                        
                        c1.markdown(f"### 📋 {tdata['name']}")
                        c1.caption(f"الفئة: {tdata['category']} | أُنشئ: {tdata['created_at']}")
                        
                        status = "✅ نشط" if tdata["is_active"] else "⏸️ غير نشط"
                        c2.write(status)
                        c2.caption(f"عدد الحقول: {len(tdata['fields'])}")
                        
                        if c3.button("🗑️", key=f"delt_{tid}"):
                            delete_template(tid)
                            st.rerun()
                        
                        with st.expander("📝 عرض الحقول"):
                            for field in tdata["fields"]:
                                req = "⭐" if field["required"] else ""
                                opts = f" - الخيارات: {field['options']}" if field["type"] == "enum" else ""
                                st.write(f"- **{field['label']}** (`{field['name']}`) - النوع: {field['type']} {req}{opts}")

# ============================================
# صفحات المختص
# ============================================
else:
    if page == "🏠 حالاتي":
        st.title(f"🏠 حالاتي - {user.get('specialty', '')}")
        
        patients = get_specialist_patients(user["username"])
        
        if not patients:
            st.info("📭 مفيش حالات موزعة عليك. يرجى التواصل مع الإدارة.")
        else:
            cols = st.columns(2)
            for i, (pid, pdata) in enumerate(patients.items()):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### 🧑 {pdata['name']}")
                        st.write(f"**الرقم**: {pid}")
                        st.write(f"**العمر**: {pdata['age']} سنة")
                        st.write(f"**📞**: {pdata['phone']}")
                        st.write(f"**📝 عدد الجلسات**: {len(pdata['sessions'])}")
                        
                        if pdata["sessions"]:
                            last = pdata["sessions"][-1]
                            st.caption(f"آخر جلسة: {last['date']}")
    
    elif page == "📝 جلسة جديدة":
        st.title("📝 جلسة جديدة")
        st.info("🚧 هذا القسم قيد التطوير - سيتم إضافة شاشة كتابة التقرير والذكاء الاصطناعي في الخطوة الجاية")
    
    elif page == "📊 تقارير مرضاي":
        st.title("📊 تقارير مرضاي")
        st.info("🚧 هذا القسم قيد التطوير")

# ============================================
# Footer
# ============================================
st.sidebar.markdown("---")
st.sidebar.caption("🏥 نظام التقارير الذكي v1.0")
