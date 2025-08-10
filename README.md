# PDF Dark Mode Converter & Merger - Complete Setup

## 🎯 Using Your Own Icon

### Easy Setup with Your Favicon:

1. **Put your favicon** in the same folder as the other files

   - Supported formats: `.ico`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`
   - Supported names: `favicon.ico`, `favicon.png`, `icon.png`, etc.

2. **Run the build script** - it will automatically use your favicon!

## 🚀 Quick Build Options

### Option 1: Automatic Build with Your Icon (Windows)

1. **Download all files** to a folder
2. **Add your favicon file** (favicon.ico, favicon.png, etc.) to the same folder
3. **Double-click `build_app.bat`**
4. **Your app uses your icon!** Find `PDF-DarkMode-Converter.exe` in `dist/`

### Option 2: Manual Build with Your Icon

```bash
# 1. Convert your favicon to ICO format
python convert_favicon.py

# 2. Install dependencies
pip install PyMuPDF==1.23.14 Pillow==10.1.0 pyinstaller

# 3. Build executable
pyinstaller --onefile --windowed --name="PDF-DarkMode-Converter" --icon="app_icon.ico" main.py
```

## 📁 Required Files + Your Icon

Put these files in your folder:

- `main.py` - Main application code
- `convert_favicon.py` - Converts your favicon to ICO format
- `create_icon.py` - Backup icon generator (if no favicon found)
- `build_app.bat` - Automatic build script (Windows)
- **`favicon.ico`** or **`favicon.png`** - **YOUR ICON FILE** ⭐

## 🔄 Icon Conversion Process

The `convert_favicon.py` script automatically:

- ✅ **Finds your favicon** (supports multiple formats)
- ✅ **Converts to ICO format** (required for Windows apps)
- ✅ **Creates multiple sizes** (16x16 up to 256x256)
- ✅ **Handles transparency** properly
- ✅ **Works with any size** favicon

### Supported Favicon Files:

- `favicon.ico` (ready to use)
- `favicon.png` (most common)
- `favicon.jpg`, `favicon.jpeg`
- `favicon.gif`, `favicon.bmp`
- `icon.png`, `icon.jpg`, `icon.ico`

## 🎯 What You Get

After building with your favicon:

- **`PDF-DarkMode-Converter.exe`** with **YOUR CUSTOM ICON**
- **Professional appearance** with your branding
- **No Python required** to run
- **Portable .exe file** works anywhere

## 🖥️ How to Use the App

1. **Double-click** `PDF-DarkMode-Converter.exe` (with your icon!)
2. **Select PDF files** to process
3. **Choose operation**:
   - **Convert to Dark Mode**: White→Black, Black→White
   - **Merge PDFs**: Combine multiple files
   - **Convert & Merge**: Do both at once
4. **Processing complete** - files saved to your location

## 🎨 App Features

✅ **YOUR Custom Icon** - Uses your favicon automatically  
✅ **Standalone Executable** - No Python needed  
✅ **Dark Theme UI** - Professional interface  
✅ **Batch Processing** - Multiple files at once  
✅ **Real-time Progress** - See conversion status  
✅ **Simple & Fast** - Just click and convert

## 🛠️ Icon Troubleshooting

**Icon not showing?**

- Make sure favicon file is in the same folder as other scripts
- Supported formats: ICO, PNG, JPG, GIF, BMP
- Try renaming to `favicon.png` or `favicon.ico`
- Run `python convert_favicon.py` manually to see what happens

**Icon looks blurry?**

- Use a high-resolution favicon (at least 64x64 pixels)
- PNG format usually gives best results
- Square images work best

## 📦 Final Result

Your built app will have:

- ✨ **Your custom icon** in the taskbar, window title, and exe file
- 🚀 **Professional appearance** with your branding
- 💼 **Complete portability** - share the .exe with anyone
- 🎯 **No installation needed** - just double-click to run

Perfect for creating a branded PDF conversion tool with your own visual identity!
