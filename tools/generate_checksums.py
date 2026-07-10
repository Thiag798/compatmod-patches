#!/usr/bin/env python3
"""
generate_checksums.py — Regenera patches/CHECKSUMS.properties

Execute na raiz do repositório:
    python3 tools/generate_checksums.py

Após executar, assine o resultado com sua chave Ed25519:
    openssl pkeyutl -sign -inkey ed25519.pem \\
      -out patches/CHECKSUMS.sig \\
      -in patches/CHECKSUMS.properties

NOVA ESTRUTURA (v7.8.0):
    patches/<modpack-slug-ou-standalone>/<modid>/<caminho-original>.class

Formato de saída (CHECKSUMS.properties):
    modpack:modid:hash16 = sha256_completo
"""

import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

PATCHES_DIR = Path(__file__).parent.parent / "patches"
CHECKSUMS_FILE = PATCHES_DIR / "CHECKSUMS.properties"
CLASS_MAGIC = bytes([0xCA, 0xFE, 0xBA, 0xBE])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_class_magic(path: Path) -> bool:
    with open(path, "rb") as f:
        magic = f.read(4)
    return magic == CLASS_MAGIC


def main():
    if not PATCHES_DIR.is_dir():
        print(f"ERRO: Diretório não encontrado: {PATCHES_DIR}", file=sys.stderr)
        sys.exit(1)

    entries = {}
    errors = []
    total = 0

    # Inclui o manifest.json
    manifest_path = PATCHES_DIR / "manifest.json"
    if manifest_path.is_file():
        manifest_checksum = sha256(manifest_path)
        entries["manifest:manifest.json"] = manifest_checksum
        total += 1
        print(f"  manifest.json: {manifest_checksum[:16]} (incluído)")

    # Percorre todos os subdiretórios (modpacks)
    for modpack_dir in sorted(PATCHES_DIR.iterdir()):
        if modpack_dir.name in ["manifest.json", "CHECKSUMS.properties", "CHECKSUMS.sig"]:
            continue

        if not modpack_dir.is_dir():
            continue
            
        modpack_slug = modpack_dir.name
        print(f"\n📦 Modpack: {modpack_slug}")

        # Percorre subdiretórios de mod dentro do modpack
        for mod_dir in sorted(modpack_dir.iterdir()):
            if not mod_dir.is_dir():
                continue
            
            mod_id = mod_dir.name
            count = 0

            # Busca recursivamente por arquivos .class (mantendo estrutura original)
            for class_file in sorted(mod_dir.rglob("*.class")):
                # Valida magic bytes antes de incluir
                if not validate_class_magic(class_file):
                    errors.append(f"  AVISO: {class_file.relative_to(PATCHES_DIR)} não tem magic CA FE BA BE — ignorado")
                    continue

                checksum = sha256(class_file)
                hash16 = checksum[:16]
                
                # A chave agora inclui o modpack para evitar colisões e permitir organização
                # Formato: modpack:modid:hash16
                key = f"{modpack_slug}:{mod_id}:{hash16}"
                entries[key] = checksum
                count += 1
                total += 1

            if count > 0:
                print(f"  {mod_id:20s}  {count:3d} patches")

    # Escreve CHECKSUMS.properties
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# CompatMod patch checksums",
        f"# Gerado em: {now}",
        f"# Total: {total} entradas (incluindo manifest.json)",
        "# Formato: modpack:modid:hash16 = sha256_completo (para patches)",
        "# Formato: manifest:manifest.json = sha256_completo (para metadados)",
        "# IMPORTANTE: Assine este arquivo com Ed25519 antes de publicar:",
        "#   openssl pkeyutl -sign -inkey ed25519.pem -out CHECKSUMS.sig -in CHECKSUMS.properties",
        "",
    ]
    for key in sorted(entries.keys()):
        lines.append(f"{key} = {entries[key]}")

    CHECKSUMS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n✔ {CHECKSUMS_FILE} atualizado com {total} patches.")

    # Reporta erros/avisos
    if errors:
        print("\nAvisos:")
        for e in errors:
            print(e)

    print("\nPróximo passo — assinar o manifesto:")
    print("  openssl pkeyutl -sign -inkey ed25519.pem \\")
    print("    -out patches/CHECKSUMS.sig \\")
    print("    -in patches/CHECKSUMS.properties")


if __name__ == "__main__":
    main()
