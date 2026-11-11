"""Class Penyewa (Anggota 2: Mikail Sani).

Berisi Penyewa, PenyewaPendaki (turunan, member dengan diskon), dan
DaftarPenyewa sebagai tempat pencarian penyewa terdaftar.
"""
from exceptions import DataTidakValidError, PenyewaTidakTerdaftarError


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
