from pathlib import Path


def generate_folders(
    parent_folder,
    prefix,
    start,
    end,
    digits=3,
    dry_run=True
):
    """
    Generate numbered folders.

    Example:
    TPS 001
    TPS 002
    TPS 003
    """

    parent = Path(parent_folder)

    if not parent.exists():
        raise FileNotFoundError(
            f"Parent folder does not exist: {parent}"
        )

    if not parent.is_dir():
        raise NotADirectoryError(
            f"Parent path is not a directory: {parent}"
        )

    if start < 0 or end < start:
        raise ValueError("Invalid folder numbering range.")

    results = []

    for number in range(start, end + 1):
        folder_name = f"{prefix}{number:0{digits}d}"
        folder_path = parent / folder_name

        if folder_path.exists():
            status = "SKIPPED"
        elif dry_run:
            status = "PREVIEW"
        else:
            folder_path.mkdir(parents=False, exist_ok=False)
            status = "CREATED"

        results.append({
            "folder": str(folder_path),
            "status": status
        })

    return results
