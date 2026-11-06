from pathlib import Path
from openpyxl import load_workbook


def load_excel_config(file_path):
    """
    Load configuration data from an Excel workbook.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    if file_path.suffix.lower() not in [".xlsx", ".xlsm"]:
        raise ValueError("Configuration file must be an Excel workbook.")

    workbook = load_workbook(
        filename=file_path,
        data_only=True
    )

    return workbook


def get_sheet_names(workbook):
    """
    Return all sheet names in the workbook.
    """

    return workbook.sheetnames
