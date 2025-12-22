#!/usr/bin/env python
"""
Script para generar clave Fernet para NoDox
Uso: python generate_key.py
"""

from cryptography.fernet import Fernet

def generate_key():
    """Generar una nueva clave Fernet"""
    key = Fernet.generate_key().decode()
    return key

if __name__ == "__main__":
    key = generate_key()
    print("\n" + "="*70)
    print("🔑 CLAVE FERNET GENERADA PARA NODOX")
    print("="*70)
    print(f"\nClave: {key}\n")
    print("PRÓXIMOS PASOS:")
    print("-" * 70)
    print("\n1. Opción A - Variable de entorno (Windows PowerShell):")
    print(f'   $env:NODOX_KEY = "{key}"')
    print("\n2. Opción A - Variable de entorno (Windows CMD):")
    print(f'   set NODOX_KEY={key}')
    print("\n3. Opción A - Variable de entorno (Linux/Mac):")
    print(f'   export NODOX_KEY="{key}"')
    print("\n4. Opción B - Guardar en archivo .env.local:")
    print(f'   NODOX_KEY={key}')
    print("\n" + "="*70)
    print("⚠️  IMPORTANTE:")
    print("- No compartas esta clave públicamente")
    print("- Guárdala en un lugar seguro")
    print("- La necesitarás para descifrar archivos después")
    print("="*70 + "\n")

