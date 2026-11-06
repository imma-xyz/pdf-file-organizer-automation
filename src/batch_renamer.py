from pathlib import Path


def batch_rename(
    source_folder,
    rename_rules,
    dry_run=True
):
    """
    Rename multiple files based on predefined rules.

    rename_rules example:
    [
        {
            "current_name": "BA 001.pdf",
            "new_name": "BA_001_JREBENG_WETAN.pdf"
        }
    ]
    """

    folder = Path(source_folder)

    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(
            f"Source folder not found: {folder}"
        )

    results = []
    planned_targets = set()

    for rule in rename_rules:
        current_name = rule.get("current_name", "").strip()
        new_name = rule.get("new_name", "").strip()

        if not current_name or not new_name:
            results.append({
                "status": "INVALID",
                "message": "Current name and new name are required."
            })
            continue

        source = folder / current_name
        target = folder / new_name

        if not source.is_file():
            results.append({
                "status": "SKIPPED",
                "message": f"Source file not found: {current_name}"
            })
            continue

        if target.exists() and source.resolve() != target.resolve():
            results.append({
                "status": "SKIPPED",
                "message": f"Target already exists: {new_name}"
            })
            continue

        if target in planned_targets:
            results.append({
                "status": "SKIPPED",
                "message": f"Duplicate target name: {new_name}"
            })
            continue

        planned_targets.add(target)

        if dry_run:
            status = "PREVIEW"
        else:
            source.rename(target)
            status = "RENAMED"

        results.append({
            "status": status,
            "old_name": current_name,
            "new_name": new_name
        })

    return results
