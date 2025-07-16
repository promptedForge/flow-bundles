"""
Authentication and API token management for Skyward Assistable Bundle

Handles secure storage and retrieval of API tokens, OAuth flows,
and authentication state management across components.
"""

import os
import json
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired"""
    pass

class AuthManager:
    """Centralized authentication management for all APIs"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.tokens = {}
        self.token_metadata = {}
        self._setup_encryption(encryption_key)
        self._load_stored_tokens()
    
    def _setup_encryption(self, key: Optional[str] = None):
        """Setup encryption for secure token storage"""
        if key:
            # Use provided key
            key_bytes = key.encode()
        else:
            # Generate key from environment or create new one
            key_bytes = os.getenv("AUTH_ENCRYPTION_KEY", "skyward-default-key-2024").encode()
        
        # Derive encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'skyward_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        self.cipher_suite = Fernet(key)
    
    def _load_stored_tokens(self):
        """Load previously stored tokens from secure storage"""
        token_file = os.getenv("AUTH_TOKEN_FILE", ".auth_tokens")
        if os.path.exists(token_file):
            try:
                with open(token_file, 'rb') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                        token_data = json.loads(decrypted_data.decode())
                        self.tokens = token_data.get("tokens", {})
                        self.token_metadata = token_data.get("metadata", {})
            except Exception as e:
                print(f"Warning: Could not load stored tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to secure storage"""
        token_file = os.getenv("AUTH_TOKEN_FILE", ".auth_tokens")
        try:
            token_data = {
                "tokens": self.tokens,
                "metadata": self.token_metadata,
                "updated_at": datetime.now().isoformat()
            }
            encrypted_data = self.cipher_suite.encrypt(json.dumps(token_data).encode())
            with open(token_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Warning: Could not save tokens: {e}")
    
    def get_assistable_token(self) -> str:
        """Get Assistable AI API token"""
        # Try stored token first
        if "assistable" in self.tokens:
            token = self.tokens["assistable"]
            if self._is_token_valid("assistable"):
                return token
        
        # Try environment variable
        token = os.getenv("ASSISTABLE_API_TOKEN")
        if token:
            self.store_token("assistable", token, token_type="api_key")
            return token
        
        raise AuthenticationError("No valid Assistable AI token found")
    
    def get_ghl_token(self, location_id: Optional[str] = None) -> str:
        """Get GoHighLevel API token"""
        # For location-specific tokens
        if location_id and f"ghl_{location_id}" in self.tokens:
            if self._is_token_valid(f"ghl_{location_id}"):
                return self.tokens[f"ghl_{location_id}"]
        
        # Try main GHL token
        if "ghl" in self.tokens:
            if self._is_token_valid("ghl"):
                return self.tokens["ghl"]
        
        # Try environment variable
        token = os.getenv("GHL_API_KEY")
        if token:
            self.store_token("ghl", token, token_type="api_key")
            return token
        
        raise AuthenticationError("No valid GoHighLevel token found")
    
    def store_token(self, service: str, token: str, token_type: str = "api_key", 
                   expires_in: Optional[int] = None, location_id: Optional[str] = None):
        """Store API token securely"""
        
        # Generate key for token storage
        token_key = f"{service}_{location_id}" if location_id else service
        
        self.tokens[token_key] = token
        self.token_metadata[token_key] = {
            "service": service,
            "token_type": token_type,
            "stored_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else None,
            "location_id": location_id
        }
        
        self._save_tokens()
    
    def _is_token_valid(self, token_key: str) -> bool:
        """Check if stored token is still valid"""
        if token_key not in self.token_metadata:
            return False
        
        metadata = self.token_metadata[token_key]
        
        # Check expiration
        if metadata.get("expires_at"):
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            if datetime.now() >= expires_at:
                return False
        
        return True
    
    def refresh_ghl_token(self, location_id: Optional[str] = None) -> str:
        """Refresh GoHighLevel OAuth token"""
        client_id = os.getenv("GHL_CLIENT_ID")
        client_secret = os.getenv("GHL_CLIENT_SECRET")
        
        if not all([client_id, client_secret]):
            raise AuthenticationError("GHL OAuth credentials not configured")
        
        # Get refresh token
        token_key = f"ghl_{location_id}" if location_id else "ghl"
        refresh_token = self.token_metadata.get(token_key, {}).get("refresh_token")
        
        if not refresh_token:
            raise AuthenticationError("No refresh token available")
        
        # Make refresh request
        token_url = "https://services.leadconnectorhq.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        try:
            response = httpx.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data["access_token"]
            new_refresh_token = token_data.get("refresh_token", refresh_token)
            expires_in = token_data.get("expires_in", 3600)
            
            # Store new tokens
            self.store_token(
                service="ghl",
                token=access_token,
                token_type="oauth",
                expires_in=expires_in,
                location_id=location_id
            )
            
            # Update refresh token in metadata
            self.token_metadata[token_key]["refresh_token"] = new_refresh_token
            self._save_tokens()
            
            return access_token
            
        except httpx.RequestError as e:
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    def validate_token(self, service: str, token: str) -> bool:
        """Validate token by making test API call"""
        
        if service == "assistable":
            return self._validate_assistable_token(token)
        elif service == "ghl":
            return self._validate_ghl_token(token)
        
        return False
    
    def _validate_assistable_token(self, token: str) -> bool:
        """Validate Assistable AI token"""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = httpx.get(
                "https://api.assistable.ai/v2/health",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _validate_ghl_token(self, token: str) -> bool:
        """Validate GoHighLevel token"""
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Version": "2021-07-28"
            }
            
            response = httpx.get(
                "https://services.leadconnectorhq.com/locations",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_auth_headers(self, service: str, location_id: Optional[str] = None) -> Dict[str, str]:
        """Get properly formatted auth headers for API calls"""
        
        if service == "assistable":
            token = self.get_assistable_token()
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "Skyward-Langflow-Bundle/1.0.0"
            }
        
        elif service == "ghl":
            token = self.get_ghl_token(location_id)
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Version": "2021-07-28",
                "User-Agent": "Skyward-Langflow-Bundle/1.0.0"
            }
        
        else:
            raise ValueError(f"Unknown service: {service}")
    
    def clear_tokens(self, service: Optional[str] = None):
        """Clear stored tokens"""
        if service:
            # Clear specific service tokens
            keys_to_remove = [key for key in self.tokens.keys() if key.startswith(service)]
            for key in keys_to_remove:
                del self.tokens[key]
                if key in self.token_metadata:
                    del self.token_metadata[key]
        else:
            # Clear all tokens
            self.tokens.clear()
            self.token_metadata.clear()
        
        self._save_tokens()
    
    def get_token_info(self) -> Dict[str, Any]:
        """Get information about stored tokens"""
        info = {}
        
        for token_key, metadata in self.token_metadata.items():
            info[token_key] = {
                "service": metadata.get("service"),
                "token_type": metadata.get("token_type"),
                "stored_at": metadata.get("stored_at"),
                "expires_at": metadata.get("expires_at"),
                "is_valid": self._is_token_valid(token_key),
                "location_id": metadata.get("location_id")
            }
        
        return info

# Global auth manager instance
auth_manager = AuthManager()
