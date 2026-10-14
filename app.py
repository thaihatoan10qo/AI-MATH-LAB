import streamlit as st
import json
import os
import streamlit.components.v1 as components
import requests

# Dán đường link URL bạn vừa sao chép vào giữa 2 dấu ngoặc kép dưới đây:
GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwdEHCrjYoQfFeKPXXf8rp-Xvcgj3_q7hey4QZC5_W8LDi7b__MmzWSL0zC_-0892DdyQ/exec"

def send_data_to_gsheet(action_type, student_name, student_class, score=None, correct_ratio="", note=""):
    """Gửi dữ liệu lên Google Sheet qua Apps Script Web App"""
    try:
        payload = {
            "action_type": action_type,
            "student_name": student_name,
            "student_class": student_class,
            "score": str(score) if score is not None else "",
            "correct_ratio": correct_ratio,
            "note": note
        }
        res = requests.post(
            GOOGLE_SHEET_WEBAPP_URL, 
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
            allow_redirects=True
        )
        return res.status_code in [200, 302]
    except Exception as e:
        print(f"Lỗi gửi dữ liệu Google Sheet: {e}")
        return False
def format_latex(text):
    if not text:
        return ""
    text_str = str(text).strip()
    # Nếu có ký hiệu latex mà chưa bọc trong $...$ thì tự động thêm dấu $
    if "\\" in text_str and not text_str.startswith("$") and not text_str.endswith("$"):
        return f"${text_str}$"
    return text_str
from google import genai
from google.genai import types

# 1. Cấu hình trang (bắt buộc phải có đủ dấu đóng ngoặc tròn ')')
st.set_page_config(
    page_title="Ôn Tập & Luyện Thi Toán 11 - Chương 1",
    page_icon="📐",
    layout="wide"
)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "student_name" not in st.session_state:
    st.session_state["student_name"] = ""
if "student_class" not in st.session_state:
    st.session_state["student_class"] = ""

# 2. Giao diện phong cách học đường (chú ý đúng 3 dấu ngoặc kép """ ở đầu và cuối)
# ================= KHAI BÁO THÔNG TIN HỌC SINH (CỔNG ĐĂNG NHẬP) =================
# ================= CỔNG ĐỊNH DANH & GIỚI THIỆU SẢN PHẨM =================
if not st.session_state.get("logged_in", False):
    import base64
    import os

    # 1. Hàm đọc file ảnh nền cục bộ sang base64
    def get_base64_bg(image_file):
        if os.path.exists(image_file):
            with open(image_file, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None

    # Tên file ảnh nền bạn đã tải lên GitHub (ví dụ: background.png)
    bg_base64 = get_base64_bg("background.png")

    if bg_base64:
        bg_style = f"""
            background: linear-gradient(rgba(240, 249, 255, 0.45), rgba(224, 242, 254, 0.55)), 
                        url("data:image/png;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        """
    else:
        bg_style = "background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);"

    # 2. Tinh chỉnh CSS kính mờ & độ tương phản cho văn bản
    st.markdown(
        f"""
        <style>
        .stApp {{
            {bg_style}
        }}
        /* Tùy chỉnh khối kính mờ */
        .glass-card {{
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.9);
            box-shadow: 0 8px 32px rgba(15, 23, 42, 0.12);
        }}
        /* Làm nổi bật nhãn và ô nhập liệu */
        .stTextInput label {{
            font-weight: 700 !important;
            color: #0f172a !important;
            font-size: 14px !important;
        }}
        .stTextInput input {{
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }}
        .stTextInput input:focus {{
            border-color: #0284c7 !important;
            box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.2) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # 3. BANNER TIÊU ĐỀ CHÍNH
    st.markdown(
        """
        <div class="glass-card" style="padding: 24px 20px; text-align: center; margin-bottom: 24px; border-top: 4px solid #0284c7;">
            <div style="display: inline-block; background: #e0f2fe; color: #0369a1; font-size: 13px; font-weight: 700; padding: 4px 16px; border-radius: 20px; margin-bottom: 10px; border: 1px solid #bae6fd;">
                ✨ HỌC TOÁN CÙNG CÔ HÀ • CHƯƠNG TRÌNH GDPT 2018
            </div>
            <h1 style="margin: 0 0 8px 0; font-size: 26px; font-weight: 800; color: #0f2b48; line-height: 1.3;">
                📐 HỆ THỐNG HỌC TẬP TƯƠNG TÁC & KHẢO THÍ TÍCH HỢP TRÍ TUỆ NHÂN TẠO
            </h1>
            <p style="margin: 0; font-size: 15px; color: #334155; font-weight: 600;">
                TOÁN 11 - Chương 1: Hàm số lượng giác và Phương trình lượng giác
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. BỐ CỤC 2 CỘT: TÍNH NĂNG & ĐĂNG NHẬP
    col_intro, col_login = st.columns([1.35, 1], gap="large")

    with col_intro:
        st.markdown(
            """
            <div class="glass-card" style="padding: 20px 22px;">
                <h3 style="margin-top: 0; color: #0f172a; font-size: 18px; font-weight: 800;">🌟 Tính năng nổi bật của ứng dụng</h3>
                <p style="font-size: 13px; color: #475569; margin-bottom: 16px;">
                    Nền tảng tích hợp công nghệ hỗ trợ học sinh hiểu rõ bản chất kiến thức toán học và cá nhân hóa lộ trình học tập:
                </p>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 14px; border-radius: 10px; border-left: 4px solid #0284c7; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-weight: 700; color: #0284c7; font-size: 14px;">🌀 MÔ PHỎNG TRỰC QUAN</div>
                        <div style="font-size: 13px; color: #334155; margin-top: 3px; line-height: 1.4;">
                            Trực quan hóa khái niệm giá trị lượng giác, đồ thị hàm số lượng giác, nghiệm của phương trình lượng giác cơ bản.
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 14px; border-radius: 10px; border-left: 4px solid #10b981; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-weight: 700; color: #059669; font-size: 14px;">📚 SƠ ĐỒ HÓA LÝ THUYẾT</div>
                        <div style="font-size: 13px; color: #334155; margin-top: 3px; line-height: 1.4;">
                            Hệ thống đầy đủ lý thuyết, công thức cốt lõi theo từng bài học chuẩn GDPT 2018.
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 14px; border-radius: 10px; border-left: 4px solid #f59e0b; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-weight: 700; color: #d97706; font-size: 14px;">🤖 GIA SƯ TRÍ TUỆ NHÂN TẠO (AI)</div>
                        <div style="font-size: 13px; color: #334155; margin-top: 3px; line-height: 1.4;">
                            Tự động sinh câu hỏi theo 4 mức độ năng lực, đối thoại giải thích bẫy sai lầm và luyện ngay câu hỏi dạng tương tự.
                        </div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 14px; border-radius: 10px; border-left: 4px solid #6366f1; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                        <div style="font-weight: 700; color: #4f46e5; font-size: 14px;">📊 KHẢO THÍ TỰ ĐỘNG & GỬI KẾT QUẢ ĐẾN GIÁO VIÊN</div>
                        <div style="font-size: 13px; color: #334155; margin-top: 3px; line-height: 1.4;">
                            Tạo đề kiểm tra ma trận chuẩn, tự động chấm điểm và đồng bộ tức thì tiến trình học tập về bảng quản lý của giáo viên.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_login:
        st.markdown(
            """
            <div class="glass-card" style="padding: 20px 22px; margin-bottom: 12px;">
                <h3 style="margin-top: 0; color: #0f172a; font-size: 18px; font-weight: 800;">📝 Khai báo học sinh</h3>
                <p style="font-size: 13px; color: #475569; margin-bottom: 0;">
                    Em vui lòng nhập thông tin trước khi bắt đầu bài học:
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            in_name = st.text_input("Họ và tên học sinh (*):", placeholder="Ví dụ: Nguyễn Văn An")
            in_class = st.text_input("Lớp học (*):", placeholder="Ví dụ: 11A1")
            
                      
            btn_login = st.form_submit_button("🚀 Bắt đầu học tập ngay", use_container_width=True, type="primary")

            if btn_login:
                if not in_name.strip() or not in_class.strip():
                    st.error("⚠️ Em vui lòng nhập đầy đủ cả Họ tên và Lớp nhé!")
                else:
                    st.session_state["student_name"] = in_name.strip()
                    st.session_state["student_class"] = in_class.strip()
                    st.session_state["logged_in"] = True
                    st.rerun()

    st.stop()
# ================= HẾT KHỐI ĐĂNG NHẬP =================
# ================= HẾT KHỐI ĐĂNG NHẬP =================
 # Dừng tại đây, không cho chạy tới dòng tạo tabs bên dưới

# KHI ĐÃ ĐĂNG NHẬP: HIỂN THỊ THANH THÔNG TIN VÀ NÚT ĐỔI TÊN
col_usr1, col_usr2 = st.columns([4, 1])
with col_usr1:
    st.success(f"👤 Học sinh: **{st.session_state['student_name']}** | Lớp: **{st.session_state['student_class']}**")
with col_usr2:
    if st.button("🚪 Đổi thông tin"):
        st.session_state["logged_in"] = False
        st.session_state["student_name"] = ""
        st.session_state["student_class"] = ""
        st.session_state["practice_total"] = 0
        st.session_state["practice_correct"] = 0
        st.session_state["practice_wrong"] = 0
        st.rerun()
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
        color: #0F172A;
    }

    /* 1. Đề mục lớn h1, h2, h3, subheader hiển thị ĐẬM & NỔI */
    h1, h2, h3, .stSubheader {
        color: #0B2545 !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px;
    }
    
    h2, .stSubheader {
        border-left: 5px solid #2563EB;
        padding-left: 12px !important;
        margin-top: 18px !important;
        margin-bottom: 14px !important;
    }

    /* 2. Tiêu đề các ô chọn, câu hỏi, label đậm và nét */
    label, .stRadio label, .stSelectbox label, .stTextInput label {
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* 3. Banner mở đầu ứng dụng */
    .school-banner {
        background: linear-gradient(135deg, #134E5E 0%, #1E3C72 100%);
        border-bottom: 4px solid #00D2FC;
        color: #FFFFFF;
        padding: 24px 20px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px rgba(30, 60, 114, 0.15);
        text-align: center;
    }
    .school-banner h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 1.75rem;
        margin-bottom: 8px;
        border-left: none !important;
        padding-left: 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .school-banner p {
        color: #A5F3FC !important;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0px;
    }

    /* 4. Thanh Tabs nổi bật */
    /* ================= THANH TABS NỔI KHỐI RÕ NÉT ================= */
    /* 1. Khung bọc bên ngoài toàn bộ thanh Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background: #EDF2F7 !important; /* Nền xám xanh làm nổi các nút tab */
        padding: 8px !important;
        border-radius: 14px !important;
        border: 2px solid #CBD5E1 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    /* 2. Các Tab bình thường (chưa chọn): Thẻ trắng nổi, viền đậm, chữ đen rõ */
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        color: #1E293B !important; /* Chữ xám đen đậm, nhìn rất rõ */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.25s ease-in-out !important;
    }

    /* Đảm bảo chữ bên trong tab không bị mờ */
    .stTabs [data-baseweb="tab"] p, 
    .stTabs [data-baseweb="tab"] span {
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* 3. Hiệu ứng rê chuột qua tab */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E0E7FF !important;
        border-color: #3B82F6 !important;
        color: #1D4ED8 !important;
        transform: translateY(-2px) !important;
    }

    /* 4. TAB ĐANG ĐƯỢC CHỌN: Nổi bật với nền Xanh Coban Gradient, chữ trắng sáng */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%) !important;
        border: 2px solid #1D4ED8 !important;
        border-radius: 10px !important;
        box-shadow: 0 6px 14px rgba(37, 99, 235, 0.35) !important;
        transform: translateY(-2px) !important;
    }

    /* Ép màu chữ tab đang chọn sang màu trắng tinh */
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* 5. Ẩn vạch gạch chân đỏ mặc định của Streamlit */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    /* 5. Nút bấm tương tác */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700 !important;
        border: none;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: #FFFFFF !important;
        padding: 10px 22px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.28);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #172554 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.38);
    }

    /* 6. Thẻ câu hỏi và nội dung */
    .exam-card, .quiz-card {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 6px solid #2563EB;
        border-radius: 10px;
        padding: 18px 20px;
        margin: 16px 0;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
    }

    /* 7. Hộp thông báo và chỉ số kết quả */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-top: 4px solid #2563EB;
        border-radius: 10px;
        padding: 12px 18px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
    }
</style>

<div class="school-banner">
    <h1>HỆ THỐNG ÔN TẬP & KHẢO THÍ CÁ NHÂN HÓA CÙNG AI</h1>
    <p>TOÁN 11 | LỚP CÔ HÀ</p>
</div>
""", unsafe_allow_html=True)

st.caption("CHƯƠNG 1: HÀM SỐ LƯỢNG GIÁC VÀ PHƯƠNG TRÌNH LƯỢNG GIÁC")

# 2. Quản lý API Key an toàn
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Nhập Gemini API Key:", type="password")

client = genai.Client(api_key=api_key) if api_key else None



# 3. Tạo các phân hệ chức năng
tab_mophong, tab_lythuyet, tab_luyentap, tab_kiemtra = st.tabs([
    "🌀 1. MÔ PHỎNG TRỰC QUAN",
    "📖 2. TÓM TẮT LÝ THUYẾT",
    "✍️ 3. LUYỆN TẬP CÙNG GIA SƯ AI",
    "📝 4. KIỂM TRA THEO MA TRẬN"
])


# ================= TAB 1: MÔ PHỎNG TRỰC QUAN =================
with tab_mophong:
    st.subheader("Mô phỏng tương tác trực quan Chương 1")
    st.write("Học sinh chọn chuyên đề để thao tác với mô hình trực quan:")
    
    # Danh mục liên kết trực tiếp tới 3 file HTML bạn đã tải lên
    danh_sach_mo_phong = {
        "1. Giá trị lượng giác & Vòng tròn đơn vị": "GIÁ TRỊ LƯỢNG GIÁC.html",
        "2. Đồ thị & Tính chất Hàm số lượng giác": "HÀM SỐ LƯỢNG GIÁC.html",
        "3. Phương trình lượng giác cơ bản": "PT LƯỢNG GIÁC.html"
    }
    
    # Hộp lựa chọn chuyên đề
    lua_chon = st.selectbox("Chọn mô hình muốn tương tác:", list(danh_sach_mo_phong.keys()))
    file_html_can_chieu = danh_sach_mo_phong[lua_chon]
    
    # Đọc và hiển thị file HTML tương ứng
    if os.path.exists(file_html_can_chieu):
        with open(file_html_can_chieu, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=680, scrolling=True)
    else:
        st.warning(f"Chưa tìm thấy file '{file_html_can_chieu}' trên hệ thống.")


 # ================= TAB 2: TÓM TẮT LÝ THUYẾT =================
with tab_lythuyet:
    st.subheader("Hệ thống hóa kiến thức trọng tâm bằng Infographic")
    st.write("Học sinh chọn bài học để xem sơ đồ tóm tắt lý thuyết:")

    # Khai báo đúng tên file thực tế bạn đã tải lên GitHub
    danh_sach_anh = {
        "Bài 1: Giá trị lượng giác của góc lượng giác": "LY-THUYET-BAI-1.jpg",
        "Bài 2: Công thức lượng giác": "LY-THUYET-BAI-2.jpg",
        "Bài 3: Hàm số lượng giác": "LY-THUYET-BAI-3.jpg",
        "Bài 4: Phương trình lượng giác cơ bản": "LY-THUYET-BAI-4.jpg"
    }

    bai_chon = st.selectbox("Chọn bài học cần ôn tập:", list(danh_sach_anh.keys()))
    file_anh = danh_sach_anh[bai_chon]

    if os.path.exists(file_anh):
        try:
            from PIL import Image
            img = Image.open(file_anh)
            st.image(img, caption=bai_chon, use_container_width=True)
        except Exception as e:
            st.error(f"Không thể đọc file ảnh '{file_anh}'. Vui lòng kiểm tra lại định dạng file (lỗi: {e}).")
    else:
        st.warning(f"Chưa tìm thấy file '{file_anh}' trên hệ thống. Hãy kiểm tra lại tên file trên GitHub.")
# ================= TAB 3: LUYỆN TẬP THÍCH ỨNG & GIA SƯ AI TRỰC TIẾP =================
with tab_luyentap:
    st.subheader("Luyện tập thông minh & Gia sư AI đồng hành")
    st.write("Em hãy luyện tập các dạng bài trọng tâm. Sau khi nộp bài, em có thể đặt câu hỏi trực tiếp cho Gia sư AI về câu hỏi vừa làm:")
    c1, c2 = st.columns(2)
    with c1:
        topic = st.selectbox(
            "Chọn chủ đề kiến thức:",
            [
                "1. Giá trị lượng giác của góc lượng giác & Công thức lượng giác",
                "2. Hàm số lượng giác (Tập xác định, tính chẵn lẻ, chu kỳ, đồ thị)",
                "3. Phương trình lượng giác cơ bản & Điều kiện nghiệm",
                "4. Ứng dụng thực tế của hàm số và phương trình lượng giác"
            ],
            key="tab3_topic_select"
        )
    with c2:
        level = st.selectbox(
            "Mức độ tư duy:",
            ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"],
            key="tab3_level_select"
        )
 
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        btn_gen = st.button("🎲 AI tạo câu hỏi từ ngân hàng đề")
    with col_btn2:
        btn_clone = st.button("🔁 Tạo câu tương tự dạng vừa làm")

    # Đọc và bốc mẫu ngắn gọn từ file kho_de.txt
    danh_sach_tat_ca_cau = []
    mau_cau_hoi = ""
    if os.path.exists("kho_de.txt"):
        try:
            with open("kho_de.txt", "r", encoding="utf-8") as f:
                noi_dung = f.read()
                danh_sach_tat_ca_cau = [c.strip() for c in noi_dung.split("Câu ") if c.strip()]
                import random
                if danh_sach_tat_ca_cau:
                    so_luong = min(3, len(danh_sach_tat_ca_cau))
                    mau_cau_hoi = "Câu " + "\n\nCâu ".join(random.sample(danh_sach_tat_ca_cau, so_luong))
        except Exception:
            mau_cau_hoi = ""

    # Xử lý sinh câu hỏi
    if btn_gen or btn_clone:
        if not client:
            st.error("Chưa cấu hình API Key trong mục Secrets của Streamlit.")
        elif btn_clone and "last_q" not in st.session_state:
            st.warning("Em cần tạo và làm thử 1 câu trước khi chọn tạo câu tương tự!")
        else:
            with st.spinner("AI đang thiết kế bài tập..."):
                # Reset lịch sử chat khi đổi sang câu hỏi mới
                st.session_state["chat_history"] = []

                gem_instructions = """
                Bạn là Trợ lý Chuyên gia Khảo thí Toán 11 THPT (GDPT 2018).
                Nhiệm vụ:
                1. Dựa vào câu hỏi mẫu/câu hỏi gốc để tạo câu hỏi trắc nghiệm tương đương.
                2. Xây dựng các phương án gây nhiễu đánh trúng lỗi sai kinh điển: quên điều kiện tan/cot, nhầm dấu công thức cộng, nhầm chu kỳ kpi/k2pi.
                3. Bắt buộc viết công thức toán bằng ký hiệu LaTeX chuẩn trong cặp $...$ hoặc $$...$$.
                4. Explanation (lời giải) trình bày chi tiết và chỉ rõ các bẫy sai lầm.
                5. Luôn trả về đúng định dạng JSON thuần.
                """

                if btn_clone:
                    prompt = f"""
                    Câu hỏi gốc học sinh vừa làm:
                    "{st.session_state['last_q']}"

                    Hãy tạo 1 câu hỏi MỚI CÙNG DẠNG (thay đổi số liệu/hàm số, giữ nguyên mô hình tư duy).
                    Trả về đúng định dạng JSON:
                    {{
                      "question": "Nội dung câu hỏi (chứa LaTeX)...",
                      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                      "correct_answer": "A",
                      "explanation": "Lời giải chi tiết từng bước và lưu ý bẫy sai lầm..."
                    }}
                    """
                else:
                    prompt = f"""
                    Dưới đây là một số câu trích mẫu từ đề kiểm tra:
                    ---
                    {mau_cau_hoi}
                    ---
                    Yêu cầu:
                    Tạo 1 câu hỏi trắc nghiệm thuộc chủ đề: "{topic}", mức độ: "{level}".
                    Bám sát văn phong câu mẫu.
                    Trả về đúng định dạng JSON:
                    {{
                      "question": "Nội dung câu hỏi (chứa LaTeX)...",
                      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                      "correct_answer": "A",
                      "explanation": "Lời giải chi tiết từng bước và lưu ý bẫy sai lầm..."
                    }}
                    """

                success = False
                cac_model = ['gemini-3.1-flash-lite', 'gemini-3.8-flash']
                for ten_model in cac_model:
                    try:
                        response = client.models.generate_content(
                            model=ten_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=gem_instructions,
                                response_mime_type="application/json",
                                temperature=0.7
                            )
                        )
                        st.session_state["quiz"] = json.loads(response.text)
                        st.session_state["submitted"] = False
                        st.session_state["last_q"] = st.session_state["quiz"]["question"]
                        success = True
                        break
                    except Exception:
                        continue

                if not success:
                    import random
                    cau_du_phong = "Tìm tập xác định của hàm số $y = \\tan\\left(x - \\frac{\\pi}{3}\\right)$."
                    if danh_sach_tat_ca_cau:
                        cau_ngau_nhien = random.choice(danh_sach_tat_ca_cau)
                        cau_du_phong = "Câu " + cau_ngau_nhien

                    st.info("💡 Đường truyền AI đang bận, hệ thống trích xuất câu chuẩn từ ngân hàng để em luyện tập ngay:")
                    st.session_state["quiz"] = {
                        "question": cau_du_phong,
                        "options": {
                            "A": "$D = \\mathbb{R} \\setminus \\left\\{\\frac{5\\pi}{6} + k\\pi, k \\in \\mathbb{Z}\\right\\}$",
                            "B": "$D = \\mathbb{R} \\setminus \\left\\{\\frac{\\pi}{3} + k\\pi, k \\in \\mathbb{Z}\\right\\}$",
                            "C": "$D = \\mathbb{R} \\setminus \\left\\{\\frac{5\\pi}{6} + k2\\pi, k \\in \\mathbb{Z}\\right\\}$",
                            "D": "$D = \\mathbb{R} \\setminus \\left\\{\\frac{\\pi}{2} + k\\pi, k \\in \\mathbb{Z}\\right\\}$"
                        },
                        "correct_answer": "A",
                        "explanation": "Hàm số xác định khi $x - \\frac{\\pi}{3} \\neq \\frac{\\pi}{2} + k\\pi \\Leftrightarrow x \\neq \\frac{5\\pi}{6} + k\\pi$ ($k \\in \\mathbb{Z}$)."
                    }
                    st.session_state["submitted"] = False
                    st.session_state["last_q"] = st.session_state["quiz"]["question"]

    # Hiển thị câu hỏi làm bài
    if "quiz" in st.session_state:
        q = st.session_state["quiz"]
        st.markdown("---")
        st.markdown(f"**Câu hỏi:** {q['question']}")
# Hàm hiển thị phương án trắc nghiệm chuẩn LaTeX không bị lỗi dấu gạch chéo
        def hien_thi_lua_chon(k):
            val = str(q['options'][k]).strip()
            if not val.startswith('$'):
                val = f"${val}$"
            return f"**{k}.** {val}"

        choice = st.radio(
            "Chọn đáp án đúng:",
            options=["A", "B", "C", "D"],
            format_func=hien_thi_lua_chon
        )
        if st.button("Nộp bài & Kiểm tra đáp án"):
            if not st.session_state.get("submitted", False):
                st.session_state["submitted"] = True
                st.session_state["user_choice"] = choice

                # 1. Tăng số câu đã làm
                st.session_state["practice_total"] = st.session_state.get("practice_total", 0) + 1
                tong_da_luyen = st.session_state["practice_total"]

                # 2. Đánh giá đúng / sai
                is_correct = (choice == q["correct_answer"])
                if is_correct:
                    st.session_state["practice_correct"] = st.session_state.get("practice_correct", 0) + 1
                else:
                    st.session_state["practice_wrong"] = st.session_state.get("practice_wrong", 0) + 1

                so_dung = st.session_state["practice_correct"]
                so_sai = st.session_state["practice_wrong"]
                chu_de = st.session_state.get("cur_question_topic", topic)

                # 3. Gửi sang Google Sheet
                da_gui = send_data_to_gsheet(
                    action_type=f"Luyện tập ( câu {tong_da_luyen} )",
                    student_name=st.session_state.get("student_name", "-"),
                    student_class=st.session_state.get("student_class", "-"),
                    score=f"Đúng: {so_dung} câu | Sai: {so_sai} câu",
                    note=f"Câu {tong_da_luyen}: {'Đúng' if is_correct else 'Sai'} (Chủ đề: {chu_de})"
                )
                if da_gui:
                    st.toast(f"✅ Đã lưu kết quả câu thứ {tong_da_luyen} vào Google Sheet!", icon="📊")
       
        # Khi học sinh nộp bài
        if st.session_state.get("submitted", False):
            user_c = st.session_state.get("user_choice", choice)
            if user_c == q["correct_answer"]:
                st.success("🎉 Chính xác! Em đã làm chủ phương pháp giải bài toán này.")
            else:
                st.error(f"❌ Chưa chính xác. Đáp án đúng là: **{q['correct_answer']}**")
                st.info("💡 Em đọc kỹ lời giải bên dưới rồi có thể trao đổi với Gia sư AI ngay phần bên dưới nhé!")

            with st.expander("📖 Xem lời giải chi tiết và phân tích bẫy sai lầm", expanded=True):
                st.markdown(q["explanation"])

            # ================= PHẦN GIA SƯ AI TRÒ CHUYỆN VỀ CÂU HỎI VỪA LÀM =================
            st.markdown("---")
            st.subheader("💬 Gia sư AI: Thắc mắc về câu hỏi này?")
            st.caption("Em chưa hiểu bước biến đổi nào, tại sao công thức lại như vậy hay muốn gợi ý cách nhớ? Hãy nhập câu hỏi bên dưới nhé!")

            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            # Hiển thị các tin nhắn đã trao đổi
            for msg in st.session_state["chat_history"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Khung nhập câu hỏi cho học sinh
            user_question = st.chat_input("Nhập câu hỏi của em về bài toán trên...")
            if user_question:
                # Lưu câu hỏi của học sinh
                st.session_state["chat_history"].append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.markdown(user_question)

                # Chuẩn bị ngữ cảnh cho Gia sư AI: Nắm rõ đề bài, đáp án học sinh chọn và lời giải
                context_prompt = f"""
                Bạn là Gia sư dạy Toán 11 THPT tận tâm, ân cần và sư phạm.
                Học sinh vừa làm câu hỏi sau:
                - Đề bài: {q['question']}
                - Các đáp án: {q['options']}
                - Đáp án đúng: {q['correct_answer']}
                - Đáp án học sinh đã chọn: {user_c}
                - Lời giải chi tiết: {q['explanation']}

                Học sinh đang thắc mắc: "{user_question}"

                Yêu cầu sư phạm:
                1. Trả lời trực tiếp vào thắc mắc của học sinh, giải thích cặn kẽ từng bước, không phán xét.
                2. Dùng lời văn động viên, gần gũi như thầy/cô hướng dẫn học sinh.
                3. Các công thức toán bắt buộc viết dạng LaTeX đặt trong $...$ hoặc $$...$$.
                4. Nhắc lại mẹo nhớ hoặc lưu ý quan trọng để học sinh không lặp lại lỗi sai.
                """

                with st.chat_message("assistant"):
                    with st.spinner("Thầy/Cô AI đang xem xét câu hỏi của em..."):
                        tutor_reply = ""
                        for ten_model in ['gemini-3.1-flash-lite', 'gemini-3.8-flash']:
                            try:
                                resp = client.models.generate_content(
                                    model=ten_model,
                                    contents=context_prompt
                                )
                                tutor_reply = resp.text
                                break
                            except Exception:
                                continue

                        if not tutor_reply:
                            tutor_reply = "Hiện hệ thống đang nghẽn mạng nhẹ. Em hãy kiểm tra lại kết nối và thử gửi lại câu hỏi nhé!"

                        st.markdown(tutor_reply)
                        st.session_state["chat_history"].append({"role": "assistant", "content": tutor_reply})
def format_latex(text):
    if not text:
        return ""
    text_str = str(text).strip()
    # Nếu chuỗi chứa ký tự latex (như \mathbb, \frac, \pi, \setminus...) mà chưa có dấu $ bao quanh
    if "\\" in text_str and not text_str.startswith("$") and not text_str.endswith("$"):
        return f"${text_str}$"
    return text_str
# ================= TAB 4: KIỂM TRA ĐÁNH GIÁ (TRẮC NGHIỆM + TRẢ LỜI NGẮN) =================
with tab_kiemtra:
    st.subheader("KIỂM TRA ĐÁNH GIÁ NĂNG LỰC")
    st.write("Đề thi kết hợp **Trắc nghiệm nhiều lựa chọn** và **Câu hỏi trả lời ngắn**")

   # 1. THÔNG TIN THÍ SINH (Tự động lấy từ màn hình đăng nhập)
    st.info(f"📝 Thí sinh: **{st.session_state.get('student_name', '')}** | Lớp: **{st.session_state.get('student_class', '')}**")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        loai_de = st.selectbox(
            "Chọn quy mô đề kiểm tra:",
            [
                "Đề tiêu chuẩn 10 câu (8 Trắc nghiệm A-B-C-D + 2 Trả lời ngắn)",
                "Đề tổng hợp 20 câu (16 Trắc nghiệm A-B-C-D + 4 Trả lời ngắn)"
            ]
        )
    with col_m2:
        st.info("""
        📋 **Cấu trúc phân bổ:**
        - **80% Trắc nghiệm 4 lựa chọn (A-B-C-D):** Đo lường kiến thức Nhận biết & Thông hiểu.
        - **20% Câu hỏi trả lời ngắn (Điền số):** Đo lường năng lực Vận dụng & Vận dụng cao.
        """)

    # Đọc dữ liệu kho câu hỏi
    danh_sach_tat_ca_cau = []
    ten_file_de = None
    for fname in ["kho_de.txt", "kho_de.txt.txt", "Kho_de.txt"]:
        if os.path.exists(fname):
            ten_file_de = fname
            break

    if ten_file_de:
        try:
            with open(ten_file_de, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
                import re
                cac_doan = re.split(r'(?i)câu\s+\d+[:\.]?', raw_text)
                danh_sach_tat_ca_cau = [d.strip() for d in cac_doan if len(d.strip()) > 30]
                if not danh_sach_tat_ca_cau:
                    danh_sach_tat_ca_cau = [d.strip() for d in raw_text.split("\n\n") if len(d.strip()) > 30]
        except Exception:
            pass

    # 2. NÚT KHỞI TẠO ĐỀ (BẮT BUỘC PHẢI ĐIỀN TÊN VÀ LỚP)
    if st.button("🚀 Bắt đầu làm bài kiểm tra"):
       
            if "10 câu" in loai_de:
                tong_cau = 10
                so_mcq = 8
                so_sa = 2
            else:
                tong_cau = 20
                so_mcq = 16
                so_sa = 4

            mau_context = ""
            if danh_sach_tat_ca_cau:
                import random
                cac_cau_chon = random.sample(danh_sach_tat_ca_cau, min(3, len(danh_sach_tat_ca_cau)))
                mau_context = "\n---\n".join(cac_cau_chon)

            with st.spinner(f"⚡ Đang khởi tạo đề kiểm tra {tong_cau} câu "):
                prompt_matrix = f"""
                Bạn là Trưởng ban Khảo thí môn Toán THPT Việt Nam (Chương trình GDPT 2018).
                Dưới đây là một số câu mẫu từ ngân hàng đề kiểm tra:
                ---
                {mau_context}
                ---

                Nhiệm vụ:
                Hãy tạo 1 đề kiểm tra Chương 1 Toán 11 gồm ĐÚNG {tong_cau} CÂU:
                - {so_mcq} câu đầu tiên: dạng TRẮC NGHIỆM 4 LỰA CHỌN (type: "mcq"), mức độ Nhận biết, Thông hiểu.
                - {so_sa} câu tiếp theo: dạng TRẢ LỜI NGẮN (type: "short_answer"), mức độ Vận dụng, Vận dụng cao. Đáp án đúng bắt buộc là MỘT CON SỐ CỤ THỂ (ví dụ: "28.3", "4", "-1", "12").
                - Công thức toán viết bằng LaTeX trong $...$.
                - Lời giải (explanation) ngắn gọn, rõ ràng.

                Trả về đúng định dạng JSON thuần là danh sách gồm {tong_cau} đối tượng:
                [
                  {{
                    "id": 1,
                    "type": "mcq",
                    "level": "Nhận biết",
                    "question": "Nội dung câu trắc nghiệm...",
                    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                    "correct_answer": "A",
                    "explanation": "Giải thích ngắn gọn..."
                  }},
                  {{
                    "id": {so_mcq + 1},
                    "type": "short_answer",
                    "level": "Vận dụng",
                    "question": "Nội dung câu hỏi trả lời ngắn...",
                    "options": null,
                    "correct_answer": "28.3",
                    "explanation": "Giải thích ngắn gọn các bước tính ra đáp số..."
                  }}
                ]
                """

                exam_success = False
                cac_model = ['gemini-3.1-flash-lite', 'gemini-3.8-flash']
                for ten_model in cac_model:
                    try:
                        resp = client.models.generate_content(
                            model=ten_model,
                            contents=prompt_matrix,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.7
                            )
                        )
                        st.session_state["exam_data"] = json.loads(resp.text)
                        st.session_state["exam_submitted"] = False
                        st.session_state["student_answers"] = {}
                        exam_success = True
                        break
                    except Exception:
                        continue

                # Dự phòng nếu mạng bận
                if not exam_success:
                    st.info("💡 Đường truyền đang bận, hệ thống kích hoạt bộ đề chuẩn 10 câu có sẵn:")
                    st.session_state["exam_data"] = [
                        {"id": 1, "type": "mcq", "level": "Nhận biết", "question": "Cho $0 < \\alpha < \\frac{\\pi}{2}$. Khẳng định nào sau đây đúng?", "options": {"A": "$\\sin \\alpha > 0$", "B": "$\\cos \\alpha < 0$", "C": "$\\tan \\alpha < 0$", "D": "$\\cot \\alpha < 0$"}, "correct_answer": "A", "explanation": "Góc phần tư thứ I thì sin, cos, tan, cot đều dương."},
                        {"id": 2, "type": "mcq", "level": "Nhận biết", "question": "Tập xác định của hàm số $y = \\tan x$ là:", "options": {"A": "$D = \\mathbb{R} \\setminus \\left\\{\\frac{\\pi}{2} + k\\pi, k \\in \\mathbb{Z}\\right\\}$", "B": "$D = \\mathbb{R} \\setminus \\{k\\pi, k \\in \\mathbb{Z}\\}$", "C": "$D = \\mathbb{R} \\setminus \\left\\{\\frac{\\pi}{4} + k\\pi, k \\in \\mathbb{Z}\\right\\}$", "D": "$D = \\mathbb{R}$"}, "correct_answer": "A", "explanation": "$\\cos x \\neq 0 \\Leftrightarrow x \\neq \\frac{\\pi}{2} + k\\pi$."},
                        {"id": 3, "type": "mcq", "level": "Nhận biết", "question": "Hàm số nào sau đây là hàm số chẵn?", "options": {"A": "$y = \\cos x$", "B": "$y = \\sin x$", "C": "$y = \\tan x$", "D": "$y = \\cot x$"}, "correct_answer": "A", "explanation": "Chỉ có $\\cos(-x) = \\cos x$ là hàm chẵn."},
                        {"id": 4, "type": "mcq", "level": "Thông hiểu", "question": "Nghiệm của phương trình $\\cos x = 1$ là:", "options": {"A": "$x = k2\\pi$ ($k \\in \\mathbb{Z}$)", "B": "$x = k\\pi$ ($k \\in \\mathbb{Z}$)", "C": "$x = \\frac{\\pi}{2} + k2\\pi$ ($k \\in \\mathbb{Z}$)", "D": "$x = \\pi + k2\\pi$ ($k \\in \\mathbb{Z}$)"}, "correct_answer": "A", "explanation": "$\\cos x = 1 \\Leftrightarrow x = k2\\pi$."},
                        {"id": 5, "type": "mcq", "level": "Thông hiểu", "question": "Tập giá trị của hàm số $y = 3\\sin 2x - 1$ là:", "options": {"A": "$[-4; 2]$", "B": "$[-3; 3]$", "C": "$[-2; 4]$", "D": "$[-1; 5]$"}, "correct_answer": "A", "explanation": "Vì $-1 \\le \\sin 2x \\le 1$ nên $-4 \\le 3\\sin 2x - 1 \\le 2$."},
                        {"id": 6, "type": "mcq", "level": "Thông hiểu", "question": "Chu kỳ tuần hoàn của hàm số $y = \\sin 2x$ là:", "options": {"A": "$\\pi$", "B": "$2\\pi$", "C": "$\\frac{\\pi}{2}$", "D": "$4\\pi$"}, "correct_answer": "A", "explanation": "$T = \\frac{2\\pi}{\vert{}a\vert{}} = \\frac{2\\pi}{2} = \\pi$."},
                        {"id": 7, "type": "mcq", "level": "Thông hiểu", "question": "Phương trình $\\tan x = \\sqrt{3}$ có họ nghiệm là:", "options": {"A": "$x = \\frac{\\pi}{3} + k\\pi$ ($k \\in \\mathbb{Z}$)", "B": "$x = \\frac{\\pi}{6} + k\\pi$ ($k \\in \\mathbb{Z}$)", "C": "$x = \\frac{\\pi}{3} + k2\\pi$ ($k \\in \\mathbb{Z}$)", "D": "$x = -\\frac{\\pi}{3} + k\\pi$ ($k \\in \\mathbb{Z}$)"}, "correct_answer": "A", "explanation": "$\\tan x = \\tan \\frac{\\pi}{3} \\Leftrightarrow x = \\frac{\\pi}{3} + k\\pi$."},
                        {"id": 8, "type": "mcq", "level": "Thông hiểu", "question": "Giá trị của $\\cos 75^\\circ$ là:", "options": {"A": "$\\frac{\\sqrt{6}-\\sqrt{2}}{4}$", "B": "$\\frac{\\sqrt{6}+\\sqrt{2}}{4}$", "C": "$\\frac{\\sqrt{2}-\\sqrt{6}}{4}$", "D": "$\\frac{1}{2}$"}, "correct_answer": "A", "explanation": "$\\cos(45^\\circ + 30^\\circ) = \\cos 45^\\circ\\cos 30^\\circ - \\sin 45^\\circ\\sin 30^\\circ = \\frac{\\sqrt{6}-\\sqrt{2}}{4}$."},
                        {"id": 9, "type": "short_answer", "level": "Vận dụng", "question": "Tìm số nghiệm của phương trình $\\sin x = 0$ trên đoạn $[0; 3\\pi]$.", "options": None, "correct_answer": "4", "explanation": "$\\sin x = 0 \\Leftrightarrow x = k\\pi$. Trên $[0; 3\\pi]$ có các nghiệm: $0, \\pi, 2\\pi, 3\\pi$ (tổng cộng 4 nghiệm)."},
                        {"id": 10, "type": "short_answer", "level": "Vận dụng cao", "question": "Mặt cắt một con kênh có dạng cung đồ thị $y = 4{,}8\\sin\\left(\\frac{x}{9}\\right)$ (với $x$ tính bằng mét). Tính bề rộng mặt kênh giữa hai bờ kề nhau khi mực nước ở mức $y = 0$ (làm tròn kết quả đến hàng phần mười).", "options": None, "correct_answer": "28.3", "explanation": "Khoảng cách giữa hai điểm kề nhau bằng nửa chu kỳ: $9\\pi \\approx 28{,}27 \\approx 28{,}3$ mét."}
                    ]
                    st.session_state["exam_submitted"] = False
                    st.session_state["student_answers"] = {}

    # 3. GIAO DIỆN LÀM BÀI VÀ NỘP BÀI
    if "exam_data" in st.session_state and st.session_state["exam_data"]:
        exam_list = st.session_state["exam_data"]
        ten_thi_sinh = st.session_state.get("cur_exam_student", "Thí sinh")
        lop_thi_sinh = st.session_state.get("cur_exam_class", "")
        
        st.markdown("---")
        st.markdown(f"### 📋 BÀI KIỂM TRA ĐÁNH GIÁ NĂNG LỰC: **{st.session_state.get('student_name', '')} - Lớp {st.session_state.get('student_class', '')}** ({len(exam_list)} câu)")

        with st.form("hybrid_exam_form"):
            user_exam_answers = {}
            for idx, item in enumerate(exam_list):
                q_type = item.get("type", "mcq")
                level_tag = item.get("level", "Thông hiểu")

                if q_type == "mcq":
                    st.markdown(f"**Câu {idx + 1}** `[Trắc nghiệm - {level_tag}]`: {item['question']}")
                    opts = item["options"]
                    user_exam_answers[idx] = st.radio(
                        f"Chọn đáp án câu {idx + 1}:",
                        options=["A", "B", "C", "D"],
                        format_func=lambda x, opt_dict=opts: f"{x}. {opt_dict[x]}",
                        key=f"hybrid_mcq_{idx}",
                        index=None
                    )
                else:
                    st.markdown(f"**Câu {idx + 1}** `[Trả lời ngắn - {level_tag}]`: {item['question']}")
                    user_exam_answers[idx] = st.text_input(
                        f"Nhập đáp số câu {idx + 1} (dạng số, ví dụ 28.3 hoặc 4):",
                        key=f"hybrid_sa_{idx}",
                        placeholder="Điền kết quả vào đây..."
                    )
                st.write("")

            btn_submit_exam = st.form_submit_button("🏁 Nộp Bài Kiểm Tra")
            if btn_submit_exam:
                st.session_state["exam_submitted"] = True
                st.session_state["student_answers"] = user_exam_answers

        # 4. CHẤM ĐIỂM VÀ TỰ ĐỘNG GỬI KẾT QUẢ VỀ GOOGLE SHEET
        if st.session_state.get("exam_submitted", False):
            ans = st.session_state.get("student_answers", {})
            dung = 0
            tong_so = len(exam_list)

            def is_same_number(s1, s2):
                if not s1 or not s2:
                    return False
                clean1 = str(s1).strip().replace(",", ".")
                clean2 = str(s2).strip().replace(",", ".")
                try:
                    return abs(float(clean1) - float(clean2)) < 0.05
                except ValueError:
                    return clean1.lower() == clean2.lower()

            for idx, item in enumerate(exam_list):
                q_type = item.get("type", "mcq")
                user_val = ans.get(idx)
                if q_type == "mcq":
                    if user_val == item["correct_answer"]:
                        dung += 1
                else:
                    if is_same_number(user_val, item["correct_answer"]):
                        dung += 1

            diem = round((dung / tong_so) * 10, 2)

            # Gửi kết quả sang Google Sheet (chỉ gửi 1 lần khi bấm nộp)
            # Gửi dữ liệu sang Google Sheet
            da_gui = send_data_to_gsheet(
                action_type="Kiểm tra (Tab 4)",
                student_name=st.session_state.get("student_name", "Ẩn danh"),
                student_class=st.session_state.get("student_class", "-"),
                score=f"{diem} điểm",
                note=f"Quy mô: {loai_de} (Đúng {dung}/{tong_so} câu)"
            )
            if da_gui:
                st.toast("🎉 Đã gửi kết quả bài thi về hệ thống!", icon="✅")
          
            st.markdown("---")
            st.markdown("## 🎯 BÁO CÁO KẾT QUẢ ĐÁNH GIÁ NĂNG LỰC")

            c_res1, c_res2, c_res3 = st.columns(3)
            with c_res1:
                st.metric("Điểm tổng kết", f"{diem} / 10")
            with c_res2:
                st.metric("Số câu đúng", f"{dung} / {tong_so}")
            with c_res3:
                ti_le = round((dung / tong_so) * 100, 1)
                st.metric("Tỉ lệ hoàn thành", f"{ti_le}%")

            if diem >= 8.0:
                st.success(f"🌟 **Xuất sắc!** Chúc mừng em **{ten_thi_sinh}** ({lop_thi_sinh}) đã hoàn thành xuất sắc bài kiểm tra!")
            elif diem >= 6.5:
                st.info(f"👍 **Khá tốt!** Em **{ten_thi_sinh}** hãy rèn thêm các bài toán vận dụng thực tế nhé.")
            else:
                st.warning(f"⚠️ **Cần cố gắng:** Em **{ten_thi_sinh}** nên ôn lại lý thuyết ở Tab 1 & Tab 2 rồi làm lại nhé!")

            with st.expander("📖 Xem bảng đối chiếu đáp án & Lời giải chi tiết", expanded=True):
                for idx, item in enumerate(exam_list):
                    q_type = item.get("type", "mcq")
                    user_val = ans.get(idx)
                    correct_val = item["correct_answer"]

                    if q_type == "mcq":
                        is_corr = (user_val == correct_val)
                    else:
                        is_corr = is_same_number(user_val, correct_val)

                    icon = "✅" if is_corr else "❌"
                    display_type = "Trắc nghiệm" if q_type == "mcq" else "Trả lời ngắn"

                    st.markdown(f"**Câu {idx + 1}** `[{display_type}]`: {icon} Em chọn/nhập: **{user_val if user_val else 'Chưa làm'}** | Đáp án đúng: **{correct_val}**")
                    st.caption(f"**Lời giải:** {item['explanation']}")
                    st.divider()
