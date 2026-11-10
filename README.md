# TPS-FILE-ORGANIZER

**Automated PDF Document Organizer for Election Administration**

TPS-FILE-ORGANIZER is a Windows-based application designed to automate the organization of election-related PDF documents by polling station (TPS).

It helps users create TPS folders, split PDF files based on specified page ranges, rename documents, and generate processing reports in batches.

The application is built to simplify repetitive document management tasks, especially in administrative environments with basic digital workflows.

## Features

- **Automatic Folder Creation** — Create numbered TPS folders in batches.
- **Batch PDF Processing** — Process multiple PDF documents in one operation.
- **PDF Splitting** — Split PDF files based on user-defined page ranges.
- **Automatic File Renaming** — Apply consistent file naming conventions.
- **Document Classification** — Organize files by election type.
- **Automatic Backup** — Preserve copies of original source documents.
- **Progress Tracking** — Display processing progress in the terminal.
- **Processing Reports** — Generate CSV and formatted Excel reports.
- **Portable Application** — Run the packaged application without installing Python.

## Supported Document Types

The application supports the following election document categories:

- PRESIDEN
- DPR RI
- DPD RI
- DPRD PROV
- DPRD KOTA

## Technology Stack

- Python
- PyPDF
- OpenPyXL
- Colorama
- tqdm
- PyInstaller
- Windows Batch Script

## How It Works

1. Select the source folder containing PDF documents.
2. Specify the output folder.
3. Enter the regional information and number of polling stations.
4. Define the page ranges for each document category.
5. Review the processing plan and confirm.
6. The application creates TPS folders, splits and renames PDF files, and organizes the results.
7. Processing reports are generated in CSV and Excel formats.

## Project Structure

```text
pdf-file-organizer-automation/
├── _TPS_ORGANIZER/
│   ├── app/
│   │   └── start.py
│   ├── src/
│   │   ├── __init__.py
│   │   ├── pdf_engine.py
│   │   └── report.py
│   └── main.py
├── TPS-ORGANIZER.bat
├── build_portable.bat
├── requirements.txt
├── README.md
└── .gitignore
```

## Getting Started

### Run from Source

**Requirements:** Windows and Python 3.10 or later.

1. Clone this repository:

   ```bash
   git clone https://github.com/imma-xyz/pdf-file-organizer-automation.git
   ```

2. Open the project folder:

   ```bash
   cd pdf-file-organizer-automation
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python _TPS_ORGANIZER/main.py
   ```

### Use the Portable Version

The portable application is distributed through **GitHub Releases**.

1. Download the latest `TPS-FILE-ORGANIZER` ZIP package from the Releases section.
2. Extract the entire ZIP file.
3. Open the extracted folder.
4. Run `TPS-FILE-ORGANIZER.bat`.
5. Follow the instructions displayed in the terminal.

The portable version does not require a separate Python installation.

## Build the Portable Application

To build the portable version from source:

1. Install Python and the project dependencies.
2. Run:

   ```text
   build_portable.bat
   ```

3. The packaged application will be generated in the `RELEASE` folder.

The build process uses PyInstaller to package the application and its required runtime files.

## Development Background

This project was developed as a practical automation solution for repetitive document management tasks in election administration.

It demonstrates how Python and freely available tools can be used to improve administrative workflows, reduce manual file handling, and make batch document processing more consistent.

---

**Developed by [imma](https://github.com/imma-xyz)**
