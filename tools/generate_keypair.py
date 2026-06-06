#!/usr/bin/env python3
"""
generate_keypair.py — Gera par de chaves Ed25519 e assina CHECKSUMS.properties

USE UMA ÚNICA VEZ para criar suas chaves. Guarde ed25519.pem em local seguro
(NUNCA commite no repositório). A chave pública vai embutida no mod.

Uso:
    # Gerar par de chaves (apenas uma vez)
    python3 tools/generate_keypair.py --keygen

    # Assinar CHECKSUMS.properties
    python3 tools/generate_keypair.py --sign

    # Verificar assinatura
    python3 tools/generate_keypair.py --verify

Requisitos:
    pip install cryptography
"""

import argparse
import base64
import sys
from pathlib import Path

PRIVATE_KEY_FILE = Path("ed25519.pem")         # NUNCA commitar — adicione ao .gitignore
PUBLIC_KEY_FILE  = Path("ed25519_public.pem")   # pode ser público
CHECKSUMS_FILE   = Path("patches/CHECKSUMS.properties")
SIG_FILE         = Path("patches/CHECKSUMS.sig")


def check_cryptography():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        return True
    except ImportError:
        print("ERRO: pip install cryptography", file=sys.stderr)
        sys.exit(1)


def cmd_keygen():
    check_cryptography()
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, PublicFormat, NoEncryption
    )

    if PRIVATE_KEY_FILE.exists():
        print(f"AVISO: {PRIVATE_KEY_FILE} já existe. Apague manualmente para regerar.")
        sys.exit(1)

    private_key = Ed25519PrivateKey.generate()
    public_key  = private_key.public_key()

    PRIVATE_KEY_FILE.write_bytes(
        private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
    PUBLIC_KEY_FILE.write_bytes(
        public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))

    # Chave pública em Base64 para embutir no mod (PatchRepository.EMBEDDED_PUBLIC_KEY_B64)
    pub_der = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    pub_b64 = base64.b64encode(pub_der).decode()

    print(f"✔ Chaves geradas:")
    print(f"  Privada : {PRIVATE_KEY_FILE}  ← NUNCA commitar!")
    print(f"  Pública : {PUBLIC_KEY_FILE}")
    print()
    print("Cole esta linha em PatchRepository.java:")
    print(f'  private static final String EMBEDDED_PUBLIC_KEY_B64 = "{pub_b64}";')
    print()
    print("Adicione ao .gitignore:")
    print("  ed25519.pem")


def cmd_sign():
    check_cryptography()
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    if not PRIVATE_KEY_FILE.exists():
        print(f"ERRO: {PRIVATE_KEY_FILE} não encontrado. Execute --keygen primeiro.")
        sys.exit(1)
    if not CHECKSUMS_FILE.exists():
        print(f"ERRO: {CHECKSUMS_FILE} não encontrado. Execute generate_checksums.py primeiro.")
        sys.exit(1)

    private_key = load_pem_private_key(PRIVATE_KEY_FILE.read_bytes(), password=None)
    data        = CHECKSUMS_FILE.read_bytes()
    signature   = private_key.sign(data)

    SIG_FILE.write_bytes(signature)
    print(f"✔ Assinatura gerada: {SIG_FILE} ({len(signature)} bytes)")
    print(f"  SHA-256 do manifesto: {__import__('hashlib').sha256(data).hexdigest()[:16]}...")


def cmd_verify():
    check_cryptography()
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    from cryptography.exceptions import InvalidSignature

    if not PUBLIC_KEY_FILE.exists():
        print(f"ERRO: {PUBLIC_KEY_FILE} não encontrado.")
        sys.exit(1)

    public_key = load_pem_public_key(PUBLIC_KEY_FILE.read_bytes())
    data       = CHECKSUMS_FILE.read_bytes()
    sig        = SIG_FILE.read_bytes()

    try:
        public_key.verify(sig, data)
        print(f"✔ Assinatura VÁLIDA para {CHECKSUMS_FILE}")
    except InvalidSignature:
        print(f"✘ Assinatura INVÁLIDA! Manifesto pode ter sido adulterado.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gerencia chaves Ed25519 para CompatMod patches")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--keygen", action="store_true", help="Gera par de chaves Ed25519")
    group.add_argument("--sign",   action="store_true", help="Assina CHECKSUMS.properties")
    group.add_argument("--verify", action="store_true", help="Verifica assinatura")
    args = parser.parse_args()

    if args.keygen:  cmd_keygen()
    elif args.sign:  cmd_sign()
    elif args.verify: cmd_verify()


if __name__ == "__main__":
    main()
