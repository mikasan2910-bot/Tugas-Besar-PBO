import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alat import AlatCamping
from laporan import Laporan
from persistence import load_state, save_state
from penyewa import PenyewaPendaki
from penyewaan import Penyewaan


class TestPersistence(unittest.TestCase):
    def test_round_trip_preserves_stock_rentals_history_and_report(self):
        with tempfile.TemporaryDirectory() as folder:
            db_path = os.path.join(folder, "rental.db")
            headlamp = AlatCamping("A04", "Headlamp", 5000, 8)
            renter = PenyewaPendaki("P02", "Dinda", 10)
            renters = {renter.id_penyewa: renter}

            open_rental = Penyewaan("S1", renter, 2)
            open_rental.tambah_alat(headlamp, 2)
            open_rental.proses()

            returned_rental = Penyewaan("S2", renter, 1)
            returned_rental.tambah_alat(headlamp, 1)
            returned_rental.proses()
            returned_rental.kembalikan()

            rentals = [open_rental, returned_rental]
            report = Laporan()
            for rental in rentals:
                report.catat(rental)

            save_state({headlamp.kode: headlamp}, renters, rentals, db_path)
            restored = load_state(db_path)

            catalog, restored_renters, _, restored_rentals, restored_report = restored
            self.assertEqual(catalog["A04"].stok, headlamp.stok)
            self.assertEqual([r.id_penyewaan for r in restored_rentals], ["S1", "S2"])
            self.assertFalse(restored_rentals[0].dikembalikan)
            self.assertTrue(restored_rentals[1].dikembalikan)
            self.assertEqual(len(restored_renters["P02"].riwayat), 2)
            self.assertEqual(restored_report.jumlah_penyewaan(), 2)
            self.assertEqual(restored_report.total_pendapatan(), report.total_pendapatan())

    def test_missing_database_returns_none(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(load_state(os.path.join(folder, "missing.db")))


if __name__ == "__main__":
    unittest.main()