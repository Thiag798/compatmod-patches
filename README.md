# CompatMod — Repositório de Patches

Repositório oficial de patches de compatibilidade para o [CompatMod](https://github.com/compatmod/compatmod) (Minecraft 1.21.1).

---

## ✨ Nova Organização (v7.8.0+)

A partir da versão 7.8.0 do servidor CompatMod, os patches são organizados por **Modpack** e **Mod**. Isso permite uma separação clara entre patches genéricos (*standalone*) e patches específicos para modpacks populares.

### Estrutura de Pastas

```text
patches/
├── CHECKSUMS.properties    ← manifesto SHA-256 de todos os patches
├── CHECKSUMS.sig           ← assinatura Ed25519 do manifesto
├── manifest.json           ← metadados da release
├── standalone/             ← patches genéricos (sem modpack específico)
│   ├── ic2/
│   ├── mekanism/
│   └── ...
└── <modpack-slug>/         ← patches específicos de um modpack
    ├── jei/
    └── ...
```

---

## 🚀 Como funciona

O CompatMod baixa patches em dois modos:

### Modo 1 — `raw.githubusercontent.com` (patch individual)
Usado para buscar um patch específico quando detectado em tempo de transformação ASM. O caminho agora inclui o contexto do modpack:
```text
GET .../patches/{modpack-ou-standalone}/{modid}/{hash16}.class
GET .../patches/CHECKSUMS.properties
GET .../patches/CHECKSUMS.sig
```

### Modo 2 — GitHub Releases (bundle ZIP)
Download de todos os patches como bundle para cache local.
```text
GET https://api.github.com/repos/compatmod/patches/releases?per_page=10
```

---

## 🔐 Segurança

Todos os patches são verificados pelo mod antes de uso:
1. **SHA-256** — hash do arquivo comparado com `CHECKSUMS.properties` (formato `modpack:modid:hash16`).
2. **Ed25519** — assinatura digital de `CHECKSUMS.properties`.
3. **Magic bytes** — todo `.class` deve começar com `CA FE BA BE`.
4. **MaliciousBytecodeScanner** — varredura ASM adicional.

---

## 🛠️ Manutenção Manual

Se precisar adicionar patches manualmente:

1.  Coloque os arquivos `.class` em `patches/<modpack-ou-standalone>/<modid>/`.
2.  Regenere o manifesto:
    ```bash
    python3 tools/generate_checksums.py
    ```
3.  Assine o manifesto com sua chave Ed25519:
    ```bash
    openssl pkeyutl -sign -inkey ed25519.pem \
      -out patches/CHECKSUMS.sig \
      -in patches/CHECKSUMS.properties
    ```
4.  Commit e push para a branch `releases/1.21.1`.

---

## 📅 Versionamento

| Branch | Uso |
|--------|-----|
| `releases/1.21.1` | Patches estáveis para MC 1.21.1 (Produção) |
| `main` | Desenvolvimento |

*Repositório atualizado para compatibilidade com CompatMod Server v7.8.0.*
