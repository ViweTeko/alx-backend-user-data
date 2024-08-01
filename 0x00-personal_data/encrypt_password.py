#!/usr/bin/env python3
""" This script encrypts passwords"""
import bcrypt


def hash_password(password: str) -> bytes:
    """Hashes password using random salt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """Checks if hashed password formed from password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
