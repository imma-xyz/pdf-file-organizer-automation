
from pathlib import Path
from datetime import datetime
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm
import os
import re
import shutil
import tempfile


INVALID_CHARS = r'[<>:"/\\|?*]'


def validate_source_pdfs(work_dir, files, rules):
    work_dir = Path(work_dir)

    scanned_files = []
    errors = []

    max_page = max(rule["end_page"] for rule in rules)

    for item in files:
        file_path = work_dir / item["filename"]

        if not file_path.exists():
            errors.append({
                "filename": item["filename"],
                "reason": "File tidak ditemukan."
            })
            continue

        try:
            reader = PdfReader(str(file_path))

            if reader.is_encrypted:
                errors.append({
                    "filename": item["filename"],
                    "reason": "PDF terenkripsi."
                })
                continue

            total_pages = len(reader.pages)

            if total_pages < max_page:
                errors.append({
                    "filename": item["filename"],
                    "reason": (
                        f"Hanya memiliki {total_pages} halaman. "
                        f"Aturan membutuhkan sampai halaman {max_page}."
                    )
                })
                continue

            scanned_files.append({
                **item,
                "path": file_path,
                "total_pages": total_pages
            })

        except Exception as exc:
            errors.append({
                "filename": item["filename"],
                "reason": f"Gagal membaca PDF: {exc}"
            })

    return scanned_files, errors


def build_output_plan(settings, files, rules, work_dir):
    """
    Menentukan struktur folder hasil berdasarkan pengaturan pengguna.
    Nomor TPS mengikuti nomor pada nama PDF sumber.
    """

    wilayah = str(settings["Nama Wilayah"]).strip()
    output_name = str(settings["Nama Folder Output"]).strip()

    output_directory = Path(
        settings["Direktori Output"]
    ).expanduser().resolve()

    digits = int(settings.get("Jumlah Digit Nomor TPS", 3))

    output_root = output_directory / output_name

    plan = []
    used_folder_names = set()

    for file_data in files:
        source_number = file_data.get("source_number")

        if source_number is None:
            match = re.fullmatch(
                r"TPS\s*(\d+)",
                Path(file_data["filename"]).stem,
                flags=re.IGNORECASE
            )

            if not match:
                raise ValueError(
                    f"Nomor TPS tidak dapat dibaca: {file_data['filename']}"
                )

            source_number = int(match.group(1))

        tps = str(source_number).zfill(digits)
        folder_name = f"TPS {tps}_{wilayah}"

        if (
            re.search(INVALID_CHARS, folder_name)
            or folder_name.endswith((".", " "))
            or folder_name.lower() in used_folder_names
        ):
            raise ValueError(
                f"Nama folder TPS tidak valid atau duplikat: {folder_name}"
            )

        used_folder_names.add(folder_name.lower())

        output_files = []
        used_file_names = set()

        for rule in rules:
            filename = rule["filename_template"].format(
                dokumen=rule["document_name"],
                tps=tps,
                wilayah=wilayah
            )

            if (
                not filename
                or Path(filename).name != filename
                or re.search(INVALID_CHARS, filename)
                or filename.endswith((".", " "))
                or not filename.lower().endswith(".pdf")
            ):
                raise ValueError(
                    f"Nama file hasil tidak valid: {filename}"
                )

            if filename.lower() in used_file_names:
                raise ValueError(
                    f"Nama file hasil duplikat: {filename}"
                )

            used_file_names.add(filename.lower())

            output_files.append({
                "document": rule["document_name"],
                "filename": filename,
                "start_page": int(rule["start_page"]),
                "end_page": int(rule["end_page"])
            })

        plan.append({
            "tps": tps,
            "source_number": source_number,
            "folder_name": folder_name,
            "source": file_data["path"],
            "output_files": output_files
        })

    return {
        "output_root": output_root,
        "output_directory": output_directory,
        "items": plan
    }


def create_backup(scanned_files, output_directory):
    """
    Membuat backup PDF sumber di direktori output.
    """

    backup_root = Path(output_directory) / "_BACKUP"
    backup_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    backup_folder = backup_root / timestamp
    temporary_folder = backup_root / f".{timestamp}.tmp"

    temporary_folder.mkdir()

    try:
        for item in scanned_files:
            shutil.copy2(
                item["path"],
                temporary_folder / item["filename"]
            )

        os.replace(temporary_folder, backup_folder)

    except Exception:
        shutil.rmtree(temporary_folder, ignore_errors=True)
        raise

    return backup_folder


def create_staging_folder(output_directory):
    """
    Membuat folder sementara di direktori output.
    """

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    return Path(
        tempfile.mkdtemp(
            prefix=".TPS_ORGANIZER_TEMP_",
            dir=output_directory
        )
    )


def split_all_pdfs(scanned_files, output_plan, staging_root):
    """
    Memisahkan seluruh PDF ke folder sementara.
    """

    results = []

    for item in tqdm(
        output_plan["items"],
        desc="Memproses TPS",
        unit="TPS",
        dynamic_ncols=True
    ):
        tps = item["tps"]
        target_folder = staging_root / item["folder_name"]
        target_folder.mkdir()

        reader = PdfReader(
            str(item["source"]),
            strict=False
        )

        for output_info in item["output_files"]:
            writer = PdfWriter()

            start = output_info["start_page"]
            end = output_info["end_page"]

            for page_number in range(start - 1, end):
                writer.add_page(reader.pages[page_number])

            target_file = target_folder / output_info["filename"]
            temporary_file = target_folder / (
                output_info["filename"] + ".tmp"
            )

            try:
                with open(temporary_file, "wb") as file:
                    writer.write(file)

                os.replace(temporary_file, target_file)

            except Exception:
                if temporary_file.exists():
                    temporary_file.unlink()
                raise

            results.append({
                "source": item["source"].name,
                "tps": tps,
                "document": output_info["document"],
                "output": str(
                    output_plan["output_root"]
                    / item["folder_name"]
                    / output_info["filename"]
                )
            })

    return results


def publish_output(staging_root, output_root):
    """
    Memindahkan hasil dari folder sementara ke folder tujuan.
    """

    output_root = Path(output_root)
    staging_root = Path(staging_root)

    if output_root.exists():
        shutil.rmtree(output_root)

    os.replace(staging_root, output_root)
