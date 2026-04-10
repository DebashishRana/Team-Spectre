from dataclasses import dataclass, asdict
from typing import Optional
import re

@dataclass
class UniversalSchema:
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # YYYY-MM-DD
    gender: Optional[str] = None
    id_number: Optional[str] = None
    document_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    def clean(self):
        """Clean and standardize fields"""
        
        if self.id_number:
            # remove spaces
            self.id_number = re.sub(r"\s+", "", self.id_number)

            # Aadhaar validation (12 digits)
            if not re.fullmatch(r"\d{12}", self.id_number):
                self.id_number = None

        if self.date_of_birth:
            # convert DD/MM/YYYY → YYYY-MM-DD
            parts = re.split(r"[/-]", self.date_of_birth)
            if len(parts) == 3:
                if len(parts[2]) == 4:  # DD/MM/YYYY
                    self.date_of_birth = f"{parts[2]}-{parts[1]}-{parts[0]}"

        if self.full_name:
            self.full_name = self.full_name.strip().title()

        if self.gender:
            self.gender = self.gender.capitalize()

        return self

    def to_dict(self):
        return asdict(self)