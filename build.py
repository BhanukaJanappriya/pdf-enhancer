#!/usr/bin/env python3
"""
Build script for PDF Dark Mode Converter
Creates a standalone executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_directories():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"Removed {spec_file}")

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = Path('app_icon.ico')
    if not icon_path.exists():
        print("Creating default icon...")
        # In a real implementation, you'd want a proper .ico file
        # For now, we'll create a placeholder
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            img = Image.new('RGB', (64, 64), color='#0078D4')
            draw = ImageDraw.Draw(img)
            
            # Draw a simple PDF icon representation
            draw.rectangle([10, 15, 54, 50], fill='white', outline='black', width=2)
            draw.polygon([(44, 15), (54, 15), (54, 25), (44, 25)], fill='#CCCCCC')
            draw.line([(15, 25), (40, 25)], fill='black', width=1)
            draw.line([(15, 30), (35, 30)], fill='black', width=1)
            draw.line([(15, 35), (45, 35)], fill='black', width=1)
            
            # Save as ICO
            img.save('app_icon.ico', format='ICO')
            print("Created app_icon.ico")
            
        except ImportError:
            print("PIL not available for icon creation. Using default.")
            # Create empty icon file
            icon_path.touch()

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("Building PDF Dark Mode Converter executable...")
    
    # PyInstaller command with optimized settings
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single file executable
        '--windowed',                   # No console window
        '--name=PDFDarkConverter',      # Output name
        '--icon=app_icon.ico',          # Application icon
        '--add-data=app_icon.ico;.',    # Include icon in bundle
        '--hidden-import=PIL._tkinter_finder',  # Ensure PIL works
        '--hidden-import=pkg_resources.py2_warn',
        '--collect-data=customtkinter', # Include CustomTkinter data
        '--collect-binaries=pdf2image', # Include pdf2image binaries
        '--collect-binaries=cv2',       # Include OpenCV binaries
        '--distpath=release',           # Output directory
        '--workpath=temp_build',        # Temporary build directory
        '--specpath=build_specs',       # Spec file location
        'main.py'                       # Main script
    ]
    
    # Additional options for Windows
    if sys.platform == 'win32':
        cmd.extend([
            '--version-file=version_info.txt',  # Version info (if exists)
            '--uac-admin'                       # Request admin privileges if needed
        ])
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        
        # Get the output file path
        if sys.platform == 'win32':
            exe_name = 'PDFDarkConverter.exe'
        else:
            exe_name = 'PDFDarkConverter'
        
        output_path = Path('release') / exe_name
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\nExecutable created: {output_path}")
            print(f"File size: {size_mb:.1f} MB")
            
            return output_path
        else:
            print("Warning: Expected executable not found!")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Installing PDF Dark Mode Converter...

set "INSTALL_DIR=%PROGRAMFILES%\\PDFDarkConverter"
set "DESKTOP=%USERPROFILE%\\Desktop"
set "STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"

:: Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy executable
copy "PDFDarkConverter.exe" "%INSTALL_DIR%\\PDFDarkConverter.exe"

:: Create desktop shortcut
echo [InternetShortcut] > "%DESKTOP%\\PDF Dark Converter.url"
echo URL=file:///%INSTALL_DIR:\=/%/PDFDarkConverter.exe >> "%DESKTOP%\\PDF Dark Converter.url"
echo IconFile=%INSTALL_DIR%\\PDFDarkConverter.exe >> "%DESKTOP%\\PDF Dark Converter.url"
echo IconIndex=0 >> "%DESKTOP%\\PDF Dark Converter.url"

:: Create start menu shortcut
if not exist "%STARTMENU%\\PDF Tools" mkdir "%STARTMENU%\\PDF Tools"
copy "%DESKTOP%\\PDF Dark Converter.url" "%STARTMENU%\\PDF Tools\\PDF Dark Converter.url"

echo Installation complete!
echo You can now run PDF Dark Mode Converter from:
echo - Desktop shortcut
echo - Start Menu ^> PDF Tools
echo - Directly from: %INSTALL_DIR%\\PDFDarkConverter.exe

pause
'''
    
    with open('install.bat', 'w') as f:
        f.write(installer_content)
    
    print("Created install.bat installer script")

def optimize_executable(exe_path):
    """Optimize the executable (Windows-specific)"""
    if sys.platform == 'win32' and exe_path and exe_path.exists():
        try:
            # Try to use UPX if available (optional compression)
            upx_result = subprocess.run(['upx', '--check', str(exe_path)], 
                                      capture_output=True)
            if upx_result.returncode == 0:
                print("Compressing executable with UPX...")
                compress_result = subprocess.run(['upx', '--best', str(exe_path)], 
                                               capture_output=True, text=True)
                if compress_result.returncode == 0:
                    print("Executable compressed successfully")
                    print(compress_result.stdout)
                else:
                    print("UPX compression failed, but executable is still functional")
            else:
                print("UPX not available, skipping compression")
        except FileNotFoundError:
            print("UPX not found in PATH, skipping compression")
        except Exception as e:
            print(f"Optimization failed: {e}")

def create_version_info():
    """Create version info file for Windows executable"""
    version_info = '''# UTF-8
#
# Version info for PDF Dark Mode Converter
#
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'PDF Tools'),
        StringStruct(u'FileDescription', u'PDF Dark Mode Converter & Merger'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'PDFDarkConverter'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024'),
        StringStruct(u'OriginalFilename', u'PDFDarkConverter.exe'),
        StringStruct(u'ProductName', u'PDF Dark Mode Converter'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    
    print("Created version_info.txt")

def create_readme():
    """Create README file for distribution"""
    readme_content = '''# PDF Dark Mode Converter & Merger

A modern desktop application that converts PDF documents from light theme to dark theme and merges multiple PDF files.

## Features

- **Dark Mode Conversion**: Converts white backgrounds to black and black text to white
- **Intelligent Color Processing**: Preserves colored elements while inverting backgrounds
- **PDF Merging**: Combine multiple PDF files into a single document
- **Batch Processing**: Process multiple files at once
- **Modern UI**: Clean, dark-themed interface
- **Cross-platform**: Works on Windows, macOS, and Linux

## Usage

### Converting PDFs to Dark Mode
1. Click "Add PDF Files" to select your PDF documents
2. Choose your output directory
3. Click "Convert to Dark Mode"
4. Your converted dark-theme PDFs will be saved with "_dark" suffix

### Merging PDFs
1. Add the PDF files you want to merge
2. Arrange them in the desired order
3. Click "Merge PDFs" to combine them into one document

### Convert and Merge
1. Add multiple PDF files
2. Click "Convert & Merge" to convert all files to dark theme and merge them

## System Requirements

- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- PDF files for processing

## Supported Formats

- Input: PDF files (.pdf)
- Output: PDF files with dark theme applied

## Troubleshooting

### Common Issues

**"Failed to analyze PDF"**
- The PDF file may be corrupted or password-protected
- Try with a different PDF file

**"Processing failed"**
- Ensure you have enough free disk space
- Check that the output directory is writable
- Very large PDFs may require more processing time

**"Cannot write output file"**
- Check that the output directory exists and is writable
- Ensure the output filename is valid
- Close any applications that might have the output file open

### Performance Tips

- For large PDFs (100+ pages), processing may take several minutes
- Close other applications to free up RAM during processing
- Use an SSD for faster file operations

## Support

For issues and questions, please check:
1. This README file
2. Try with a different PDF file to isolate the issue
3. Ensure your system meets the minimum requirements

## License

This software is provided "as is" without warranty of any kind.
'''
    
    with open('README.txt', 'w') as f:
        f.write(readme_content)
    
    print("Created README.txt")

def main():
    """Main build process"""
    print("=== PDF Dark Mode Converter Build Process ===\n")
    
    # Check if running in correct environment
    try:
        import PyInstaller
    except ImportError:
        print("Error: PyInstaller not installed!")
        print("Please run: pip install pyinstaller")
        return 1
    
    # Step 1: Clean previous builds
    print("1. Cleaning previous build artifacts...")
    clean_build_directories()
    
    # Step 2: Create necessary files
    print("\n2. Creating build files...")
    create_icon()
    create_version_info()
    create_readme()
    
    # Step 3: Build executable
    print("\n3. Building executable...")
    exe_path = build_executable()
    
    if not exe_path:
        print("Build failed!")
        return 1
    
    # Step 4: Optimize executable
    print("\n4. Optimizing executable...")
    optimize_executable(exe_path)
    
    # Step 5: Create installer
    print("\n5. Creating installer script...")
    create_installer_script()
    
    # Step 6: Final summary
    print("\n=== Build Complete ===")
    print(f"Executable: {exe_path}")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"Size: {size_mb:.1f} MB")
    
    print("\nFiles created:")
    print("- release/PDFDarkConverter.exe (main executable)")
    print("- install.bat (installer script)")
    print("- README.txt (user documentation)")
    
    print("\nTo distribute:")
    print("1. Copy PDFDarkConverter.exe to target machine")
    print("2. Optionally, use install.bat for system installation")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())