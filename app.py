#!/usr/bin/env python3
"""
PDF Dark Mode Converter & Merger
A modern desktop application for converting PDFs to dark theme and merging documents.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
import threading
from typing import List, Optional, Tuple
import queue
import os
import sys
from dataclasses import dataclass
from enum import Enum

# PDF Processing imports
try:
    import pypdf
    from PIL import Image, ImageOps
    import pdf2image
    import numpy as np
    import cv2
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError as e:
    print(f"Required library missing: {e}")
    print("Please install: pip install pypdf pillow pdf2image numpy opencv-python customtkinter")
    sys.exit(1)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ConversionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"

@dataclass
class PDFFile:
    """Represents a PDF file in the processing queue"""
    path: Path
    name: str
    size: int
    pages: int
    status: ConversionStatus = ConversionStatus.PENDING
    error_message: str = ""
    output_path: Optional[Path] = None

class PDFProcessor:
    """Core PDF processing functionality"""
    
    def __init__(self):
        self.progress_callback = None
        self.cancel_requested = False
    
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def cancel_processing(self):
        """Request cancellation of current processing"""
        self.cancel_requested = True
    
    def analyze_pdf(self, file_path: Path) -> Tuple[int, bool]:
        """Analyze PDF to get page count and detect if conversion is needed"""
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                page_count = len(reader.pages)
                
                # Simple heuristic: assume conversion needed for all PDFs
                # In a full implementation, this would analyze colors
                needs_conversion = True
                
                return page_count, needs_conversion
        except Exception as e:
            raise Exception(f"Failed to analyze PDF: {str(e)}")
    
    def convert_pdf_to_dark(self, input_path: Path, output_path: Path) -> bool:
        """Convert a PDF to dark theme"""
        try:
            if self.cancel_requested:
                return False
            
            # Method 1: Try direct color inversion (for vector-based PDFs)
            if self._try_vector_conversion(input_path, output_path):
                return True
            
            # Method 2: Fallback to image-based conversion
            return self._image_based_conversion(input_path, output_path)
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error: {str(e)}")
            return False
    
    def _try_vector_conversion(self, input_path: Path, output_path: Path) -> bool:
        """Attempt vector-based color inversion"""
        try:
            with open(input_path, 'rb') as input_file:
                reader = pypdf.PdfReader(input_file)
                writer = pypdf.PdfWriter()
                
                total_pages = len(reader.pages)
                
                for i, page in enumerate(reader.pages):
                    if self.cancel_requested:
                        return False
                    
                    # Progress update
                    if self.progress_callback:
                        progress = (i + 1) / total_pages * 100
                        self.progress_callback(f"Processing page {i+1}/{total_pages} ({progress:.0f}%)")
                    
                    # Apply color inversion to page content
                    modified_page = self._invert_page_colors(page)
                    writer.add_page(modified_page)
                
                # Write the output
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True
                
        except Exception as e:
            print(f"Vector conversion failed: {e}")
            return False
    
    def _invert_page_colors(self, page):
        """Invert colors in a PDF page (simplified implementation)"""
        # This is a simplified version. A full implementation would:
        # 1. Parse the page's content stream
        # 2. Identify color operations (rg, RG, k, K, etc.)
        # 3. Invert color values appropriately
        # 4. Handle different color spaces (RGB, CMYK, Gray)
        
        # For now, we'll return the page as-is and rely on image-based conversion
        return page
    
    def _image_based_conversion(self, input_path: Path, output_path: Path) -> bool:
        """Convert PDF using image-based approach"""
        try:
            # Convert PDF to images
            if self.progress_callback:
                self.progress_callback("Converting PDF to images...")
            
            images = pdf2image.convert_from_path(
                input_path,
                dpi=200,  # High quality conversion
                fmt='RGB'
            )
            
            inverted_images = []
            total_pages = len(images)
            
            for i, img in enumerate(images):
                if self.cancel_requested:
                    return False
                
                # Progress update
                if self.progress_callback:
                    progress = (i + 1) / total_pages * 100
                    self.progress_callback(f"Inverting colors page {i+1}/{total_pages} ({progress:.0f}%)")
                
                # Convert PIL Image to numpy array
                img_array = np.array(img)
                
                # Apply intelligent color inversion
                inverted_array = self._smart_color_inversion(img_array)
                
                # Convert back to PIL Image
                inverted_img = Image.fromarray(inverted_array)
                inverted_images.append(inverted_img)
            
            # Convert images back to PDF
            if self.progress_callback:
                self.progress_callback("Saving converted PDF...")
            
            if inverted_images:
                inverted_images[0].save(
                    output_path,
                    "PDF",
                    resolution=200.0,
                    save_all=True,
                    append_images=inverted_images[1:] if len(inverted_images) > 1 else []
                )
            
            return True
            
        except Exception as e:
            print(f"Image-based conversion failed: {e}")
            return False
    
    def _smart_color_inversion(self, img_array: np.ndarray) -> np.ndarray:
        """Apply intelligent color inversion"""
        # Convert to float for processing
        img_float = img_array.astype(np.float32) / 255.0
        
        # Detect predominantly white areas (background)
        grayscale = np.mean(img_float, axis=2)
        white_mask = grayscale > 0.85  # Threshold for "white" areas
        
        # Invert colors
        inverted = 1.0 - img_float
        
        # For areas that aren't predominantly white or black, preserve some colors
        # This is a simplified heuristic - could be much more sophisticated
        color_variance = np.std(img_float, axis=2)
        colored_areas = color_variance > 0.1
        
        # Apply selective inversion
        result = img_float.copy()
        
        # Invert white backgrounds to black
        result[white_mask] = inverted[white_mask]
        
        # Invert very dark text to white
        dark_mask = grayscale < 0.15
        result[dark_mask] = inverted[dark_mask]
        
        # For colored areas, apply a gentler inversion
        if np.any(colored_areas & ~white_mask & ~dark_mask):
            mixed_mask = colored_areas & ~white_mask & ~dark_mask
            result[mixed_mask] = 0.7 * inverted[mixed_mask] + 0.3 * img_float[mixed_mask]
        
        # Convert back to uint8
        result = np.clip(result * 255, 0, 255).astype(np.uint8)
        
        return result
    
    def merge_pdfs(self, pdf_files: List[Path], output_path: Path) -> bool:
        """Merge multiple PDF files into one"""
        try:
            writer = pypdf.PdfWriter()
            total_files = len(pdf_files)
            
            for i, pdf_path in enumerate(pdf_files):
                if self.cancel_requested:
                    return False
                
                if self.progress_callback:
                    progress = (i + 1) / total_files * 100
                    self.progress_callback(f"Merging file {i+1}/{total_files} ({progress:.0f}%)")
                
                with open(pdf_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    for page in reader.pages:
                        writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Merge error: {str(e)}")
            return False

class PDFDarkConverterApp:
    """Main application class"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("PDF Dark Mode Converter & Merger")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Application state
        self.pdf_files: List[PDFFile] = []
        self.processor = PDFProcessor()
        self.processor.set_progress_callback(self.update_progress)
        self.processing = False
        
        # GUI elements
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_bar = None
        self.file_listbox = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="PDF Dark Mode Converter & Merger",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Content area with two columns
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Left column - File management
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # File input section
        file_section = ctk.CTkLabel(left_frame, text="PDF Files", font=ctk.CTkFont(size=16, weight="bold"))
        file_section.pack(pady=(10, 5))
        
        # File buttons
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        add_files_btn = ctk.CTkButton(
            button_frame,
            text="Add PDF Files",
            command=self.add_files,
            width=120
        )
        add_files_btn.pack(side="left", padx=(0, 5))
        
        clear_files_btn = ctk.CTkButton(
            button_frame,
            text="Clear All",
            command=self.clear_files,
            width=100
        )
        clear_files_btn.pack(side="left")
        
        # File list
        self.file_listbox = tk.Listbox(
            left_frame,
            bg="#2B2B2B",
            fg="white",
            selectbackground="#0078D4",
            font=("Consolas", 10)
        )
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right column - Options and actions
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.configure(width=300)
        
        # Processing options
        options_label = ctk.CTkLabel(right_frame, text="Options", font=ctk.CTkFont(size=16, weight="bold"))
        options_label.pack(pady=(10, 5))
        
        # Output directory
        output_frame = ctk.CTkFrame(right_frame)
        output_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(output_frame, text="Output Directory:").pack(anchor="w", padx=10, pady=(10, 0))
        
        self.output_path = tk.StringVar(value=str(Path.home() / "Documents"))
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_path, width=200)
        output_entry.pack(padx=10, pady=5)
        
        browse_output_btn = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self.browse_output_directory,
            width=80
        )
        browse_output_btn.pack(pady=(0, 10))
        
        # Action buttons
        actions_label = ctk.CTkLabel(right_frame, text="Actions", font=ctk.CTkFont(size=16, weight="bold"))
        actions_label.pack(pady=(20, 5))
        
        convert_btn = ctk.CTkButton(
            right_frame,
            text="Convert to Dark Mode",
            command=self.convert_to_dark,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        convert_btn.pack(fill="x", padx=10, pady=5)
        
        merge_btn = ctk.CTkButton(
            right_frame,
            text="Merge PDFs",
            command=self.merge_pdfs,
            height=40
        )
        merge_btn.pack(fill="x", padx=10, pady=5)
        
        convert_merge_btn = ctk.CTkButton(
            right_frame,
            text="Convert & Merge",
            command=self.convert_and_merge,
            height=40,
            fg_color="#00BCF2"
        )
        convert_merge_btn.pack(fill="x", padx=10, pady=5)
        
        # Progress section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=(20, 0))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(20, 10))
        self.progress_bar.set(0)
        
        progress_label = ctk.CTkLabel(progress_frame, textvariable=self.progress_var)
        progress_label.pack(pady=(0, 20))
    
    def add_files(self):
        """Add PDF files to the processing list"""
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        for file_path in file_paths:
            path = Path(file_path)
            if path.suffix.lower() == '.pdf':
                try:
                    # Analyze the PDF
                    page_count, needs_conversion = self.processor.analyze_pdf(path)
                    
                    pdf_file = PDFFile(
                        path=path,
                        name=path.name,
                        size=path.stat().st_size,
                        pages=page_count
                    )
                    
                    self.pdf_files.append(pdf_file)
                    
                    # Add to listbox
                    size_mb = pdf_file.size / (1024 * 1024)
                    display_text = f"{pdf_file.name} ({pdf_file.pages} pages, {size_mb:.1f}MB)"
                    self.file_listbox.insert(tk.END, display_text)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add {path.name}: {str(e)}")
        
        self.update_progress(f"Added {len(file_paths)} files")
    
    def clear_files(self):
        """Clear all files from the list"""
        self.pdf_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_progress("Files cleared")
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_path.set(directory)
    
    def convert_to_dark(self):
        """Convert selected PDFs to dark theme"""
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files first")
            return
        
        self.start_processing("convert")
    
    def merge_pdfs(self):
        """Merge PDFs without conversion"""
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files first")
            return
        
        self.start_processing("merge")
    
    def convert_and_merge(self):
        """Convert PDFs to dark theme and then merge"""
        if not self.pdf_files:
            messagebox.showwarning("No Files", "Please add PDF files first")
            return
        
        self.start_processing("convert_merge")
    
    def start_processing(self, operation):
        """Start processing in a separate thread"""
        if self.processing:
            return
        
        self.processing = True
        self.progress_bar.set(0)
        
        thread = threading.Thread(
            target=self.process_files,
            args=(operation,),
            daemon=True
        )
        thread.start()
    
    def process_files(self, operation):
        """Process files based on operation type"""
        try:
            output_dir = Path(self.output_path.get())
            output_dir.mkdir(exist_ok=True)
            
            if operation == "convert":
                self.convert_files(output_dir)
            elif operation == "merge":
                self.merge_files(output_dir)
            elif operation == "convert_merge":
                # First convert, then merge
                converted_files = self.convert_files(output_dir)
                if converted_files:
                    self.merge_converted_files(converted_files, output_dir)
            
        except Exception as e:
            self.update_progress(f"Error: {str(e)}")
        finally:
            self.processing = False
            self.progress_bar.set(1.0)
    
    def convert_files(self, output_dir: Path) -> List[Path]:
        """Convert files to dark theme"""
        converted_files = []
        total_files = len(self.pdf_files)
        
        for i, pdf_file in enumerate(self.pdf_files):
            base_progress = i / total_files
            
            # Generate output filename
            output_name = f"{pdf_file.path.stem}_dark.pdf"
            output_path = output_dir / output_name
            
            self.update_progress(f"Converting {pdf_file.name}...")
            
            # Convert the file
            success = self.processor.convert_pdf_to_dark(pdf_file.path, output_path)
            
            if success:
                converted_files.append(output_path)
                pdf_file.status = ConversionStatus.COMPLETED
                pdf_file.output_path = output_path
            else:
                pdf_file.status = ConversionStatus.ERROR
            
            # Update overall progress
            self.progress_bar.set((i + 1) / total_files)
        
        self.update_progress(f"Converted {len(converted_files)} files successfully")
        return converted_files
    
    def merge_files(self, output_dir: Path):
        """Merge original files"""
        file_paths = [pdf.path for pdf in self.pdf_files]
        output_path = output_dir / "merged_document.pdf"
        
        self.update_progress("Merging PDF files...")
        success = self.processor.merge_pdfs(file_paths, output_path)
        
        if success:
            self.update_progress(f"Successfully merged to {output_path}")
        else:
            self.update_progress("Merge failed")
    
    def merge_converted_files(self, converted_files: List[Path], output_dir: Path):
        """Merge converted dark theme files"""
        output_path = output_dir / "merged_dark_document.pdf"
        
        self.update_progress("Merging converted PDF files...")
        success = self.processor.merge_pdfs(converted_files, output_path)
        
        if success:
            self.update_progress(f"Successfully created merged dark PDF: {output_path}")
        else:
            self.update_progress("Merge of converted files failed")
    
    def update_progress(self, message: str):
        """Update progress display (thread-safe)"""
        self.root.after(0, lambda: self.progress_var.set(message))
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = PDFDarkConverterApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main()