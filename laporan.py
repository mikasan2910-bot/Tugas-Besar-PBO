"""Class Laporan (Anggota 4: Ahmad Najib Najmuddin).

Menyimpan riwayat penyewaan memakai Collection (list dan dict) dan
mencetak nota sewa.
"""
from exceptions import DataTidakValidError, RentalError


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
