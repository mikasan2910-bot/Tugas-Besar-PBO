"""SQLite persistence for the rental application's domain state."""
import os
import sqlite3
from pathlib import Path

from alat import AlatCamping, AlatMasak, AlatShelter
from laporan import Laporan
from penyewa import DaftarPenyewa, Penyewa, PenyewaPendaki
from penyewaan import Penyewaan


DEFAULT_DB_PATH = Path(
    os.environ.get("RENTAL_DB_PATH", Path(__file__).with_name("rental.db"))
)


def _create_tables(connection):
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS equipment (
            code TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            rate REAL NOT NULL,
            stock INTEGER NOT NULL,
            extra REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS renters (
            renter_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            is_member INTEGER NOT NULL,
            discount REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rentals (
            rental_id TEXT PRIMARY KEY,
            renter_id TEXT NOT NULL,
            days INTEGER NOT NULL,
            returned INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rental_items (
            rental_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            equipment_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            PRIMARY KEY (rental_id, position)
        );
        """
    )


def save_state(catalog, renters, rentals, db_path=DEFAULT_DB_PATH):
    """Atomically replace the local snapshot with the current domain state."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        with connection:
            _create_tables(connection)
            connection.execute("DELETE FROM rental_items")
            connection.execute("DELETE FROM rentals")
            connection.execute("DELETE FROM renters")
            connection.execute("DELETE FROM equipment")

            for item in catalog.values():
                if isinstance(item, AlatShelter):
                    category, extra = "Shelter", item.kapasitas_orang
                elif isinstance(item, AlatMasak):
                    category, extra = "Masak", item.biaya_gas
                else:
                    category, extra = "Umum", 0
                connection.execute(
                    "INSERT INTO equipment VALUES (?, ?, ?, ?, ?, ?)",
                    (item.kode, category, item.nama, item.tarif_per_hari, item.stok, extra),
                )

            for renter in renters.values():
                is_member = isinstance(renter, PenyewaPendaki)
                connection.execute(
                    "INSERT INTO renters VALUES (?, ?, ?, ?)",
                    (renter.id_penyewa, renter.nama, int(is_member), renter.persen_diskon()),
                )

            for rental in rentals:
                connection.execute(
                    "INSERT INTO rentals VALUES (?, ?, ?, ?)",
                    (rental.id_penyewaan, rental.penyewa.id_penyewa,
                     rental.lama_hari, int(rental.dikembalikan)),
                )
                for position, item in enumerate(rental.item):
                    connection.execute(
                        "INSERT INTO rental_items VALUES (?, ?, ?, ?)",
                        (rental.id_penyewaan, position, item["alat"].kode, item["jumlah"]),
                    )
    finally:
        connection.close()


def load_state(db_path=DEFAULT_DB_PATH):
    """Restore domain objects and rebuild renter history and report from rentals."""
    path = Path(db_path)
    if not path.exists():
        return None

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        _create_tables(connection)
        equipment_rows = connection.execute("SELECT * FROM equipment ORDER BY rowid").fetchall()
        if not equipment_rows:
            return None

        catalog = {}
        for row in equipment_rows:
            if row["category"] == "Shelter":
                item = AlatShelter(
                    row["code"], row["name"], row["rate"], row["stock"], int(row["extra"])
                )
            elif row["category"] == "Masak":
                item = AlatMasak(row["code"], row["name"], row["rate"], row["stock"], row["extra"])
            else:
                item = AlatCamping(row["code"], row["name"], row["rate"], row["stock"])
            catalog[item.kode] = item

        renters = {}
        registry = DaftarPenyewa()
        renter_rows = connection.execute("SELECT * FROM renters ORDER BY rowid").fetchall()
        for row in renter_rows:
            if row["is_member"]:
                renter = PenyewaPendaki(row["renter_id"], row["name"], row["discount"])
            else:
                renter = Penyewa(row["renter_id"], row["name"])
            renters[renter.id_penyewa] = renter
            registry.daftarkan(renter)

        rental_rows = connection.execute("SELECT * FROM rentals ORDER BY rowid").fetchall()
        item_rows = connection.execute(
            "SELECT * FROM rental_items ORDER BY rental_id, position"
        ).fetchall()
    finally:
        connection.close()

    items_by_rental = {}
    for row in item_rows:
        items_by_rental.setdefault(row["rental_id"], []).append(row)

    # Temporarily restore the quantities on open rentals so replaying their
    # normal domain transitions returns inventory to the saved stock level.
    for row in rental_rows:
        if not row["returned"]:
            for item_row in items_by_rental.get(row["rental_id"], []):
                item = catalog[item_row["equipment_code"]]
                item.stok += item_row["quantity"]

    rentals = []
    report = Laporan("Jelajah Alam Rental")
    for row in rental_rows:
        rental = Penyewaan(row["rental_id"], renters[row["renter_id"]], row["days"])
        for item_row in items_by_rental.get(row["rental_id"], []):
            rental.tambah_alat(catalog[item_row["equipment_code"]], item_row["quantity"])
        rental.proses()
        if row["returned"]:
            rental.kembalikan()
        report.catat(rental)
        rentals.append(rental)

    return catalog, renters, registry, rentals, report