import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF
import os
from pathlib import Path
import threading
from PIL import Image, ImageTk
import io

class PDFDarkModeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Dark Mode Converter & Merger")
        self.root.geometry("800x600")
        self.root.configure(bg="#2B2B2B")
        
        # Set window icon - tries multiple possible icon files
        icon_files = ["favicon.ico", "app_icon.ico", "icon.ico"]
        for icon_file in icon_files:
            try:
                if os.path.exists(icon_file):
                    self.root.iconbitmap(icon_file)
                    print(f"✓ Using icon: {icon_file}")
                    break
            except Exception as e:
                print(f"Could not load {icon_file}: {e}")
                continue
        
        # Configure dark theme colors
        self.colors = {
            'bg': '#2B2B2B',
            'fg': '#FFFFFF',
            'button_bg': '#404040',
            'button_fg': '#FFFFFF',
            'entry_bg': '#404040',
            'entry_fg': '#FFFFFF'
        }
        
        self.pdf_files = []
        self.converted_files = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="PDF Dark Mode Converter & Merger",
            font=('Arial', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        title_label.pack(pady=20)
        
        # File selection frame
        file_frame = tk.Frame(self.root, bg=self.colors['bg'])
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        select_btn = tk.Button(
            file_frame,
            text="Select PDF Files",
            command=self.select_files,
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        select_btn.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(
            file_frame,
            text="Clear Files",
            command=self.clear_files,
            bg='#5C5C5C',
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # File list
        list_frame = tk.Frame(self.root, bg=self.colors['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            list_frame,
            text="Selected Files:",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W)
        
        # Scrollable listbox
        listbox_frame = tk.Frame(list_frame, bg=self.colors['bg'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            listbox_frame,
            bg=self.colors['entry_bg'],
            fg=self.colors['entry_fg'],
            selectbackground='#0078D4',
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = tk.Label(
            self.root,
            textvariable=self.progress_var,
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(
            self.root,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=5)
        
        # Action buttons frame
        action_frame = tk.Frame(self.root, bg=self.colors['bg'])
        action_frame.pack(pady=20)
        
        convert_btn = tk.Button(
            action_frame,
            text="Convert to Dark Mode",
            command=self.convert_to_dark,
            bg='#0078D4',
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            font=('Arial', 10, 'bold')
        )
        convert_btn.pack(side=tk.LEFT, padx=5)
        
        merge_btn = tk.Button(
            action_frame,
            text="Merge PDFs",
            command=self.merge_pdfs,
            bg='#00BCF2',
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            font=('Arial', 10, 'bold')
        )
        merge_btn.pack(side=tk.LEFT, padx=5)
        
        convert_merge_btn = tk.Button(
            action_frame,
            text="Convert & Merge",
            command=self.convert_and_merge,
            bg='#00AA00',
            fg=self.colors['button_fg'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            font=('Arial', 10, 'bold')
        )
        convert_merge_btn.pack(side=tk.LEFT, padx=5)
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        for file in files:
            if file not in self.pdf_files:
                self.pdf_files.append(file)
                filename = os.path.basename(file)
                self.file_listbox.insert(tk.END, filename)
                
    def clear_files(self):
        self.pdf_files.clear()
        self.converted_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.progress_var.set("Ready")
        self.progress_bar['value'] = 0
        
    def invert_pdf_colors(self, input_path, output_path):
        """Convert PDF from light to dark theme"""
        try:
            doc = fitz.open(input_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get page as pixmap (image)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                
                # Convert to RGBA for processing
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Invert colors (white->black, black->white)
                pixels = img.load()
                for y in range(img.height):
                    for x in range(img.width):
                        r, g, b, a = pixels[x, y]
                        
                        # Simple inversion for near-white and near-black
                        if r > 240 and g > 240 and b > 240:  # Near white -> black
                            pixels[x, y] = (0, 0, 0, a)
                        elif r < 15 and g < 15 and b < 15:  # Near black -> white
                            pixels[x, y] = (255, 255, 255, a)
                        else:
                            # Invert other colors
                            pixels[x, y] = (255 - r, 255 - g, 255 - b, a)
                
                # Convert back to RGB
                img_rgb = Image.new('RGB', img.size, (0, 0, 0))
                img_rgb.paste(img, mask=img.split()[-1])
                
                # Replace page with inverted image
                img_bytes = io.BytesIO()
                img_rgb.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Create new page with inverted image
                page.clean_contents()
                page_rect = page.rect
                page.insert_image(page_rect, stream=img_bytes.getvalue())
            
            doc.save(output_path)
            doc.close()
            return True
            
        except Exception as e:
            print(f"Error converting {input_path}: {str(e)}")
            return False
            
    def merge_pdf_files(self, file_list, output_path):
        """Merge multiple PDF files into one"""
        try:
            merged_doc = fitz.open()
            
            for file_path in file_list:
                doc = fitz.open(file_path)
                merged_doc.insert_pdf(doc)
                doc.close()
                
            merged_doc.save(output_path)
            merged_doc.close()
            return True
            
        except Exception as e:
            print(f"Error merging PDFs: {str(e)}")
            return False
            
    def convert_to_dark(self):
        if not self.pdf_files:
            messagebox.showwarning("Warning", "Please select PDF files first!")
            return
            
        def convert_thread():
            self.converted_files.clear()
            total_files = len(self.pdf_files)
            
            for i, pdf_file in enumerate(self.pdf_files):
                self.progress_var.set(f"Converting {os.path.basename(pdf_file)}...")
                self.progress_bar['value'] = (i / total_files) * 100
                self.root.update()
                
                # Create output filename
                input_path = Path(pdf_file)
                output_path = input_path.parent / f"{input_path.stem}_dark.pdf"
                
                if self.invert_pdf_colors(pdf_file, str(output_path)):
                    self.converted_files.append(str(output_path))
                    
            self.progress_bar['value'] = 100
            self.progress_var.set(f"Conversion complete! {len(self.converted_files)} files converted.")
            
            if self.converted_files:
                messagebox.showinfo("Success", f"Converted {len(self.converted_files)} PDF(s) to dark mode!")
            
        threading.Thread(target=convert_thread, daemon=True).start()
        
    def merge_pdfs(self):
        files_to_merge = self.converted_files if self.converted_files else self.pdf_files
        
        if not files_to_merge:
            messagebox.showwarning("Warning", "Please select PDF files first!")
            return
            
        # Ask for output location
        output_path = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_path:
            return
            
        def merge_thread():
            self.progress_var.set("Merging PDFs...")
            self.progress_bar['value'] = 50
            self.root.update()
            
            if self.merge_pdf_files(files_to_merge, output_path):
                self.progress_bar['value'] = 100
                self.progress_var.set("Merge complete!")
                messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved to: {output_path}")
            else:
                self.progress_var.set("Merge failed!")
                messagebox.showerror("Error", "Failed to merge PDFs!")
                
        threading.Thread(target=merge_thread, daemon=True).start()
        
    def convert_and_merge(self):
        if not self.pdf_files:
            messagebox.showwarning("Warning", "Please select PDF files first!")
            return
            
        # Ask for output location
        output_path = filedialog.asksaveasfilename(
            title="Save Converted & Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not output_path:
            return
            
        def convert_and_merge_thread():
            # First convert all files
            self.converted_files.clear()
            total_files = len(self.pdf_files)
            
            for i, pdf_file in enumerate(self.pdf_files):
                self.progress_var.set(f"Converting {os.path.basename(pdf_file)}...")
                self.progress_bar['value'] = (i / total_files) * 70  # 70% for conversion
                self.root.update()
                
                # Create temporary output filename
                input_path = Path(pdf_file)
                temp_output = input_path.parent / f"temp_{input_path.stem}_dark.pdf"
                
                if self.invert_pdf_colors(pdf_file, str(temp_output)):
                    self.converted_files.append(str(temp_output))
                    
            # Then merge converted files
            if self.converted_files:
                self.progress_var.set("Merging converted PDFs...")
                self.progress_bar['value'] = 85
                self.root.update()
                
                if self.merge_pdf_files(self.converted_files, output_path):
                    # Clean up temporary files
                    for temp_file in self.converted_files:
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                    
                    self.progress_bar['value'] = 100
                    self.progress_var.set("Convert & merge complete!")
                    messagebox.showinfo("Success", f"PDFs converted and merged successfully!\nSaved to: {output_path}")
                else:
                    self.progress_var.set("Merge failed!")
                    messagebox.showerror("Error", "Failed to merge converted PDFs!")
            else:
                self.progress_var.set("Conversion failed!")
                messagebox.showerror("Error", "Failed to convert PDFs!")
                
        threading.Thread(target=convert_and_merge_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = PDFDarkModeConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()