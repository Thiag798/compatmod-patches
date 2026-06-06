# CompatMod — Repositório de Patches

Repositório oficial de patches de compatibilidade para o [CompatMod](https://github.com/compatmod/compatmod) (Minecraft 1.21.1).

## Estrutura

```
patches/
├── CHECKSUMS.properties    ← manifesto SHA-256 de todos os patches
├── CHECKSUMS.sig           ← assinatura Ed25519 do manifesto
├── ic2/
│   └── <hash16>.class      ← patch compilado
├── buildcraft/
├── mekanism/
├── thermal/
├── ae2/
├── thaumcraft/
├── gregtech/
└── tconstruct/
```

## Como funciona

O CompatMod baixa patches em dois modos:

### Modo 1 — `raw.githubusercontent.com` (patch individual)
Usado pelo `PatchRepository` para buscar um patch específico quando detectado em tempo de transformação ASM:
```
GET https://raw.githubusercontent.com/compatmod/patches/releases/1.21.1/patches/{modid}/{hash16}.class
GET https://raw.githubusercontent.com/compatmod/patches/releases/1.21.1/patches/CHECKSUMS.properties
GET https://raw.githubusercontent.com/compatmod/patches/releases/1.21.1/patches/CHECKSUMS.sig
```

### Modo 2 — GitHub Releases (bundle ZIP)
Usado pelo `ReleaseRepository` para baixar todos os patches de uma vez como bundle:
```
GET https://api.github.com/repos/compatmod/patches/releases?per_page=10
→ baixa asset "patches-1.21.1.zip" da release mais recente com tag "1.21.1-*"
```

O bundle é extraído em `.minecraft/compatmod/patch-cache/release/<tag>/` e reutilizado entre sessões enquanto a tag não mudar.

## Versionamento

| Branch | Uso |
|--------|-----|
| `releases/1.21.1` | Patches estáveis para MC 1.21.1 — usados pelo mod em produção |
| `releases/1.20.4` | Patches estáveis para MC 1.20.4 |
| `main` | Desenvolvimento — **não usado em produção** |

Cada GitHub Release tem:
- Tag no formato `1.21.1-vYYYY.MM.DD` (ex: `1.21.1-v2024.06.01`)
- Asset `patches-1.21.1.zip` com todos os patches desta versão do MC

## Segurança

Todos os patches são verificados pelo mod antes de uso:
1. **SHA-256** — hash do arquivo `.class` comparado com `CHECKSUMS.properties`
2. **Ed25519** — assinatura digital de `CHECKSUMS.properties` verificada com chave pública embutida no mod
3. **Magic bytes** — todo `.class` deve começar com `CA FE BA BE`
4. **MaliciousBytecodeScanner** — varredura ASM adicional no lado do mod

## Contribuindo patches

Patches gerados pelos usuários via sistema de contribuição do mod ficam em quarentena no servidor de submissão e são revisados manualmente antes de aparecer aqui.

Para contribuir manualmente: abra uma issue com o patch e o contexto do mod/versão.

## Publicando uma nova release

```bash
# 1. Adicione os novos patches em patches/<modid>/
# 2. Regenere o manifesto
cd tools && python3 generate_checksums.py

# 3. Assine o manifesto com sua chave Ed25519
openssl pkeyutl -sign -inkey ed25519.pem \
  -out patches/CHECKSUMS.sig \
  -in patches/CHECKSUMS.properties

# 4. Commit e push para a branch de release
git add patches/
git commit -m "release: adiciona patches para ic2 v2.8.222"
git push origin releases/1.21.1

# 5. Crie a GitHub Release via workflow ou manualmente
# O workflow .github/workflows/release.yml faz isso automaticamente
# quando você faz push de uma tag "1.21.1-v*"
```
