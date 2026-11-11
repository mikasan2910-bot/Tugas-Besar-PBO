"""Program utama Rental Alat Camping Jelajah Alam: menyatukan AlatCamping,
Penyewa, Penyewaan, dan Laporan."""
from alat import AlatCamping, AlatMasak, AlatShelter
from exceptions import PenyewaTidakTerdaftarError, RentalError, StokHabisError
from laporan import Laporan, rupiah
from penyewa import DaftarPenyewa, Penyewa, PenyewaPendaki
from penyewaan import Penyewaan


def main():
    # ----- data awal -----
    katalog = {
        "A01": AlatShelter("A01", "Tenda Dome 4 Orang", 40000, 3, kapasitas_orang=4),
        "A02": AlatShelter("A02", "Sleeping Bag", 10000, 10),
        "A03": AlatMasak("A03", "Kompor Portable", 8000, 4, biaya_gas=5000),
        "A04": AlatCamping("A04", "Headlamp", 5000, 12),
    }
    penyewa = DaftarPenyewa()
    penyewa.daftarkan(Penyewa("P01", "Raka"))
    penyewa.daftarkan(PenyewaPendaki("P02", "Dinda", diskon_persen=10))

    laporan = Laporan("Jelajah Alam Rental")

    print("=== Katalog Alat ===")
    for a in katalog.values():
        print(" ", a, f"({a.jenis()})")

    # ----- penyewaan 1: penyewa reguler, 2 hari -----
    s1 = Penyewaan("SWA-001", penyewa.cari("P01"), 2)
    s1.tambah_alat(katalog["A01"], 1)
    s1.tambah_alat(katalog["A04"], 2)
    s1.proses()
    laporan.catat(s1)
    print("\n" + laporan.cetak_nota(s1))

    # ----- penyewaan 2: member pendaki, 3 hari -----
    s2 = Penyewaan("SWA-002", penyewa.cari("p02"), 3)
    s2.tambah_alat(katalog["A01"], 2)
    s2.tambah_alat(katalog["A03"], 1)
    s2.tambah_alat(katalog["A02"], 4)
    s2.proses()
    laporan.catat(s2)
    print("\n" + laporan.cetak_nota(s2))

    # ----- alat dikembalikan -----
    print("\n=== Pengembalian SWA-001 ===")
    print("Stok Tenda Dome sebelum kembali:", katalog["A01"].stok)
    s1.kembalikan()
    print("Stok Tenda Dome sesudah kembali:", katalog["A01"].stok)

    # ----- skenario error -----
    print("\n=== Uji skenario error ===")
    try:
        s3 = Penyewaan("SWA-003", penyewa.cari("P01"), 2)
        s3.tambah_alat(katalog["A01"], 5)
    except StokHabisError as e:
        print("Gagal (stok):", e)

    try:
        penyewa.cari("P99")
    except PenyewaTidakTerdaftarError as e:
        print("Gagal (penyewa):", e)

    try:
        Penyewaan("SWA-004", penyewa.cari("P01"), 1).proses()
    except RentalError as e:
        print("Gagal (penyewaan):", e)

    print("\n" + laporan.cetak_rekap())
    print("\nRiwayat sewa Dinda:")
    for r in penyewa.cari("P02").riwayat:
        print(f"  {r['id_penyewaan']} -> {rupiah(r['total'])}")


if __name__ == "__main__":
    main()
