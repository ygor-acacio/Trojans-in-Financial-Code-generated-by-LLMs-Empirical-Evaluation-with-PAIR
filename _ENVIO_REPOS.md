# Como enviar os dois repositórios (no seu nome)

Tudo já está preparado em **duas pastas-irmãs, limpas e separadas**. Nada foi commitado —
você faz os dois envios, com os commits no **seu** nome.

| Repo | Visibilidade | Pasta de onde sai |
|---|---|---|
| **Privado** | privada | `tcc-trojans-llm/`  ← esta pasta (TCC inteiro, organizado) |
| **Público** | pública | `tcc-trojans-site/`  ← pasta-irmã (só o site + GitHub Pages) |

> As duas ficam em `C:/Users/ygora/Documents/USP/TCC/TCC - project/`.
> A pasta antiga `JailbreakingLLMs/` não é mais necessária para o envio — pode mantê-la como
> backup e apagar quando quiser.

Antes de tudo, garanta que o Git vai assinar os commits com o seu nome:

```bash
git config --global user.name  "Ygor Acacio Maria"
git config --global user.email "SEU-EMAIL-DO-GITHUB"
```

> Use o e-mail da sua conta do GitHub (ou o `@users.noreply.github.com` de
> Settings → Emails, se quiser esconder o e-mail real).

---

## 1) Repositório PRIVADO — o TCC inteiro

Já há um `.gitignore` que protege o essencial: **não** envia `.env`, `.venv/` nem caches.
O gabarito privado e os nomes de avaliadores ficam aqui — tudo bem, é privado.

No **GitHub**, crie um repositório **privado** vazio (sem README), ex. `tcc-trojans-llm`.
Depois:

```bash
cd "C:/Users/ygora/Documents/USP/TCC/TCC - project/tcc-trojans-llm"
git init
git add -A

# >>> CONFERÊNCIA DE SEGURANÇA <<<  (não deve haver .env real; só .env.example)
git status --short | grep -i "\.env$"     # esperado: nada (ou só .env.example)

git commit -m "TCC: monografia, artigo, entregas, experimento e site"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/tcc-trojans-llm.git
git push -u origin main
```

---

## 2) Repositório PÚBLICO — o site + o GitHub Pages

No **GitHub**, crie um repositório **público** vazio (sem README), ex. `tcc-trojans-site`.
Depois:

```bash
cd "C:/Users/ygora/Documents/USP/TCC/TCC - project/tcc-trojans-site"
git init
git add -A
git commit -m "Project site (static) with gated offline demonstration"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/tcc-trojans-site.git
git push -u origin main
```

Ligar o Pages:

1. No repositório público: **Settings → Pages**.
2. **Source:** *Deploy from a branch*.
3. **Branch:** `main` · **Folder:** `/ (root)` · **Save**.
4. Em ~1 min: `https://SEU-USUARIO.github.io/tcc-trojans-site/`.

### Ligar/desligar a demonstração depois
Começa **desligada**. Para ligar: edite `config.js` → `demoEnabled: true`, depois
`git add config.js && git commit -m "enable demo" && git push`. Para desligar, volte a
`false`. (A demo é um replay offline — não chama modelo nem gasta nada; o flag só controla a
visibilidade.)

---

## Resumo do que está protegido

- ✅ `.env` (token HF) — nunca entra; nem no privado nem no público.
- ✅ Nenhum token em outros arquivos (verificado nas duas pastas).
- ✅ Público = só o site; sem dados brutos, sem gabarito, sem nomes de avaliadores.
- ✅ `.venv/`, `__pycache__/` e lixo de SO — fora.

Com **GitHub CLI**, dá para criar e enviar em um comando por pasta:
`gh repo create SEU-USUARIO/tcc-trojans-llm --private --source . --push` (dentro desta pasta)
e `gh repo create SEU-USUARIO/tcc-trojans-site --public --source . --push` (dentro da pasta do site).
