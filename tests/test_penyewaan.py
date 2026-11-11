import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alat import AlatCamping, AlatMasak, AlatShelter
from exceptions import DataTidakValidError, RentalError, StokHabisError
from penyewa import Penyewa, PenyewaPendaki
from penyewaan import Penyewaan


class TestPenyewaan(unittest.TestCase):
    def setUp(self):
        self.lampu = AlatCamping("A04", "Headlamp", 5000, 10)
        self.tenda = AlatShelter("A01", "Tenda", 40000, 2)
        self.kompor = AlatMasak("A03", "Kompor", 8000, 3, biaya_gas=5000)
        self.raka = Penyewa("P01", "Raka")
        self.dinda = PenyewaPendaki("P02", "Dinda", 10)

    def test_hitung_subtotal(self):
        s = Penyewaan("S1", self.raka, 2)
        s.tambah_alat(self.lampu, 3)
        s.tambah_alat(self.tenda, 1)
        self.assertAlmostEqual(s.subtotal(), 30000 + 80000)

    def test_subtotal_pakai_tarif_turunan(self):
        s = Penyewaan("S1", self.raka, 3)
        s.tambah_alat(self.tenda, 1)
        s.tambah_alat(self.kompor, 1)
        self.assertAlmostEqual(s.subtotal(), 108000 + 29000)

    def test_diskon_member(self):
        s = Penyewaan("S1", self.dinda, 2)
        s.tambah_alat(self.lampu, 10)
        self.assertAlmostEqual(s.diskon(), 10000)
        self.assertAlmostEqual(s.total_bayar(), 90000)

    def test_penyewa_reguler_tanpa_diskon(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.lampu, 2)
        self.assertEqual(s.diskon(), 0)

    def test_stok_habis_saat_tambah_alat(self):
        s = Penyewaan("S1", self.raka, 1)
        with self.assertRaises(StokHabisError):
            s.tambah_alat(self.tenda, 3)

    def test_stok_habis_akibat_alat_ganda(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.tenda, 2)
        with self.assertRaises(StokHabisError):
            s.tambah_alat(self.tenda, 1)

    def test_pesan_exception_stok(self):
        s = Penyewaan("S1", self.raka, 1)
        try:
            s.tambah_alat(self.tenda, 5)
        except StokHabisError as e:
            self.assertEqual(e.diminta, 5)
            self.assertEqual(e.tersedia, 2)
            self.assertIn("Tenda", str(e))

    def test_jumlah_tidak_valid(self):
        s = Penyewaan("S1", self.raka, 1)
        with self.assertRaises(DataTidakValidError):
            s.tambah_alat(self.lampu, 0)

    def test_lama_hari_tidak_valid(self):
        for hari in (0, -1, 31, "2"):
            with self.assertRaises(DataTidakValidError):
                Penyewaan("S1", self.raka, hari)

    def test_id_kosong_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            Penyewaan(" ", self.raka, 1)

    def test_proses_mengurangi_stok_dan_mencatat_riwayat(self):
        s = Penyewaan("S1", self.dinda, 2)
        s.tambah_alat(self.lampu, 4)
        total = s.proses()
        self.assertEqual(self.lampu.stok, 6)
        self.assertTrue(s.diproses)
        self.assertEqual(self.dinda.riwayat[0]["id_penyewaan"], "S1")
        self.assertAlmostEqual(total, 36000)

    def test_proses_daftar_kosong(self):
        with self.assertRaises(RentalError):
            Penyewaan("S1", self.raka, 1).proses()

    def test_proses_dua_kali_ditolak(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.lampu, 1)
        s.proses()
        with self.assertRaises(RentalError):
            s.proses()

    def test_tambah_alat_setelah_diproses_ditolak(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.lampu, 1)
        s.proses()
        with self.assertRaises(RentalError):
            s.tambah_alat(self.lampu, 1)

    def test_kembalikan_mengembalikan_stok(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.tenda, 2)
        s.proses()
        self.assertEqual(self.tenda.stok, 0)
        s.kembalikan()
        self.assertEqual(self.tenda.stok, 2)
        self.assertTrue(s.dikembalikan)

    def test_kembalikan_sebelum_diproses_ditolak(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.lampu, 1)
        with self.assertRaises(RentalError):
            s.kembalikan()

    def test_kembalikan_dua_kali_ditolak(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.lampu, 1)
        s.proses()
        s.kembalikan()
        with self.assertRaises(RentalError):
            s.kembalikan()


if __name__ == "__main__":
    unittest.main()
