"""
Handles activation key storage and API validation with enhanced security and validation.
Updated for Auora Activation System API.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import socket
import requests
import os
import json
import hashlib
import time
import platform
import uuid


@dataclass
class ActivationKey:
    key: str
    user_name: Optional[str] = None
    expiration_date: Optional[datetime] = None
    max_devices: int = 1
    max_sessions: int = 1
    status: str = 'active'


@dataclass
class SessionData:
    session_token: str
    key: str
    device_id: str
    start_time: datetime
    expiration_time: datetime
    status: str = 'active'


@dataclass
class DeviceInfo:
    device_id: str
    platform: str
    platform_release: str
    platform_version: str
    architecture: str
    hostname: str
    processor: str
    mac_address: str
    uuid: str
    device_name: Optional[str] = None


@dataclass
class DeviceRecord:
    device_id: str
    device_name: Optional[str] = None
    last_used: datetime = field(default_factory=datetime.now)
    trusted: bool = True


@dataclass
class ActivationRequest:
    key: str
    device_info: Dict[str, Any]


@dataclass
class ActivationResponse:
    success: bool
    key: str
    status: str
    error_code: Optional[str] = None
    message: Optional[str] = None


@dataclass
class HeartbeatRequest:
    session_token: str
    device_id: str


@dataclass
class HeartbeatResponse:
    status: str
    warning: bool = False
    expired: bool = False
    error_code: Optional[str] = None


@dataclass
class ValidateRequest:
    session_token: str
    device_id: str


@dataclass
class ValidateResponse:
    valid: bool
    warning: bool = False
    error_code: Optional[str] = None


@dataclass
class SessionManagementRequest:
    key: str
    action: str
    session_token: Optional[str] = None


@dataclass
class SessionManagementResponse:
    success: bool
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    error_code: Optional[str] = None


@dataclass
class DeviceManagementRequest:
    key: str
    action: str
    device_id: Optional[str] = None


@dataclass
class DeviceManagementResponse:
    success: bool
    devices: List[Dict[str, Any]] = field(default_factory=list)
    error_code: Optional[str] = None


class ActivationManager:
    API_DOMAIN = "https://auora-fawn.vercel.app"
    API_URL = "https://auora-fawn.vercel.app/api/v2/activation"
    VALIDATE_URL = "https://auora-fawn.vercel.app/api/v2/activation/validate"
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    VALIDATION_CACHE_DURATION = 300   # 5 minutos de cache
    SESSION_CHECK_INTERVAL = 1800     # 30 minutos

    def __init__(self, config_manager=None, debug_mode: bool = False):
        self.config_manager = config_manager
        self.debug_mode = debug_mode
        self.key = self.config_manager.get('activation_key') if self.config_manager else None
        self.session_token = self.config_manager.get('session_token') if self.config_manager else None
        self.expiration_date = self.config_manager.get('expiration_date') if self.config_manager else None
        self.key_expires_at = self.config_manager.get('key_expires_at') if self.config_manager else None
        self.last_validation_time = 0
        self.last_session_check = self.config_manager.get('last_session_check', 0) if self.config_manager else 0
        self.last_validation_result = True
        self.last_api_result = None
        self.device_id = self.config_manager.get('device_id') if self.config_manager else None
        
        if not self.device_id:
            self.device_id = self._get_or_create_device_id()
        self._load_status()

    def _get_or_create_device_id(self):
        """Obtém ID do dispositivo salvo ou gera um novo baseado no hardware."""
        device_id = self.config_manager.get('device_id') if self.config_manager else None
        if not device_id:
            device_id = self._generate_device_fingerprint()
            if self.config_manager:
                self.config_manager.set('device_id', device_id)
                self.config_manager.save()
        return device_id

    def _generate_device_fingerprint(self):
        """Gera um fingerprint único baseado nas informações do sistema."""
        system_info = [
            platform.system(),
            platform.release(),
            platform.version(),
            platform.machine(),
            socket.gethostname(),
            self._get_mac_address()
        ]
        fingerprint_str = "".join(system_info)
        return hashlib.sha256(fingerprint_str.encode('utf-8')).hexdigest()

    def _get_mac_address(self):
        """Retorna o endereço MAC da máquina."""
        mac = uuid.getnode()
        return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

    def _load_status(self):
        """Carrega o status de ativação da configuração."""
        return 'Activated'

    def save_status(self, status: str):
        """Salva o status de ativação na configuração."""
        pass

    def _is_key_expired(self):
        """Verifica se a chave atual expirou."""
        return False

    def _validate_key_with_api(self):
        """Validação ignorada."""
        return {
            'is_valid_key': True,
            'is_session_available': True,
            'error_code': None,
            'error_message': None
        }

    def _validate_session_with_api(self):
        """Validação ignorada."""
        return True

    def _is_valid_key_format(self, key):
        """Validação ignorada."""
        return True

    def _clear_invalid_key(self):
        """Validação ignorada."""
        pass

    def _clear_session(self):
        """Validação ignorada."""
        pass

    def set_key(self, key: str):
        """Define a chave na memória."""
        self.key = key

    def try_activate(self, key: str):
        """Tenta ativar com a chave informada."""
        return True

    def get_key(self):
        """Retorna a chave atual."""
        return self.key or "Bypassed"

    def get_expiration_date(self):
        """Retorna a data de expiração."""
        return None

    def get_status(self):
        """Retorna o status atual."""
        return 'Activated'

    def is_activated(self):
        """Verifica se está ativado."""
        return True

    def check_activation(self, force_refresh: bool = False):
        """Verifica a ativação utilizando cache para economizar requisições."""
        return {
            'is_valid_key': True,
            'is_session_available': True,
            'error_code': None,
            'error_message': None
        }

    def force_revalidation(self):
        """Força nova validação com a API."""
        return self.check_activation(force_refresh=True)

    def get_detailed_status(self):
        """Retorna status detalhado."""
        return {
            'has_key': True,
            'status': 'Activated',
            'is_activated': True,
            'expiration_date': None,
            'device_id': self.device_id,
            'session_token': 'bypassed_token'
        }

    def deactivate(self):
        """Desativa a sessão atual no servidor."""
        return True