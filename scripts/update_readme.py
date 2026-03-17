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

LANGUAGE_STACKS = {
    "TypeScript": "TypeScript · React",
    "JavaScript": "JavaScript · Node.js",
    "Python": "Python",
    "Shell": "Shell · Linux",
    "HTML": "HTML · CSS",
    "PHP": "PHP",
    "C": "C",
}


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
    rows = []
    for r in repos:
        name = r["name"]
        if name in SKIP_REPOS or r.get("fork") or r.get("archived"):
            continue
        desc = r.get("description") or "—"
        # Remove pipes que quebram tabelas markdown
        desc = desc.replace("|", "-")
        # Trunca descrições longas
        if len(desc) > 80:
            desc = desc[:77] + "..."
        lang = r.get("language") or "—"
        stack = LANGUAGE_STACKS.get(lang, lang)
        url = r["html_url"]
        rows.append(f"| [{name}]({url}) | {desc} | {stack} |")

    if not rows:
        return "| — | Nenhum projeto encontrado | — |"

    return "\n".join(rows)


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
