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
st.warning("🔒 Aman: Data rekening Anda tidak disimpan di server. Data akan hilang begitu web ditutup.")

# --- INISIALISASI PENYIMPANAN SEMENTARA (SESSION STATE) ---
if "target_accounts" not in st.session_state:
    st.session_state.target_accounts = []

# --- FORM INPUT DENGAN TOMBOL SUBMIT ---
st.subheader("1. Masukkan Data Rekening Target")

with st.form("form_rekening"):
    data_input = st.text_area(
        "Paste/Tempel daftar nomor rekening di sini (pisahkan dengan Enter):", 
        height=120,
        placeholder="Contoh:\n1234567890\n0987654321\n1122334455"
    )
    # Tombol Submit khusus untuk input teks
    submit_button = st.form_submit_button("💾 Simpan Data Rekening", type="primary", use_container_width=True)

# Logika saat tombol Submit ditekan
if submit_button:
    # Memproses teks input menjadi list
    accounts = [line.strip() for line in data_input.split('\n') if line.strip()]
    st.session_state.target_accounts = accounts
    if accounts:
        st.toast(f"Berhasil menyimpan {len(accounts)} nomor rekening!", icon="✅")

# Status data rekening saat ini
if not st.session_state.target_accounts:
    st.info("📌 Silakan paste nomor rekening di atas, lalu pencet tombol **'Simpan Data Rekening'**.")
else:
    st.success(f"✅ Data Aktif: **{len(st.session_state.target_accounts)}** nomor rekening tersimpan dan siap dicari.")
    
    st.divider()
    
    # --- BAGIAN PINDAI DOKUMEN ---
    st.subheader("2. Mulai Pindai Dokumen")
    
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

    # Tombol untuk memproses foto
    if image_to_process is not None:
        if st.button("🔍 Pindai Dokumen Sekarang", type="primary", use_container_width=True):
            with st.spinner("AI sedang membaca angka pada kertas..."):
                found, raw_text = process_image_for_accounts(image_to_process, st.session_state.target_accounts)
                
            st.divider()
            if found:
                st.success("✅ **DOKUMEN DITEMUKAN! SIMPAN KERTAS INI.**")
                st.write("Nomor rekening yang cocok:")
                for acc in found:
                    st.write(f"- **{acc}**")
            else:
                st.error("❌ **TIDAK COCOK. KERTAS BISA DISINGKIRKAN.**")
                
            with st.expander("Lihat teks yang berhasil dibaca AI"):
                st.text(raw_text)
