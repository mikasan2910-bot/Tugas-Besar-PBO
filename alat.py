"""Class AlatCamping (Anggota 1: Mikail Sani).

Berisi class induk AlatCamping beserta dua turunannya (AlatShelter dan
AlatMasak) untuk menerapkan inheritance dan polymorphism.
"""
from exceptions import DataTidakValidError, StokHabisError


def _bulat_positif(nilai):
    return isinstance(nilai, int) and not isinstance(nilai, bool) and nilai > 0


class AlatCamping:
    """Alat camping yang disewakan, dengan tarif per hari dan jumlah stok."""

    def __init__(self, kode, nama, tarif_per_hari, stok):
        self.__kode = None
        self.__nama = None
        self.__tarif = 0
        self.__stok = 0
        # lewat setter supaya validasi ikut jalan saat objek dibuat
        self.kode = kode
        self.nama = nama
        self.tarif_per_hari = tarif_per_hari
        self.stok = stok

    # ---------- getter dan setter (encapsulation) ----------
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
            raise DataTidakValidError("Tarif sewa harus berupa angka lebih dari 0")
        self.__tarif = nilai

    @property
    def stok(self):
        return self.__stok

    @stok.setter
    def stok(self, nilai):
        if not isinstance(nilai, int) or isinstance(nilai, bool) or nilai < 0:
            raise DataTidakValidError("Stok alat harus berupa bilangan bulat, minimal 0")
        self.__stok = nilai

    # ---------- method bisnis ----------
    def tersedia(self, jumlah=1):
        """True jika stok cukup untuk jumlah yang diminta."""
        if not _bulat_positif(jumlah):
            raise DataTidakValidError("Jumlah alat harus bilangan bulat lebih dari 0")
        return self.__stok >= jumlah

    def kurangi_stok(self, jumlah):
        """Alat dibawa penyewa, stok berkurang. Lempar StokHabisError jika kurang."""
        if not _bulat_positif(jumlah):
            raise DataTidakValidError("Jumlah alat harus bilangan bulat lebih dari 0")
        if not self.tersedia(jumlah):
            raise StokHabisError(self.__nama, jumlah, self.__stok)
        self.__stok -= jumlah

    def kembalikan_stok(self, jumlah):
        """Alat dikembalikan penyewa, stok bertambah lagi."""
        if not _bulat_positif(jumlah):
            raise DataTidakValidError("Jumlah alat harus bilangan bulat lebih dari 0")
        self.__stok += jumlah

    def tarif_sewa(self, hari):
        """Biaya sewa satu unit untuk sekian hari. Bisa di-override class turunan."""
        if not _bulat_positif(hari):
            raise DataTidakValidError("Lama sewa harus bilangan bulat lebih dari 0 hari")
        return self.__tarif * hari

    def jenis(self):
        return "Umum"

    def __str__(self):
        tarif = f"{self.__tarif:,.0f}".replace(",", ".")
        return f"[{self.__kode}] {self.__nama} | Rp {tarif}/hari | stok {self.__stok}"


class AlatShelter(AlatCamping):
    """Tenda dan perlengkapan tidur. Sewa 3 hari atau lebih dapat potongan 10 persen."""

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
        if not _bulat_positif(nilai):
            raise DataTidakValidError("Kapasitas harus bilangan bulat lebih dari 0")
        self.__kapasitas = nilai

    def tarif_sewa(self, hari):
        biaya = super().tarif_sewa(hari)
        if hari >= self.HARI_DISKON:
            biaya *= 1 - self.DISKON_LAMA
        return biaya

    def jenis(self):
        return "Shelter"


class AlatMasak(AlatCamping):
    """Kompor dan alat masak. Ada biaya gas tetap setiap kali disewa."""

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
