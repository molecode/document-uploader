#!/usr/bin/env python3
"""
Helper script to generate password hash for the document uploader.
Usage: python generate_password.py
"""
import secrets
from getpass import getpass
from werkzeug.security import generate_password_hash

def main():
    print("=" * 60)
    print("Document Uploader - Password Generator")
    print("=" * 60)
    print()

    # Generate secret key
    secret_key = secrets.token_hex(32)
    print("1. Secret Key (for SECRET_KEY):")
    print(f"   {secret_key}")
    print()

    # Generate password hash
    print("2. Password Hash (for PASSWORD_HASH):")
    password = getpass("   Enter your desired password: ")

    if not password:
        print("   Error: Password cannot be empty!")
        return

    password_confirm = getpass("   Confirm password: ")

    if password != password_confirm:
        print("   Error: Passwords do not match!")
        return

    password_hash = generate_password_hash(password)
    # Escape $ for Docker Compose
    password_hash_escaped = password_hash.replace('$', '$$')

    print(f"   {password_hash}")
    print()

    print("=" * 60)
    print("Add these values to your .env file:")
    print("=" * 60)
    print(f"SECRET_KEY={secret_key}")
    print(f'PASSWORD_HASH="{password_hash_escaped}"')
    print()
    print("Note: $ characters are automatically escaped as $$ for Docker Compose")

if __name__ == "__main__":
    main()
