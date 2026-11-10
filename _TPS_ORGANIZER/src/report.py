from pathlib import Path
from datetime import datetime
import csv

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def generate_report(work_dir, results, status, message):
    """
    Membuat laporan proses dalam format CSV.
    """

    log_folder = Path(work_dir) / "_LOGS"
    log_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = log_folder / f"Laporan_{timestamp}.csv"

    with open(
        report_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file, delimiter=";")

        writer.writerow([
            "STATUS PROSES",
            "PESAN PROSES",
            "STATUS FILE",
            "FILE SUMBER",
            "NOMOR TPS",
            "JENIS DOKUMEN",
            "LOKASI OUTPUT"
        ])

        if not results:
            writer.writerow([
                status,
                message,
                "-",
                "-",
                "-",
                "-",
                "-"
            ])

        for item in results:
            file_status = item.get(
                "status",
                "BERHASIL"
            )

            writer.writerow([
                status,
                message,
                file_status,
                item.get("source", "-"),
                item.get("tps", "-"),
                item.get("document", "-"),
                item.get("output", item.get("message", "-"))
            ])

    return report_path


def generate_excel_report(work_dir, results, status, message, timestamp):
    """
    Membuat laporan proses dalam format Excel.
    """

    log_folder = Path(work_dir) / "_LOGS"
    log_folder.mkdir(parents=True, exist_ok=True)

    report_path = log_folder / f"Laporan_{timestamp}.xlsx"

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Laporan Proses"

    headers = [
        "STATUS PROSES",
        "PESAN PROSES",
        "STATUS FILE",
        "FILE SUMBER",
        "NOMOR TPS",
        "JENIS DOKUMEN",
        "LOKASI OUTPUT"
    ]

    sheet.append(headers)

    if not results:
        sheet.append([
            status, message, "-", "-", "-", "-", "-"
        ])

    for item in results:
        sheet.append([
            status,
            message,
            item.get("status", "BERHASIL"),
            item.get("source", "-"),
            item.get("tps", "-"),
            item.get("document", "-"),
            item.get("output", item.get("message", "-"))
        ])

    # Format header
    for cell in sheet[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="E31E24"
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # Format isi tabel
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(
                vertical="center"
            )

    # Aktifkan filter dan freeze header
    sheet.auto_filter.ref = sheet.dimensions
    sheet.freeze_panes = "A2"

    # Sesuaikan lebar kolom
    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )

        column_letter = get_column_letter(
            column[0].column
        )

        sheet.column_dimensions[column_letter].width = min(
            max(max_length + 3, 15),
            60
        )

    sheet.row_dimensions[1].height = 25

    workbook.save(report_path)

    return report_path

