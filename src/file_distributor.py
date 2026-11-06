from pathlib import Path
import shutil


def distribute_file(
    source_file,
    target_folder,
    action="COPY",
    dry_run=True
):
    """
    Copy or move a file to a designated folder.
    """

    source = Path(source_file)
    destination = Path(target_folder)
    action = action.strip().upper()

    if not source.exists() or not source.is_file():
        raise FileNotFoundError(
            f"Source file not found: {source}"
        )

    if action not in ["COPY", "MOVE"]:
        raise ValueError("Action must be COPY or MOVE.")

    target_path = destination / source.name

    if target_path.exists():
        raise FileExistsError(
            f"Target file already exists: {target_path}"
        )

    if dry_run:
        return {
            "status": "PREVIEW",
            "action": action,
            "source": str(source),
            "destination": str(target_path)
        }

    destination.mkdir(parents=True, exist_ok=True)

    if action == "COPY":
        shutil.copy2(source, target_path)
    else:
        shutil.move(str(source), str(target_path))

    return {
        "status": "SUCCESS",
        "action": action,
        "source": str(source),
        "destination": str(target_path)
    }
