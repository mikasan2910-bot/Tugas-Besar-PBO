"""Class Penyewaan (Anggota 3: Ahmad Najib Najmuddin).

Menghitung total biaya sewa, memanggil class AlatCamping, dan memakai
custom exception StokHabisError.
"""
from exceptions import DataTidakValidError, RentalError, StokHabisError


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
