import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import DataTidakValidError, PenyewaTidakTerdaftarError
from penyewa import DaftarPenyewa, Penyewa, PenyewaPendaki


class TestPenyewa(unittest.TestCase):
    def setUp(self):
        self.p = Penyewa("p01", "Raka")

    def test_atribut_awal(self):
        self.assertEqual(self.p.id_penyewa, "P01")
        self.assertEqual(self.p.nama, "Raka")
        self.assertEqual(self.p.status(), "Reguler")
        self.assertEqual(self.p.persen_diskon(), 0)

    def test_nama_kosong_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            Penyewa("P02", "")

    def test_riwayat_awal_kosong(self):
        self.assertEqual(self.p.riwayat, [])
        self.assertEqual(self.p.total_sewa(), 0)

    def test_tambah_riwayat(self):
        self.p.tambah_riwayat("SWA-1", 10000)
        self.p.tambah_riwayat("SWA-2", 25000)
        self.assertEqual(len(self.p.riwayat), 2)
        self.assertEqual(self.p.total_sewa(), 35000)

    def test_riwayat_tidak_bisa_diubah_dari_luar(self):
        self.p.tambah_riwayat("SWA-1", 10000)
        salinan = self.p.riwayat
        salinan.clear()
        self.assertEqual(len(self.p.riwayat), 1)

    def test_total_negatif_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            self.p.tambah_riwayat("SWA-1", -5)


class TestPenyewaPendaki(unittest.TestCase):
    def test_diskon_member(self):
        m = PenyewaPendaki("P02", "Dinda", diskon_persen=8)
        self.assertEqual(m.persen_diskon(), 8)
        self.assertEqual(m.status(), "Member Pendaki")

    def test_diskon_bawaan_10_persen(self):
        self.assertEqual(PenyewaPendaki("P02", "Dinda").persen_diskon(), 10)

    def test_diskon_member_tidak_valid(self):
        with self.assertRaises(DataTidakValidError):
            PenyewaPendaki("P02", "Dinda", diskon_persen=-1)

    def test_polymorphism_persen_diskon(self):
        semua = [Penyewa("A", "Reguler"), PenyewaPendaki("B", "Member", 15)]
        self.assertEqual([x.persen_diskon() for x in semua], [0, 15])


class TestDaftarPenyewa(unittest.TestCase):
    def setUp(self):
        self.daftar = DaftarPenyewa()
        self.daftar.daftarkan(Penyewa("P01", "Raka"))

    def test_cari_penyewa_terdaftar(self):
        self.assertEqual(self.daftar.cari("p01").nama, "Raka")

    def test_cari_penyewa_tidak_terdaftar(self):
        with self.assertRaises(PenyewaTidakTerdaftarError):
            self.daftar.cari("P99")

    def test_id_ganda_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            self.daftar.daftarkan(Penyewa("p01", "Orang Lain"))

    def test_jumlah(self):
        self.assertEqual(self.daftar.jumlah(), 1)


if __name__ == "__main__":
    unittest.main()
