"""Dashboard Streamlit untuk Rental Alat Camping Jelajah Alam."""
from datetime import datetime
import sqlite3

import streamlit as st

from alat import AlatCamping, AlatMasak, AlatShelter
from exceptions import RentalError
from laporan import Laporan, rupiah
from persistence import load_state, save_state
from penyewa import DaftarPenyewa, Penyewa, PenyewaPendaki
from penyewaan import Penyewaan


st.set_page_config(
    page_title="Jelajah Alam | Rental",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root {
        --forest: #173c32;
        --forest-deep: #102c25;
        --leaf: #c9ef72;
        --paper: #f5f6ef;
        --ink: #1b2822;
        --muted: #718078;
        --line: #dfe5dc;
        --coral: #e67d5e;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: var(--paper); }
    [data-testid="stSidebar"] { background: var(--forest-deep); }
    [data-testid="stSidebar"] * { color: #f5f6ef; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .38rem .2rem; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0 !important; }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.05rem !important; }
    [data-testid="stMetric"] { background: white; border: 1px solid var(--line); padding: 1rem 1.1rem; border-radius: 6px; }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; color: var(--forest); font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: .82rem; }
    div.stButton > button[kind="primary"] { background: var(--forest); border-color: var(--forest); color: white; }
    div.stButton > button[kind="primary"]:hover { background: var(--forest-deep); border-color: var(--forest-deep); }
    .brand-mark { color: var(--leaf); font: 700 1.2rem 'Space Grotesk', sans-serif; }
    .eyebrow { color: var(--muted); text-transform: uppercase; font-size: .73rem; font-weight: 700; letter-spacing: 1px; }
    .welcome { background: var(--forest); color: white; padding: 1.4rem 1.6rem; border-radius: 7px; margin: .4rem 0 1.4rem; }
    .welcome h2 { color: white !important; margin: .2rem 0 .35rem; }
    .welcome p { color: #d3ded7; margin: 0; }
    .stock-low { color: #b34f36; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state():
    if "catalog" not in st.session_state:
        restored = load_state()
        if restored is not None:
            (st.session_state.catalog, st.session_state.renters,
             st.session_state.registry, st.session_state.rentals,
             st.session_state.report) = restored
        else:
            st.session_state.catalog = {
                "A01": AlatShelter("A01", "Tenda Dome 4 Orang", 40000, 3, kapasitas_orang=4),
                "A02": AlatShelter("A02", "Sleeping Bag", 10000, 10),
                "A03": AlatMasak("A03", "Kompor Portable", 8000, 4, biaya_gas=5000),
                "A04": AlatCamping("A04", "Headlamp", 5000, 12),
            }
            registry = DaftarPenyewa()
            renters = [
                Penyewa("P01", "Raka Pratama"),
                PenyewaPendaki("P02", "Dinda Lestari", diskon_persen=10),
            ]
            for renter in renters:
                registry.daftarkan(renter)
            st.session_state.registry = registry
            st.session_state.renters = {r.id_penyewa: r for r in renters}
            st.session_state.rentals = []
            st.session_state.report = Laporan("Jelajah Alam Rental")
    if "draft" not in st.session_state:
        st.session_state.draft = []


def persist_state():
    try:
        save_state(
            st.session_state.catalog,
            st.session_state.renters,
            st.session_state.rentals,
        )
    except (OSError, sqlite3.Error) as error:
        st.error(f"Perubahan belum tersimpan ke database lokal: {error}")


def page_header(title, subtitle):
    st.markdown(f'<div class="eyebrow">Jelajah Alam Rental</div><h1>{title}</h1><p style="color:#718078;margin-top:-.6rem">{subtitle}</p>', unsafe_allow_html=True)


def dashboard():
    page_header("Ringkasan operasional", "Pantau penyewaan, ketersediaan alat, dan aktivitas hari ini.")
    st.markdown(
        "<div class='welcome'><div class='eyebrow' style='color:#c9ef72'>RUANG OPERASIONAL</div>"
        "<h2>Siap untuk petualangan berikutnya?</h2>"
        "<p>Kelola inventaris dan transaksi rental dalam satu tempat.</p></div>",
        unsafe_allow_html=True,
    )
    rentals = st.session_state.rentals
    open_rentals = [r for r in rentals if not r.dikembalikan]
    report = st.session_state.report
    metrics = st.columns(2)
    metrics[0].metric("Jenis alat", len(st.session_state.catalog))
    metrics[1].metric("Penyewa", len(st.session_state.renters))
    metrics = st.columns(2)
    metrics[0].metric("Belum kembali", len(open_rentals))
    metrics[1].metric("Pendapatan tercatat", rupiah(report.total_pendapatan()))

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Transaksi terbaru")
        if rentals:
            rows = [{
                "ID sewa": rental.id_penyewaan,
                "Penyewa": rental.penyewa.nama,
                "Durasi": f"{rental.lama_hari} hari",
                "Total": rupiah(rental.total_bayar()),
                "Status": "Dikembalikan" if rental.dikembalikan else "Disewa",
            } for rental in reversed(rentals[-6:])]
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.info("Belum ada transaksi. Mulai dari menu Transaksi Sewa.")
    with right:
        st.subheader("Stok perlu diperhatikan")
        low_stock = [item for item in st.session_state.catalog.values() if item.stok <= 2]
        if low_stock:
            for item in low_stock:
                st.markdown(f"**{item.nama}**  \n<span class='stock-low'>Sisa {item.stok} unit</span>", unsafe_allow_html=True)
        else:
            st.success("Semua stok tersedia dalam jumlah aman.")


def catalog_page():
    page_header("Katalog alat", "Inventaris dan tarif sewa per hari.")
    catalog = st.session_state.catalog
    rows = [{
        "Kode": item.kode,
        "Nama alat": item.nama,
        "Kategori": item.jenis(),
        "Tarif / hari": rupiah(item.tarif_per_hari),
        "Stok tersedia": item.stok,
        "Detail": (f"Kapasitas {item.kapasitas_orang} orang" if isinstance(item, AlatShelter)
                   else f"Biaya gas {rupiah(item.biaya_gas)}" if isinstance(item, AlatMasak) else "-"),
    } for item in catalog.values()]
    st.dataframe(rows, width="stretch", hide_index=True)

    with st.expander("Tambah alat ke katalog"):
        with st.form("add_equipment", clear_on_submit=True):
            col1, col2 = st.columns(2)
            code = col1.text_input("Kode alat", placeholder="A05")
            name = col2.text_input("Nama alat")
            category = col1.selectbox("Kategori", ["Umum", "Shelter", "Masak"])
            rate = col2.number_input("Tarif per hari (Rp)", min_value=1, step=1000, value=10000)
            stock = col1.number_input("Stok awal", min_value=0, step=1, value=1)
            extra = None
            if category == "Shelter":
                extra = col2.number_input("Kapasitas orang", min_value=1, step=1, value=2)
            elif category == "Masak":
                extra = col2.number_input("Biaya gas (Rp)", min_value=0, step=1000, value=5000)
            submitted = st.form_submit_button("Tambah alat", type="primary")
            if submitted:
                normalized_code = code.strip().upper()
                if not normalized_code or not name.strip():
                    st.error("Kode dan nama alat wajib diisi.")
                elif normalized_code in catalog:
                    st.error(f"Kode {normalized_code} sudah digunakan.")
                else:
                    try:
                        if category == "Shelter":
                            item = AlatShelter(normalized_code, name, rate, stock, kapasitas_orang=extra)
                        elif category == "Masak":
                            item = AlatMasak(normalized_code, name, rate, stock, biaya_gas=extra)
                        else:
                            item = AlatCamping(normalized_code, name, rate, stock)
                        catalog[normalized_code] = item
                        persist_state()
                        st.success(f"{name.strip()} berhasil ditambahkan.")
                        st.rerun()
                    except RentalError as error:
                        st.error(str(error))


def renters_page():
    page_header("Data penyewa", "Daftar pelanggan dan status keanggotaan.")
    renters = st.session_state.renters
    rows = [{
        "ID": renter.id_penyewa,
        "Nama": renter.nama,
        "Status": renter.status(),
        "Diskon": f"{renter.persen_diskon():g}%",
        "Total transaksi": len(renter.riwayat),
        "Total belanja": rupiah(renter.total_sewa()),
    } for renter in renters.values()]
    st.dataframe(rows, width="stretch", hide_index=True)

    with st.expander("Daftarkan penyewa"):
        with st.form("add_renter", clear_on_submit=True):
            col1, col2 = st.columns(2)
            renter_id = col1.text_input("ID penyewa", placeholder="P03")
            renter_name = col2.text_input("Nama lengkap")
            member = col1.toggle("Member Pendaki")
            discount = col2.number_input("Diskon member (%)", min_value=0, max_value=100, value=10, disabled=not member)
            submitted = st.form_submit_button("Daftarkan penyewa", type="primary")
            if submitted:
                normalized_id = renter_id.strip().upper()
                if not normalized_id or not renter_name.strip():
                    st.error("ID dan nama penyewa wajib diisi.")
                elif normalized_id in renters:
                    st.error(f"ID {normalized_id} sudah terdaftar.")
                else:
                    try:
                        renter = (PenyewaPendaki(normalized_id, renter_name, discount)
                                  if member else Penyewa(normalized_id, renter_name))
                        st.session_state.registry.daftarkan(renter)
                        renters[normalized_id] = renter
                        persist_state()
                        st.success(f"{renter_name.strip()} berhasil didaftarkan.")
                        st.rerun()
                    except RentalError as error:
                        st.error(str(error))


def rental_page():
    page_header("Transaksi sewa", "Susun keranjang, cek total, lalu proses penyewaan.")
    renters = st.session_state.renters
    catalog = st.session_state.catalog
    if not renters or not catalog:
        st.warning("Tambahkan penyewa dan alat terlebih dahulu.")
        return

    controls = st.columns([1.3, 1, 1])
    renter_id = controls[0].selectbox("Penyewa", list(renters), format_func=lambda key: f"{renters[key].nama} · {key}")
    days = controls[1].number_input("Lama sewa (hari)", min_value=1, max_value=Penyewaan.MAKS_HARI, value=1, step=1)
    rental_id = f"SWA-{datetime.now():%y%m%d}-{len(st.session_state.rentals) + 1:03d}"
    controls[2].text_input("ID transaksi", value=rental_id, disabled=True)

    st.subheader("Pilih alat")
    with st.form("add_to_draft"):
        available_codes = list(catalog)
        item_cols = st.columns([2, 1, 1])
        code = item_cols[0].selectbox("Alat", available_codes, format_func=lambda key: f"{catalog[key].nama} · {key}")
        item_cols[0].caption(f"Stok tersedia: {catalog[code].stok} unit")
        quantity = item_cols[1].number_input("Jumlah", min_value=1, step=1, value=1)
        item_cols[2].markdown(f"**{rupiah(catalog[code].tarif_sewa(days))}**\n\nper unit / transaksi")
        add_item = st.form_submit_button("Tambah ke keranjang")
        if add_item:
            existing = sum(qty for item_code, qty in st.session_state.draft if item_code == code)
            if not catalog[code].tersedia(existing + quantity):
                st.error(f"Stok {catalog[code].nama} tidak cukup. Tersedia {catalog[code].stok} unit.")
            else:
                st.session_state.draft.append((code, quantity))
                st.rerun()

    draft = st.session_state.draft
    if draft:
        renter = renters[renter_id]
        subtotal = sum(catalog[item_code].tarif_sewa(days) * qty for item_code, qty in draft)
        discount = subtotal * renter.persen_diskon() / 100
        cart_rows = [{
            "Alat": catalog[item_code].nama,
            "Jumlah": qty,
            "Tarif sewa / unit": rupiah(catalog[item_code].tarif_sewa(days)),
            "Total": rupiah(catalog[item_code].tarif_sewa(days) * qty),
        } for item_code, qty in draft]
        st.subheader("Keranjang sewa")
        st.dataframe(cart_rows, width="stretch", hide_index=True)
        totals = st.columns(3)
        totals[0].metric("Subtotal", rupiah(subtotal))
        totals[1].metric(f"Diskon ({renter.persen_diskon():g}%)", f"- {rupiah(discount)}")
        totals[2].metric("Total bayar", rupiah(subtotal - discount))
        action_col, clear_col = st.columns([1, 5])
        if action_col.button("Proses transaksi", type="primary", width="stretch"):
            try:
                rental = Penyewaan(rental_id, renter, days)
                for item_code, qty in draft:
                    rental.tambah_alat(catalog[item_code], qty)
                rental.proses()
                st.session_state.report.catat(rental)
                st.session_state.rentals.append(rental)
                st.session_state.draft = []
                persist_state()
                st.success("Transaksi berhasil diproses dan stok telah diperbarui.")
                st.code(st.session_state.report.cetak_nota(rental))
            except RentalError as error:
                st.error(str(error))
        if clear_col.button("Kosongkan keranjang", width="stretch"):
            st.session_state.draft = []
            st.rerun()
    else:
        st.info("Keranjang masih kosong. Tambahkan alat untuk memulai transaksi.")


def returns_page():
    page_header("Pengembalian", "Catat alat kembali dan perbarui stok inventaris.")
    open_rentals = [rental for rental in st.session_state.rentals if not rental.dikembalikan]
    if not open_rentals:
        st.info("Tidak ada penyewaan yang menunggu pengembalian.")
        return
    for rental in open_rentals:
        with st.container(border=True):
            details = st.columns([1.2, 1.3, 2, 1])
            details[0].markdown(f"**{rental.id_penyewaan}**  \n{rental.lama_hari} hari")
            details[1].markdown(f"**{rental.penyewa.nama}**  \n{rupiah(rental.total_bayar())}")
            details[2].write(", ".join(f"{item['alat'].nama} × {item['jumlah']}" for item in rental.item))
            if details[3].button("Terima kembali", key=f"return_{rental.id_penyewaan}", type="primary"):
                try:
                    rental.kembalikan()
                    persist_state()
                    st.success(f"{rental.id_penyewaan} selesai dikembalikan.")
                    st.rerun()
                except RentalError as error:
                    st.error(str(error))


def report_page():
    page_header("Laporan", "Ringkasan pendapatan dan pergerakan alat.")
    report = st.session_state.report
    metrics = st.columns(3)
    metrics[0].metric("Jumlah penyewaan", report.jumlah_penyewaan())
    metrics[1].metric("Total pendapatan", rupiah(report.total_pendapatan()))
    metrics[2].metric("Alat terlaris", report.alat_terlaris() or "-")
    st.subheader("Unit alat yang disewa")
    summary = report.rekap_alat()
    if summary:
        st.bar_chart(summary, color="#527e50")
    else:
        st.info("Laporan akan terisi setelah transaksi pertama diproses.")
    with st.expander("Tampilkan rekap teks"):
        st.code(report.cetak_rekap())


initialize_state()

with st.sidebar:
    st.markdown("<div class='brand-mark'>⛰ JELAJAH ALAM</div><div style='color:#b6c8bc;font-size:.8rem;margin:.25rem 0 1.5rem'>Sistem rental perlengkapan</div>", unsafe_allow_html=True)
    page = st.radio(
        "MENU UTAMA",
        ["Ringkasan", "Katalog Alat", "Data Penyewa", "Transaksi Sewa", "Pengembalian", "Laporan"],
        label_visibility="visible",
    )
    st.markdown("<div style='position:fixed;bottom:1.5rem;color:#91a99b;font-size:.75rem'>JELAJAH ALAM RENTAL · LOKAL</div>", unsafe_allow_html=True)

{
    "Ringkasan": dashboard,
    "Katalog Alat": catalog_page,
    "Data Penyewa": renters_page,
    "Transaksi Sewa": rental_page,
    "Pengembalian": returns_page,
    "Laporan": report_page,
}[page]()