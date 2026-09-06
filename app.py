import streamlit as st
import pytesseract
from PIL import Image
import os

def load_target_accounts(filepath="data_rekening.txt"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as file:
        accounts = [line.strip() for line in file.readlines() if line.strip()]
    return accounts

def process_image_for_accounts(image, target_accounts):
    extracted_text = pytesseract.image_to_string(image)
    cleaned_text = extracted_text.replace(" ", "").replace("-", "")
    
    found_accounts = []
    for account in target_accounts:
        if account in cleaned_text or account in extracted_text:
            found_accounts.append(account)
            
    return found_accounts, extracted_text

st.set_page_config(page_title="AI Scanner Rekening", page_icon="📱", layout="centered")
st.title("📱 AI Mobile Scanner")
st.write("Arahkan kamera HP Anda ke dokumen, atau unggah foto dari galeri.")

target_accounts = load_target_accounts()

if not target_accounts:
    st.warning("Data kosong. Masukkan nomor rekening di file data_rekening.txt di GitHub.")
else:
    st.success(f"Database aktif: {len(target_accounts)} nomor rekening siap dicari.")

tab1, tab2 = st.tabs(["📸 Ambil Foto", "📂 Pilih dari Galeri"])
image_to_process = None

with tab1:
    camera_photo = st.camera_input("Ambil foto dokumen langsung")
    if camera_photo is not None:
        image_to_process = Image.open(camera_photo)

with tab2:
    uploaded_file = st.file_uploader("Pilih gambar", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image_to_process = Image.open(uploaded_file)
        st.image(image_to_process, caption="Preview Dokumen", use_container_width=True)

if image_to_process is not None:
    if st.button("🔍 Pindai Dokumen Sekarang", type="primary", use_container_width=True):
        with st.spinner("AI sedang membaca angka pada kertas..."):
            found, raw_text = process_image_for_accounts(image_to_process, target_accounts)
            
        st.divider()
        if found:
            st.success("✅ **DOKUMEN DITEMUKAN! SIMPAN KERTAS INI.**")
            for acc in found:
                st.write(f"- **{acc}**")
        else:
            st.error("❌ **TIDAK COCOK. KERTAS BISA DISINGKIRKAN.**")
            
        with st.expander("Lihat teks yang berhasil dibaca AI"):
            st.text(raw_text)
