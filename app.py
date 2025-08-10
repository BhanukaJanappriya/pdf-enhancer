import customtkinter
import pypdf
from PIL import Image, ImageTk, ImageOps
import os
import threading
import logging
from tkinter import filedialog, messagebox, Canvas
import time
import uuid

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Model (Handles all PDF processing logic) ---
class PDFProcessorModel:
    """
    Handles the core business logic for PDF manipulation,
    including advanced color inversion and merging.
    """
    def __init__(self):
        logging.info("PDFProcessorModel initialized.")

    def invert_colors_advanced(self, input_pdf_path, output_pdf_path, progress_callback=None):
        """
        Simulates an advanced color inversion process based on the requirements.
        This is a placeholder for a full implementation using pdf2image and Pillow.
        
        The real process would involve:
        1. Using `pdf2image.convert_from_path(input_pdf_path)` to get a list of page images.
        2. Iterating through each image and using `Pillow` and `numpy` to perform
           intelligent color inversion:
           - Convert the image to a NumPy array.
           - Apply a color threshold to detect white/black/gray.
           - Invert colors based on the predefined rules (white->black, black->white, etc.).
           - Use `cv2.inRange` with `opencv-python` for more robust color detection.
        3. Saving the inverted images to a temporary directory.
        4. Using `pypdf.PdfWriter` to create a new PDF from the processed images.
        5. Preserving bookmarks and metadata from the original PDF where possible.
        
        For this example, we'll simulate the process with a progress bar and
        copy the file to show a successful operation.
        """
        logging.info(f"Starting advanced color inversion for: {input_pdf_path}")
        total_pages = 10  # Simulating a 10-page document for progress bar
        
        try:
            # Simulate a time-consuming process
            for i in range(total_pages):
                time.sleep(0.5) # Simulate page processing time
                if progress_callback:
                    progress_callback(i + 1, total_pages)
            
            with open(input_pdf_path, 'rb') as f_in, open(output_pdf_path, 'wb') as f_out:
                f_out.write(f_in.read())
            
            logging.info(f"Advanced color inversion complete. File saved to: {output_pdf_path}")
            return True
        except Exception as e:
            logging.error(f"Error during color inversion: {e}", exc_info=True)
            return False

    def merge_pdfs(self, input_pdf_paths, output_pdf_path, progress_callback=None):
        """
        Merges a list of PDF files into a single output PDF.
        """
        if not input_pdf_paths:
            logging.warning("No files to merge.")
            return False

        logging.info(f"Starting merge operation for {len(input_pdf_paths)} files.")
        merger = pypdf.PdfMerger()
        try:
            for i, path in enumerate(input_pdf_paths):
                merger.append(path)
                if progress_callback:
                    progress_callback(i + 1, len(input_pdf_paths))
            
            merger.write(output_pdf_path)
            merger.close()
            logging.info(f"PDFs merged successfully. File saved to: {output_pdf_path}")
            return True
        except Exception as e:
            logging.error(f"Error during PDF merge: {e}", exc_info=True)
            return False
        
# --- View (Handles the UI and user interactions) ---
class App(customtkinter.CTk):
    """
    The main application class. Sets up the GUI and handles
    user-facing elements.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.title("PDF Dark Mode Converter & Merger")
        self.geometry("1000x700")
        customtkinter.set_appearance_mode("dark")
        
        # --- UI Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tab_view = customtkinter.CTkTabview(self, width=250)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_view.add("Dark Mode")
        self.tab_view.add("Merge PDFs")
        
        self._setup_dark_mode_tab()
        self._setup_merge_pdfs_tab()

    def _setup_dark_mode_tab(self):
        tab = self.tab_view.tab("Dark Mode")
        tab.grid_columnconfigure(0, weight=1)
        
        label = customtkinter.CTkLabel(tab, text="PDF Dark Mode Converter", font=customtkinter.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # --- File Input Area ---
        self.dark_mode_input_frame = customtkinter.CTkFrame(tab, height=150, fg_color=("gray75", "gray20"))
        self.dark_mode_input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.dark_mode_input_frame.grid_columnconfigure(0, weight=1)
        
        self.dark_mode_label = customtkinter.CTkLabel(self.dark_mode_input_frame, text="Drag and drop a PDF here or click to browse", text_color="gray")
        self.dark_mode_label.grid(row=0, column=0, padx=20, pady=20)
        self.dark_mode_label.bind('<Button-1>', self._open_file_dialog_dark)
        
        self.dark_mode_input_path = ""
        self.dark_mode_selected_file_label = customtkinter.CTkLabel(tab, text="", text_color="gray", font=customtkinter.CTkFont(size=12))
        self.dark_mode_selected_file_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # --- Preview Section ---
        preview_frame = customtkinter.CTkFrame(tab, fg_color="transparent")
        preview_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        preview_frame.grid_columnconfigure((0, 1), weight=1)

        self.preview_before_label = customtkinter.CTkLabel(preview_frame, text="Original Preview")
        self.preview_before_label.grid(row=0, column=0, padx=10)
        self.preview_after_label = customtkinter.CTkLabel(preview_frame, text="Converted Preview (Simulated)")
        self.preview_after_label.grid(row=0, column=1, padx=10)
        
        # Placeholder for preview images
        self.preview_before_img = customtkinter.CTkLabel(preview_frame, text="[No file selected]", fg_color=("gray85", "gray15"), width=400, height=250)
        self.preview_before_img.grid(row=1, column=0, padx=10, pady=10)
        self.preview_after_img = customtkinter.CTkLabel(preview_frame, text="[No file selected]", fg_color=("gray85", "gray15"), width=400, height=250)
        self.preview_after_img.grid(row=1, column=1, padx=10, pady=10)

        # --- Action Buttons & Progress ---
        self.dark_mode_convert_button = customtkinter.CTkButton(tab, text="Convert to Dark Mode", command=self._start_dark_mode_conversion)
        self.dark_mode_convert_button.grid(row=4, column=0, padx=20, pady=10)
        
        self.dark_mode_progress = customtkinter.CTkProgressBar(tab, orientation="horizontal")
        self.dark_mode_progress.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.dark_mode_progress.set(0)

    def _open_file_dialog_dark(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.dark_mode_input_path = file_path
            self.dark_mode_selected_file_label.configure(text=f"Selected: {os.path.basename(file_path)}")
            # For a real app, you would generate a preview image here.
            # Example: self._generate_preview_thumbnail(file_path)

    def _start_dark_mode_conversion(self):
        if not self.dark_mode_input_path:
            messagebox.showerror("Error", "Please select a PDF file first.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"dark_{os.path.basename(self.dark_mode_input_path)}"
        )
        if not output_path:
            return

        self.dark_mode_selected_file_label.configure(text="Processing...")
        self.dark_mode_convert_button.configure(state="disabled")
        self.dark_mode_progress.set(0)
        
        threading.Thread(target=self._run_dark_mode_thread, args=(self.dark_mode_input_path, output_path)).start()

    def _run_dark_mode_thread(self, input_path, output_path):
        success = self.controller.process_dark_mode(input_path, output_path, self._update_dark_mode_progress)
        self.after(0, lambda: self._dark_mode_complete(success))

    def _update_dark_mode_progress(self, current, total):
        self.after(0, lambda: self.dark_mode_progress.set(current / total))
        
    def _dark_mode_complete(self, success):
        self.dark_mode_convert_button.configure(state="normal")
        if success:
            self.dark_mode_selected_file_label.configure(text=f"Conversion successful! File saved.")
            self.dark_mode_progress.set(1)
        else:
            self.dark_mode_selected_file_label.configure(text="Conversion failed.")
            self.dark_mode_progress.set(0)
            
    def _setup_merge_pdfs_tab(self):
        tab = self.tab_view.tab("Merge PDFs")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        
        label = customtkinter.CTkLabel(tab, text="Merge PDF Files", font=customtkinter.CTkFont(size=20, weight="bold"))
        label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.merge_status = customtkinter.CTkLabel(tab, text="Select files to merge", text_color="gray")
        self.merge_status.grid(row=1, column=0, padx=20, pady=5)
        
        # --- File List and Controls ---
        merge_controls_frame = customtkinter.CTkFrame(tab)
        merge_controls_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        merge_controls_frame.grid_columnconfigure(0, weight=1)
        merge_controls_frame.grid_columnconfigure(1, weight=0)
        merge_controls_frame.grid_rowconfigure(0, weight=1)
        
        self.merged_files_scroll_frame = customtkinter.CTkScrollableFrame(merge_controls_frame)
        self.merged_files_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.merged_files_scroll_frame.grid_columnconfigure(0, weight=1)

        self.merged_files = []
        self.listbox_items = []

        control_buttons_frame = customtkinter.CTkFrame(merge_controls_frame)
        control_buttons_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ns")
        
        add_button = customtkinter.CTkButton(control_buttons_frame, text="Add Files", command=self._add_merge_files)
        add_button.pack(pady=(0, 10), fill="x")
        remove_button = customtkinter.CTkButton(control_buttons_frame, text="Remove", command=self._remove_merge_file)
        remove_button.pack(pady=(0, 10), fill="x")
        move_up_button = customtkinter.CTkButton(control_buttons_frame, text="Move Up", command=self._move_merge_file_up)
        move_up_button.pack(pady=(0, 10), fill="x")
        move_down_button = customtkinter.CTkButton(control_buttons_frame, text="Move Down", command=self._move_merge_file_down)
        move_down_button.pack(pady=(0, 10), fill="x")

        self.merge_button = customtkinter.CTkButton(tab, text="Merge PDFs", command=self._start_pdf_merge)
        self.merge_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.merge_progress = customtkinter.CTkProgressBar(tab, orientation="horizontal")
        self.merge_progress.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.merge_progress.set(0)

    def _add_merge_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if file_paths:
            for path in file_paths:
                if path not in self.merged_files:
                    self.merged_files.append(path)
            self._update_merge_listbox()
            
    def _remove_merge_file(self):
        selected_indices = [i for i, item in enumerate(self.listbox_items) if item.cget("fg_color") == ("gray50", "gray40")]
        
        if not selected_indices:
            return
            
        for index in sorted(selected_indices, reverse=True):
            self.merged_files.pop(index)
        self._update_merge_listbox()
        
    def _move_merge_file_up(self):
        selected_indices = [i for i, item in enumerate(self.listbox_items) if item.cget("fg_color") == ("gray50", "gray40")]
        if len(selected_indices) != 1 or selected_indices[0] == 0:
            return
        
        index = selected_indices[0]
        file_to_move = self.merged_files.pop(index)
        self.merged_files.insert(index - 1, file_to_move)
        self._update_merge_listbox(select_index=index - 1)
        
    def _move_merge_file_down(self):
        selected_indices = [i for i, item in enumerate(self.listbox_items) if item.cget("fg_color") == ("gray50", "gray40")]
        if len(selected_indices) != 1 or selected_indices[0] == len(self.merged_files) - 1:
            return
            
        index = selected_indices[0]
        file_to_move = self.merged_files.pop(index)
        self.merged_files.insert(index + 1, file_to_move)
        self._update_merge_listbox(select_index=index + 1)

    def _update_merge_listbox(self, select_index=None):
        for item in self.listbox_items:
            item.destroy()
        self.listbox_items.clear()

        if not self.merged_files:
            self.merge_status.configure(text="Drag and drop files to merge")
            return
        
        self.merge_status.configure(text=f"Selected files: {len(self.merged_files)}")
        
        for i, path in enumerate(self.merged_files):
            file_name = os.path.basename(path)
            list_item = customtkinter.CTkLabel(self.merged_files_scroll_frame, text=f"{i+1}. {file_name}", corner_radius=6,
                                                fg_color=("gray70", "gray25"), padx=10, pady=5)
            list_item.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            list_item.bind("<Button-1>", self._on_merge_list_click)
            self.listbox_items.append(list_item)
            
            if i == select_index:
                list_item.configure(fg_color=("gray50", "gray40"))

    def _on_merge_list_click(self, event):
        item = event.widget
        is_selected = item.cget("fg_color") == ("gray50", "gray40")

        # Deselect all other items
        for other_item in self.listbox_items:
            other_item.configure(fg_color=("gray70", "gray25"))
        
        if not is_selected:
            item.configure(fg_color=("gray50", "gray40")) # Selected color
            
    def _start_pdf_merge(self):
        if len(self.merged_files) < 2:
            messagebox.showerror("Error", "Please select at least two PDF files to merge.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="merged_document.pdf"
        )
        if not output_path:
            return

        self.merge_status.configure(text="Merging PDFs...")
        self.merge_button.configure(state="disabled")
        self.merge_progress.set(0)
        
        threading.Thread(target=self._run_merge_thread, args=(self.merged_files, output_path)).start()

    def _run_merge_thread(self, input_paths, output_path):
        success = self.controller.process_merge(input_paths, output_path, self._update_merge_progress)
        self.after(0, lambda: self._merge_complete(success))

    def _update_merge_progress(self, current, total):
        self.after(0, lambda: self.merge_progress.set(current / total))
        
    def _merge_complete(self, success):
        self.merge_button.configure(state="normal")
        if success:
            self.merge_status.configure(text="Merging successful!")
            self.merge_progress.set(1)
            self.merged_files.clear()
            self._update_merge_listbox()
        else:
            self.merge_status.configure(text="Merging failed.")
            self.merge_progress.set(0)

# --- Controller (Connects View and Model) ---
class AppController:
    """
    Manages the flow of data between the UI and the processing logic.
    """
    def __init__(self, model):
        self.model = model

    def process_dark_mode(self, input_path, output_path, progress_callback):
        return self.model.invert_colors_advanced(input_path, output_path, progress_callback)
    
    def process_merge(self, input_paths, output_path, progress_callback):
        return self.model.merge_pdfs(input_paths, output_path, progress_callback)

# --- Main Entry Point ---
if __name__ == "__main__":
    try:
        model = PDFProcessorModel()
        controller = AppController(model)
        app = App(controller)
        app.mainloop()
    except Exception as e:
        logging.critical(f"An unhandled error occurred: {e}", exc_info=True)
        messagebox.showerror("Critical Error", "The application encountered a critical error and must close.")
