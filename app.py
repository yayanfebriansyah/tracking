import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import re

# --- FITUR KUNCI: CACHING MODEL ---
# @st.cache_resource memberitahu Streamlit untuk menyimpan model AI di RAM server.
# Model TIDAK AKAN di-load/download ulang setiap kali tombol dipencet atau web dibuka.
@st.cache_resource(show_spinner="Memuat model AI ke memori server (hanya 1x)...")
def get_ocr_reader():
    # Menyimpan model ke memori server agar siap pakai kapan saja
    return easyocr.Reader(['en'], gpu=False)

def process_handwritten_accounts(image, target_accounts):
    # Mengambil model yang SUDAH SIAP dari RAM (Super Cepat!)
    reader = get_ocr_reader()
    
    image_np = np.array(image)
    
    # Membaca teks/angka dari gambar
    results = reader.readtext(image_np, detail=0)
    
    extracted_text = " ".join(results)
    cleaned_digits_only = re.sub(r'\D', '', extracted_text)
    
    found_accounts = []
    for account in target_accounts:
        clean_target = re.sub(r'\D', '', str(account))
        if clean_target and clean_target in cleaned_digits_only:
            found_accounts.append(account)
            
    return found_accounts, extracted_text

# --- TAMPILAN STREAMLIT ---
st.set_page_config(page_title="AI Scanner Instant", page_icon="⚡", layout="centered")
st.title("⚡ AI Scanner Super Cepat")
st.caption("Model AI tersimpan di server RAM untuk respons instan.")

# Panggil fungsi ini di awal agar model AI langsung siap di memori
reader_status = get_ocr_reader()

if "target_accounts" not in st.session_state:
    st.session_state.target_accounts = []

st.subheader("1. Masukkan Data Rekening Target")

with st.form("form_rekening"):
    data_input = st.text_area(
        "Paste/Tempel daftar nomor rekening di sini (pisahkan dengan Enter):", 
        height=120,
        placeholder="Contoh:\n1234567890\n0987654321"
    )
    submit_button = st.form_submit_button("💾 Simpan Data Rekening", type="primary", use_container_width=True)

if submit_button:
    accounts = [line.strip() for line in data_input.split('\n') if line.strip()]
    st.session_state.target_accounts = accounts
    if accounts:
        st.toast(f"Berhasil menyimpan {len(accounts)} nomor rekening!", icon="✅")

if not st.session_state.target_accounts:
    st.info("📌 Silakan paste nomor rekening di atas, lalu pencet tombol **'Simpan Data Rekening'**.")
else:
    st.success(f"✅ Data Aktif: **{len(st.session_state.target_accounts)}** nomor rekening tersimpan.")
    
    st.divider()
    st.subheader("2. Pindai Kertas Dokumen")
    
    tab1, tab2 = st.tabs(["📸 Ambil Foto", "📂 Pilih dari Galeri"])
    image_to_process = None

    with tab1:
        camera_photo = st.camera_input("Ambil foto dokumen langsung")
        if camera_photo is not None:
            image_to_process = Image.open(camera_photo)

    with tab2:
        uploaded_file = st.file_uploader("Pilih gambar dari galeri", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)
            st.image(image_to_process, caption="Preview Dokumen", use_container_width=True)

    if image_to_process is not None:
        if st.button("🔍 Pindai Sekarang", type="primary", use_container_width=True):
            with st.spinner("AI sedang membaca angka..."):
                found, raw_text = process_handwritten_accounts(image_to_process, st.session_state.target_accounts)
                
            st.divider()
            if found:
                st.success("✅ **DOKUMEN DITEMUKAN! SIMPAN KERTAS INI.**")
                st.write("Nomor rekening yang cocok:")
                for acc in found:
                    st.write(f"- **{acc}**")
            else:
                st.error("❌ **TIDAK COCOK. KERTAS BISA DISINGKIRKAN.**")
                
            with st.expander("Lihat teks/angka yang terbaca"):
                st.text(raw_text if raw_text else "Tidak ada teks/angka terdeteksi.")
