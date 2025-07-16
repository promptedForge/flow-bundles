"""
Input validation and sanitization utilities for Skyward Assistable Bundle

Provides comprehensive validation for API inputs, user data, and configuration
to ensure security and data integrity across all components.
"""

import re
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class Validators:
    """Collection of validation utilities"""
    
    # Regular expressions for common patterns
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
    ASSISTABLE_ID_PATTERN = re.compile(r'^asst_[a-zA-Z0-9]{8,}$')
    GHL_ID_PATTERN = re.compile(r'^[a-zA-Z0-9]{20,}$')
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            raise ValidationError("Email must be a non-empty string")
        
        try:
            validate_email(email)
            return True
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email format: {str(e)}")
    
    @staticmethod
    def validate_phone_number(phone: str, region: str = "US") -> str:
        """Validate and format phone number"""
        if not phone or not isinstance(phone, str):
            raise ValidationError("Phone number must be a non-empty string")
        
        try:
            parsed_number = phonenumbers.parse(phone, region)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Invalid phone number")
            
            # Return formatted number
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
        except NumberParseException as e:
            raise ValidationError(f"Invalid phone number format: {str(e)}")
    
    @staticmethod
    def validate_uuid(value: str) -> bool:
        """Validate UUID format"""
        if not value or not isinstance(value, str):
            raise ValidationError("UUID must be a non-empty string")
        
        if not Validators.UUID_PATTERN.match(value):
            raise ValidationError("Invalid UUID format")
        
        return True
    
    @staticmethod
    def validate_assistable_id(assistant_id: str) -> bool:
        """Validate Assistable AI assistant ID format"""
        if not assistant_id or not isinstance(assistant_id, str):
            raise ValidationError("Assistant ID must be a non-empty string")
        
        if not Validators.ASSISTABLE_ID_PATTERN.match(assistant_id):
            raise ValidationError("Invalid Assistable AI assistant ID format (should start with 'asst_')")
        
        return True
    
    @staticmethod
    def validate_ghl_id(ghl_id: str, id_type: str = "contact") -> bool:
        """Validate GoHighLevel ID format"""
        if not ghl_id or not isinstance(ghl_id, str):
            raise ValidationError(f"{id_type} ID must be a non-empty string")
        
        if not Validators.GHL_ID_PATTERN.match(ghl_id):
            raise ValidationError(f"Invalid GoHighLevel {id_type} ID format")
        
        return True
    
    @staticmethod
    def validate_text_input(text: str, min_length: int = 1, max_length: int = 5000, 
                           allow_html: bool = False) -> str:
        """Validate and sanitize text input"""
        if not isinstance(text, str):
            raise ValidationError("Text input must be a string")
        
        # Check length
        if len(text) < min_length:
            raise ValidationError(f"Text must be at least {min_length} characters long")
        
        if len(text) > max_length:
            raise ValidationError(f"Text must not exceed {max_length} characters")
        
        # Sanitize if HTML not allowed
        if not allow_html:
            # Remove potential HTML/script tags
            text = re.sub(r'<[^>]+>', '', text)
            # Remove potential script injections
            text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        
        # Remove null bytes and other control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return text.strip()
    
    @staticmethod
    def validate_json_data(data: Union[str, Dict, List]) -> Dict[str, Any]:
        """Validate and parse JSON data"""
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON format: {str(e)}")
        elif isinstance(data, (dict, list)):
            parsed_data = data
        else:
            raise ValidationError("Data must be JSON string, dict, or list")
        
        return parsed_data
    
    @staticmethod
    def validate_batch_data(batch_data: List[Dict[str, Any]], 
                           max_batch_size: int = 100) -> List[Dict[str, Any]]:
        """Validate batch processing data"""
        if not isinstance(batch_data, list):
            raise ValidationError("Batch data must be a list")
        
        if len(batch_data) == 0:
            raise ValidationError("Batch data cannot be empty")
        
        if len(batch_data) > max_batch_size:
            raise ValidationError(f"Batch size cannot exceed {max_batch_size} items")
        
        # Validate each item is a dictionary
        for i, item in enumerate(batch_data):
            if not isinstance(item, dict):
                raise ValidationError(f"Batch item {i} must be a dictionary")
        
        return batch_data
    
    @staticmethod
    def validate_api_token(token: str, token_type: str = "bearer") -> bool:
        """Validate API token format"""
        if not token or not isinstance(token, str):
            raise ValidationError("API token must be a non-empty string")
        
        # Remove any whitespace
        token = token.strip()
        
        # Basic length check
        if len(token) < 10:
            raise ValidationError("API token appears to be too short")
        
        # Check for common token prefixes
        if token_type == "assistable" and not token.startswith(("asst_", "sk-")):
            raise ValidationError("Assistable AI token should start with 'asst_' or 'sk-'")
        
        # Check for suspicious characters
        if re.search(r'[<>"\'\s]', token):
            raise ValidationError("API token contains invalid characters")
        
        return True
    
    @staticmethod
    def validate_location_id(location_id: str) -> bool:
        """Validate GoHighLevel location ID"""
        return Validators.validate_ghl_id(location_id, "location")
    
    @staticmethod
    def validate_conversation_id(conversation_id: str) -> bool:
        """Validate conversation ID (can be UUID or custom format)"""
        if not conversation_id or not isinstance(conversation_id, str):
            raise ValidationError("Conversation ID must be a non-empty string")
        
        # Allow UUID format or custom format
        if not (Validators.UUID_PATTERN.match(conversation_id) or 
                Validators.ALPHANUMERIC_PATTERN.match(conversation_id)):
            raise ValidationError("Invalid conversation ID format")
        
        return True
    
    @staticmethod
    def validate_message_content(content: str) -> str:
        """Validate and sanitize message content"""
        if not content or not isinstance(content, str):
            raise ValidationError("Message content must be a non-empty string")
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Check for minimum content
        if len(content) < 1:
            raise ValidationError("Message content cannot be empty")
        
        # Check for maximum length
        if len(content) > 2000:
            raise ValidationError("Message content too long (max 2000 characters)")
        
        return content
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename or not isinstance(filename, str):
            raise ValidationError("Filename must be a non-empty string")
        
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure it's not empty after sanitization
        if not filename:
            filename = f"file_{uuid.uuid4().hex[:8]}"
        
        return filename
    
    @staticmethod
    def validate_hook_data(hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate runtime hook data structure"""
        required_fields = ["hook_type", "component", "data"]
        
        Validators.validate_required_fields(hook_data, required_fields)
        
        # Validate hook_type
        valid_hook_types = ["pre_task", "start_task", "end_run", "error", "custom"]
        if hook_data["hook_type"] not in valid_hook_types:
            raise ValidationError(f"Invalid hook_type. Must be one of: {', '.join(valid_hook_types)}")
        
        # Validate component name
        component = hook_data["component"]
        if not isinstance(component, str) or not Validators.ALPHANUMERIC_PATTERN.match(component):
            raise ValidationError("Component name must be alphanumeric with underscores/hyphens")
        
        # Validate data is a dictionary
        if not isinstance(hook_data["data"], dict):
            raise ValidationError("Hook data must be a dictionary")
        
        return hook_data

class InputSanitizer:
    """Sanitization utilities for user inputs"""
    
    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """Remove potentially dangerous HTML elements"""
        if not html_content:
            return ""
        
        # Simple HTML tag removal (for production, consider using bleach library)
        clean_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        clean_content = re.sub(r'<[^>]+>', '', clean_content)
        
        return clean_content
    
    @staticmethod
    def sanitize_sql(input_str: str) -> str:
        """Basic SQL injection prevention"""
        if not input_str:
            return ""
        
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r'union\s+select', r'drop\s+table', r'delete\s+from',
            r'insert\s+into', r'update\s+set', r'exec\s*\(',
            r'script\s*:', r'javascript\s*:'
        ]
        
        clean_str = input_str
        for pattern in dangerous_patterns:
            clean_str = re.sub(pattern, '', clean_str, flags=re.IGNORECASE)
        
        return clean_str
    
    @staticmethod
    def sanitize_for_logging(data: Any) -> str:
        """Sanitize data for safe logging (remove sensitive info)"""
        if isinstance(data, dict):
            sanitized = {}
            sensitive_keys = ['password', 'token', 'key', 'secret', 'auth']
            
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "***REDACTED***"
                else:
                    sanitized[key] = InputSanitizer.sanitize_for_logging(value)
            
            return json.dumps(sanitized, indent=2)
        
        elif isinstance(data, list):
            return json.dumps([InputSanitizer.sanitize_for_logging(item) for item in data], indent=2)
        
        elif isinstance(data, str):
            # Redact potential tokens or sensitive data
            if len(data) > 20 and any(char in data for char in ['_', '-']) and data.replace('_', '').replace('-', '').isalnum():
                return "***REDACTED_TOKEN***"
            return data
        
        else:
            return str(data)

# Convenience functions for common validations
def validate_contact_data(contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate contact creation/update data"""
    # Email or phone required
    if not any(key in contact_data for key in ['email', 'phone']):
        raise ValidationError("Either email or phone is required for contact")
    
    # Validate email if present
    if 'email' in contact_data:
        Validators.validate_email(contact_data['email'])
    
    # Validate phone if present
    if 'phone' in contact_data:
        contact_data['phone'] = Validators.validate_phone_number(contact_data['phone'])
    
    # Sanitize text fields
    text_fields = ['firstName', 'lastName', 'first_name', 'last_name', 'name']
    for field in text_fields:
        if field in contact_data:
            contact_data[field] = Validators.validate_text_input(
                contact_data[field], 
                min_length=1, 
                max_length=100
            )
    
    return contact_data

def validate_assistant_data(assistant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate assistant creation/update data"""
    required_fields = ['name']
    Validators.validate_required_fields(assistant_data, required_fields)
    
    # Validate and sanitize text fields
    assistant_data['name'] = Validators.validate_text_input(
        assistant_data['name'], 
        min_length=1, 
        max_length=200
    )
    
    if 'description' in assistant_data:
        assistant_data['description'] = Validators.validate_text_input(
            assistant_data['description'], 
            min_length=0, 
            max_length=1000
        )
    
    if 'prompt' in assistant_data:
        assistant_data['prompt'] = Validators.validate_text_input(
            assistant_data['prompt'], 
            min_length=1, 
            max_length=5000
        )
    
    return assistant_data

def validate_api_operation_data(operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data for specific API operations"""
    
    if operation == "create_assistant":
        return validate_assistant_data(data)
    
    elif operation == "create_contact":
        return validate_contact_data(data)
    
    elif operation == "make_ai_call":
        required_fields = ['assistant_id', 'contact_id', 'number_pool_id']
        Validators.validate_required_fields(data, required_fields)
        
        Validators.validate_assistable_id(data['assistant_id'])
        Validators.validate_ghl_id(data['contact_id'], 'contact')
        Validators.validate_ghl_id(data['number_pool_id'], 'number_pool')
    
    elif operation == "chat_completion":
        required_fields = ['input']
        Validators.validate_required_fields(data, required_fields)
        
        data['input'] = Validators.validate_message_content(data['input'])
    
    return data
