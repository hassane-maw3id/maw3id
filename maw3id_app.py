# -*- coding: utf-8 -*-
"""
MAW3ID | موعد
Prototype de présentation - application de rappel et de gestion des paiements.
Lancer avec : streamlit run maw3id_app.py

IMPORTANT :
- Les paiements sont simulés. Aucune banque, carte, NFC ou passerelle réelle n'est connectée.
- Les notifications sont affichées dans l'application. Les notifications push nécessitent un service backend.
- Les données sont stockées localement dans maw3id_data.json.
"""

import json
import uuid
from pathlib import Path
from datetime import date, datetime, timedelta
import calendar

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "maw3id_data.json"

st.set_page_config(
    page_title="MAW3ID | موعد",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- STYLE -----------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], button, input, textarea, select {
    font-family: 'Cairo', sans-serif !important;
}
.stApp { background: #f4f7fb; }
.block-container { padding-top: 1.35rem; padding-bottom: 2.5rem; max-width: 1450px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#102b50,#164b7c); }
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stRadio label { padding: 5px 0; }
.hero {
    background: linear-gradient(115deg,#102b50 0%,#1769aa 100%);
    border-radius: 22px; padding: 27px 30px; color: white; margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(16,43,80,.12);
}
.hero h1 { color:#fff !important; font-size:34px !important; margin:0 !important; font-weight:800; }
.hero p { color:#e3f1ff !important; margin:5px 0 0 0; }
.metric-card {
    background:#fff; border:1px solid #e5edf6; border-radius:16px;
    padding:17px 18px; min-height:112px; box-shadow:0 3px 12px rgba(20,55,90,.035);
}
.metric-label { color:#64748b; font-size:13px; }
.metric-value { color:#12345b; font-size:25px; font-weight:800; margin-top:4px; }
.metric-foot { color:#8492a6; font-size:11px; margin-top:2px; }
.section-title { color:#153a63; font-size:22px; font-weight:800; margin: 8px 0 13px; }
.soft-card {
    background:white; border:1px solid #e5edf6; border-radius:16px;
    padding:17px 19px; margin-bottom:11px;
}
.small-muted { color:#64748b; font-size:12px; }
.pill {
    display:inline-block; border-radius:30px; padding:3px 10px;
    background:#eaf3ff; color:#155b99; font-size:11px; font-weight:700;
}
div.stButton > button { border-radius:10px; font-weight:700; min-height:2.55rem; }
div[data-testid="stForm"] { background:white; border:1px solid #e5edf6; border-radius:15px; padding:18px; }
[data-testid="stMetric"] { background:white; border:1px solid #e5edf6; padding:12px; border-radius:13px; }
hr { border-color:#e5edf6; }
</style>
""", unsafe_allow_html=True)

# RTL support for Arabic text and layout
st.markdown("""
<style>
.main .block-container { direction: rtl; text-align: right; }
[data-testid="stSidebar"] { direction: rtl; text-align: right; }
div[data-testid="stDataFrame"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

# --------------------------- DATA ------------------------------------------
def seed_data():
    today = date.today()
    return {
        "profile": {"name": "مستخدم موعد", "email": "user@example.com", "phone": "", "language": "العربية"},
        "settings": {"reminder_48": True, "reminder_24": True, "reminder_day": True,
                     "currency": "MAD", "demo_mode": True},
        "items": [
            {"id": str(uuid.uuid4()), "name": "فاتورة الكهرباء", "category": "فاتورة",
             "provider": "المكتب الوطني للكهرباء والماء", "amount": 250.0,
             "due": (today + timedelta(days=2)).isoformat(), "frequency": "شهري",
             "status": "غير مؤداة", "note": "مثال توضيحي", "created": today.isoformat()},
            {"id": str(uuid.uuid4()), "name": "الإنترنت", "category": "فاتورة",
             "provider": "مزود خدمة الإنترنت", "amount": 200.0,
             "due": (today + timedelta(days=5)).isoformat(), "frequency": "شهري",
             "status": "غير مؤداة", "note": "", "created": today.isoformat()},
            {"id": str(uuid.uuid4()), "name": "ضريبة السيارة", "category": "ضريبة",
             "provider": "الجهة المختصة", "amount": 350.0,
             "due": (today + timedelta(days=12)).isoformat(), "frequency": "سنوي",
             "status": "غير مؤداة", "note": "موعد سنوي تجريبي", "created": today.isoformat()},
            {"id": str(uuid.uuid4()), "name": "Netflix", "category": "اشتراك",
             "provider": "Netflix", "amount": 95.0,
             "due": (today + timedelta(days=1)).isoformat(), "frequency": "شهري",
             "status": "نشط", "note": "تجديد الاشتراك", "created": today.isoformat()},
            {"id": str(uuid.uuid4()), "name": "تأمين السيارة", "category": "تأمين",
             "provider": "شركة التأمين", "amount": 1200.0,
             "due": (today + timedelta(days=25)).isoformat(), "frequency": "سنوي",
             "status": "غير مؤداة", "note": "", "created": today.isoformat()},
        ],
        "payments": [],
        "cancellation_requests": [],
    }

def load_data():
    if not DATA_FILE.exists():
        data = seed_data()
        save_data(data)
        return data
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in seed_data().items():
            data.setdefault(key, value)
        return data
    except Exception:
        data = seed_data()
        save_data(data)
        return data

def save_data(data):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

def persist():
    save_data(st.session_state.db)

def money(value):
    return f"{float(value):,.2f} درهم"

def as_date(value):
    return date.fromisoformat(value)

def days_left(item):
    return (as_date(item["due"]) - date.today()).days

def status_label(item):
    if item["status"] == "مؤداة":
        return "مؤداة"
    if item["status"] == "ملغى":
        return "ملغى"
    if item["category"] == "اشتراك" and item["status"] == "نشط":
        return "اشتراك نشط"
    d = days_left(item)
    if d < 0:
        return "متأخر"
    if d == 0:
        return "اليوم"
    if d <= 2:
        return "قريب جداً"
    return "قادم"

def add_payment(item, method):
    payment = {
        "id": str(uuid.uuid4()),
        "item_id": item["id"],
        "name": item["name"],
        "amount": float(item["amount"]),
        "date": date.today().isoformat(),
        "method": method,
        "reference": "MW-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "receipt": "وصل تجريبي",
    }
    db["payments"].append(payment)
    item["status"] = "مؤداة"
    persist()
    return payment

def get_item(item_id):
    return next((x for x in db["items"] if x["id"] == item_id), None)

# --------------------------- SIDEBAR ---------------------------------------
st.sidebar.markdown("""
<div style="padding:8px 5px 18px">
  <div style="font-size:30px;font-weight:800">📅 MAW3ID</div>
  <div style="font-size:13px;color:#d9eaff">موعد • مساعدك لتنظيم الالتزامات</div>
</div>
""", unsafe_allow_html=True)

pages = [
    "🏠 الرئيسية", "📋 الفواتير والمواعيد", "➕ إضافة التزام",
    "🧾 الضرائب", "🔁 الاشتراكات", "💳 الأداءات",
    "🔔 الإشعارات", "🗓️ التقويم", "🧾 سجل الأداءات",
    "📊 المصاريف", "⭐ Premium", "👤 حسابي", "ℹ️ عن المشروع"
]
page = st.sidebar.radio("القائمة الرئيسية", pages, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption("نسخة العرض التجريبية")
if st.sidebar.button("↻ إعادة البيانات التجريبية", use_container_width=True):
    st.session_state.db = seed_data()
    persist()
    st.rerun()
st.sidebar.markdown("""
<div style="font-size:11px;color:#d8e8f8;margin-top:20px">
MAW3ID Prototype v1.0<br>البيانات محفوظة محلياً على هذا الجهاز.
</div>
""", unsafe_allow_html=True)

# --------------------------- COMMON HEADER ---------------------------------
st.markdown(f"""
<div class="hero">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:15px;flex-wrap:wrap">
    <div>
      <h1>مرحباً بك في موعد 👋</h1>
      <p>لا تنشغل بتذكّر مواعيدك، تطبيقنا يتكفل بتذكيرك بها.</p>
    </div>
    <div style="text-align:left;color:#e3f1ff">
      <div style="font-size:13px">تاريخ اليوم</div>
      <div style="font-size:20px;font-weight:700">{date.today().strftime("%d/%m/%Y")}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

items = db["items"]
unpaid = [x for x in items if x["status"] == "غير مؤداة"]
upcoming = sorted([x for x in items if x["status"] not in ("مؤداة", "ملغى")], key=lambda x:x["due"])
total_unpaid = sum(float(x["amount"]) for x in unpaid)
active_subs = [x for x in items if x["category"] == "اشتراك" and x["status"] == "نشط"]

def metric_card(label, value, foot=""):
    st.markdown(f"""<div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-foot">{foot}</div>
    </div>""", unsafe_allow_html=True)

def item_card(item, show_actions=True, prefix="item"):
    d = days_left(item)
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    a,b = st.columns([3,1])
    with a:
        st.markdown(f"**{item['name']}** <span class='pill'>{item['category']}</span>", unsafe_allow_html=True)
        st.caption(f"الجهة: {item.get('provider') or 'غير محددة'}")
        st.write(f"📅 تاريخ الاستحقاق: **{as_date(item['due']).strftime('%d/%m/%Y')}** | الدورية: {item['frequency']}")
        st.caption(f"الحالة: {status_label(item)}")
    with b:
        st.markdown(f"<div style='font-size:12px;color:#64748b'>المبلغ</div><div style='font-size:21px;font-weight:800;color:#12345b'>{money(item['amount'])}</div>", unsafe_allow_html=True)
        if show_actions:
            if item["status"] == "غير مؤداة":
                with st.popover("أداء الآن"):
                    method = st.selectbox("وسيلة الأداء", ["بطاقة بنكية (محاكاة)", "تحويل بنكي (محاكاة)", "NFC (محاكاة)", "الموقع الرسمي"], key=f"{prefix}_method_{item['id']}")
                    st.warning("هذه عملية تجريبية فقط، لن يتم سحب أي أموال.")
                    if st.button("تأكيد الأداء التجريبي", key=f"{prefix}_pay_{item['id']}", type="primary"):
                        add_payment(item, method)
                        st.success("تم تسجيل الأداء التجريبي.")
                        st.rerun()
            elif item["status"] == "مؤداة":
                st.success("تم الأداء")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------- PAGES -----------------------------------------
if page == "🏠 الرئيسية":
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("المبالغ غير المؤداة", money(total_unpaid), "إجمالي الالتزامات المفتوحة")
    with c2: metric_card("الفواتير غير المؤداة", str(len(unpaid)), "تحتاج إلى المتابعة")
    with c3: metric_card("الاشتراكات النشطة", str(len(active_subs)), "اشتراكات مسجلة")
    with c4: metric_card("المواعيد القادمة", str(len(upcoming)), "كل الالتزامات المسجلة")
    st.markdown('<div class="section-title">⏰ أقرب المواعيد</div>', unsafe_allow_html=True)
    if upcoming:
        for item in upcoming[:4]:
            item_card(item, prefix="home")
    else:
        st.success("رائع! لا توجد مواعيد معلقة.")
    left,right = st.columns([1.2,1])
    with left:
        st.markdown('<div class="section-title">📈 توزيع الالتزامات</div>', unsafe_allow_html=True)
        if items:
            df = pd.DataFrame(items)
            totals = df.groupby("category")["amount"].sum()
            st.bar_chart(totals)
    with right:
        st.markdown('<div class="section-title">💡 ملخص موعد</div>', unsafe_allow_html=True)
        paid_total = sum(p["amount"] for p in db["payments"])
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.write(f"✅ مجموع الأداءات المسجلة: **{money(paid_total)}**")
        st.write(f"🔔 أقرب موعد: **{upcoming[0]['name'] if upcoming else 'لا يوجد'}**")
        st.write(f"💰 مجموع الالتزامات غير المؤداة: **{money(total_unpaid)}**")
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("نصيحة: أضف جميع فواتيرك واشتراكاتك حتى يساعدك موعد على تتبعها.")

elif page == "📋 الفواتير والمواعيد":
    st.markdown('<div class="section-title">📋 جميع الفواتير والمواعيد</div>', unsafe_allow_html=True)
    q = st.text_input("🔎 ابحث عن فاتورة أو خدمة", placeholder="مثال: الكهرباء، الإنترنت...")
    f1,f2 = st.columns(2)
    category_filter = f1.selectbox("تصفية حسب النوع", ["الكل","فاتورة","ضريبة","اشتراك","تأمين","موعد شخصي","موعد إداري","أخرى"])
    status_filter = f2.selectbox("تصفية حسب الحالة", ["الكل","غير مؤداة","مؤداة","نشط","ملغى"])
    filtered = []
    for x in items:
        if q and q.lower() not in (x["name"] + x.get("provider","")).lower(): continue
        if category_filter != "الكل" and x["category"] != category_filter: continue
        if status_filter != "الكل" and x["status"] != status_filter: continue
        filtered.append(x)
    st.caption(f"عدد النتائج: {len(filtered)}")
    for x in sorted(filtered,key=lambda y:y["due"]):
        item_card(x, prefix="list")
        with st.expander(f"إدارة: {x['name']}"):
            e1,e2,e3 = st.columns(3)
            with e1:
                new_name = st.text_input("الاسم", x["name"], key=f"edit_name_{x['id']}")
                new_amount = st.number_input("المبلغ", min_value=0.0, value=float(x["amount"]), key=f"edit_amount_{x['id']}")
            with e2:
                new_due = st.date_input("التاريخ", value=as_date(x["due"]), key=f"edit_due_{x['id']}")
                new_category = st.selectbox("النوع", ["فاتورة","ضريبة","اشتراك","تأمين","موعد شخصي","موعد إداري","أخرى"], index=["فاتورة","ضريبة","اشتراك","تأمين","موعد شخصي","موعد إداري","أخرى"].index(x["category"]) if x["category"] in ["فاتورة","ضريبة","اشتراك","تأمين","موعد شخصي","موعد إداري","أخرى"] else 0, key=f"edit_cat_{x['id']}")
            with e3:
                new_status = st.selectbox("الحالة", ["غير مؤداة","مؤداة","نشط","ملغى"], index=["غير مؤداة","مؤداة","نشط","ملغى"].index(x["status"]) if x["status"] in ["غير مؤداة","مؤداة","نشط","ملغى"] else 0, key=f"edit_status_{x['id']}")
                new_note = st.text_input("ملاحظات", x.get("note",""), key=f"edit_note_{x['id']}")
            if st.button("حفظ التعديلات", key=f"save_edit_{x['id']}"):
                x.update({"name":new_name,"amount":new_amount,"due":new_due.isoformat(),"category":new_category,"status":new_status,"note":new_note})
                persist(); st.success("تم حفظ التعديلات."); st.rerun()
            if st.button("حذف هذا الالتزام", key=f"delete_{x['id']}"):
                db["items"] = [z for z in db["items"] if z["id"] != x["id"]]
                persist()
                st.warning("تم حذف الالتزام.")
                st.rerun()
