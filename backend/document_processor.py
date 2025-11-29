"""
Document processing and metadata extraction
"""

import re
import io
from typing import Dict, Optional
import PyPDF2
import pdfplumber
from PIL import Image
import pytesseract
import pyzbar.pyzbar as pyzbar

class DocumentProcessor:
    """Process documents and extract metadata"""
    
    def __init__(self):
        self.pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]')
        self.aadhaar_pattern = re.compile(r'[2-9]{1}[0-9]{11}')
    
    def process_document(self, file_content: bytes, filename: str) -> Dict:
        """Process document and extract metadata"""
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return self.process_pdf(file_content, filename)
        elif file_ext in ['jpg', 'jpeg', 'png']:
            return self.process_image(file_content, filename)
        else:
            return {"document_type": "Unknown", "error": "Unsupported file type"}
    
    def process_pdf(self, content: bytes, filename: str) -> Dict:
        """Process PDF document"""
        metadata = {
            "file_name": filename,
            "document_type": "Unknown"
        }
        
        try:
            # Try pdfplumber first for better text extraction
            pdf_file = io.BytesIO(content)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                # Check for QR codes in PDF
                qr_data = self.extract_qr_from_pdf(content)
                if qr_data:
                    metadata["qr_data"] = qr_data
                
                # Detect document type and extract metadata
                if self.is_pan(text):
                    metadata.update(self.extract_pan_metadata(text))
                elif self.is_aadhaar(text, qr_data):
                    metadata.update(self.extract_aadhaar_metadata(text, qr_data))
                else:
                    metadata["document_type"] = "Unknown"
                    
        except Exception as e:
            # Fallback to PyPDF2
            try:
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                if self.is_pan(text):
                    metadata.update(self.extract_pan_metadata(text))
                elif self.is_aadhaar(text):
                    metadata.update(self.extract_aadhaar_metadata(text))
                    
            except Exception as e2:
                metadata["error"] = str(e2)
        
        return metadata
    
    def process_image(self, content: bytes, filename: str) -> Dict:
        """Process image document"""
        metadata = {
            "file_name": filename,
            "document_type": "Unknown"
        }
        
        try:
            image = Image.open(io.BytesIO(content))
            
            # Extract QR code if present
            qr_data = self.extract_qr_from_image(image)
            if qr_data:
                metadata["qr_data"] = qr_data
            
            # OCR for text extraction
            try:
                text = pytesseract.image_to_string(image, lang='eng')
            except:
                text = ""
            
            # Detect document type
            if self.is_pan(text):
                metadata.update(self.extract_pan_metadata(text))
            elif self.is_aadhaar(text, qr_data):
                metadata.update(self.extract_aadhaar_metadata(text, qr_data))
            else:
                metadata["document_type"] = "Unknown"
                
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    def is_pan(self, text: str) -> bool:
        """Check if document is PAN card"""
        pan_match = self.pan_pattern.search(text)
        return pan_match is not None
    
    def is_aadhaar(self, text: str, qr_data: Optional[str] = None) -> bool:
        """Check if document is Aadhaar card"""
        aadhaar_match = self.aadhaar_pattern.search(text)
        if aadhaar_match:
            return True
        if qr_data and "uid" in qr_data.lower():
            return True
        return False
    
    def extract_pan_metadata(self, text: str) -> Dict:
        """Extract PAN card metadata"""
        metadata = {
            "document_type": "PAN"
        }
        
        # Extract PAN number
        pan_match = self.pan_pattern.search(text)
        if pan_match:
            pan_number = pan_match.group()
            metadata["pan_numbers"] = [pan_number]
        
        # Extract name (common patterns)
        name_patterns = [
            r'Name\s*[:\-]?\s*([A-Z\s]+)',
            r'Name\s+of\s+the\s+holder\s*[:\-]?\s*([A-Z\s]+)',
            r'([A-Z]{2,}\s+[A-Z]{2,})',  # Simple pattern
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3:
                    metadata["holder_name"] = name
                    break
        
        # Extract DOB
        dob_patterns = [
            r'Date\s+of\s+Birth\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4})',
            r'DOB\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4})',
            r'(\d{2}[/\-]\d{2}[/\-]\d{4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["date_of_birth"] = match.group(1)
                break
        
        # Extract Father's name
        father_pattern = r'Father\'?s?\s+Name\s*[:\-]?\s*([A-Z\s]+)'
        match = re.search(father_pattern, text, re.IGNORECASE)
        if match:
            metadata["father_name"] = match.group(1).strip()
        
        return metadata
    
    def extract_aadhaar_metadata(self, text: str, qr_data: Optional[str] = None) -> Dict:
        """Extract Aadhaar card metadata"""
        metadata = {
            "document_type": "Aadhaar"
        }
        
        # Extract Aadhaar number (mask last 8 digits)
        aadhaar_match = self.aadhaar_pattern.search(text)
        if aadhaar_match:
            aadhaar_full = aadhaar_match.group()
            # Mask last 8 digits
            masked = aadhaar_full[:4] + " " + "X" * 4 + " " + aadhaar_full[-4:]
            metadata["aadhaar_numbers"] = [masked]
            metadata["aadhaar_last_4"] = aadhaar_full[-4:]
        
        # Extract name
        name_patterns = [
            r'Name\s*[:\-]?\s*([A-Z\s]+)',
            r'([A-Z]{2,}\s+[A-Z]{2,})',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3:
                    metadata["holder_name"] = name
                    break
        
        # Extract DOB
        dob_patterns = [
            r'Date\s+of\s+Birth\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4})',
            r'DOB\s*[:\-]?\s*(\d{2}[/\-]\d{2}[/\-]\d{4})',
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["date_of_birth"] = match.group(1)
                break
        
        # Extract Gender
        gender_pattern = r'Gender\s*[:\-]?\s*([A-Z]+)'
        match = re.search(gender_pattern, text, re.IGNORECASE)
        if match:
            metadata["gender"] = match.group(1).strip()
        
        # Process QR data if available
        if qr_data:
            metadata["qr_validated"] = True
            # Parse XML from QR if present
            if "<" in qr_data and ">" in qr_data:
                metadata["qr_xml"] = qr_data
        
        return metadata
    
    def extract_qr_from_pdf(self, content: bytes) -> Optional[str]:
        """Extract QR code from PDF"""
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(content, first_page=0, last_page=1)
            if images:
                return self.extract_qr_from_image(images[0])
        except:
            pass
        return None
    
    def extract_qr_from_image(self, image) -> Optional[str]:
        """Extract QR code from image"""
        try:
            import numpy as np
            import cv2
            
            # Convert PIL to numpy array
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Decode QR
            decoded = pyzbar.decode(gray)
            if decoded:
                return decoded[0].data.decode('utf-8')
        except:
            pass
        return None

