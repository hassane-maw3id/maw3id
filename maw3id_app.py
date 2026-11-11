
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
import streamlit as st
st.markdown("""
<style>
    html, body, [class*="css"], p, span, label, div, small {
        color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #020617 !important;
    }
</style>
""", unsafe_allow_html=True)

)
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
        st.markdown(f"**{item['name']}**　<span class='pill'>{item['category']}</span>", unsafe_allow_html=True)
        st.caption(f"الجهة: {item.get('provider') or 'غير محددة'}")
        st.write(f"📅 تاريخ الاستحقاق: **{as_date(item['due']).strftime('%d/%m/%Y')}**　|　الدورية: {item['frequency']}")
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
                persist(); st.warning("تم حذف الالتزام."); st.rerun()

elif page == "➕ إضافة التزام":
    st.markdown('<div class="section-title">➕ إضافة فاتورة أو التزام جديد</div>', unsafe_allow_html=True)
    st.write("سجّل المعلومات الأساسية، وسيظهر الالتزام مباشرة في لوحة التحكم.")
    with st.form("new_item_form", clear_on_submit=True):
        col1,col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم الفاتورة أو الخدمة *", placeholder="مثال: فاتورة الماء")
            category = st.selectbox("نوع الالتزام", ["فاتورة","ضريبة","اشتراك","تأمين","موعد شخصي","موعد إداري","أخرى"])
            provider = st.text_input("الجهة أو مقدم الخدمة", placeholder="مثال: شركة أو مؤسسة")
            amount = st.number_input("المبلغ بالدرهم", min_value=0.0, step=10.0)
        with col2:
            due = st.date_input("تاريخ الأداء أو الموعد", value=date.today()+timedelta(days=7))
            frequency = st.selectbox("دورية الأداء", ["مرة واحدة","شهري","كل 3 أشهر","نصف سنوي","سنوي"])
            status = st.selectbox("الحالة الأولية", ["غير مؤداة","نشط"])
            note = st.text_area("ملاحظات إضافية")
        submitted = st.form_submit_button("💾 حفظ الالتزام", type="primary", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("المرجو إدخال اسم الالتزام.")
            else:
                db["items"].append({
                    "id":str(uuid.uuid4()),"name":name.strip(),"category":category,
                    "provider":provider.strip(),"amount":float(amount),"due":due.isoformat(),
                    "frequency":frequency,"status":"نشط" if category=="اشتراك" and status=="نشط" else status,
                    "note":note.strip(),"created":date.today().isoformat()
                })
                persist(); st.success("تمت إضافة الالتزام بنجاح."); st.rerun()
    st.markdown("---")
    st.subheader("📷 إضافة فاتورة عن طريق الصورة — ميزة مستقبلية")
    st.info("في النسخة النهائية يمكن إضافة OCR لاستخراج اسم الجهة والمبلغ وتاريخ الاستحقاق من صورة الفاتورة تلقائياً. هذه الخاصية غير مفعلة في هذا النموذج.")

elif page == "🧾 الضرائب":
    st.markdown('<div class="section-title">🧾 الضرائب والرسوم</div>', unsafe_allow_html=True)
    tax_items = [x for x in items if x["category"] == "ضريبة"]
    st.write("تابع المواعيد الضريبية السنوية أو الدورية في مكان واحد.")
    if tax_items:
        for x in tax_items: item_card(x, prefix="tax")
    else: st.info("لم تتم إضافة ضرائب بعد. استعمل صفحة إضافة التزام.")

elif page == "🔁 الاشتراكات":
    st.markdown('<div class="section-title">🔁 إدارة الاشتراكات</div>', unsafe_allow_html=True)
    st.write("راقب تواريخ التجديد واتخذ قرارك قبل اقتطاع المبلغ.")
    subs = [x for x in items if x["category"] == "اشتراك"]
    if not subs: st.info("لا توجد اشتراكات مسجلة.")
    for x in subs:
        item_card(x, prefix="sub")
        if x["status"] == "نشط":
            with st.expander(f"قرار التجديد: {x['name']}"):
                st.write(f"سيتم تجديد الاشتراك بتاريخ {as_date(x['due']).strftime('%d/%m/%Y')} بمبلغ {money(x['amount'])}.")
                choice = st.radio("ماذا تريد أن تفعل؟", ["أريد الاستمرار","أريد طلب الإلغاء"], horizontal=True, key=f"decision_{x['id']}")
                if st.button("تأكيد الاختيار", key=f"confirm_decision_{x['id']}"):
                    if choice == "أريد طلب الإلغاء":
                        db["cancellation_requests"].append({"name":x["name"],"date":date.today().isoformat(),"status":"يحتاج إلى إتمام الإلغاء لدى مقدم الخدمة"})
                        x["status"] = "طلب إلغاء"
                        persist()
                        st.warning("تم تسجيل طلب الإلغاء داخل موعد. يجب إتمام الإلغاء لدى مقدم الخدمة الرسمي.")
                    else:
                        st.success("تم تسجيل رغبتك في الاستمرار.")
                    st.rerun()
    st.caption("موعد لا يلغي الاشتراكات لدى الشركات تلقائياً؛ يعرض تذكيراً وإرشادات لتجنب التجديد غير المرغوب.")

elif page == "💳 الأداءات":
    st.markdown('<div class="section-title">💳 مركز الأداءات</div>', unsafe_allow_html=True)
    st.warning("وضع العرض: جميع وسائل الأداء هنا محاكاة فقط. لا تدخل بيانات بطاقتك البنكية ولا يتم تحويل أي أموال.")
    payable = [x for x in items if x["status"] == "غير مؤداة"]
    st.write(f"لديك {len(payable)} التزاماً غير مؤدى.")
    for x in payable:
        item_card(x, prefix="payments")
    st.markdown("#### وسائل الأداء التي يستهدف التطبيق دعمها")
    a,b,c,d = st.columns(4)
    with a: st.markdown("### 💳"); st.write("البطاقة البنكية")
    with b: st.markdown("### 📲"); st.write("NFC عند الدعم")
    with c: st.markdown("### 🏦"); st.write("تحويل بنكي")
    with d: st.markdown("### 🌐"); st.write("الموقع الرسمي")
    st.caption("التكامل الحقيقي يتطلب اتفاقيات مع مزودي الأداء والجهات المعنية، واعتماداً أمنياً وقانونياً.")

elif page == "🔔 الإشعارات":
    st.markdown('<div class="section-title">🔔 مركز الإشعارات والتذكير</div>', unsafe_allow_html=True)
    s = db["settings"]
    st.write("اختر متى تريد أن يذكّرك التطبيق قبل الموعد:")
    with st.form("reminder_settings"):
        r1 = st.checkbox("التذكير الأول: قبل الموعد بـ 48 ساعة", value=s.get("reminder_48",True))
        r2 = st.checkbox("التذكير الثاني: قبل الموعد بـ 24 ساعة", value=s.get("reminder_24",True))
        r3 = st.checkbox("التذكير الثالث: يوم الموعد", value=s.get("reminder_day",True))
        saved = st.form_submit_button("حفظ إعدادات التذكير", type="primary")
        if saved:
            s.update({"reminder_48":r1,"reminder_24":r2,"reminder_day":r3}); persist()
            st.success("تم حفظ إعدادات التذكير.")
    st.markdown("---")
    st.subheader("التنبيهات التي تستحق الانتباه الآن")
    alerts = []
    for x in items:
        if x["status"] in ("مؤداة","ملغى"): continue
        d = days_left(x)
        if d < 0: alerts.append(("🔴",f"فات الموعد: {x['name']} منذ {abs(d)} يوم"))
        elif d == 0 and s.get("reminder_day"): alerts.append(("🟠",f"اليوم موعد: {x['name']} — {money(x['amount'])}"))
        elif d == 1 and s.get("reminder_24"): alerts.append(("🟠",f"بقي 24 ساعة على: {x['name']} — {money(x['amount'])}"))
        elif d == 2 and s.get("reminder_48"): alerts.append(("🔵",f"بقي 48 ساعة على: {x['name']} — {money(x['amount'])}"))
    if alerts:
        for icon,msg in alerts: st.warning(f"{icon} {msg}")
    else: st.success("لا توجد تنبيهات مستحقة حالياً.")
    st.info("ملاحظة تقنية: هذه تنبيهات داخل التطبيق. إرسال إشعارات فعلية حتى والتطبيق مغلق يحتاج إلى خادم خلفي وخدمة Push Notifications.")

elif page == "🗓️ التقويم":
    st.markdown('<div class="section-title">🗓️ تقويم المواعيد</div>', unsafe_allow_html=True)
    chosen = st.date_input("اختر يوماً لعرض التزاماته", value=date.today())
    day_items = [x for x in items if as_date(x["due"]) == chosen]
    if day_items:
        for x in day_items:
            st.info(f"**{x['name']}** — {money(x['amount'])} — {status_label(x)}")
    else: st.write("لا توجد التزامات في هذا اليوم.")
    st.markdown("#### المواعيد المسجلة")
    for x in sorted(items,key=lambda y:y["due"]):
        icon = "✅" if x["status"]=="مؤداة" else ("🔴" if days_left(x)<0 else "🟠" if days_left(x)<=2 else "🔵")
        st.write(f"{icon} **{as_date(x['due']).strftime('%d/%m/%Y')}** — {x['name']} — {money(x['amount'])}")
    st.caption("الألوان: الأخضر مؤدى، الأحمر متأخر، البرتقالي قريب، الأزرق موعد قادم.")

elif page == "🧾 سجل الأداءات":
    st.markdown('<div class="section-title">🧾 سجل الأداءات والوصولات</div>', unsafe_allow_html=True)
    payments = db["payments"]
    if not payments:
        st.info("لا توجد أداءات مسجلة بعد. جرّب تسجيل أداء تجريبي من مركز الأداءات.")
    else:
        df = pd.DataFrame(payments)
        df = df.rename(columns={"name":"العملية","amount":"المبلغ","date":"التاريخ","method":"طريقة الأداء","reference":"رقم المرجع"})
        st.dataframe(df[["العملية","المبلغ","التاريخ","طريقة الأداء","رقم المرجع"]], use_container_width=True, hide_index=True)
        for p in reversed(payments):
            with st.expander(f"وصل الأداء: {p['name']} — {money(p['amount'])}"):
                receipt_text = (
                    "MAW3ID | موعد - وصل أداء تجريبي\n"
                    f"الخدمة: {p['name']}\nالمبلغ: {money(p['amount'])}\n"
                    f"التاريخ: {p['date']}\nطريقة الأداء: {p['method']}\n"
                    f"المرجع: {p['reference']}\n"
                    "هذا وصل تجريبي وليس إثباتاً لأداء مالي حقيقي."
                )
                st.text(receipt_text)
                st.download_button("⬇️ تحميل الوصل TXT", data=receipt_text.encode("utf-8"),
                                   file_name=f"receipt_{p['reference']}.txt", mime="text/plain",
                                   key=f"download_{p['id']}")

elif page == "📊 المصاريف":
    st.markdown('<div class="section-title">📊 تحليل المصاريف والميزانية</div>', unsafe_allow_html=True)
    paid_total = sum(float(p["amount"]) for p in db["payments"])
    unpaid_total = sum(float(x["amount"]) for x in items if x["status"]=="غير مؤداة")
    x1,x2,x3 = st.columns(3)
    with x1: metric_card("الأداءات المسجلة",money(paid_total))
    with x2: metric_card("الالتزامات المفتوحة",money(unpaid_total))
    with x3: metric_card("عدد العمليات",str(len(db["payments"])))
    if items:
        df = pd.DataFrame(items)
        by_cat = df.groupby("category",as_index=False)["amount"].sum().set_index("category")
        st.subheader("المبالغ حسب الفئة")
        st.bar_chart(by_cat)
        st.subheader("تفاصيل الالتزامات")
        view = df[["name","category","amount","due","status"]].copy()
        view.columns = ["الاسم","الفئة","المبلغ (درهم)","تاريخ الاستحقاق","الحالة"]
        st.dataframe(view,use_container_width=True,hide_index=True)
    st.caption("الأرقام توضيحية وتعتمد على البيانات التي أدخلتها في هذا النموذج.")

elif page == "⭐ Premium":
    st.markdown('<div class="section-title">⭐ اكتشف MAW3ID Premium</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <h1>تحكم أفضل في التزاماتك</h1>
      <p>خدمات إضافية للعائلات والأشخاص الذين يريدون إدارة مالية أكثر ذكاءً.</p>
    </div>
    """,unsafe_allow_html=True)
    free,pro = st.columns(2)
    with free:
        st.markdown("### 🆓 النسخة المجانية")
        st.markdown("- إضافة الفواتير والمواعيد\n- تذكيرات أساسية\n- سجل الأداءات\n- تتبع المصاريف")
    with pro:
        st.markdown("### 💎 النسخة المميزة")
        st.markdown("- حساب عائلي مشترك\n- عدد أكبر من الالتزامات\n- قراءة الفواتير بالكاميرا OCR\n- تحليل ذكي للاشتراكات\n- تقارير متقدمة\n- تذكيرات مخصصة")
        st.success("مزايا مقترحة — غير مفعلة تجارياً في النموذج.")
    st.button("تجربة عرض Premium", disabled=True, help="زر توضيحي، لا توجد عملية اشتراك حقيقية.")

elif page == "👤 حسابي":
    st.markdown('<div class="section-title">👤 الحساب والإعدادات</div>', unsafe_allow_html=True)
    p = db["profile"]
    with st.form("profile_form"):
        name = st.text_input("الاسم الكامل",value=p.get("name",""))
        email = st.text_input("البريد الإلكتروني",value=p.get("email",""))
        phone = st.text_input("رقم الهاتف",value=p.get("phone",""))
        language = st.selectbox("اللغة",["العربية","Français","English"],index=["العربية","Français","English"].index(p.get("language","العربية")))
        save_profile = st.form_submit_button("حفظ المعلومات",type="primary")
        if save_profile:
            p.update({"name":name,"email":email,"phone":phone,"language":language}); persist()
            st.success("تم حفظ معلومات الحساب.")
    st.markdown("---")
    st.subheader("الخصوصية والأمان")
    st.info("في النسخة التجارية يجب تشفير البيانات الحساسة، وإضافة تسجيل دخول آمن، وسياسة خصوصية وشروط استخدام واضحة.")
    st.subheader("إدارة البيانات")
    export = json.dumps(db,ensure_ascii=False,indent=2)
    st.download_button("⬇️ تصدير نسخة من بياناتي",data=export.encode("utf-8"),
                       file_name="maw3id_backup.json",mime="application/json")
    st.caption("يتم حفظ بيانات النموذج محلياً في ملف maw3id_data.json بجانب التطبيق.")

elif page == "ℹ️ عن المشروع":
    st.markdown('<div class="section-title">ℹ️ تقديم مشروع MAW3ID</div>', unsafe_allow_html=True)
    st.markdown("""
    ### الفكرة
    MAW3ID تطبيق ذكي يساعد الأفراد والعائلات على تنظيم مواعيد الفواتير والضرائب والاشتراكات والالتزامات الشخصية في مكان واحد.

    ### المشكلة
    نسيان تواريخ الأداء والتجديد قد يؤدي إلى التأخر والغرامات أو استمرار دفع اشتراكات لم يعد المستخدم يحتاج إليها.

    ### الحل
    يجمع التطبيق الالتزامات في لوحة واحدة، ويرتبها حسب التاريخ، ويعرض تنبيهات قبل الموعد، ويساعد المستخدم على تتبع الأداءات والمصاريف.

    ### الفئات المستهدفة
    الأفراد، العائلات، الموظفون، الطلبة، التجار وأصحاب المقاولات الصغيرة.

    ### نموذج العمل المقترح
    نسخة مجانية بخصائص أساسية، ونسخة Premium بخصائص عائلية وتحليل متقدم وقراءة الفواتير آلياً.

    ### الرؤية المستقبلية
    الربط مع مزودي الأداء المرخصين، إشعارات الهاتف، استخراج بيانات الفواتير بالذكاء الاصطناعي، وحسابات عائلية مشتركة.
    """)
    st.markdown("---")
    st.subheader("سيناريو العرض أمام اللجنة")
    st.markdown("""
    1. أضف فاتورة جديدة وحدد المبلغ وتاريخ الاستحقاق.
    2. ارجع إلى الرئيسية ولاحظ ظهور الالتزام.
    3. افتح مركز الإشعارات لعرض التنبيهات.
    4. انتقل إلى الأداءات وسجل أداءً تجريبياً.
    5. افتح سجل الأداءات واعرض الوصل.
    6. افتح المصاريف لعرض أثر العملية على الإحصائيات.
    """)
    st.success("الشعار: لا تنشغل بتذكّر مواعيدك، تطبيقنا يتكفل بتذكيرك بها.")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#8090a5;font-size:12px'>"
    "MAW3ID – موعد | نموذج أولي للعرض والتجربة | جميع الأداءات تجريبية"
    "</div>", unsafe_allow_html=True
)
