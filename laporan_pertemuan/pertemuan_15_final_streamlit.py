"""Pertemuan 15 - Aplikasi Web Streamlit Final Jelajah Alam."""

######################################################################
# SUMBER: rental/exceptions.py
######################################################################
"""Custom exception untuk Sistem Rental Alat Camping Jelajah Alam."""


class RentalError(Exception):
    """Exception dasar untuk semua kesalahan pada sistem rental."""


class DataTidakValidError(RentalError):
    """Dilempar jika data masukan (tarif, stok, nama, lama sewa, dan sebagainya) tidak valid."""


class StokHabisError(RentalError):
    """Dilempar jika stok alat tidak cukup untuk jumlah yang diminta."""

    def __init__(self, nama_alat, diminta, tersedia):
        self.nama_alat = nama_alat
        self.diminta = diminta
        self.tersedia = tersedia
        super().__init__(
            f"Stok {nama_alat} tidak cukup (diminta {diminta}, tersedia {tersedia})"
        )


class PenyewaTidakTerdaftarError(RentalError):
    """Dilempar jika ID penyewa tidak ditemukan di daftar penyewa."""

    def __init__(self, id_penyewa):
        self.id_penyewa = id_penyewa
        super().__init__(f"Penyewa dengan ID {id_penyewa} tidak terdaftar")

######################################################################
# SUMBER: rental/alat.py
######################################################################
# [digabung dalam satu file] from .exceptions import DataTidakValidError, StokHabisError


class AlatCamping:
    def __init__(self, kode, nama, tarif_per_hari, stok):
        self.__kode = None
        self.__nama = None
        self.__tarif = 0
        self.__stok = 0
        self.kode = kode
        self.nama = nama
        self.tarif_per_hari = tarif_per_hari
        self.stok = stok

    @property
    def kode(self):
        return self.__kode

    @kode.setter
    def kode(self, nilai):
        if not isinstance(nilai, str) or not nilai.strip():
            raise DataTidakValidError("Kode alat tidak boleh kosong")
        self.__kode = nilai.strip().upper()

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        if not isinstance(nilai, str) or not nilai.strip():
            raise DataTidakValidError("Nama alat tidak boleh kosong")
        self.__nama = nilai.strip()

    @property
    def tarif_per_hari(self):
        return self.__tarif

    @tarif_per_hari.setter
    def tarif_per_hari(self, nilai):
        if not isinstance(nilai, (int, float)) or isinstance(nilai, bool) or nilai <= 0:
            raise DataTidakValidError("Tarif per hari harus lebih dari 0")
        self.__tarif = nilai

    @property
    def stok(self):
        return self.__stok

    @stok.setter
    def stok(self, nilai):
        if not isinstance(nilai, int) or isinstance(nilai, bool) or nilai < 0:
            raise DataTidakValidError("Stok tidak boleh negatif")
        self.__stok = nilai

    def tersedia(self, jumlah=1):
        if not isinstance(jumlah, int) or isinstance(jumlah, bool) or jumlah <= 0:
            return False
        return self.__stok >= jumlah

    def kurangi_stok(self, jumlah):
        if not isinstance(jumlah, int) or isinstance(jumlah, bool) or jumlah <= 0:
            raise DataTidakValidError("Jumlah harus bilangan bulat lebih dari 0")
        if jumlah > self.__stok:
            raise StokHabisError(self.__nama, jumlah, self.__stok)
        self.__stok -= jumlah

    def kembalikan_stok(self, jumlah):
        if not isinstance(jumlah, int) or isinstance(jumlah, bool) or jumlah <= 0:
            raise DataTidakValidError("Jumlah harus bilangan bulat lebih dari 0")
        self.__stok += jumlah

    def tarif_sewa(self, hari):
        if not isinstance(hari, int) or isinstance(hari, bool) or hari <= 0:
            raise DataTidakValidError("Lama sewa harus bilangan bulat lebih dari 0")
        return self.__tarif * hari

    def jenis(self):
        return "Umum"

    def __str__(self):
        return f"{self.__kode} - {self.__nama} ({self.jenis()})"


class AlatShelter(AlatCamping):
    HARI_DISKON = 3
    DISKON_LAMA = 0.10

    def __init__(self, kode, nama, tarif_per_hari, stok, kapasitas_orang=1):
        super().__init__(kode, nama, tarif_per_hari, stok)
        self.__kapasitas = 1
        self.kapasitas_orang = kapasitas_orang

    @property
    def kapasitas_orang(self):
        return self.__kapasitas

    @kapasitas_orang.setter
    def kapasitas_orang(self, nilai):
        if not isinstance(nilai, int) or isinstance(nilai, bool) or nilai < 1:
            raise DataTidakValidError("Kapasitas orang minimal 1")
        self.__kapasitas = nilai

    def tarif_sewa(self, hari):
        total = super().tarif_sewa(hari)
        if hari >= self.HARI_DISKON:
            total *= 1 - self.DISKON_LAMA
        return total

    def jenis(self):
        return "Shelter"


class AlatMasak(AlatCamping):
    def __init__(self, kode, nama, tarif_per_hari, stok, biaya_gas=5000):
        super().__init__(kode, nama, tarif_per_hari, stok)
        self.__biaya_gas = 0
        self.biaya_gas = biaya_gas

    @property
    def biaya_gas(self):
        return self.__biaya_gas

    @biaya_gas.setter
    def biaya_gas(self, nilai):
        if not isinstance(nilai, (int, float)) or isinstance(nilai, bool) or nilai < 0:
            raise DataTidakValidError("Biaya gas tidak boleh negatif")
        self.__biaya_gas = nilai

    def tarif_sewa(self, hari):
        return super().tarif_sewa(hari) + self.__biaya_gas

    def jenis(self):
        return "Masak"

######################################################################
# SUMBER: rental/penyewa.py
######################################################################
"""Class Penyewa (Anggota 2: Mikail Sani).

Berisi Penyewa, PenyewaPendaki (turunan, member dengan diskon), dan
DaftarPenyewa sebagai tempat pencarian penyewa terdaftar.
"""
# [digabung dalam satu file] from .exceptions import DataTidakValidError, PenyewaTidakTerdaftarError


class Penyewa:
    """Penyewa biasa tanpa diskon."""

    def __init__(self, id_penyewa, nama):
        self.__id = None
        self.__nama = None
        self.__riwayat = []
        self.id_penyewa = id_penyewa
        self.nama = nama

    @property
    def id_penyewa(self):
        return self.__id

    @id_penyewa.setter
    def id_penyewa(self, nilai):
        if not isinstance(nilai, str) or not nilai.strip():
            raise DataTidakValidError("ID penyewa tidak boleh kosong")
        self.__id = nilai.strip().upper()

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        if not isinstance(nilai, str) or not nilai.strip():
            raise DataTidakValidError("Nama penyewa tidak boleh kosong")
        self.__nama = nilai.strip()

    @property
    def riwayat(self):
        """Salinan riwayat sewa, supaya list aslinya tidak bisa diubah dari luar."""
        return list(self.__riwayat)

    def tambah_riwayat(self, id_penyewaan, total):
        if total < 0:
            raise DataTidakValidError("Total sewa tidak boleh negatif")
        self.__riwayat.append({"id_penyewaan": id_penyewaan, "total": total})

    def total_sewa(self):
        return sum(item["total"] for item in self.__riwayat)

    def persen_diskon(self):
        """Penyewa biasa tidak mendapat diskon. Di-override oleh member."""
        return 0

    def status(self):
        return "Reguler"

    def __str__(self):
        return f"{self.__id} - {self.__nama} ({self.status()})"


class PenyewaPendaki(Penyewa):
    """Member Pendaki, dapat diskon dari total sewa."""

    def __init__(self, id_penyewa, nama, diskon_persen=10):
        super().__init__(id_penyewa, nama)
        self.__diskon = 0
        self.diskon_persen = diskon_persen

    @property
    def diskon_persen(self):
        return self.__diskon

    @diskon_persen.setter
    def diskon_persen(self, nilai):
        if not isinstance(nilai, (int, float)) or isinstance(nilai, bool) or not 0 <= nilai <= 100:
            raise DataTidakValidError("Diskon member harus di antara 0 sampai 100 persen")
        self.__diskon = nilai

    def persen_diskon(self):
        return self.__diskon

    def status(self):
        return "Member Pendaki"


class DaftarPenyewa:
    """Kumpulan penyewa yang terdaftar (disimpan dalam dict)."""

    def __init__(self):
        self.__data = {}

    def daftarkan(self, penyewa):
        if penyewa.id_penyewa in self.__data:
            raise DataTidakValidError(f"ID {penyewa.id_penyewa} sudah dipakai")
        self.__data[penyewa.id_penyewa] = penyewa

    def cari(self, id_penyewa):
        """Cari penyewa. Lempar PenyewaTidakTerdaftarError jika tidak ada."""
        kunci = str(id_penyewa).strip().upper()
        if kunci not in self.__data:
            raise PenyewaTidakTerdaftarError(id_penyewa)
        return self.__data[kunci]

    def jumlah(self):
        return len(self.__data)

######################################################################
# SUMBER: rental/penyewaan.py
######################################################################
"""Class Penyewaan (Anggota 3: Ahmad Najib Najmuddin).

Menghitung total biaya sewa, memanggil class AlatCamping, dan memakai
custom exception StokHabisError.
"""
# [digabung dalam satu file] from .exceptions import DataTidakValidError, RentalError, StokHabisError


class Penyewaan:
    """Satu kali penyewaan oleh satu penyewa untuk lama hari tertentu."""

    MAKS_HARI = 30

    def __init__(self, id_penyewaan, penyewa, lama_hari):
        if not isinstance(id_penyewaan, str) or not id_penyewaan.strip():
            raise DataTidakValidError("ID penyewaan tidak boleh kosong")
        if (not isinstance(lama_hari, int) or isinstance(lama_hari, bool)
                or not 1 <= lama_hari <= self.MAKS_HARI):
            raise DataTidakValidError(f"Lama sewa harus 1 sampai {self.MAKS_HARI} hari")
        self.__id = id_penyewaan.strip()
        self.__penyewa = penyewa
        self.__lama_hari = lama_hari
        self.__item = []          # list of dict: alat, jumlah, biaya_satuan
        self.__diproses = False
        self.__dikembalikan = False

    @property
    def id_penyewaan(self):
        return self.__id

    @property
    def penyewa(self):
        return self.__penyewa

    @property
    def lama_hari(self):
        return self.__lama_hari

    @property
    def item(self):
        return [dict(i) for i in self.__item]

    @property
    def diproses(self):
        return self.__diproses

    @property
    def dikembalikan(self):
        return self.__dikembalikan

    def tambah_alat(self, alat, jumlah):
        """Tambah alat ke daftar sewa. Stok dicek dulu, StokHabisError jika kurang."""
        if self.__diproses:
            raise RentalError("Penyewaan sudah diproses, tidak bisa menambah alat")
        if not isinstance(jumlah, int) or isinstance(jumlah, bool) or jumlah <= 0:
            raise DataTidakValidError("Jumlah harus bilangan bulat lebih dari 0")
        # kalau alat yang sama ditambah dua kali, hitung jumlah totalnya
        sudah_ada = sum(i["jumlah"] for i in self.__item if i["alat"] is alat)
        if not alat.tersedia(sudah_ada + jumlah):
            raise StokHabisError(alat.nama, sudah_ada + jumlah, alat.stok)
        self.__item.append(
            {"alat": alat, "jumlah": jumlah, "biaya_satuan": alat.tarif_sewa(self.__lama_hari)}
        )

    def subtotal(self):
        return sum(i["biaya_satuan"] * i["jumlah"] for i in self.__item)

    def diskon(self):
        return self.subtotal() * self.__penyewa.persen_diskon() / 100

    def total_bayar(self):
        return self.subtotal() - self.diskon()

    def proses(self):
        """Selesaikan penyewaan: stok dikurangi, riwayat penyewa dicatat."""
        if self.__diproses:
            raise RentalError("Penyewaan sudah diproses sebelumnya")
        if not self.__item:
            raise RentalError("Daftar alat masih kosong")
        for i in self.__item:
            i["alat"].kurangi_stok(i["jumlah"])
        self.__penyewa.tambah_riwayat(self.__id, self.total_bayar())
        self.__diproses = True
        return self.total_bayar()

    def kembalikan(self):
        """Alat dikembalikan: stok bertambah lagi."""
        if not self.__diproses:
            raise RentalError("Penyewaan belum diproses, belum ada alat yang dibawa")
        if self.__dikembalikan:
            raise RentalError("Alat sudah dikembalikan sebelumnya")
        for i in self.__item:
            i["alat"].kembalikan_stok(i["jumlah"])
        self.__dikembalikan = True

######################################################################
# SUMBER: rental/laporan.py
######################################################################
"""Class Laporan (Anggota 4: Ahmad Najib Najmuddin).

Menyimpan riwayat penyewaan memakai Collection (list dan dict) dan
mencetak nota sewa.
"""
# [digabung dalam satu file] from .exceptions import DataTidakValidError, RentalError


def rupiah(angka):
    """Format angka ke bentuk Rp 12.500 (titik sebagai pemisah ribuan)."""
    return "Rp " + f"{angka:,.0f}".replace(",", ".")


class Laporan:
    """Pencatat penyewaan yang sudah diproses dan pembuat nota/rekap."""

    LEBAR = 44

    def __init__(self, nama_usaha="Jelajah Alam Rental"):
        if not isinstance(nama_usaha, str) or not nama_usaha.strip():
            raise DataTidakValidError("Nama usaha tidak boleh kosong")
        self.__nama_usaha = nama_usaha.strip()
        self.__riwayat = []         # list penyewaan yang sudah diproses
        self.__rekap_alat = {}      # dict: nama alat -> jumlah unit disewa

    @property
    def nama_usaha(self):
        return self.__nama_usaha

    @property
    def riwayat(self):
        return list(self.__riwayat)

    def catat(self, penyewaan):
        """Masukkan penyewaan yang sudah diproses ke riwayat."""
        if not penyewaan.diproses:
            raise RentalError("Hanya penyewaan yang sudah diproses yang bisa dicatat")
        self.__riwayat.append(penyewaan)
        for i in penyewaan.item:
            nama = i["alat"].nama
            self.__rekap_alat[nama] = self.__rekap_alat.get(nama, 0) + i["jumlah"]

    def jumlah_penyewaan(self):
        return len(self.__riwayat)

    def total_pendapatan(self):
        return sum(p.total_bayar() for p in self.__riwayat)

    def rekap_alat(self):
        return dict(self.__rekap_alat)

    def alat_terlaris(self):
        """Nama alat yang paling banyak disewa, None jika belum ada."""
        if not self.__rekap_alat:
            return None
        return max(self.__rekap_alat, key=self.__rekap_alat.get)

    def cetak_nota(self, penyewaan):
        """Kembalikan nota sewa dalam bentuk string."""
        garis = "=" * self.LEBAR
        strip = "-" * self.LEBAR

        def kanan(kiri, nilai):
            return kiri.ljust(self.LEBAR - len(nilai)) + nilai

        baris = [garis, self.__nama_usaha.center(self.LEBAR), garis]
        baris.append(f"No. Sewa   : {penyewaan.id_penyewaan}")
        baris.append(f"Penyewa    : {penyewaan.penyewa.nama} ({penyewaan.penyewa.status()})")
        baris.append(f"Lama sewa  : {penyewaan.lama_hari} hari")
        baris.append(strip)
        for i in penyewaan.item:
            baris.append(i["alat"].nama)
            baris.append(kanan(f"  {i['jumlah']} unit x {rupiah(i['biaya_satuan'])}",
                               rupiah(i["jumlah"] * i["biaya_satuan"])))
        baris.append(strip)
        baris.append(kanan("Subtotal", rupiah(penyewaan.subtotal())))
        potongan = rupiah(penyewaan.diskon())
        if penyewaan.diskon() > 0:
            potongan = "-" + potongan
        baris.append(kanan("Diskon member", potongan))
        baris.append(kanan("TOTAL BAYAR", rupiah(penyewaan.total_bayar())))
        baris.append(garis)
        baris.append("Selamat berpetualang!".center(self.LEBAR))
        return "\n".join(baris)

    def cetak_rekap(self):
        baris = [f"REKAP PENYEWAAN {self.__nama_usaha}", "-" * self.LEBAR]
        baris.append(f"Jumlah penyewaan  : {self.jumlah_penyewaan()}")
        baris.append(f"Total pendapatan  : {rupiah(self.total_pendapatan())}")
        baris.append(f"Alat terlaris     : {self.alat_terlaris() or '-'}")
        baris.append("Rincian alat disewa:")
        for nama, jml in sorted(self.__rekap_alat.items()):
            baris.append(f"  - {nama}: {jml} unit")
        return "\n".join(baris)

######################################################################
# SUMBER: rental/persistence.py
######################################################################
"""SQLite persistence for the rental application's domain state."""
import os
import sqlite3
from pathlib import Path

# [digabung dalam satu file] from .alat import AlatCamping, AlatMasak, AlatShelter
# [digabung dalam satu file] from .laporan import Laporan
# [digabung dalam satu file] from .penyewa import DaftarPenyewa, Penyewa, PenyewaPendaki
# [digabung dalam satu file] from .penyewaan import Penyewaan


DEFAULT_DB_PATH = Path(
    os.environ.get("RENTAL_DB_PATH", Path(__file__).resolve().parent.parent / "rental.db")
)


def _create_tables(connection):
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS equipment (
            code TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            rate REAL NOT NULL,
            stock INTEGER NOT NULL,
            extra REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS renters (
            renter_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            is_member INTEGER NOT NULL,
            discount REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rentals (
            rental_id TEXT PRIMARY KEY,
            renter_id TEXT NOT NULL,
            days INTEGER NOT NULL,
            returned INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rental_items (
            rental_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            equipment_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            PRIMARY KEY (rental_id, position)
        );
        """
    )


def save_state(catalog, renters, rentals, db_path=DEFAULT_DB_PATH):
    """Atomically replace the local snapshot with the current domain state."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        with connection:
            _create_tables(connection)
            connection.execute("DELETE FROM rental_items")
            connection.execute("DELETE FROM rentals")
            connection.execute("DELETE FROM renters")
            connection.execute("DELETE FROM equipment")

            for item in catalog.values():
                if isinstance(item, AlatShelter):
                    category, extra = "Shelter", item.kapasitas_orang
                elif isinstance(item, AlatMasak):
                    category, extra = "Masak", item.biaya_gas
                else:
                    category, extra = "Umum", 0
                connection.execute(
                    "INSERT INTO equipment VALUES (?, ?, ?, ?, ?, ?)",
                    (item.kode, category, item.nama, item.tarif_per_hari, item.stok, extra),
                )

            for renter in renters.values():
                is_member = isinstance(renter, PenyewaPendaki)
                connection.execute(
                    "INSERT INTO renters VALUES (?, ?, ?, ?)",
                    (renter.id_penyewa, renter.nama, int(is_member), renter.persen_diskon()),
                )

            for rental in rentals:
                connection.execute(
                    "INSERT INTO rentals VALUES (?, ?, ?, ?)",
                    (rental.id_penyewaan, rental.penyewa.id_penyewa,
                     rental.lama_hari, int(rental.dikembalikan)),
                )
                for position, item in enumerate(rental.item):
                    connection.execute(
                        "INSERT INTO rental_items VALUES (?, ?, ?, ?)",
                        (rental.id_penyewaan, position, item["alat"].kode, item["jumlah"]),
                    )
    finally:
        connection.close()


def load_state(db_path=DEFAULT_DB_PATH):
    """Restore domain objects and rebuild renter history and report from rentals."""
    path = Path(db_path)
    if not path.exists():
        return None

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        _create_tables(connection)
        equipment_rows = connection.execute("SELECT * FROM equipment ORDER BY rowid").fetchall()
        if not equipment_rows:
            return None

        catalog = {}
        for row in equipment_rows:
            if row["category"] == "Shelter":
                item = AlatShelter(
                    row["code"], row["name"], row["rate"], row["stock"], int(row["extra"])
                )
            elif row["category"] == "Masak":
                item = AlatMasak(row["code"], row["name"], row["rate"], row["stock"], row["extra"])
            else:
                item = AlatCamping(row["code"], row["name"], row["rate"], row["stock"])
            catalog[item.kode] = item

        renters = {}
        registry = DaftarPenyewa()
        renter_rows = connection.execute("SELECT * FROM renters ORDER BY rowid").fetchall()
        for row in renter_rows:
            if row["is_member"]:
                renter = PenyewaPendaki(row["renter_id"], row["name"], row["discount"])
            else:
                renter = Penyewa(row["renter_id"], row["name"])
            renters[renter.id_penyewa] = renter
            registry.daftarkan(renter)

        rental_rows = connection.execute("SELECT * FROM rentals ORDER BY rowid").fetchall()
        item_rows = connection.execute(
            "SELECT * FROM rental_items ORDER BY rental_id, position"
        ).fetchall()
    finally:
        connection.close()

    items_by_rental = {}
    for row in item_rows:
        items_by_rental.setdefault(row["rental_id"], []).append(row)

    # Temporarily restore the quantities on open rentals so replaying their
    # normal domain transitions returns inventory to the saved stock level.
    for row in rental_rows:
        if not row["returned"]:
            for item_row in items_by_rental.get(row["rental_id"], []):
                item = catalog[item_row["equipment_code"]]
                item.stok += item_row["quantity"]

    rentals = []
    report = Laporan("Jelajah Alam Rental")
    for row in rental_rows:
        rental = Penyewaan(row["rental_id"], renters[row["renter_id"]], row["days"])
        for item_row in items_by_rental.get(row["rental_id"], []):
            rental.tambah_alat(catalog[item_row["equipment_code"]], item_row["quantity"])
        rental.proses()
        if row["returned"]:
            rental.kembalikan()
        report.catat(rental)
        rentals.append(rental)

    return catalog, renters, registry, rentals, report

######################################################################
# SUMBER: rental/__init__.py
######################################################################
"""Domain model and persistence for the camping rental application."""

# [digabung dalam satu file] from .alat import AlatCamping, AlatMasak, AlatShelter
# [digabung dalam satu file] from .exceptions import (
# [digabung dalam satu file]     DataTidakValidError,
# [digabung dalam satu file]     PenyewaTidakTerdaftarError,
# [digabung dalam satu file]     RentalError,
# [digabung dalam satu file]     StokHabisError,
# [digabung dalam satu file] )
# [digabung dalam satu file] from .laporan import Laporan, rupiah
# [digabung dalam satu file] from .penyewa import DaftarPenyewa, Penyewa, PenyewaPendaki
# [digabung dalam satu file] from .penyewaan import Penyewaan

__all__ = [
    "AlatCamping",
    "AlatMasak",
    "AlatShelter",
    "DataTidakValidError",
    "DaftarPenyewa",
    "Laporan",
    "Penyewa",
    "PenyewaPendaki",
    "PenyewaTidakTerdaftarError",
    "RentalError",
    "StokHabisError",
    "Penyewaan",
    "rupiah",
]

######################################################################
# SUMBER: app.py
######################################################################
"""Dashboard Streamlit untuk Rental Alat Camping Jelajah Alam."""
from datetime import datetime
import sqlite3

import streamlit as st

# [digabung dalam satu file] from rental import (
# [digabung dalam satu file]     AlatCamping,
# [digabung dalam satu file]     AlatMasak,
# [digabung dalam satu file]     AlatShelter,
# [digabung dalam satu file]     DaftarPenyewa,
# [digabung dalam satu file]     Laporan,
# [digabung dalam satu file]     Penyewa,
# [digabung dalam satu file]     PenyewaPendaki,
# [digabung dalam satu file]     Penyewaan,
# [digabung dalam satu file]     RentalError,
# [digabung dalam satu file]     rupiah,
# [digabung dalam satu file] )
# [digabung dalam satu file] from rental.persistence import load_state, save_state


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
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: .82rem; }
    [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; color: var(--forest); font-size: 1.2rem !important; }
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
    st.session_state.setdefault("draft", [])
    st.session_state.setdefault("flash_success", None)
    st.session_state.setdefault("last_receipt", None)


def persist_state():
    try:
        save_state(
            st.session_state.catalog,
            st.session_state.renters,
            st.session_state.rentals,
        )
    except (OSError, sqlite3.Error) as error:
        st.error(f"Perubahan belum tersimpan ke database lokal: {error}")


def show_flash_messages():
    if st.session_state.flash_success:
        st.success(st.session_state.flash_success)
        st.session_state.flash_success = None


def page_header(title, subtitle):
    st.markdown(
        f'<div class="eyebrow">Jelajah Alam Rental</div><h1>{title}</h1>'
        f'<p style="color:#718078;margin-top:-.6rem">{subtitle}</p>',
        unsafe_allow_html=True,
    )


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
    row1 = st.columns(2)
    row1[0].metric("Jenis alat", len(st.session_state.catalog))
    row1[1].metric("Penyewa", len(st.session_state.renters))
    row2 = st.columns(2)
    row2[0].metric("Belum kembali", len(open_rentals))
    row2[1].metric("Pendapatan tercatat", rupiah(report.total_pendapatan()))

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
                st.markdown(
                    f"**{item.nama}**  \n<span class='stock-low'>Sisa {item.stok} unit</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.success("Semua stok tersedia dalam jumlah aman.")


def catalog_page():
    page_header("Katalog alat", "Inventaris dan tarif sewa per hari.")
    show_flash_messages()
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
        with st.container():
            col1, col2 = st.columns(2)
            code = col1.text_input("Kode alat", placeholder="A05", key="cat_code")
            name = col2.text_input("Nama alat", key="cat_name")
            category = col1.selectbox("Kategori", ["Umum", "Shelter", "Masak"], key="cat_type")
            rate = col2.number_input("Tarif per hari (Rp)", min_value=1, step=1000, value=10000, key="cat_rate")
            stock = col1.number_input("Stok awal", min_value=0, step=1, value=1, key="cat_stock")
            extra = None
            if category == "Shelter":
                extra = col2.number_input("Kapasitas orang", min_value=1, step=1, value=2, key="cat_cap")
            elif category == "Masak":
                extra = col2.number_input("Biaya gas (Rp)", min_value=0, step=1000, value=5000, key="cat_gas")

            if st.button("Tambah alat", type="primary", key="btn_add_equipment"):
                normalized_code = code.strip().upper()
                clean_name = name.strip()
                if not normalized_code or not clean_name:
                    st.error("Kode dan nama alat wajib diisi.")
                elif normalized_code in catalog:
                    st.error(f"Kode {normalized_code} sudah digunakan.")
                else:
                    try:
                        if category == "Shelter":
                            item = AlatShelter(normalized_code, clean_name, rate, stock, kapasitas_orang=extra)
                        elif category == "Masak":
                            item = AlatMasak(normalized_code, clean_name, rate, stock, biaya_gas=extra)
                        else:
                            item = AlatCamping(normalized_code, clean_name, rate, stock)
                        catalog[normalized_code] = item
                        persist_state()
                        st.session_state.flash_success = f"{clean_name} berhasil ditambahkan."
                        st.rerun()
                    except RentalError as error:
                        st.error(str(error))


def renters_page():
    page_header("Data penyewa", "Daftar pelanggan dan status keanggotaan.")
    show_flash_messages()
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
        with st.container():
            col1, col2 = st.columns(2)
            renter_id = col1.text_input("ID penyewa", placeholder="P03", key="renter_id")
            renter_name = col2.text_input("Nama lengkap", key="renter_name")
            member = col1.toggle("Member Pendaki", key="renter_member")
            discount = col2.number_input(
                "Diskon member (%)", min_value=0, max_value=100, value=10,
                disabled=not member, key="renter_discount",
            )
            if st.button("Daftarkan penyewa", type="primary", key="btn_add_renter"):
                normalized_id = renter_id.strip().upper()
                clean_name = renter_name.strip()
                if not normalized_id or not clean_name:
                    st.error("ID dan nama penyewa wajib diisi.")
                elif normalized_id in renters:
                    st.error(f"ID {normalized_id} sudah terdaftar.")
                else:
                    try:
                        renter = (PenyewaPendaki(normalized_id, clean_name, discount)
                                  if member else Penyewa(normalized_id, clean_name))
                        st.session_state.registry.daftarkan(renter)
                        renters[normalized_id] = renter
                        persist_state()
                        st.session_state.flash_success = f"{clean_name} berhasil didaftarkan."
                        st.rerun()
                    except RentalError as error:
                        st.error(str(error))


def rental_page():
    page_header("Transaksi sewa", "Susun keranjang, cek total, lalu proses penyewaan.")
    show_flash_messages()

    if st.session_state.last_receipt:
        st.code(st.session_state.last_receipt)
        st.session_state.last_receipt = None

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
    with st.container(border=True):
        available_codes = list(catalog)
        item_cols = st.columns([2, 1, 1])
        code = item_cols[0].selectbox("Alat", available_codes, format_func=lambda key: f"{catalog[key].nama} · {key}")
        item_cols[0].caption(f"Stok tersedia: {catalog[code].stok} unit")
        quantity = item_cols[1].number_input("Jumlah", min_value=1, step=1, value=1)
        item_cols[2].markdown(f"**{rupiah(catalog[code].tarif_sewa(days))}**\n\nper unit / transaksi")
        if st.button("Tambah ke keranjang", key="btn_add_draft"):
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

        action_col, clear_col, _ = st.columns([1.3, 1.5, 3.2])
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
                st.session_state.flash_success = "Transaksi berhasil diproses dan stok telah diperbarui."
                st.session_state.last_receipt = st.session_state.report.cetak_nota(rental)
                st.rerun()
            except RentalError as error:
                st.error(str(error))
        if clear_col.button("Kosongkan keranjang", width="stretch"):
            st.session_state.draft = []
            st.rerun()
    else:
        st.info("Keranjang masih kosong. Tambahkan alat untuk memulai transaksi.")


def returns_page():
    page_header("Pengembalian", "Catat alat kembali dan perbarui stok inventaris.")
    show_flash_messages()
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
                    st.session_state.flash_success = f"{rental.id_penyewaan} selesai dikembalikan."
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


def main():
    initialize_state()

    with st.sidebar:
        st.markdown(
            "<div class='brand-mark'>⛰ JELAJAH ALAM</div>"
            "<div style='color:#b6c8bc;font-size:.8rem;margin:.25rem 0 1.5rem'>Sistem rental perlengkapan</div>",
            unsafe_allow_html=True,
        )
        page = st.radio(
            "MENU UTAMA",
            ["Ringkasan", "Katalog Alat", "Data Penyewa", "Transaksi Sewa", "Pengembalian", "Laporan"],
            label_visibility="visible",
        )
        st.markdown(
            "<div style='position:fixed;bottom:1.5rem;color:#91a99b;font-size:.75rem'>JELAJAH ALAM RENTAL · LOKAL</div>",
            unsafe_allow_html=True,
        )

    {
        "Ringkasan": dashboard,
        "Katalog Alat": catalog_page,
        "Data Penyewa": renters_page,
        "Transaksi Sewa": rental_page,
        "Pengembalian": returns_page,
        "Laporan": report_page,
    }[page]()


if __name__ == "__main__":
    main()
