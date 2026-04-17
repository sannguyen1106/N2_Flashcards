import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import base64

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Flashcard N2 Pro", layout="centered")

# --- GIAO DIỆN CSS (Tối ưu cho iPhone & Màu sắc giống bản PC) ---
st.markdown("""
    <style>
    .kanji-card {
        font-size: 60px !important;
        font-weight: bold;
        color: #1a237e;
        text-align: center;
        padding: 50px 10px;
        background-color: white;
        border-radius: 15px;
        border: 2px solid #d1d8e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        min-height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .back-card {
        font-size: 18px !important;
        color: #1b5e20;
        text-align: left;
        padding: 25px;
        background-color: #f7fff7;
        border-radius: 15px;
        border: 2px solid #27ae60;
        white-space: pre-wrap;
        line-height: 1.6;
        min-height: 250px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM PHÁT ÂM (Dùng cho Web/iPhone) ---
def speak(text):
    if text.strip():
        tts = gTTS(text=text, lang='ja')
        tts.save("temp.mp3")
        with open("temp.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
        os.remove("temp.mp3")

# --- TẢI DỮ LIỆU ---
@st.cache_data
def load_data():
    # Tên file phải khớp với file bạn upload lên GitHub
    file_name = "N2_Flashcards.xlsx" 
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        return df.to_dict('records')
    return []

data = load_data()

# --- KHỞI TẠO TRẠNG THÁI (Lưu vị trí học) ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'flipped' not in st.session_state:
    st.session_state.flipped = False

# --- XỬ LÝ LOGIC ---
def next_card():
    st.session_state.index = (st.session_state.index + 1) % len(data)
    st.session_state.flipped = False

def prev_card():
    st.session_state.index = (st.session_state.index - 1) % len(data)
    st.session_state.flipped = False

def flip():
    st.session_state.flipped = not st.session_state.flipped

# --- GIAO DIỆN CHÍNH ---
st.title("🇯🇵 Flashcard N2 Pro")

if data:
    current_card = data[st.session_state.index]

    # Hiển thị mặt thẻ
    if not st.session_state.flipped:
        st.markdown(f'<div class="kanji-card">{current_card["前"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="back-card">{current_card["後ろ"]}</div>', unsafe_allow_html=True)

    st.write("")

    # Cụm nút bấm chính (Dành cho iPhone)
    col_flip, col_audio = st.columns([2, 1])
    with col_flip:
        if st.button("🔄 LẬT MẶT THẺ", type="primary"):
            flip()
            st.rerun()
    with col_audio:
        if st.button("🔊 NGHE"):
            text_to_read = ""
            if not st.session_state.flipped:
                text_to_read = str(current_card.get('前', ''))
            else:
                text_back = str(current_card.get('後ろ', ''))
                # Logic tách chữ để đọc giống bản PC của bạn
                cach_doc = text_back.split("Cách đọc :")[1].split("\n")[0].strip() if "Cách đọc :" in text_back else ""
                vi_du = text_back.split("Ví dụ :")[1].strip().split("\n")[0].strip() if "Ví dụ :" in text_back else ""
                text_to_read = f"{cach_doc}. {vi_du}"
            speak(text_to_read)

    # Nút điều hướng
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("<< TRƯỚC"):
            prev_card()
            st.rerun()
    with col_next:
        if st.button("TIẾP THEO >>"):
            next_card()
            st.rerun()

    st.caption(f"Thẻ số: {st.session_state.index + 1} / {len(data)}")
else:
    st.error("Không tìm thấy file dữ liệu. Hãy kiểm tra lại tên file trên GitHub!")
