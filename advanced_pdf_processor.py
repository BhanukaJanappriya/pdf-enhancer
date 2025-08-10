#!/usr/bin/env python3
"""
Advanced PDF Processing Module
Enhanced color inversion and intelligent processing algorithms
"""

import io
import re
import struct
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pypdf
from pypdf import ContentStream
import cv2
import pdf2image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColorSpace:
    """Color space definitions and conversions"""
    
    RGB = "RGB"
    CMYK = "CMYK"
    GRAY = "Gray"
    
    @staticmethod
    def rgb_to_grayscale(r: float, g: float, b: float) -> float:
        """Convert RGB to grayscale using luminance formula"""
        return 0.299 * r + 0.587 * g + 0.114 * b
    
    @staticmethod
    def invert_rgb(r: float, g: float, b: float) -> Tuple[float, float, float]:
        """Invert RGB colors"""
        return 1.0 - r, 1.0 - g, 1.0 - b
    
    @staticmethod
    def invert_cmyk(c: float, m: float, y: float, k: float) -> Tuple[float, float, float, float]:
        """Invert CMYK colors (simplified approach)"""
        # For dark mode, we primarily invert the K (black) channel
        return c, m, y, 1.0 - k
    
    @staticmethod
    def invert_gray(gray: float) -> float:
        """Invert grayscale value"""
        return 1.0 - gray

class PDFContentAnalyzer:
    """Analyzes PDF content to determine optimal inversion strategy"""
    
    def __init__(self):
        self.text_color_threshold = 0.2  # Colors darker than this are considered text
        self.background_threshold = 0.8   # Colors lighter than this are considered background
    
    def analyze_page(self, page: pypdf.PageObject) -> Dict[str, Any]:
        """Analyze a PDF page to determine content characteristics"""
        analysis = {
            'has_text': False,
            'has_images': False,
            'has_vector_graphics': False,
            'background_color': None,
            'text_colors': [],
            'dominant_colors': [],
            'complexity_score': 0,
            'recommended_method': 'auto'
        }
        
        try:
            # Extract text to determine if page has text content
            text_content = page.extract_text()
            analysis['has_text'] = len(text_content.strip()) > 0
            
            # Analyze page resources
            if '/XObject' in page['/Resources']:
                analysis['has_images'] = True
            
            # Analyze content stream for colors and graphics
            content_analysis = self._analyze_content_stream(page)
            analysis.update(content_analysis)
            
            # Determine processing method based on analysis
            analysis['recommended_method'] = self._determine_processing_method(analysis)
            
        except Exception as e:
            logger.warning(f"Page analysis failed: {e}")
            analysis['recommended_method'] = 'image_based'
        
        return analysis
    
    def _analyze_content_stream(self, page: pypdf.PageObject) -> Dict[str, Any]:
        """Analyze the PDF content stream for color information"""
        colors_found = []
        has_vector = False
        
        try:
            content = page.get_contents()
            if content:
                content_stream = ContentStream(content, page.pdf)
                
                # Parse content stream operations
                for operands, operator in content_stream.operations:
                    # Color setting operations
                    if operator in ['rg', 'RG']:  # RGB color
                        if len(operands) >= 3:
                            r, g, b = float(operands[0]), float(operands[1]), float(operands[2])
                            colors_found.append(('RGB', r, g, b))
                    
                    elif operator in ['k', 'K']:  # CMYK color
                        if len(operands) >= 4:
                            c, m, y, k = [float(op) for op in operands[:4]]
                            colors_found.append(('CMYK', c, m, y, k))
                    
                    elif operator in ['g', 'G']:  # Grayscale
                        if len(operands) >= 1:
                            gray = float(operands[0])
                            colors_found.append(('Gray', gray))
                    
                    # Vector graphics operations
                    elif operator in ['l', 'm', 'c', 'v', 'y', 'h', 're']:
                        has_vector = True
        
        except Exception as e:
            logger.warning(f"Content stream analysis failed: {e}")
        
        return {
            'colors_found': colors_found,
            'has_vector_graphics': has_vector,
            'complexity_score': len(colors_found) + (10 if has_vector else 0)
        }
    
    def _determine_processing_method(self, analysis: Dict[str, Any]) -> str:
        """Determine the best processing method based on analysis"""
        
        # If page is very complex or has many images, use image-based processing
        if analysis['complexity_score'] > 50 or analysis['has_images']:
            return 'image_based'
        
        # If page has primarily text and simple graphics, try vector processing
        if analysis['has_text'] and not analysis['has_images']:
            return 'vector_based'
        
        # Default to hybrid approach
        return 'hybrid'

class AdvancedColorInverter:
    """Advanced color inversion algorithms"""
    
    def __init__(self):
        self.preserve_colors = True  # Preserve colored elements when possible
        self.smart_inversion = True   # Use intelligent inversion algorithms
        self.contrast_enhancement = True  # Enhance contrast in dark mode
    
    def invert_image_smart(self, image: Image.Image) -> Image.Image:
        """Apply intelligent color inversion to an image"""
        
        # Convert to numpy array for processing
        img_array = np.array(image)
        
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:  # RGB image
            return self._invert_rgb_image(img_array)
        elif len(img_array.shape) == 2:  # Grayscale image
            return self._invert_grayscale_image(img_array)
        else:
            # Fallback to simple inversion
            return ImageOps.invert(image)
    
    def _invert_rgb_image(self, img_array: np.ndarray) -> Image.Image:
        """Advanced RGB image inversion"""
        
        # Convert to float for processing
        img_float = img_array.astype(np.float32) / 255.0
        
        # Calculate luminance
        luminance = np.dot(img_float[...,:3], [0.299, 0.587, 0.114])
        
        # Detect different regions
        dark_text = luminance < 0.2      # Very dark areas (likely text)
        light_bg = luminance > 0.8       # Very light areas (likely background)
        colored_areas = np.std(img_float, axis=2) > 0.1  # Areas with color variation
        
        # Create output array
        result = img_float.copy()
        
        # Invert light backgrounds to dark
        result[light_bg] = 1.0 - img_float[light_bg]
        
        # Invert dark text to light
        result[dark_text] = 1.0 - img_float[dark_text]
        
        # Handle colored areas more carefully
        if self.preserve_colors:
            # For colored areas that aren't clearly text or background,
            # apply a more nuanced inversion
            mixed_areas = colored_areas & ~light_bg & ~dark_text
            if np.any(mixed_areas):
                # Invert luminance but preserve hue relationships
                result[mixed_areas] = self._preserve_hue_inversion(
                    img_float[mixed_areas], luminance[mixed_areas]
                )
        
        # Enhance contrast if requested
        if self.contrast_enhancement:
            result = self._enhance_contrast(result)
        
        # Convert back to uint8 and create PIL image
        result = np.clip(result * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(result)
    
    def _invert_grayscale_image(self, img_array: np.ndarray) -> Image.Image:
        """Advanced grayscale image inversion"""
        
        # Simple but effective grayscale inversion
        inverted = 255 - img_array
        
        # Optional: Apply gamma correction for better readability
        gamma = 0.8
        inverted = np.power(inverted / 255.0, gamma) * 255
        
        return Image.fromarray(inverted.astype(np.uint8))
    
    def _preserve_hue_inversion(self, colored_pixels: np.ndarray, luminance: np.ndarray) -> np.ndarray:
        """Invert luminance while preserving hue information"""
        
        # Convert to HSV to work with hue and saturation separately
        hsv_pixels = cv2.cvtColor(colored_pixels.reshape(-1, 1, 3), cv2.COLOR_RGB2HSV)
        hsv_pixels = hsv_pixels.reshape(colored_pixels.shape)
        
        # Invert the value (brightness) channel
        hsv_pixels[..., 2] = 1.0 - hsv_pixels[..., 2]
        
        # Convert back to RGB
        rgb_result = cv2.cvtColor(hsv_pixels.reshape(-1, 1, 3), cv2.COLOR_HSV2RGB)
        return rgb_result.reshape(colored_pixels.shape)
    
    def _enhance_contrast(self, img_float: np.ndarray) -> np.ndarray:
        """Enhance contrast for better dark mode readability"""
        
        # Apply gentle contrast enhancement
        # Use a sigmoid function to enhance mid-tones
        enhanced = 1 / (1 + np.exp(-12 * (img_float - 0.5)))
        
        # Blend with original for subtle effect
        return 0.7 * enhanced + 0.3 * img_float

class VectorPDFProcessor:
    """Process PDF at vector level for high-quality text inversion"""
    
    def __init__(self):
        self.color_mappings = {
            # Common color mappings for dark mode
            (0, 0, 0): (1, 1, 1),      # Black to White
            (1, 1, 1): (0, 0, 0),      # White to Black
            (0.5, 0.5, 0.5): (0.7, 0.7, 0.7),  # Gray adjustments
        }
    
    def process_page_vector(self, page: pypdf.PageObject) -> pypdf.PageObject:
        """Process a PDF page at vector level"""
        
        try:
            # Get the page's content stream
            content = page.get_contents()
            if not content:
                return page
            
            # Parse and modify content stream
            content_stream = ContentStream(content, page.pdf)
            modified_operations = []
            
            for operands, operator in content_stream.operations:
                # Process color-setting operations
                if operator in ['rg', 'RG', 'g', 'G', 'k', 'K']:
                    modified_operands = self._invert_color_operation(operands, operator)
                    modified_operations.append((modified_operands, operator))
                else:
                    modified_operations.append((operands, operator))
            
            # Reconstruct content stream
            modified_content = self._reconstruct_content_stream(modified_operations)
            
            # Create new page with modified content
            new_page = pypdf.PageObject.create_blank_page(
                width=page.mediabox.width,
                height=page.mediabox.height
            )
            new_page.merge_page(page)  # Copy resources and other properties
            
            # Replace content
            new_page[pypdf.generic.NameObject("/Contents")] = modified_content
            
            return new_page
            
        except Exception as e:
            logger.warning(f"Vector processing failed: {e}")
            return page  # Return original page if processing fails
    
    def _invert_color_operation(self, operands: List, operator: str) -> List:
        """Invert color values in PDF operations"""
        
        try:
            if operator in ['rg', 'RG']:  # RGB colors
                if len(operands) >= 3:
                    r, g, b = [float(op) for op in operands[:3]]
                    inv_r, inv_g, inv_b = ColorSpace.invert_rgb(r, g, b)
                    return [inv_r, inv_g, inv_b] + operands[3:]
            
            elif operator in ['g', 'G']:  # Grayscale
                if len(operands) >= 1:
                    gray = float(operands[0])
                    inv_gray = ColorSpace.invert_gray(gray)
                    return [inv_gray] + operands[1:]
            
            elif operator in ['k', 'K']:  # CMYK colors
                if len(operands) >= 4:
                    c, m, y, k = [float(op) for op in operands[:4]]
                    inv_c, inv_m, inv_y, inv_k = ColorSpace.invert_cmyk(c, m, y, k)
                    return [inv_c, inv_m, inv_y, inv_k] + operands[4:]
        
        except (ValueError, TypeError) as e:
            logger.warning(f"Color inversion failed for {operator}: {e}")
        
        return operands  # Return original if inversion fails
    
    def _reconstruct_content_stream(self, operations: List[Tuple]) -> pypdf.generic.DecodedStreamObject:
        """Reconstruct PDF content stream from operations"""
        
        content_parts = []
        
        for operands, operator in operations:
            # Convert operands to string representation
            operand_strs = []
            for operand in operands:
                if isinstance(operand, (int, float)):
                    operand_strs.append(str(operand))
                else:
                    operand_strs.append(str(operand))
            
            # Construct the operation string
            if operand_strs:
                content_parts.append(" ".join(operand_strs) + " " + operator)
            else:
                content_parts.append(operator)
        
        # Join all operations
        content_str = "\n".join(content_parts)
        
        # Create new stream object
        stream_obj = pypdf.generic.DecodedStreamObject()
        stream_obj._data = content_str.encode()
        
        return stream_obj

class HybridPDFProcessor:
    """Combines vector and image processing for optimal results"""
    
    def __init__(self):
        self.analyzer = PDFContentAnalyzer()
        self.vector_processor = VectorPDFProcessor()
        self.color_inverter = AdvancedColorInverter()
    
    def process_pdf(self, input_path: Path, output_path: Path, 
                   progress_callback=None) -> bool:
        """Process PDF using hybrid approach"""
        
        try:
            with open(input_path, 'rb') as input_file:
                reader = pypdf.PdfReader(input_file)
                writer = pypdf.PdfWriter()
                
                total_pages = len(reader.pages)
                
                for i, page in enumerate(reader.pages):
                    if progress_callback:
                        progress = (i + 1) / total_pages * 100
                        progress_callback(f"Processing page {i+1}/{total_pages} ({progress:.0f}%)")
                    
                    # Analyze page to determine best processing method
                    analysis = self.analyzer.analyze_page(page)
                    method = analysis['recommended_method']
                    
                    # Process based on determined method
                    if method == 'vector_based':
                        processed_page = self.vector_processor.process_page_vector(page)
                        writer.add_page(processed_page)
                    
                    elif method == 'image_based':
                        # Convert to image, process, and add back
                        processed_page = self._process_page_as_image(page, input_path, i)
                        if processed_page:
                            writer.add_page(processed_page)
                        else:
                            writer.add_page(page)  # Fallback to original
                    
                    else:  # hybrid
                        # Try vector first, fallback to image
                        try:
                            processed_page = self.vector_processor.process_page_vector(page)
                            writer.add_page(processed_page)
                        except Exception:
                            processed_page = self._process_page_as_image(page, input_path, i)
                            if processed_page:
                                writer.add_page(processed_page)
                            else:
                                writer.add_page(page)
                
                # Write output file
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True
                
        except Exception as e:
            logger.error(f"Hybrid processing failed: {e}")
            return False
    
    def _process_page_as_image(self, page: pypdf.PageObject, 
                              pdf_path: Path, page_num: int) -> Optional[pypdf.PageObject]:
        """Process a single page as an image"""
        
        try:
            # Convert single page to image
            images = pdf2image.convert_from_path(
                pdf_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=200
            )
            
            if not images:
                return None
            
            # Process the image
            processed_image = self.color_inverter.invert_image_smart(images[0])
            
            # Convert back to PDF page
            img_buffer = io.BytesIO()
            processed_image.save(img_buffer, format='PDF', resolution=200.0)
            img_buffer.seek(0)
            
            img_reader = pypdf.PdfReader(img_buffer)
            return img_reader.pages[0]
            
        except Exception as e:
            logger.warning(f"Image processing failed for page {page_num}: {e}")
            return None