import streamlit as st
import pytesseract
from PIL import Image

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
st.warning("🔒 Aman: Data rekening Anda tidak disimpan di server. Data akan hilang setelah web ini ditutup.")

# --- FITUR BARU: COPY-PASTE DATA DARI HP ---
st.subheader("1. Masukkan Data Rekening")
data_input = st.text_area("Paste/Tempel daftar nomor rekening yang dicari di sini (pisahkan dengan Enter):", height=100)

# Mengolah data teks dari input menjadi daftar (list)
target_accounts = [line.strip() for line in data_input.split('\n') if line.strip()]

if not target_accounts:
    st.info("Silakan paste nomor rekening di kotak atas terlebih dahulu sebelum memindai dokumen.")
else:
    st.success(f"Berhasil memuat {len(target_accounts)} nomor rekening sementara.")
    
    st.divider()
    st.subheader("2. Mulai Pindai Dokumen")
    
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
