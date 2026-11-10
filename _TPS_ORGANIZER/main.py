from colorama import init, Fore, Style
from pathlib import Path
import re
import shutil

from src.pdf_engine import (
    validate_source_pdfs,
    build_output_plan,
    create_backup,
    create_staging_folder,
    split_all_pdfs,
    publish_output
)

from src.report import (
    generate_report,
    generate_excel_report
)

import builtins

DOCUMENTS = [
    "PRESIDEN",
    "DPR RI",
    "DPD RI",
    "DPRD PROV",
    "DPRD KOTA"
]

INVALID_CHARS = r'[<>:"/\\|?*]'


def print(*args, **kwargs):
    """
    Pewarnaan otomatis setiap baris output terminal.
    """

    sep = kwargs.pop("sep", " ")
    message = sep.join(str(arg) for arg in args)

    if "\033[" in message:
        builtins.print(message, **kwargs)
        return

    colored_lines = []

    for line in message.split("\n"):
        text = line.strip()
        lower = text.lower()

        if not text:
            color = Fore.WHITE

        elif any(word in lower for word in [
            "proses gagal", "gagal", "kesalahan",
            "tidak ditemukan", "tidak dapat",
            "dibatalkan", "tidak memenuhi"
        ]):
            color = Fore.RED + Style.BRIGHT

        elif any(word in lower for word in [
            "peringatan", "dilewati", "alasan:",
            "bertabrakan", "tidak valid",
            "akan diganti", "tidak boleh"
        ]):
            color = Fore.YELLOW

        elif any(word in lower for word in [
            "berhasil", "tersimpan", "dibuat",
            "memenuhi aturan", "pdf valid",
            "pdf terdeteksi", "pdf hasil dibuat",
            "pdf sumber diproses", "folder tps dibuat",
            "total halaman hasil", "akan diproses"
        ]):
            color = Fore.GREEN

        elif (
            set(text) <= {"=", "-"}
            or any(word in lower for word in [
                "tps organizer", "ringkasan",
                "lokasi penyimpanan", "lokasi hasil",
                "pengaturan", "validasi pdf",
                "membaca pdf", "memproses pdf",
                "jumlah halaman dokumen",
                "rentang halaman", "pilihan",
                "daftar pdf", "dokumen",
                "lokasi folder sumber",
                "direktori penyimpanan hasil",
                "nama folder output", "nama wilayah",
                "jumlah tps", "pdf tidak memenuhi aturan"
            ])
            or (
                text.isupper()
                and any(char.isalpha() for char in text)
            )
        ):
            color = Fore.CYAN + Style.BRIGHT

        else:
            color = Fore.WHITE

        colored_lines.append(color + line + Style.RESET_ALL)

    builtins.print(
        "\n".join(colored_lines),
        **kwargs
    )


def input(prompt=""):
    return builtins.input(
        Fore.CYAN + str(prompt) + Style.RESET_ALL
    )



def discover_pdf_files(source_dir):
    """Mendeteksi dan mengurutkan PDF berdasarkan nomor TPS."""

    pdf_files = []
    seen_numbers = {}

    for file_path in Path(source_dir).iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() != ".pdf":
            continue

        match = re.fullmatch(
            r"TPS\s*(\d+)",
            file_path.stem,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        number = int(match.group(1))

        if number in seen_numbers:
            raise ValueError(
                f"Nomor TPS ganda: {seen_numbers[number]} "
                f"dan {file_path.name}"
            )

        seen_numbers[number] = file_path.name

        pdf_files.append({
            "row": 0,
            "filename": file_path.name,
            "source_number": number,
            "path": file_path.resolve()
        })

    pdf_files.sort(
        key=lambda item: item["source_number"]
    )

    for index, item in enumerate(pdf_files, start=1):
        item["row"] = index

    return pdf_files


def ask_directory(message, must_exist=True):
    while True:
        value = input(message).strip()

        # Mendukung path hasil drag-and-drop dari File Explorer
        value = value.strip().strip('"').strip("'")

        if not value:
            print("  Lokasi tidak boleh kosong.")
            continue

        path = Path(value).expanduser()

        if must_exist and not path.is_dir():
            print("  Folder tidak ditemukan.")
            continue

        if not must_exist:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                print(f"  Folder tidak dapat dibuat: {exc}")
                continue

        return path.resolve()


def ask_name(message):
    while True:
        value = input(message).strip().upper()

        if not value:
            print("  Nama tidak boleh kosong.")
            continue

        if (
            re.search(INVALID_CHARS, value)
            or value.endswith((".", " "))
            or value in (".", "..")
        ):
            print("  Nama mengandung karakter yang tidak diperbolehkan.")
            continue

        return value


def ask_integer(message, minimum=1):
    while True:
        value = input(message).strip()

        try:
            number = int(value)

            if number < minimum:
                print(f"  Angka minimal {minimum}.")
                continue

            return number

        except ValueError:
            print("  Masukkan angka bulat.")


def ask_yes_no(message, default="YA"):
    while True:
        value = input(message).strip().upper()

        if not value:
            value = default

        if value in ("YA", "TIDAK"):
            return value

        print("  Masukkan YA atau TIDAK.")


def ask_page_ranges():
    print("\n" + "=" * 65)
    print("                 PENGATURAN RENTANG HALAMAN")
    print("=" * 65)
    print("Tentukan halaman awal dan akhir untuk setiap jenis dokumen.")
    print()
    print(f"{'DOKUMEN':<20}{'HALAMAN AWAL':<20}{'HALAMAN AKHIR'}")
    print("-" * 65)

    rules = []

    for document in DOCUMENTS:
        print(f"\n{document}")

        start = ask_integer("  Halaman awal  : ")
        end = ask_integer("  Halaman akhir : ")

        while end < start:
            print(
                "  Halaman akhir tidak boleh lebih kecil "
                "dari halaman awal."
            )
            end = ask_integer("  Halaman akhir : ")

        rules.append({
            "row": len(rules) + 1,
            "document_name": document,
            "start_page": start,
            "end_page": end,
            "filename_template": (
                "{dokumen}_{tps}_{wilayah}.pdf"
            )
        })

    return rules


def find_overlaps(rules):
    """Mencari rentang halaman yang saling bertabrakan."""

    ranges = sorted(
        [
            (
                rule["start_page"],
                rule["end_page"],
                rule["document_name"]
            )
            for rule in rules
        ],
        key=lambda item: item[0]
    )

    overlaps = []

    for index in range(1, len(ranges)):
        previous = ranges[index - 1]
        current = ranges[index]

        if current[0] <= previous[1]:
            overlaps.append({
                "first": previous,
                "second": current,
                "start": current[0],
                "end": min(previous[1], current[1])
            })

    return overlaps


def edit_page_range(rule):
    """Meminta ulang rentang halaman satu dokumen."""

    print(f"\nEDIT RENTANG: {rule['document_name']}")

    while True:
        start = ask_integer("  Halaman awal  : ")
        end = ask_integer("  Halaman akhir : ")

        if end < start:
            print(
                "  Halaman akhir tidak boleh lebih kecil "
                "dari halaman awal."
            )
            continue

        rule["start_page"] = start
        rule["end_page"] = end

        return


def resolve_page_overlaps(rules):
    """Memperbaiki rentang yang bertabrakan tanpa mengulang semuanya."""

    while True:
        overlaps = find_overlaps(rules)

        if not overlaps:
            print("\nSemua rentang halaman sudah valid.")
            return

        print("\n" + "=" * 55)
        print("         RENTANG HALAMAN BERTABRAKAN")
        print("=" * 55)

        for index, overlap in enumerate(overlaps, start=1):
            first = overlap["first"]
            second = overlap["second"]

            print(f"\n{index}. Ditemukan tabrakan:")
            print(
                f"   {first[2]}       : halaman "
                f"{first[0]}-{first[1]}"
            )
            print(
                f"   {second[2]}      : halaman "
                f"{second[0]}-{second[1]}"
            )
            print(
                f"   Halaman bertabrakan: "
                f"{overlap['start']}-{overlap['end']}"
            )

        document_names = []

        for overlap in overlaps:
            for item in (overlap["first"], overlap["second"]):
                if item[2] not in document_names:
                    document_names.append(item[2])

        print("\nPILIH DOKUMEN YANG INGIN DIPERBAIKI:")

        for index, name in enumerate(document_names, start=1):
            print(f"[{index}] {name}")

        print("[0] Batalkan pengaturan")

        while True:
            choice = input(
                "\nPilih dokumen yang akan diedit: "
            ).strip()

            if choice == "0":
                raise ValueError(
                    "Pengaturan rentang halaman dibatalkan."
                )

            try:
                selected = int(choice)

                if 1 <= selected <= len(document_names):
                    break

            except ValueError:
                pass

            print("Pilihan tidak valid.")

        selected_name = document_names[selected - 1]

        selected_rule = next(
            rule for rule in rules
            if rule["document_name"] == selected_name
        )

        edit_page_range(selected_rule)


def validate_rules(rules):
    errors = []
    ranges = []

    for rule in rules:
        start = rule["start_page"]
        end = rule["end_page"]

        if start < 1:
            errors.append(
                f"{rule['document_name']}: halaman awal minimal 1."
            )

        if end < start:
            errors.append(
                f"{rule['document_name']}: rentang halaman tidak valid."
            )

        ranges.append((
            start,
            end,
            rule["document_name"]
        ))

    ranges.sort()

    for index in range(1, len(ranges)):
        previous = ranges[index - 1]
        current = ranges[index]

        if current[0] <= previous[1]:
            overlap_start = current[0]
            overlap_end = min(previous[1], current[1])

            errors.append(
                f"Rentang {current[2]} halaman "
                f"{current[0]}-{current[1]} bertabrakan dengan "
                f"{previous[2]} halaman "
                f"{previous[0]}-{previous[1]}. "
                f"Halaman yang bertabrakan: "
                f"{overlap_start}-{overlap_end}."
            )

    return errors


def show_errors(errors):
    print("\nDITEMUKAN KESALAHAN:")

    for number, error in enumerate(errors, start=1):
        if isinstance(error, dict):
            print(f"{number}. {error['filename']}")
            print(f"   {error['reason']}")
        else:
            print(f"{number}. {error}")


def save_reports(work_dir, results, status, message):
    try:
        # Membuat laporan CSV
        csv_report = generate_report(
            work_dir,
            results,
            status,
            message
        )

        # Menggunakan timestamp yang sama dengan CSV
        timestamp = csv_report.stem.replace("Laporan_", "")

        # Membuat laporan Excel
        excel_report = generate_excel_report(
            work_dir,
            results,
            status,
            message,
            timestamp
        )

        print(f"Laporan CSV   : {csv_report}")
        print(f"Laporan Excel : {excel_report}")

        return csv_report, excel_report

    except Exception as exc:
        print(f"Laporan tidak dapat dibuat: {exc}")
        return None, None

def process_once():
    staging_root = None
    results = []
    skipped_files = []

    output_directory = Path.cwd()

    print("=" * 55)
    print("                 TPS ORGANIZER")
    print("=" * 55)

    try:
        # 1. LOKASI FOLDER SUMBER PDF
        print("\n[1/8] LOKASI FOLDER SUMBER PDF")

        source_dir = ask_directory(
            "Folder sumber PDF (ketik atau drag & drop folder di sini): "
        )

        # 2. DIREKTORI PENYIMPANAN HASIL
        print("\n[2/8] DIREKTORI PENYIMPANAN HASIL")

        output_directory = ask_directory(
            "Lokasi penyimpanan hasil (ketik atau drag & drop folder di sini): ",
            must_exist=False
        )

        # 3. NAMA FOLDER OUTPUT
        print("\n[3/8] NAMA FOLDER OUTPUT")

        output_name = ask_name(
            "Masukkan nama folder untuk hasil penyimpanan: "
        )

        # 4. NAMA WILAYAH
        print("\n[4/8] NAMA WILAYAH")

        wilayah = ask_name(
            "Masukkan nama wilayah TPS: "
        )

        # 5. JUMLAH TPS
        print("\n[5/8] JUMLAH TPS")

        tps_count = ask_integer(
            "Masukkan jumlah TPS sesuai jumlah file PDF: "
        )

        # 6. MEMBACA PDF SUMBER
        print("\n[6/8] MEMBACA PDF SUMBER")

        files = discover_pdf_files(source_dir)

        print(f"  PDF terdeteksi: {len(files)} file")

        if not files:
            raise ValueError(
                "Tidak ditemukan PDF dengan format nama TPS, "
                "contoh: TPS 1.pdf atau TPS 01.pdf."
            )

        if len(files) != tps_count:
            raise ValueError(
                f"Jumlah TPS yang dimasukkan adalah {tps_count}, "
                f"tetapi PDF yang ditemukan berjumlah {len(files)}."
            )

        # 7. PENGATURAN RENTANG HALAMAN
        print("\n[7/8] PENGATURAN RENTANG HALAMAN")

        rules = ask_page_ranges()

        resolve_page_overlaps(rules)

        rule_errors = validate_rules(rules)

        if rule_errors:
            show_errors(rule_errors)
            raise ValueError(
                "Pengaturan rentang halaman tidak valid."
            )

        print("\nJUMLAH HALAMAN DOKUMEN")
        print("-" * 45)

        total_pages_per_tps = 0

        for rule in rules:
            page_count = (
                rule["end_page"] - rule["start_page"] + 1
            )

            total_pages_per_tps += page_count

            print(
                f"  {rule['document_name']:<12} "
                f"{page_count} halaman"
            )

        print("-" * 45)
        print(f"  Total per TPS : {total_pages_per_tps} halaman")

        # 8. VALIDASI PDF SUMBER
        print("\n[8/8] VALIDASI PDF SUMBER")

        scanned_files, errors = validate_source_pdfs(
            source_dir,
            files,
            rules
        )

        if errors:
            print("\n" + "=" * 55)
            print("              PDF TIDAK MEMENUHI ATURAN")
            print("=" * 55)

            show_errors(errors)

            print("\nPILIHAN:")
            print("[1] Lewati PDF bermasalah dan lanjutkan proses")
            print("[2] Batalkan seluruh proses")

            choice = input("\nMasukkan pilihan (1/2): ").strip()

            if choice != "1":
                skipped_files = errors

                save_reports(
                    output_directory,
                    [
                        {
                            "status": "DILEWATI",
                            "source": item["filename"],
                            "message": item["reason"]
                        }
                        for item in errors
                    ],
                    "DIBATALKAN",
                    "Proses dibatalkan oleh pengguna."
                )

                print("\nProses dibatalkan.")
                return 1

            skipped_files = errors

            if not scanned_files:
                raise ValueError(
                    "Tidak ada PDF valid yang dapat diproses."
                )

            print(
                f"\n{len(skipped_files)} PDF dilewati."
                f"\n{len(scanned_files)} PDF akan diproses."
            )

            print("\nDAFTAR PDF YANG DILEWATI")
            print("-" * 55)

            for index, item in enumerate(skipped_files, start=1):
                print(f"{index}. {item['filename']}")
                print(f"   Alasan: {item['reason']}")

            print("-" * 55)

        else:
            print("\nSemua PDF memenuhi aturan.")

        print(f"\nPDF valid    : {len(scanned_files)}")
        print(f"PDF dilewati : {len(skipped_files)}")

        # RINGKASAN DAN KONFIRMASI
        print("\nRINGKASAN DAN KONFIRMASI")
        print("=" * 55)

        settings = {
            "Nama Wilayah": wilayah,
            "Nama Folder Output": output_name,
            "Jumlah Digit Nomor TPS": 3,
            "Direktori Output": str(output_directory)
        }

        output_plan = build_output_plan(
            settings,
            scanned_files,
            rules,
            source_dir
        )

        output_root = output_plan["output_root"]

        source_resolved = source_dir.resolve()
        output_resolved = output_root.resolve()

        if (
            output_resolved == source_resolved
            or source_resolved.is_relative_to(output_resolved)
        ):
            raise ValueError(
                "Lokasi output tidak boleh sama dengan folder sumber "
                "atau menjadi folder induk dari folder sumber."
            )

        if output_root.exists() and not output_root.is_dir():
            raise ValueError(
                "Lokasi output sudah digunakan oleh sebuah file."
            )

        total_output_pages = sum(
            output_info["end_page"] - output_info["start_page"] + 1
            for item in output_plan["items"]
            for output_info in item["output_files"]
        )

        total_outputs = sum(
            len(item["output_files"])
            for item in output_plan["items"]
        )

        print("\nFolder sumber  :", source_dir)
        print("Direktori hasil:", output_directory)
        print("Nama wilayah   :", wilayah)
        print("Folder output  :", output_name)
        print("Jumlah TPS     :", tps_count)

        print("\nRentang halaman:")

        for rule in rules:
            page_count = (
                rule["end_page"] - rule["start_page"] + 1
            )

            print(
                f"  {rule['document_name']:<12} "
                f"{rule['start_page']} - {rule['end_page']} "
                f"({page_count} halaman)"
            )

        print("\nRINGKASAN HASIL YANG AKAN DIBUAT")
        print("-" * 55)
        print(f"  PDF sumber diproses : {len(scanned_files)}")
        print(f"  PDF sumber dilewati : {len(skipped_files)}")

        if skipped_files:
            print("\n  DAFTAR PDF YANG DILEWATI:")

            for index, item in enumerate(skipped_files, start=1):
                print(f"  {index}. {item['filename']}")

        print()
        print(f"  Folder TPS dibuat   : {len(output_plan['items'])}")
        print(f"  PDF hasil dibuat    : {total_outputs}")
        print(f"  Total halaman hasil : {total_output_pages}")
        print("-" * 55)

        print("\nLokasi hasil:", output_root)

        if output_root.exists():
            print(
                "\nPERINGATAN: Folder output sudah ada."
                "\nFolder tersebut akan diganti dengan hasil baru."
            )

        backup_choice = ask_yes_no(
            "\nBuat backup PDF sumber? (YA/TIDAK) [YA]: "
        )

        confirmation = ask_yes_no(
            "Lanjutkan proses? (YA/TIDAK): "
        )

        if confirmation != "YA":
            print("\nProses dibatalkan.")

            save_reports(
                output_directory,
                [],
                "DIBATALKAN",
                "Proses dibatalkan oleh pengguna."
            )

            return 1

        # PEMROSESAN PDF
        print("\n" + "=" * 55)
        print("                  MEMPROSES PDF")
        print("=" * 55)

        if backup_choice == "YA":
            backup_folder = create_backup(
                scanned_files,
                output_directory
            )

            print(f"Backup tersimpan: {backup_folder}")

        else:
            print("Backup tidak diaktifkan.")

        staging_root = create_staging_folder(
            output_directory
        )

        results = split_all_pdfs(
            scanned_files,
            output_plan,
            staging_root
        )

        print(f"PDF hasil dibuat: {len(results)}")

        publish_output(
            staging_root,
            output_root
        )

        staging_root = None

        # Mencatat PDF yang dilewati.
        for item in skipped_files:
            results.append({
                "status": "DILEWATI",
                "source": item["filename"],
                "message": item["reason"]
            })

        save_reports(
            output_directory,
            results,
            "BERHASIL",
            (
                f"{len(scanned_files)} PDF diproses; "
                f"{len(skipped_files)} PDF dilewati."
            )
        )

        
        print("\n" + "=" * 55)
        print("              PROSES BERHASIL!")
        print("=" * 55)

        print("\nRINGKASAN HASIL")
        print("-" * 55)

        print(f"  PDF sumber diproses : {len(scanned_files)}")
        print(f"  PDF sumber dilewati : {len(skipped_files)}")

        if skipped_files:
            print("\n  DAFTAR PDF YANG DILEWATI:")

            for index, item in enumerate(skipped_files, start=1):
                print(f"  {index}. {item['filename']}")
                print(f"     Alasan: {item['reason']}")

        print()
        print(f"  Folder TPS dibuat   : {len(output_plan['items'])}")
        print(f"  PDF hasil dibuat    : {len(results) - len(skipped_files)}")
        print(f"  Total halaman hasil : {total_output_pages}")

        print("-" * 55)

        print("\nLOKASI PENYIMPANAN")
        print(f"  Hasil   : {output_root}")
        print(f"  Backup  : {output_directory / '_BACKUP'}")

        print("=" * 55)


        return 0

    except Exception as exc:
        message = str(exc)

        print("\n" + "=" * 55)
        print("               PROSES GAGAL!")
        print("=" * 55)
        print(f"Detail: {message}")

        save_reports(
            output_directory,
            results,
            "GAGAL",
            message
        )

        return 1

    finally:
        if staging_root and staging_root.exists():
            shutil.rmtree(
                staging_root,
                ignore_errors=True
            )


def main():
    init(autoreset=True)

    while True:
        process_once()

        print("\n" + "=" * 55)
        print("             TPS ORGANIZER")
        print("=" * 55)
        print("\nApakah ingin memproses dokumen lain?")
        print("[Y] Ya, proses lagi")
        print("[T] Tidak, keluar dari aplikasi")

        while True:
            choice = input("\nPilihan (Y/T): ").strip().upper()

            if choice == "Y":
                print("\nMemulai proses baru...\n")
                break

            elif choice == "T":
                print("\nTerima kasih telah menggunakan TPS ORGANIZER.")
                return 0

            else:
                print("Pilihan tidak valid. Masukkan Y atau T.")


if __name__ == "__main__":
    raise SystemExit(main())
