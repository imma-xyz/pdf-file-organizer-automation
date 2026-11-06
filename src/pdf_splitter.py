from pathlib import Path
from pypdf import PdfReader, PdfWriter


def split_pdf(
    source_pdf,
    output_folder,
    output_name,
    start_page,
    end_page,
    dry_run=True
):
    """
    Split a PDF using a specified page range.

    Page numbering starts from 1.
    """

    source = Path(source_pdf)
    destination = Path(output_folder)

    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Source PDF not found: {source}")

    if source.suffix.lower() != ".pdf":
        raise ValueError("Source file must be a PDF.")

    if not isinstance(start_page, int) or not isinstance(end_page, int):
        raise ValueError("Page numbers must be integers.")

    if start_page < 1 or end_page < start_page:
        raise ValueError("Invalid page range.")

    reader = PdfReader(str(source))
    total_pages = len(reader.pages)

    if end_page > total_pages:
        raise ValueError(
            f"Page range exceeds PDF length ({total_pages} pages)."
        )

    if not output_name.lower().endswith(".pdf"):
        output_name += ".pdf"

    output_path = destination / output_name

    if output_path.exists():
        raise FileExistsError(
            f"Output file already exists: {output_path}"
        )

    if dry_run:
        return {
            "status": "PREVIEW",
            "output": str(output_path),
            "pages": f"{start_page}-{end_page}"
        }

    destination.mkdir(parents=True, exist_ok=True)

    writer = PdfWriter()

    for page_number in range(start_page - 1, end_page):
        writer.add_page(reader.pages[page_number])

    with output_path.open("wb") as output_file:
        writer.write(output_file)

    return {
        "status": "CREATED",
        "output": str(output_path),
        "pages": f"{start_page}-{end_page}"
    }
