import streamlit as st
import json
import os
import streamlit.components.v1 as components
import requests

# Dán đường link URL bạn vừa sao chép vào giữa 2 dấu ngoặc kép dưới đây:
GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzhoxFdi6idF6RZOM65xUqd8hBhDxRRO1Hd_58ZlGocPY_s1Zb7wg1q_da_ARoNJGxgPw/exec
"

def send_data_to_gsheet(action_type, student_name, student_class, score=None, correct_ratio="", note=""):
    """Gửi dữ liệu ngầm lên Google Sheet, không làm treo ứng dụng nếu mạng chậm"""
    try:
        payload = {
            "action_type": action_type,
            "student_name": student_name,
            "student_class": student_class,
            "score": score,
            "correct_ratio": correct_ratio,
            "note": note
        }
        requests.post(GOOGLE_SHEET_WEBAPP_URL, json=payload, timeout=5)
    except Exception:
        pass
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

# 2. Giao diện phong cách học đường (chú ý đúng 3 dấu ngoặc kép """ ở đầu và cuối)
# ================= GIAO DIỆN MỚI: COBALT BLUE HIỆN ĐẠI & ĐỀ MỤC NỔI BẬT =================
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
    col_hs1, col_hs2 = st.columns(2)
    with col_hs1:
        hs_ten = st.text_input("Họ và tên học sinh:", key="tab3_hs_ten", placeholder="Ví dụ: Nguyễn Văn A")
    with col_hs2:
        hs_lop = st.text_input("Lớp:", key="tab3_hs_lop", placeholder="Ví dụ: 11A1")
    c1, c2 = st.columns(2)
    with c1:
        topic = st.selectbox(
            "Chọn chủ đề kiến thức:",
            [
                "1. Giá trị lượng giác của góc lượng giác & Công thức lượng giác",
                "2. Hàm số lượng giác (Tập xác định, tính chẵn lẻ, chu kỳ, đồ thị)",
                "3. Phương trình lượng giác cơ bản & Điều kiện nghiệm",
                "4. Ứng dụng thực tế của hàm số và phương trình lượng giác"
            ]
        )
    with c2:
        level = st.selectbox("Mức độ tư duy:", ["Nhận biết", "Thông hiểu", "Vận dụng"])

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
            st.session_state["submitted"] = True
            st.session_state["user_choice"] = choice
            if hs_ten and hs_lop:
                send_data_to_gsheet(
                    action_type="Luyện tập AI (Tab 3)",
                    student_name=hs_ten,
                    student_class=hs_lop,
                    note=f"Chủ đề: {topic} | Mức độ: {level}"
        )
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
    st.subheader("Kiểm tra đánh giá năng lực theo cấu trúc đề thi mới (GDPT 2018)")
    st.write("Đề thi kết hợp **Trắc nghiệm nhiều lựa chọn** và **Câu hỏi trả lời ngắn**")

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
        - **20% Câu hỏi trả lời ngắn (Điền số):** Đo lường năng lực Vận dụng & Vận dụng cao (bài toán thực tế, tìm số nghiệm, GTLN/GTNN).
        """)

    # Đọc dữ liệu kho 82 câu an toàn
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

    # Nút bấm tạo đề kiểm tra
    if st.button("🚀 Khởi tạo đề kiểm tra mới (Có câu hỏi trả lời ngắn)"):
        if not client:
            st.error("Chưa cấu hình API Key trong mục Secrets.")
        else:
            # Thiết lập tỉ lệ đúng theo yêu cầu:
            if "10 câu" in loai_de:
                tong_cau = 10
                so_mcq = 8
                so_sa = 2
            else:
                tong_cau = 20
                so_mcq = 16
                so_sa = 4

            # Bốc ngẫu nhiên câu mẫu từ kho để định hướng AI
            mau_context = ""
            if danh_sach_tat_ca_cau:
                import random
                cac_cau_chon = random.sample(danh_sach_tat_ca_cau, min(3, len(danh_sach_tat_ca_cau)))
                mau_context = "\n---\n".join(cac_cau_chon)

            with st.spinner(f"⚡ Đang khởi tạo đề kiểm tra {tong_cau} câu ({so_mcq} trắc nghiệm + {so_sa} trả lời ngắn)..."):
                prompt_matrix = f"""
                Bạn là Trưởng ban Khảo thí môn Toán THPT Việt Nam (Chương trình GDPT 2018).
                Dưới đây là một số câu mẫu từ ngân hàng đề kiểm tra thực tế:
                ---
                {mau_context}
                ---

                Nhiệm vụ:
                Hãy tạo 1 đề kiểm tra Chương 1 Toán 11 gồm ĐÚNG {tong_cau} CÂU:
                - {so_mcq} câu đầu tiên: dạng TRẮC NGHIỆM 4 LỰA CHỌN (type: "mcq"), mức độ Nhận biết, Thông hiểu.
                - {so_sa} câu tiếp theo: dạng TRẢ LỜI NGẮN (type: "short_answer"), mức độ Vận dụng, Vận dụng cao (bài toán ứng dụng thực tế hoặc tìm số nghiệm, giá trị lớn nhất/nhỏ nhất). Đáp án đúng bắt buộc là MỘT CON SỐ CỤ THỂ (ví dụ: "28.3", "4", "-1", "12").
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

                # Dự phòng nếu máy chủ mạng bận đột xuất
                if not exam_success:
                    st.info("💡 Đường truyền đang bận, hệ thống kích hoạt bộ đề chuẩn 10 câu (8 trắc nghiệm + 2 trả lời ngắn) có sẵn:")
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

    # ================= GIAO DIỆN LÀM BÀI =================
    if "exam_data" in st.session_state and st.session_state["exam_data"]:
        exam_list = st.session_state["exam_data"]
        st.markdown("---")
        st.markdown(f"### 📋 BÀI KIỂM TRA ĐÁNH GIÁ NĂNG LỰC ({len(exam_list)} CÂU)")

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

        # ================= CHẤM ĐIỂM & BÁO CÁO PHÂN TÍCH =================
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
                st.success("🌟 **Xuất sắc!** Em làm chủ rất tốt cả phần trắc nghiệm phương án lẫn giải toán trả lời ngắn.")
            elif diem >= 6.5:
                st.info("👍 **Khá tốt!** Hãy rèn thêm các bài toán ứng dụng thực tế và tính toán cẩn thận hơn.")
            else:
                st.warning("⚠️ **Cần củng cố:** Em nên mở lại **Tab 1 & Tab 2** để xem lại lý thuyết và làm lại bài nhé!")

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
