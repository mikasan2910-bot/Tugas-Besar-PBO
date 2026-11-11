"""Custom exception untuk Sistem Rental Alat Camping Jelajah Alam."""


class RentalError(Exception):
    """Exception dasar untuk semua kesalahan pada sistem rental."""


class DataTidakValidError(RentalError):
    """Dilempar jika data masukan (tarif, stok, nama, lama sewa, dan sebagainya) tidak valid."""


class StokHabisError(RentalError):
    """Dilempar jika stok alat tidak cukup untuk jumlah yang diminta."""

    def __init__(self, nama_alat, diminta, tersedia):
        self.nama_alat = nama_alat
        self.diminta = diminta
        self.tersedia = tersedia
        super().__init__(
            f"Stok {nama_alat} tidak cukup (diminta {diminta}, tersedia {tersedia})"
        )


class PenyewaTidakTerdaftarError(RentalError):
    """Dilempar jika ID penyewa tidak ditemukan di daftar penyewa."""

    def __init__(self, id_penyewa):
        self.id_penyewa = id_penyewa
        super().__init__(f"Penyewa dengan ID {id_penyewa} tidak terdaftar")
