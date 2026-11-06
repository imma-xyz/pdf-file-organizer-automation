import logging
from pathlib import Path


def setup_logger(log_folder="logs"):
    """
    Configure application logging.
    """

    folder = Path(log_folder)
    folder.mkdir(parents=True, exist_ok=True)

    log_file = folder / "processing.log"

    logger = logging.getLogger("PDFOrganizer")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
