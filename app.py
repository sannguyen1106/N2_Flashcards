import streamlit as st
import pandas as pd
import os
from gtts import gTTS
import base64

# 1. Cấu hình tên tab trình duyệt
st.set_page_config(page_title="Flashcard", layout="centered")

# 2. CSS Giao diện & Ẩn biểu tượng móc xích
st.markdown("""
    <style>
    /* Ẩn móc xích ở tiêu đề */
    a.header-anchor { display: none !important; } 
    
    .kanji-card { font-size: 55px !important; font-weight: bold; color: #1a237e; text-align: center; padding: 40px 10px; background-color: white; border-radius: 15px; border: 2px solid #d1d8e0; min-height: 250px; display: flex; align-items: center; justify-content: center; }
    .back-card { font-size: 18px !important; color: #1b5e20; text-align: left; padding: 25px; background-color: #f7fff7; border-radius: 15px; border: 2px solid #27ae60; white-space: pre-wrap; line-height: 1.6; min-height: 250px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Hàm phát âm tiếng Nhật
def speak(text):
    if text.strip():
        try:
            tts = gTTS(text=text, lang='ja')
            tts.save("temp.mp3")
            with open("temp.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            os.remove("temp.mp3")
        except: pass

# Đọc file Excel
@st.cache_data
def load_data():
    file_name = "N2_Flashcards.xlsx"
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        return df.to_dict('records')
    return []

# Hàm lưu và đọc vị trí thẻ học
def load_last_index():
    try:
        with open("last_index.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_index(index):
    try:
        with open("last_index.txt", "w") as f:
            f.write(str(index))
    except:
        pass

# Khởi tạo dữ liệu
data = load_data()

# Nhớ vị trí khi mở lại App
if 'index' not in st.session_state: 
    st.session_state.index = load_last_index()
    if st.session_state.index >= len(data) and len(data) > 0:
        st.session_state.index = 0

if 'flipped' not in st.session_state: st.session_state.flipped = False

# 3. Tiêu đề lớn trên màn hình
st.title("Flashcard")

# Xử lý hiển thị thẻ
if data:
    current_card = data[st.session_state.index]
    if not st.session_state.flipped:
        st.markdown(f'<div class="kanji-card">{current_card["前"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="back-card">{current_card["後ろ"]}</div>', unsafe_allow_html=True)

    # Hàng nút 1: Lật thẻ & Nghe
    col_flip, col_audio = st.columns([2, 1])
    with col_flip:
        if st.button("🔄 LẬT MẶT THẺ", type="primary"):
            st.session_state.flipped = not st.session_state.flipped
            st.rerun()
    with col_audio:
        if st.button("🔊 NGHE"):
            if not st.session_state.flipped:
                text = str(current_card.get('前', '')).split('\n')[0]
            else:
                text_back = str(current_card.get('後ろ', ''))
                cd = text_back.split("Cách đọc :")[1].split("\n")[0] if "Cách đọc :" in text_back else ""
                vd = text_back.split("Ví dụ :")[1].strip().split("\n")[0] if "Ví dụ :" in text_back else ""
                text = f"{cd}. {vd}"
            speak(text)

    # Hàng nút 2: Điều hướng thẻ & Tự động lưu vị trí
    c1, c2 = st.columns(2)
    with c1:
        if st.button("<< TRƯỚC"):
            st.session_state.index = (st.session_state.index - 1) % len(data)
            st.session_state.flipped = False
            save_index(st.session_state.index)
            st.rerun()
    with c2:
        if st.button("TIẾP THEO >>"):
            st.session_state.index = (st.session_state.index + 1) % len(data)
            st.session_state.flipped = False
            save_index(st.session_state.index)
            st.rerun()
            
    st.caption(f"Thẻ số: {st.session_state.index + 1} / {len(data)}")
else:
    st.error("Lỗi: Không tìm thấy file N2_Flashcards.xlsx!")
