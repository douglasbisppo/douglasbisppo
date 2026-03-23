"""
Atualiza automaticamente a seção de Projetos em Destaque no README.md
com base nos repositórios públicos do usuário no GitHub.
"""

import json
import os
import re
import urllib.request

USERNAME = "douglasbisppo"
SKIP_REPOS = {USERNAME}  # ignora o repo do perfil

# Stack manual por repositório (os repos públicos são vitrines sem código)
REPO_STACKS = {
    "goip-auto-call-2": "Python · FastAPI · React · TypeScript · Asterisk",
    "linkr-sms-link-tracker-v2": "Node.js · Express · React · PostgreSQL · Redis",
    "validador": "React · TypeScript · Supabase · Tailwind CSS",
    "solana-sniper-bot": "Python · Solana · Raydium · Telegram Bot",
    "beia-brain": "Python · FastAPI · LLaMA · Qwen · DeepSeek",
    "locamotos-v2": "React · TypeScript · Supabase · Mercado Pago",
    "giga-studio-panel": "React · Node.js · TypeScript · Anthropic AI",
}

# Ordem de exibição preferida (do mais relevante para o menos)
REPO_ORDER = [
    "goip-auto-call-2",
    "linkr-sms-link-tracker-v2",
    "validador",
    "solana-sniper-bot",
    "beia-brain",
    "locamotos-v2",
    "giga-studio-panel",
]


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner"
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def build_table(repos):
    repo_map = {}
    for r in repos:
        name = r["name"]
        if name in SKIP_REPOS or r.get("fork") or r.get("archived") or r.get("private"):
            continue
        repo_map[name] = r

    rows = []
    # Primeiro os repos na ordem preferida
    for name in REPO_ORDER:
        if name in repo_map:
            r = repo_map.pop(name)
            rows.append(_format_row(r))

    # Depois qualquer repo público novo que não esteja na lista
    for name, r in sorted(repo_map.items()):
        rows.append(_format_row(r))

    if not rows:
        return "| — | Nenhum projeto encontrado | — |"

    return "\n".join(rows)


def _format_row(r):
    name = r["name"]
    desc = r.get("description") or "—"
    desc = desc.replace("|", "-")
    if len(desc) > 90:
        desc = desc[:87] + "..."
    stack = REPO_STACKS.get(name, r.get("language") or "—")
    url = r["html_url"]
    return f"| [{name}]({url}) | {desc} | {stack} |"


def update_readme(table_content):
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    readme_path = os.path.normpath(readme_path)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    header = "| Projeto | Descrição | Stack |\n|---|---|---|"
    new_section = f"{header}\n{table_content}"

    pattern = r"(<!-- PROJECTS:START -->\n).*?(\n<!-- PROJECTS:END -->)"
    replacement = rf"\1{new_section}\2"

    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        print("WARN: Marcadores <!-- PROJECTS:START/END --> não encontrados.")
        return False

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def main():
    repos = fetch_repos()
    table = build_table(repos)
    if update_readme(table):
        print(f"README atualizado com {table.count('|[') + table.count('| [')} projetos.")
    else:
        print("Falha ao atualizar README.")


if __name__ == "__main__":
    main()
