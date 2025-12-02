from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Admin:
    """Admin aggregate - Represents system administrators"""
    
    id: Optional[int]
    email: str
    name: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def is_valid_email(self) -> bool:
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email) is not None
    
    def is_authorized_for_admin_panel(self) -> bool:
        """Check if admin is authorized for admin panel access"""
        return self.email is not None and self.name is not None
    
    def validate(self) -> bool:
        """Validate admin data"""
        return (
            self.email is not None and 
            self.name is not None and 
            len(self.name.strip()) > 0 and
            self.is_valid_email()
        )