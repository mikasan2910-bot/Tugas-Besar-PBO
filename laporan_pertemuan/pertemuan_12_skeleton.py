"""Pertemuan 12 - Kerangka Class dan Exception (Skeleton)."""

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
