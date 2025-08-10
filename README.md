# PDF Dark Mode Converter & Merger - Setup Instructions

## Quick Setup

### 1. Install Python Dependencies

```bash
pip install PyMuPDF==1.23.14 Pillow==10.1.0
```

### 2. Run the Application

```bash
python main.py
```

## Building Standalone Executable

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Create Executable

```bash
pyinstaller --onefile --windowed --name="PDF-DarkMode-Converter" main.py
```

The executable will be created in the `dist/` folder.

## How to Use

1. **Launch the application** - Run the Python script or the executable
2. **Select PDF files** - Click "Select PDF Files" to choose one or more PDFs
3. **Choose an action**:
   - **Convert to Dark Mode**: Converts selected PDFs to dark theme (white→black, black→white)
   - **Merge PDFs**: Combines selected PDFs into one file
   - **Convert & Merge**: Converts all PDFs to dark mode, then merges them into one file

## Features

- **Simple Dark Mode Conversion**: Converts white backgrounds to black, black text to white
- **Batch Processing**: Handle multiple PDF files at once
- **PDF Merging**: Combine multiple PDFs into a single document
- **Progress Tracking**: Real-time progress updates during processing
- **Dark Theme UI**: Modern dark interface that matches the output PDFs

## Technical Details

- Uses **PyMuPDF (fitz)** for PDF manipulation
- Uses **Pillow (PIL)** for image processing and color inversion
- **Threading** for non-blocking UI during processing
- Simple pixel-level color inversion algorithm
- Temporary file management for convert & merge operations

## File Structure

```
pdf-darkmode-converter/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended for large PDFs)
- **Storage**: 100MB free space plus space for processed files

## Troubleshooting

### Common Issues:

1. **Large files taking too long**: The app processes files at high quality - larger PDFs may take several minutes
2. **Memory errors**: Close other applications and try processing files one at a time
3. **Permission errors**: Ensure you have write permissions to the output directory

### Performance Tips:

- Process smaller batches of files for better performance
- Ensure sufficient disk space (processed files can be larger than originals)
- Close unnecessary applications to free up memory
