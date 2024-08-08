#!/usr/bin/env python3
""" Authentication module for the API"""
import re
from typing import List, TypeVar
from flask import request


class Auth:
    """Authentication class"""
    def authorization_header(self, request=None) -> str:
        """Gets authorization header"""
        if request is not None:
            return request.headers.get('Authorization', None)
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """Gets current user"""
        return None

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """Checks if path requires authentication"""
        if path is not None and excluded_paths is not None:
            for exclusion_path in map(lambda x: x.strip(), excluded_paths):
                pattern = ''
                if exclusion_path[-1] == '*':
                    pattern = f'{exclusion_path[0:-1]}.*'
                elif exclusion_path[-1] == '/':
                    pattern = f'{exclusion_path[0:-1]}/*'
                else:
                    pattern = f'{exlcusion_path}/*'
                if re.match(pattern, path):
                    return False
        return True
