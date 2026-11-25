from .exceptions import DataTidakValidError, StokHabisError


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
            raise DataTidakValidError("Jumlah harus bilangan bulat lebih dari 0")
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