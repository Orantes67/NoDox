#!/usr/bin/env python3
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodox.nodox import main

if __name__ == "__main__":
    main()
