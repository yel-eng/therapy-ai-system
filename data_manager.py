"""
data_manager.py
إدارة كل بيانات النظام (مستخدمين، مرضى، قوالب، جلسات)
"""
import streamlit as st
from datetime import datetime


# ============================================
# تهيئة البيانات الافتراضية
# ============================================
def init_data():
    """
    تهيئة البيانات مرة واحدة فقط.
    الأدمن فقط هو الموجود افتراضياً - كل الباقي يُضاف من الشاشة.
    """
    if "db" not in st.session_state:
        st.session_state.db = {
            "users": {
                "admin": {
                    "password": "admin123",
                    "role": "admin",
                    "name": "مدير المركز",
                    "specialty": None
                }
            },
            "patients": {},
            "templates": {}
        }


# ============================================
# تسجيل الدخول والخروج
# ============================================
def login(username, password):
    """يتحقق من بيانات الدخول ويرجع بيانات المستخدم"""
    init_data()
    users = st.session_state.db["users"]
    if username in users and users[username]["password"] == password:
        return users[username]
    return None


def logout():
    """تسجيل الخروج"""
    if "user" in st.session_state:
        del st.session_state["user"]


# ============================================
# إدارة المستخدمين
# ============================================
def add_user(username, password, name, role, specialty=None):
    """إضافة مستخدم جديد (مختص أو أدمن)"""
    init_data()
    if username in st.session_state.db["users"]:
        return False, "اسم المستخدم موجود بالفعل"
    
    st.session_state.db["users"][username] = {
        "password": password,
        "role": role,
        "name": name,
        "specialty": specialty
    }
    return True, "تمت الإضافة بنجاح"


def delete_user(username):
    """حذف مستخدم - مع حماية الأدمن"""
    init_data()
    if username == "admin":
        return False
    if username in st.session_state.db["users"]:
        del st.session_state.db["users"][username]
        return True
    return False


def get_all_users():
    """جلب كل المستخدمين"""
    init_data()
    return st.session_state.db["users"]


def get_specialists_list():
    """جلب قائمة بالمختصين فقط"""
    init_data()
    return {
        uid: udata["name"] 
        for uid, udata in st.session_state.db["users"].items()
        if udata["role"] == "specialist"
    }


# ============================================
# إدارة المرضى
# ============================================
def add_patient(name, age, phone, assigned_to):
    """إضافة مريض جديد مع توليد رقم تلقائي"""
    init_data()
    existing_ids = [
        int(pid[1:]) for pid in st.session_state.db["patients"].keys() 
        if pid[1:].isdigit()
    ]
    new_id = f"P{max(existing_ids) + 1:03d}" if existing_ids else "P001"
    
    st.session_state.db["patients"][new_id] = {
        "name": name,
        "age": age,
        "phone": phone,
        "assigned_to": assigned_to,
        "sessions": []
    }
    return True, new_id


def delete_patient(patient_id):
    """حذف مريض"""
    init_data()
    if patient_id in st.session_state.db["patients"]:
        del st.session_state.db["patients"][patient_id]
        return True
    return False


def update_patient_assignment(patient_id, new_specialist):
    """تغيير المختص المسؤول عن مريض"""
    init_data()
    if patient_id in st.session_state.db["patients"]:
        st.session_state.db["patients"][patient_id]["assigned_to"] = new_specialist
        return True
    return False


def get_all_patients():
    """جلب كل المرضى"""
    init_data()
    return st.session_state.db["patients"]


def get_specialist_patients(username):
    """جلب مرضى مختص معين بس"""
    init_data()
    return {
        pid: pdata for pid, pdata in st.session_state.db["patients"].items()
        if pdata.get("assigned_to") == username
    }


def get_patient_by_id(patient_id):
    """جلب مريض بالرقم"""
    init_data()
    return st.session_state.db["patients"].get(patient_id)


# ============================================
# إدارة القوالب (Templates)
# ============================================
def add_template(name, category, fields):
    """
    إضافة قالب جديد
    fields: list of dicts, كل dict فيه:
    {
        "name": "mood",
        "label": "الحالة المزاجية",
        "type": "text" | "number" | "enum" | "textarea",
        "options": [],
        "required": True/False
    }
    """
    init_data()
    existing_ids = [
        int(tid[1:]) for tid in st.session_state.db["templates"].keys() 
        if tid[1:].isdigit()
    ]
    new_id = f"T{max(existing_ids) + 1:03d}" if existing_ids else "T001"
    
    st.session_state.db["templates"][new_id] = {
        "name": name,
        "category": category,
        "fields": fields,
        "is_active": True,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # إلغاء تفعيل القوالب التانية لنفس الفئة
    for tid, tdata in st.session_state.db["templates"].items():
        if tid != new_id and tdata["category"] == category:
            tdata["is_active"] = False
    
    return True, new_id


def get_all_templates():
    """جلب كل القوالب"""
    init_data()
    return st.session_state.db["templates"]


def get_active_template(category):
    """جلب القالب النشط لفئة معينة"""
    init_data()
    for tdata in st.session_state.db["templates"].values():
        if tdata["category"] == category and tdata["is_active"]:
            return tdata
    return None


def delete_template(template_id):
    """حذف قالب"""
    init_data()
    if template_id in st.session_state.db["templates"]:
        del st.session_state.db["templates"][template_id]
        return True
    return False


def get_template_categories():
    """جلب قائمة بالفئات الموجودة"""
    init_data()
    categories = set()
    for tdata in st.session_state.db["templates"].values():
        categories.add(tdata["category"])
    return list(categories)


# ============================================
# إدارة الجلسات
# ============================================
def add_session(patient_id, category, raw_text, extracted_data, specialist_name):
    """إضافة جلسة جديدة لمريض"""
    init_data()
    if patient_id in st.session_state.db["patients"]:
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": category,
            "raw_text": raw_text,
            "extracted_data": extracted_data,
            "specialist": specialist_name
        }
        st.session_state.db["patients"][patient_id]["sessions"].append(session)
        return True
    return False
