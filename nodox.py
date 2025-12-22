import argparse
import sys
import os

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nodox.core.scanner import scan_files, scan_and_collect
from nodox.core.encryptor import encrypt_file_list
from nodox.core.decryptor import decrypt_files
from nodox.core.exfil import monitor_exfiltration
from nodox.core.canary import setup_canary_files, monitor_canary_files, setup_canary
from nodox.core.protect import protect


VERSION = "0.1.0"


def banner():
    print("""
 ███╗   ██╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗
 ████╗  ██║██╔═══██╗██╔══██╗██╔═══██╗╚██╗██╔╝
 ██╔██╗ ██║██║   ██║██║  ██║██║   ██║ ╚███╔╝ 
 ██║╚██╗██║██║   ██║██║  ██║██║   ██║ ██╔██╗ 
 ██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██╔╝ ██╗
 ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
        NoDox – Neutralizing Doxware
""")


def main():
    parser = argparse.ArgumentParser(
        description="NoDox - Reduce el impacto del ransomware moderno"
    )

    subparsers = parser.add_subparsers(dest="command")

    # scan
    scan_parser = subparsers.add_parser(
        "scan", help="Escanear archivos en busca de datos sensibles"
    )
    scan_parser.add_argument("-p", "--path", default=".", help="Ruta a escanear")

    # encrypt (manual)
    encrypt_parser = subparsers.add_parser(
        "encrypt", help="Cifrado manual (recomendado usar protect)"
    )
    encrypt_parser.add_argument("-p", "--path", default=".", help="Ruta base")

    # decrypt
    decrypt_parser = subparsers.add_parser(
        "decrypt", help="Descifrar archivos cifrados por NoDox"
    )
    decrypt_parser.add_argument("-p", "--path", default=".", help="Ruta base")

    # canary (solo setup manual)
    canary_parser = subparsers.add_parser(
        "canary", help="Crear canary files (monitoreo se usa en protect)"
    )
    canary_parser.add_argument("-p", "--path", default=".", help="Ruta base")

    # monitor (exfil manual)
    subparsers.add_parser(
        "monitor", help="Monitorear exfiltración (manual)"
    )

    # protect
    subparsers.add_parser(
        "protect", help="Modo protección completa (RECOMENDADO)"
    )

    # version / about
    subparsers.add_parser("version", help="Mostrar versión")
    subparsers.add_parser("about", help="Acerca de NoDox")

    args = parser.parse_args()

    if not args.command:
        banner()
        parser.print_help()
        sys.exit(0)

    if args.command == "scan":
        scan_files(args.path)

    elif args.command == "encrypt":
        # Escanear y cifrar
        sensitive_files = scan_and_collect(args.path)
        if sensitive_files:
            encrypt_file_list(sensitive_files)

    elif args.command == "decrypt":
        decrypt_files(args.path)

    elif args.command == "canary":
        setup_canary(True, args.path)

    elif args.command == "monitor":
        monitor_exfiltration()

    elif args.command == "protect":
        protect()

    elif args.command == "version":
        print(f"NoDox version {VERSION}")

    elif args.command == "about":
        print(
            "NoDox es una herramienta open-source para reducir el daño del ransomware\n"
            "neutralizando el doxxing y la extorsión de datos."
        )


if __name__ == "__main__":
    main()
