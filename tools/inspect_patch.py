#!/usr/bin/env python3
"""
inspect_patch.py — Analisa um arquivo .class de patch para validação técnica.

Uso:
    python3 tools/inspect_patch.py patches/ic2/75d3acc46040d66d.class
"""

import sys
import hashlib
from pathlib import Path

def inspect_class(path: Path):
    if not path.exists():
        print(f"ERRO: Arquivo {path} não encontrado.")
        return

    data = path.read_bytes()
    size = len(data)
    sha256 = hashlib.sha256(data).hexdigest()
    
    print(f"--- Inspeção de Patch: {path.name} ---")
    print(f"Caminho: {path}")
    print(f"Tamanho: {size} bytes")
    print(f"SHA-256: {sha256}")
    
    # Validação de Magic Bytes
    magic = data[:4]
    if magic == bytes([0xCA, 0xFE, 0xBA, 0xBE]):
        print("Status Magic: VÁLIDO (Java Class)")
    else:
        print(f"Status Magic: INVÁLIDO ({magic.hex().upper()})")

    # Análise de Conteúdo (Simples)
    if size < 100:
        print("Aviso: O arquivo é muito pequeno (< 100 bytes). Provavelmente é um placeholder.")
    
    print("-" * 30)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 tools/inspect_patch.py <caminho_do_patch>")
        sys.exit(1)
    
    inspect_class(Path(sys.argv[1]))
