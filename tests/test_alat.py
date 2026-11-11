import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alat import AlatCamping, AlatMasak, AlatShelter
from exceptions import DataTidakValidError, StokHabisError


class TestAlatCamping(unittest.TestCase):
    def setUp(self):
        self.a = AlatCamping("a04", "Headlamp", 5000, 10)

    def test_atribut_awal(self):
        self.assertEqual(self.a.kode, "A04")
        self.assertEqual(self.a.nama, "Headlamp")
        self.assertEqual(self.a.tarif_per_hari, 5000)
        self.assertEqual(self.a.stok, 10)

    def test_atribut_private_tidak_bisa_diakses_langsung(self):
        with self.assertRaises(AttributeError):
            _ = self.a.__tarif

    def test_setter_tarif_valid(self):
        self.a.tarif_per_hari = 7500
        self.assertEqual(self.a.tarif_per_hari, 7500)

    def test_tarif_nol_atau_negatif_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            self.a.tarif_per_hari = 0
        with self.assertRaises(DataTidakValidError):
            self.a.tarif_per_hari = -100

    def test_tarif_bukan_angka_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            self.a.tarif_per_hari = "murah"

    def test_stok_negatif_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            self.a.stok = -1

    def test_nama_kosong_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            AlatCamping("A05", "   ", 1000, 1)

    def test_kurangi_stok(self):
        self.a.kurangi_stok(4)
        self.assertEqual(self.a.stok, 6)

    def test_kurangi_stok_melebihi_stok(self):
        with self.assertRaises(StokHabisError):
            self.a.kurangi_stok(11)
        self.assertEqual(self.a.stok, 10)

    def test_kurangi_stok_jumlah_tidak_valid(self):
        with self.assertRaises(DataTidakValidError):
            self.a.kurangi_stok(0)

    def test_kembalikan_stok(self):
        self.a.kurangi_stok(4)
        self.a.kembalikan_stok(4)
        self.assertEqual(self.a.stok, 10)

    def test_kembalikan_stok_tidak_valid(self):
        with self.assertRaises(DataTidakValidError):
            self.a.kembalikan_stok(-2)

    def test_tersedia(self):
        self.assertTrue(self.a.tersedia(10))
        self.assertFalse(self.a.tersedia(11))

    def test_tersedia_jumlah_tidak_valid(self):
        for jumlah in (0, -1, True, 1.5, "1"):
            with self.subTest(jumlah=jumlah):
                with self.assertRaises(DataTidakValidError):
                    self.a.tersedia(jumlah)

    def test_tarif_sewa_dikali_hari(self):
        self.assertEqual(self.a.tarif_sewa(3), 15000)

    def test_lama_sewa_tidak_valid(self):
        with self.assertRaises(DataTidakValidError):
            self.a.tarif_sewa(0)


class TestTurunanAlat(unittest.TestCase):
    def test_shelter_tanpa_diskon_di_bawah_3_hari(self):
        tenda = AlatShelter("A01", "Tenda", 40000, 2, kapasitas_orang=4)
        self.assertAlmostEqual(tenda.tarif_sewa(2), 80000)
        self.assertEqual(tenda.jenis(), "Shelter")

    def test_shelter_diskon_mulai_3_hari(self):
        tenda = AlatShelter("A01", "Tenda", 40000, 2)
        self.assertAlmostEqual(tenda.tarif_sewa(3), 108000)

    def test_shelter_kapasitas_tidak_valid(self):
        with self.assertRaises(DataTidakValidError):
            AlatShelter("A01", "Tenda", 40000, 2, kapasitas_orang=0)

    def test_masak_ada_biaya_gas(self):
        kompor = AlatMasak("A03", "Kompor", 8000, 4, biaya_gas=5000)
        self.assertAlmostEqual(kompor.tarif_sewa(3), 29000)
        self.assertEqual(kompor.jenis(), "Masak")

    def test_biaya_gas_negatif_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            AlatMasak("A03", "Kompor", 8000, 4, biaya_gas=-1)

    def test_polymorphism_tarif_sewa(self):
        daftar = [
            AlatCamping("A", "Umum", 1000, 1),
            AlatShelter("B", "Shelter", 1000, 1),
            AlatMasak("C", "Masak", 1000, 1, biaya_gas=500),
        ]
        hasil = [round(x.tarif_sewa(3), 2) for x in daftar]
        self.assertEqual(hasil, [3000, 2700.0, 3500])


if __name__ == "__main__":
    unittest.main()
