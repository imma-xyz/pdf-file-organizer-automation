from pathlib import Path


def validate_folder_range(start, end):
    """Validate folder numbering range."""

    if not isinstance(start, int) or not isinstance(end, int):
        return False, "Start and end must be integers."

    if start < 0 or end < start:
        return False, "Invalid folder numbering range."

    return True, "Folder range is valid."


def validate_page_range(start_page, end_page, total_pages):
    """Validate PDF page range."""

    if not all(
        isinstance(value, int)
        for value in [start_page, end_page, total_pages]
    ):
        return False, "Page numbers must be integers."

    if start_page < 1:
        return False, "Start page must be at least 1."

    if end_page < start_page:
        return False, "End page cannot be smaller than start page."

    if end_page > total_pages:
        return False, "Page range exceeds the PDF page count."

    return True, "Page range is valid."


def validate_file_path(file_path):
    """Check whether a source file exists."""

    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {path}"

    if not path.is_file():
        return False, f"Path is not a file: {path}"

    return True, "File path is valid."


def validate_action(action):
    """Validate file distribution action."""

    if str(action).strip().upper() not in ["COPY", "MOVE"]:
        return False, "Action must be COPY or MOVE."

    return True, "Action is valid."
