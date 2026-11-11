import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alat import AlatCamping
from exceptions import DataTidakValidError, RentalError
from laporan import Laporan, rupiah
from penyewa import Penyewa, PenyewaPendaki
from penyewaan import Penyewaan


class TestLaporan(unittest.TestCase):
    def setUp(self):
        self.lampu = AlatCamping("A04", "Headlamp", 5000, 100)
        self.matras = AlatCamping("A05", "Matras", 2000, 100)
        self.raka = Penyewa("P01", "Raka")
        self.dinda = PenyewaPendaki("P02", "Dinda", 10)
        self.lap = Laporan("Rental Uji")

    def _sewa(self, ids, penyewa, hari, daftar):
        s = Penyewaan(ids, penyewa, hari)
        for alat, jml in daftar:
            s.tambah_alat(alat, jml)
        s.proses()
        return s

    def test_laporan_awal_kosong(self):
        self.assertEqual(self.lap.jumlah_penyewaan(), 0)
        self.assertEqual(self.lap.total_pendapatan(), 0)
        self.assertIsNone(self.lap.alat_terlaris())

    def test_nama_usaha_kosong_ditolak(self):
        with self.assertRaises(DataTidakValidError):
            Laporan("")

    def test_catat_dan_total_pendapatan(self):
        self.lap.catat(self._sewa("S1", self.raka, 1, [(self.lampu, 2)]))
        self.lap.catat(self._sewa("S2", self.dinda, 2, [(self.lampu, 10)]))
        self.assertEqual(self.lap.jumlah_penyewaan(), 2)
        self.assertAlmostEqual(self.lap.total_pendapatan(), 10000 + 90000)

    def test_catat_penyewaan_belum_diproses_ditolak(self):
        s = Penyewaan("S1", self.raka, 1)
        s.tambah_alat(self.lampu, 1)
        with self.assertRaises(RentalError):
            self.lap.catat(s)

    def test_rekap_alat_dan_terlaris(self):
        self.lap.catat(self._sewa("S1", self.raka, 1, [(self.lampu, 2), (self.matras, 5)]))
        self.lap.catat(self._sewa("S2", self.raka, 1, [(self.matras, 1)]))
        self.assertEqual(self.lap.rekap_alat(), {"Headlamp": 2, "Matras": 6})
        self.assertEqual(self.lap.alat_terlaris(), "Matras")

    def test_riwayat_salinan(self):
        self.lap.catat(self._sewa("S1", self.raka, 1, [(self.lampu, 1)]))
        self.lap.riwayat.clear()
        self.assertEqual(self.lap.jumlah_penyewaan(), 1)

    def test_isi_nota(self):
        s = self._sewa("S1", self.dinda, 2, [(self.lampu, 10)])
        nota = self.lap.cetak_nota(s)
        self.assertIn("Rental Uji", nota)
        self.assertIn("S1", nota)
        self.assertIn("Dinda", nota)
        self.assertIn("2 hari", nota)
        self.assertIn("Rp 90.000", nota)
        self.assertIn("-Rp 10.000", nota)

    def test_nota_tanpa_diskon(self):
        s = self._sewa("S1", self.raka, 1, [(self.lampu, 1)])
        self.assertNotIn("-Rp", self.lap.cetak_nota(s))

    def test_format_rupiah(self):
        self.assertEqual(rupiah(1500000), "Rp 1.500.000")
        self.assertEqual(rupiah(0), "Rp 0")

    def test_cetak_rekap(self):
        self.lap.catat(self._sewa("S1", self.raka, 1, [(self.lampu, 3)]))
        rekap = self.lap.cetak_rekap()
        self.assertIn("Jumlah penyewaan  : 1", rekap)
        self.assertIn("Headlamp: 3 unit", rekap)


if __name__ == "__main__":
    unittest.main()
