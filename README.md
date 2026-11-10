
# PDF File Organizer Automation

A portable Windows application for automating bulk PDF document organization and page splitting.

Designed for repetitive document processing tasks, especially organizing election documents by polling station (TPS).

## Features

- Automatically detect and sort source PDFs by TPS number.
- Create numbered TPS folders.
- Split multiple PDF files using configurable page ranges.
- Generate standardized output filenames.
- Validate source PDFs before processing.
- Skip invalid PDFs or cancel the entire process.
- Create backups of source documents.
- Generate CSV processing reports.
- Run as a portable Windows application without requiring Python on the user's computer.

## Technology

- Python
- PyInstaller
- pypdf
- Windows Batch Script

## User Workflow

1. Prepare a folder containing source PDFs.
2. Name source files using the format `TPS 1.pdf`, `TPS 2.pdf`, and so on.
3. Run `TPS-ORGANIZER.bat`.
4. Enter the source folder location.
5. Enter the output directory and folder names.
6. Specify the number of TPS.
7. Configure page ranges for five document categories.
8. Review the configuration and confirm processing.
9. Choose whether to create a backup.
10. Retrieve the organized PDF files from the output directory.

## PDF Naming Convention

Source PDF filenames must follow this pattern:

```text
TPS 1.pdf
TPS 2.pdf
TPS 3.pdf
...
```

The application automatically sorts files numerically based on their TPS numbers.

## Document Categories

Each source PDF is split into five document categories:

- PRESIDEN
- DPR RI
- DPD RI
- DPRD PROV
- DPRD KOTA

Page ranges are entered interactively during application execution.

All source PDFs use the same page separation rules for each execution.

## Output Structure

Example:

```text
Output Directory/
│
├── OUTPUT/
│   ├── TPS 001_JREBENG LOR/
│   │   ├── PRESIDEN_001_JREBENG LOR.pdf
│   │   ├── DPR RI_001_JREBENG LOR.pdf
│   │   ├── DPD RI_001_JREBENG LOR.pdf
│   │   ├── DPRD PROV_001_JREBENG LOR.pdf
│   │   └── DPRD KOTA_001_JREBENG LOR.pdf
│   │
│   └── TPS 002_JREBENG LOR/
│       └── ...
│
├── _BACKUP/
│   └── Original source PDFs
│
└── _LOGS/
    └── CSV processing reports
```

## Error Handling

The application validates source PDFs before processing.

If invalid PDFs are detected, users can choose to:

1. Skip invalid PDFs and continue processing.
2. Cancel the entire process.

Invalid files are recorded in the processing report.

## Portable Application

The application is packaged using PyInstaller.

End users only need:

- Windows operating system.
- The distributed application folder.
- Source PDF documents.

Python installation is not required on the end user's computer.

## Build

To create the portable application package:

```text
build_portable.bat
```

The distribution package is generated in the `RELEASE` directory.

## Project Structure

```text
PDF-File-Organizer/
│
├── _TPS_ORGANIZER/
│   ├── app/
│   │   └── start.py
│   └── src/
│       ├── pdf_engine.py
│       └── report.py
│
├── main.py
├── TPS-ORGANIZER.bat
├── build_portable.bat
├── requirements.txt
├── README.md
└── .gitignore
```
