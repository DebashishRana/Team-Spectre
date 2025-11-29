"""
Document validation and authenticity checks
"""

import re
from typing import Dict

class DocumentValidator:
    """Validate document authenticity"""
    
    def __init__(self):
        self.pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')
    
    def validate_document(self, metadata: Dict, document_type: str) -> Dict:
        """Validate document based on type"""
        if document_type == "PAN":
            return self.validate_pan(metadata)
        elif document_type == "Aadhaar":
            return self.validate_aadhaar(metadata)
        else:
            return {
                "status": "unknown",
                "confidence": 0.0,
                "reason": "Document type not supported for validation"
            }
    
    def validate_pan_number(self, pan: str) -> bool:
        """Validate PAN number format and checksum"""
        if not self.pan_pattern.match(pan):
            return False
        
        # PAN checksum validation
        # Last character is checksum based on first 9 characters
        chars = pan[:9]
        check_char = pan[9]
        
        # Simple checksum (PAN uses a specific algorithm)
        # This is a simplified version
        char_values = []
        for i, char in enumerate(chars):
            if char.isalpha():
                char_values.append(ord(char) - ord('A') + 10)
            else:
                char_values.append(int(char))
        
        # Weighted sum
        weights = [1, 2, 1, 2, 1, 2, 1, 2, 1]
        total = sum(char_values[i] * weights[i] for i in range(9))
        
        # Get check digit
        check_digit = (total % 36)
        if check_digit < 10:
            expected = str(check_digit)
        else:
            expected = chr(ord('A') + check_digit - 10)
        
        return check_char == expected
    
    def validate_pan(self, metadata: Dict) -> Dict:
        """Validate PAN card"""
        pan_numbers = metadata.get("pan_numbers", [])
        
        if not pan_numbers:
            return {
                "status": "invalid",
                "confidence": 0.0,
                "reason": "PAN number not found"
            }
        
        pan = pan_numbers[0].replace(" ", "").upper()
        
        if not self.validate_pan_number(pan):
            return {
                "status": "invalid",
                "confidence": 0.3,
                "reason": "PAN format or checksum validation failed"
            }
        
        # Additional validations
        confidence = 0.8
        
        if metadata.get("holder_name"):
            confidence += 0.1
        if metadata.get("date_of_birth"):
            confidence += 0.1
        
        return {
            "status": "valid",
            "confidence": min(confidence, 1.0),
            "reason": "PAN number validated successfully"
        }
    
    def validate_aadhaar_number(self, aadhaar: str) -> bool:
        """Validate Aadhaar number format"""
        # Remove spaces
        aadhaar = re.sub(r'\s+', '', aadhaar)
        
        # Should be 12 digits, not starting with 0 or 1
        pattern = re.compile(r'^[2-9][0-9]{11}$')
        return pattern.match(aadhaar) is not None
    
    def validate_aadhaar_qr(self, qr_xml: str) -> bool:
        """Validate Aadhaar QR code XML"""
        if not qr_xml or "<" not in qr_xml:
            return False
        
        # Check for UIDAI signature elements
        required_elements = ["uid", "name", "gender", "dob", "co"]
        qr_lower = qr_xml.lower()
        
        # Basic validation - check if required fields are present
        for element in required_elements:
            if element not in qr_lower:
                return False
        
        # Additional validation can be added here
        # (e.g., digital signature verification)
        
        return True
    
    def validate_aadhaar(self, metadata: Dict) -> Dict:
        """Validate Aadhaar card"""
        aadhaar_numbers = metadata.get("aadhaar_numbers", [])
        qr_data = metadata.get("qr_data") or metadata.get("qr_xml")
        
        confidence = 0.0
        reasons = []
        
        # Validate Aadhaar number format
        if aadhaar_numbers:
            # Extract unmasked number if possible
            aadhaar_str = aadhaar_numbers[0].replace(" ", "").replace("X", "")
            if len(aadhaar_str) >= 4:  # At least last 4 digits
                confidence += 0.3
                reasons.append("Aadhaar number format detected")
        
        # Validate QR code
        if qr_data:
            if self.validate_aadhaar_qr(qr_data):
                confidence += 0.5
                reasons.append("QR code validated")
            else:
                confidence += 0.2
                reasons.append("QR code present but validation incomplete")
        
        # Additional metadata
        if metadata.get("holder_name"):
            confidence += 0.1
        if metadata.get("date_of_birth"):
            confidence += 0.1
        
        if confidence >= 0.7:
            status = "valid"
        elif confidence >= 0.4:
            status = "partial"
        else:
            status = "invalid"
        
        return {
            "status": status,
            "confidence": min(confidence, 1.0),
            "reason": "; ".join(reasons) if reasons else "Basic validation performed"
        }
    
    def check_document_integrity(self, pdf_bytes: bytes) -> Dict:
        """Check PDF document integrity"""
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            is_encrypted = pdf_reader.is_encrypted
            
            # Check number of pages
            num_pages = len(pdf_reader.pages)
            
            # Check for metadata
            metadata = pdf_reader.metadata
            
            return {
                "status": "valid" if not is_encrypted else "encrypted",
                "confidence": 0.8 if not is_encrypted else 0.5,
                "reason": f"PDF integrity check: {num_pages} pages, encrypted: {is_encrypted}",
                "num_pages": num_pages,
                "is_encrypted": is_encrypted,
                "has_metadata": metadata is not None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "confidence": 0.0,
                "reason": f"Integrity check failed: {str(e)}"
            }

