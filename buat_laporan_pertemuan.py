"""Membuat file laporan .py per pertemuan dari kode lama di folder rental_pbo."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "laporan_pertemuan"

PERTEMUAN = {
    "pertemuan_12_skeleton.py": {
        "judul": "Pertemuan 12 - Kerangka Class dan Exception (Skeleton)",
        "files": [
            "rental/exceptions.py",
            "rental/alat.py",
            "rental/penyewa.py",
        ],
    },
    "pertemuan_13_class_dan_unit_test.py": {
        "judul": "Pertemuan 13 - Implementasi Class, SQLite, CLI, dan Unit Test",
        "files": [
            "rental/exceptions.py",
            "rental/alat.py",
            "rental/penyewa.py",
            "rental/penyewaan.py",
            "rental/laporan.py",
            "rental/persistence.py",
            "rental/__init__.py",
            "main.py",
            "tests/test_alat.py",
            "tests/test_penyewa.py",
            "tests/test_penyewaan.py",
            "tests/test_laporan.py",
            "tests/test_persistence.py",
        ],
    },
    "pertemuan_14_pengujian_dan_web.py": {
        "judul": "Pertemuan 14 - Pengujian Sistem dan Antarmuka Streamlit",
        "files": [
            "rental/exceptions.py",
            "rental/alat.py",
            "rental/penyewa.py",
            "rental/penyewaan.py",
            "rental/laporan.py",
            "rental/persistence.py",
            "rental/__init__.py",
            "tests/test_alat.py",
            "tests/test_penyewa.py",
            "tests/test_penyewaan.py",
            "tests/test_laporan.py",
            "tests/test_persistence.py",
            "app.py",
        ],
    },
    "pertemuan_15_final_streamlit.py": {
        "judul": "Pertemuan 15 - Aplikasi Web Streamlit Final Jelajah Alam",
        "files": [
            "rental/exceptions.py",
            "rental/alat.py",
            "rental/penyewa.py",
            "rental/penyewaan.py",
            "rental/laporan.py",
            "rental/persistence.py",
            "rental/__init__.py",
            "app.py",
        ],
    },
}


def bersihkan_import_internal(source: str) -> tuple[list[str], str]:
    """Pisahkan __future__ import dan nonaktifkan import internal paket rental."""
    tree = ast.parse(source)
    lines = source.splitlines()
    future_lines: list[str] = []
    future_line_nums: set[int] = set()
    internal_line_nums: set[int] = set()

    for node in tree.body:
        end_lineno = node.end_lineno or node.lineno
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                for num in range(node.lineno, end_lineno + 1):
                    future_lines.append(lines[num - 1])
                    future_line_nums.add(num)
            elif node.level > 0 or (node.module and node.module.split(".")[0] == "rental"):
                for num in range(node.lineno, end_lineno + 1):
                    internal_line_nums.add(num)
        elif isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] == "rental" for alias in node.names):
                for num in range(node.lineno, end_lineno + 1):
                    internal_line_nums.add(num)

    hasil: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if idx in future_line_nums:
            continue
        if idx in internal_line_nums:
            hasil.append(f"# [digabung dalam satu file] {line}")
        else:
            hasil.append(line)

    return future_lines, "\n".join(hasil)


def bangun_file_pertemuan():
    OUTPUT_DIR.mkdir(exist_ok=True)

    for nama_output, info in PERTEMUAN.items():
        semua_future: list[str] = []
        bagian_kode: list[str] = []

        for rel_path in info["files"]:
            file_asal = ROOT / rel_path
            if not file_asal.exists():
                print(f"[LEWATI] File tidak ditemukan: {rel_path}")
                continue

            isi = file_asal.read_text(encoding="utf-8")
            future_lines, isi_bersih = bersihkan_import_internal(isi)
            semua_future.extend(future_lines)

            pembatas = "#" * 70
            bagian_kode.append(
                f"{pembatas}\n# SUMBER: {rel_path}\n{pembatas}\n{isi_bersih}\n"
            )

        header = [f'"""{info["judul"]}."""']
        if semua_future:
            header.extend(dict.fromkeys(semua_future))

        konten_final = "\n".join(header) + "\n\n" + "\n".join(bagian_kode)
        target = OUTPUT_DIR / nama_output
        target.write_text(konten_final, encoding="utf-8")
        print(f"[OK] Dibuat: {target.relative_to(ROOT)}")


if __name__ == "__main__":
    bangun_file_pertemuan()