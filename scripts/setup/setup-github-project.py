#!/usr/bin/env python3
"""Populate a GitHub Project v2 from an agile plan markdown file."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = PACKAGE_ROOT / "examples" / "agile-plan.md"
GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"

FALLBACK_EPICS = [
    {"id": "E1", "name": "Estrutura base do repositório"},
    {"id": "E2", "name": "Pipeline Unity WebGL"},
    {"id": "E3", "name": "Pipeline Docker"},
    {"id": "E4", "name": "Migrações e banco"},
    {"id": "E5", "name": "Health checks e rollback"},
]

FALLBACK_STORIES = [
    {
        "epic": "E1",
        "sprint": 1,
        "title": "Estrutura de diretórios",
        "priority": "High",
        "acceptance": [
            "Diretório `.github/workflows/` criado",
            "Diretório `scripts/deploy/`, `scripts/health/`, `scripts/rollback/` criados",
            "Diretório `runners/` com README de instalação",
            "Diretório `docs/` com `architecture.md` e `runbooks/`",
            "Diretório `monitoring/` vazio com README placeholder",
            "`.gitignore` configurado para ignorar `.env`, `*.pem`, `*.key`",
            "`README.md` atualizado refletindo a estrutura real",
        ],
    },
    {
        "epic": "E1",
        "sprint": 1,
        "title": "Documentação de arquitetura",
        "priority": "Medium",
        "acceptance": [
            "`docs/architecture.md` descreve EC2 Games e EC2 API/App",
            "Inclui tabela de serviços, portas e responsabilidades",
            "Inclui diagrama textual (ASCII ou Mermaid) da topologia",
            "Descreve o fluxo de deploy de cada tipo de aplicação",
        ],
    },
    {
        "epic": "E2",
        "sprint": 2,
        "title": "Workflow deploy-webgl.yml",
        "priority": "High",
        "acceptance": [
            "Workflow aceita inputs: `game_name`, `deploy_path`",
            "Faz checkout do repositório no runner",
            "Copia arquivos da pasta `Build/` para o caminho correto no Nginx",
            "Reinicia ou recarrega Nginx após deploy",
            "Registra log de deploy com timestamp e commit hash",
            "Workflow pode ser chamado via `workflow_call` de outros repositórios",
        ],
    },
    {
        "epic": "E2",
        "sprint": 2,
        "title": "Caller workflow para cada jogo",
        "priority": "High",
        "acceptance": [
            "Template de `.github/workflows/deploy.yml` criado no `ciatec-devops`",
            "Template usa `workflow_call` apontando para `ciatec-devops`",
            "Documentação explica como copiar e configurar o template",
        ],
    },
    {
        "epic": "E3",
        "sprint": 3,
        "title": "Script deploy-docker.sh",
        "priority": "High",
        "acceptance": [
            "Script `scripts/deploy/deploy-docker.sh` criado",
            "Suporta argumento para deploy seletivo (api | app | all)",
            "Faz pull da imagem antes de subir o container",
            "Executa health check após o deploy",
            "Faz rollback automático se health check falhar",
            "Registra log com timestamp e versão",
        ],
    },
    {
        "epic": "E3",
        "sprint": 3,
        "title": "Workflow deploy-docker.yml",
        "priority": "High",
        "acceptance": [
            "Workflow aceita inputs: `service` (api | app | all)",
            "Conecta ao servidor via SSH usando secret",
            "Executa o script `deploy-docker.sh` remotamente",
            "Captura e exibe o log de deploy no output do GitHub Actions",
            "Falha o workflow se o deploy falhar",
        ],
    },
    {
        "epic": "E3",
        "sprint": 3,
        "title": "Caller workflow monorepo",
        "priority": "Medium",
        "acceptance": [
            "Template `docs/templates/monorepo-deploy-caller.yml` criado",
            "Detecta quais serviços foram alterados via `paths` filter",
            "Deploy da API se arquivos em `api/` mudaram",
            "Deploy do App se arquivos em `app/` mudaram",
            "Deploy de ambos se `docker-compose.yml` mudou",
        ],
    },
    {
        "epic": "E4",
        "sprint": 4,
        "title": "Script run-migrations.sh",
        "priority": "High",
        "acceptance": [
            "Script `scripts/deploy/run-migrations.sh` criado",
            "Executa `alembic upgrade head` dentro do container da API",
            "Verifica conexão com o banco antes de tentar migrar",
            "Registra log de migrações separado de deploy",
            "Falha o deploy se a migração falhar",
        ],
    },
    {
        "epic": "E5",
        "sprint": 4,
        "title": "Scripts de health check",
        "priority": "Medium",
        "acceptance": [
            "`scripts/health/check-all.sh` verifica todos os serviços",
            "`scripts/health/check-webgl.sh` verifica os 3 jogos Unity",
            "`scripts/health/check-docker.sh` verifica API e App",
            "Saída colorida com status por serviço",
            "Exit code 0 se tudo OK, 1 se qualquer serviço falhou",
        ],
    },
]

STORY_TO_EPIC = {
    "1": "E1",
    "2": "E2",
    "3": "E3",
    "4": "E4",
}


def log_ok(msg: str) -> None:
    print(f"✅ {msg}")


def log_err(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def parse_plan(path: Path) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Parse epics and stories from the agile plan markdown."""
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Plan file is empty: {path}")

    epics: list[dict[str, str]] = []
    for match in re.finditer(
        r"\|\s*(E\d+)\s*\|\s*([^|]+)\|",
        text,
    ):
        epic_id, name = match.group(1), match.group(2).strip()
        if epic_id.startswith("E") and name and "Épico" not in name and "---" not in name:
            if not any(e["id"] == epic_id for e in epics):
                epics.append({"id": epic_id, "name": name})

    stories: list[dict[str, Any]] = []
    story_blocks = re.split(r"\n### Story ", text)
    for block in story_blocks[1:]:
        header = block.split("\n", 1)[0]
        header_match = re.match(r"(\d+)\.(\d+)\s*—\s*(.+)", header.strip())
        if not header_match:
            continue
        sprint = int(header_match.group(1))
        title = header_match.group(3).strip()
        major = header_match.group(1)

        # Story 4.2 maps to E5 (health); 4.1 to E4 (migrations)
        if major == "4" and "health" in title.lower():
            epic = "E5"
        else:
            epic = STORY_TO_EPIC.get(major, f"E{major}")

        priority_match = re.search(r"\*\*Priority:\*\*\s*(\w+)", block, re.IGNORECASE)
        if not priority_match:
            # Infer from original plan conventions
            priority = "High" if sprint <= 3 and "Caller workflow monorepo" not in title else "Medium"
            if "arquitetura" in title.lower() or "health" in title.lower():
                priority = "Medium"
            if "Caller workflow monorepo" in title:
                priority = "Medium"
        else:
            priority = priority_match.group(1)

        acceptance = re.findall(r"^- \[ \] (.+)$", block, re.MULTILINE)
        stories.append(
            {
                "epic": epic,
                "sprint": sprint,
                "title": title,
                "priority": priority,
                "acceptance": acceptance,
            }
        )

    if not epics or not stories:
        raise ValueError("Could not parse epics/stories from plan")

    return epics, stories


def load_plan_data(plan_path: Path) -> tuple[list[dict[str, str]], list[dict[str, Any]], str]:
    candidates = [
        plan_path,
        PACKAGE_ROOT / "examples" / "agile-plan.md",
    ]
    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size > 0:
            try:
                epics, stories = parse_plan(candidate)
                return epics, stories, str(candidate)
            except ValueError as exc:
                log_err(f"Parse failed for {candidate}: {exc}")
    return FALLBACK_EPICS, FALLBACK_STORIES, "fallback-hardcoded"


class GitHubClient:
    def __init__(self, token: str, dry_run: bool = False) -> None:
        self.token = token
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.dry_run:
            return {"data": {}}
        response = self.session.post(
            GRAPHQL_URL,
            json={"query": query, "variables": variables or {}},
            timeout=60,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"GraphQL HTTP {response.status_code}: {response.text}")
        payload = response.json()
        if payload.get("errors"):
            raise RuntimeError(f"GraphQL errors: {payload['errors']}")
        return payload

    def rest(self, method: str, path: str, json_body: dict[str, Any] | None = None) -> Any:
        if self.dry_run:
            return {}
        response = self.session.request(
            method,
            f"{REST_URL}{path}",
            json=json_body,
            timeout=60,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"REST {method} {path} → {response.status_code}: {response.text}")
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()


def get_owner_node_id(client: GitHubClient, org: str | None, user: str | None) -> str:
    if org:
        query = """
        query($login: String!) {
          organization(login: $login) { id }
        }
        """
        data = client.graphql(query, {"login": org})
        node_id = data.get("data", {}).get("organization", {}).get("id")
        if not node_id and not client.dry_run:
            raise RuntimeError(f"Organization not found: {org}")
        return node_id or "dry-run-org-id"
    if user:
        query = """
        query($login: String!) {
          user(login: $login) { id }
        }
        """
        data = client.graphql(query, {"login": user})
        node_id = data.get("data", {}).get("user", {}).get("id")
        if not node_id and not client.dry_run:
            raise RuntimeError(f"User not found: {user}")
        return node_id or "dry-run-user-id"
    raise RuntimeError("Set GITHUB_ORG or GITHUB_USER in .env")


def get_project_by_number(
    client: GitHubClient,
    org: str | None,
    user: str | None,
    number: int,
) -> dict[str, str]:
    if client.dry_run:
        return {
            "id": "dry-run-project-id",
            "url": f"https://github.com/orgs/dry-run/projects/{number}",
        }
    if org:
        query = """
        query($login: String!, $number: Int!) {
          organization(login: $login) {
            projectV2(number: $number) { id url title }
          }
        }
        """
        data = client.graphql(query, {"login": org, "number": number})
        project = data["data"]["organization"]["projectV2"]
    else:
        query = """
        query($login: String!, $number: Int!) {
          user(login: $login) {
            projectV2(number: $number) { id url title }
          }
        }
        """
        data = client.graphql(query, {"login": user, "number": number})
        project = data["data"]["user"]["projectV2"]
    if not project:
        raise RuntimeError(f"Project number {number} not found")
    log_ok(f"Using existing project: {project['url']}")
    return {"id": project["id"], "url": project["url"]}


def create_project(client: GitHubClient, owner_id: str, title: str) -> dict[str, str]:
    if client.dry_run:
        log_ok(f"[dry-run] Would create project '{title}'")
        return {"id": "dry-run-project-id", "url": "https://github.com/users/dry-run/projects/1"}

    mutation = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id url }
      }
    }
    """
    data = client.graphql(mutation, {"ownerId": owner_id, "title": title})
    project = data["data"]["createProjectV2"]["projectV2"]
    log_ok(f"Created project: {project['url']}")
    return {"id": project["id"], "url": project["url"]}


def list_project_fields(client: GitHubClient, project_id: str) -> dict[str, Any]:
    """Return fields keyed by name with id + option map."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2FieldCommon { id name }
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
              ... on ProjectV2IterationField { id name }
            }
          }
        }
      }
    }
    """
    data = client.graphql(query, {"projectId": project_id})
    nodes = data.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])
    result: dict[str, Any] = {}
    for node in nodes:
        if not node or "name" not in node:
            continue
        options = {o["name"]: o["id"] for o in node.get("options", [])} if node.get("options") else {}
        result[node["name"]] = {"id": node["id"], "options": options}
    return result


def create_fields(
    client: GitHubClient,
    project_id: str,
    epics: list[dict[str, str]],
) -> dict[str, Any]:
    """Ensure Sprint, Epic, Status, Priority fields exist. Reuses reserved Status."""
    if client.dry_run:
        log_ok("[dry-run] Would ensure fields: Sprint, Epic, Status, Priority")
        return {
            "Sprint": {"id": "dry-sprint", "options": {}},
            "Epic": {
                "id": "dry-epic",
                "options": {f"{e['id']} — {e['name']}": f"dry-{e['id']}" for e in epics},
            },
            "Status": {
                "id": "dry-status",
                "options": {
                    "Backlog": "dry-backlog",
                    "Todo": "dry-todo",
                    "In Progress": "dry-progress",
                    "Done": "dry-done",
                },
            },
            "Priority": {
                "id": "dry-priority",
                "options": {
                    "High": "dry-high",
                    "Medium": "dry-medium",
                    "Low": "dry-low",
                },
            },
        }

    fields = list_project_fields(client, project_id)

    def create_iteration(name: str) -> dict[str, Any]:
        mutation = """
        mutation($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {
            projectId: $projectId
            dataType: ITERATION
            name: $name
          }) {
            projectV2Field {
              ... on ProjectV2IterationField { id name }
            }
          }
        }
        """
        data = client.graphql(mutation, {"projectId": project_id, "name": name})
        field = data["data"]["createProjectV2Field"]["projectV2Field"]
        log_ok(f"Created field: {name} (iteration)")
        return {"id": field["id"], "options": {}}

    def create_single_select(name: str, options: list[str]) -> dict[str, Any]:
        mutation = """
        mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
          createProjectV2Field(input: {
            projectId: $projectId
            dataType: SINGLE_SELECT
            name: $name
            singleSelectOptions: $options
          }) {
            projectV2Field {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
            }
          }
        }
        """
        option_inputs = [
            {"name": opt, "color": "GRAY", "description": opt} for opt in options
        ]
        data = client.graphql(
            mutation,
            {"projectId": project_id, "name": name, "options": option_inputs},
        )
        field = data["data"]["createProjectV2Field"]["projectV2Field"]
        opt_map = {o["name"]: o["id"] for o in field.get("options", [])}
        log_ok(f"Created field: {name}")
        return {"id": field["id"], "options": opt_map}

    if "Sprint" not in fields:
        try:
            fields["Sprint"] = create_iteration("Sprint")
        except RuntimeError as exc:
            log_err(f"Sprint field: {exc}")
            fields = list_project_fields(client, project_id)
    else:
        log_ok("Reusing field: Sprint")

    epic_options = [f"{e['id']} — {e['name']}" for e in epics]
    if "Epic" not in fields:
        try:
            fields["Epic"] = create_single_select("Epic", epic_options)
        except RuntimeError as exc:
            log_err(f"Epic field: {exc}")
            fields = {**fields, **list_project_fields(client, project_id)}
    else:
        log_ok("Reusing field: Epic")

    # Status is a built-in reserved field on Projects v2 — never recreate
    if "Status" in fields:
        log_ok("Reusing built-in field: Status")
    else:
        log_err("Built-in Status field not found on project")

    if "Priority" not in fields:
        try:
            fields["Priority"] = create_single_select("Priority", ["High", "Medium", "Low"])
        except RuntimeError as exc:
            log_err(f"Priority field: {exc}")
            fields = {**fields, **list_project_fields(client, project_id)}
    else:
        log_ok("Reusing field: Priority")

    return fields


def ensure_label(client: GitHubClient, owner: str, repo: str, name: str, color: str = "0052cc") -> None:
    if client.dry_run:
        log_ok(f"[dry-run] Would ensure label: {name}")
        return
    try:
        client.rest("POST", f"/repos/{owner}/{repo}/labels", {"name": name, "color": color})
        log_ok(f"Created label: {name}")
    except RuntimeError as exc:
        if "already_exists" in str(exc) or "422" in str(exc):
            log_ok(f"Label already exists: {name}")
        else:
            raise


def create_issue(
    client: GitHubClient,
    owner: str,
    repo: str,
    epic_id: str,
    title: str,
    acceptance: list[str],
    label: str,
) -> dict[str, Any]:
    body_lines = ["## Acceptance Criteria", ""]
    if acceptance:
        body_lines.extend(f"- [ ] {item}" for item in acceptance)
    else:
        body_lines.append("- [ ] Definir critérios de aceite")
    body_lines.extend(["", f"**Epic:** {epic_id}"])
    issue_title = f"[{epic_id}] {title}"

    if client.dry_run:
        log_ok(f"[dry-run] Would create issue: {issue_title}")
        return {"number": 0, "node_id": "dry-issue-node", "html_url": "https://github.com/dry-run"}

    issue = client.rest(
        "POST",
        f"/repos/{owner}/{repo}/issues",
        {"title": issue_title, "body": "\n".join(body_lines), "labels": [label]},
    )
    log_ok(f"Created issue #{issue['number']}: {issue_title}")
    return issue


def add_to_project(
    client: GitHubClient,
    project_id: str,
    issue_node_id: str,
    fields: dict[str, Any],
    epic_id: str,
    epic_name: str,
    priority: str,
    sprint: int,
) -> None:
    if client.dry_run:
        log_ok(
            f"[dry-run] Would add issue to project "
            f"(Epic={epic_id}, Priority={priority}, Sprint={sprint}, Status=Backlog)"
        )
        return

    add_mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }
    """
    data = client.graphql(
        add_mutation, {"projectId": project_id, "contentId": issue_node_id}
    )
    item_id = data["data"]["addProjectV2ItemById"]["item"]["id"]

    def set_select(field_key: str, option_name: str) -> None:
        field = fields.get(field_key)
        if not field:
            return
        option_id = field["options"].get(option_name)
        if not option_id:
            # try partial match for epic labels like "E1 — name"
            for name, oid in field["options"].items():
                if name.startswith(option_name) or option_name in name:
                    option_id = oid
                    break
        if not option_id:
            log_err(f"Option '{option_name}' not found on field {field_key}")
            return
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { singleSelectOptionId: $optionId }
          }) {
            projectV2Item { id }
          }
        }
        """
        client.graphql(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field["id"],
                "optionId": option_id,
            },
        )

    epic_label = f"{epic_id} — {epic_name}"
    set_select("Epic", epic_label)
    # Built-in Status often uses Todo instead of Backlog
    status_field = fields.get("Status", {})
    status_options = status_field.get("options", {})
    status_value = "Backlog" if "Backlog" in status_options else (
        "Todo" if "Todo" in status_options else next(iter(status_options), "Todo")
    )
    set_select("Status", status_value)
    set_select("Priority", priority)
    # Iteration values require iteration IDs created by GitHub; leave Sprint for manual fill if empty
    log_ok(f"Added issue to project (Epic={epic_id}, Priority={priority})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup CIATec DevOps GitHub Project from agile plan")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without calling the API")
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN,
        help="Path to agile plan markdown",
    )
    parser.add_argument(
        "--project-number",
        type=int,
        default=None,
        help="Use an existing Project number instead of creating a new one",
    )
    args = parser.parse_args()

    load_dotenv(PACKAGE_ROOT / ".env")
    load_dotenv(Path.cwd() / ".env")

    token = os.getenv("GITHUB_TOKEN", "")
    org = os.getenv("GITHUB_ORG") or None
    user = os.getenv("GITHUB_USER") or None
    repo = os.getenv("GITHUB_REPO", "meu-projeto")
    title = os.getenv("PROJECT_TITLE", "CIATec Project")
    project_number = args.project_number
    if project_number is None and os.getenv("GITHUB_PROJECT_NUMBER"):
        project_number = int(os.getenv("GITHUB_PROJECT_NUMBER", "0")) or None

    if not args.dry_run and not token:
        log_err("GITHUB_TOKEN is required (or use --dry-run)")
        return 1
    if not org and not user:
        # Allow dry-run without owner
        if args.dry_run:
            user = user or "dry-run-user"
        else:
            log_err("Set GITHUB_ORG or GITHUB_USER in .env")
            return 1

    owner_login = org or user or "dry-run-user"
    epics, stories, source = load_plan_data(args.plan)
    log_ok(f"Plan source: {source} ({len(epics)} epics, {len(stories)} stories)")

    client = GitHubClient(token or "dry-run", dry_run=args.dry_run)

    try:
        owner_id = get_owner_node_id(client, org, user)
        if project_number:
            project = get_project_by_number(client, org, user, project_number)
        else:
            project = create_project(client, owner_id, title)
        fields = create_fields(client, project["id"], epics)

        epic_name_by_id = {e["id"]: e["name"] for e in epics}
        for epic in epics:
            ensure_label(client, owner_login, repo, epic["id"])
            ensure_label(client, owner_login, repo, epic["name"][:50])

        for story in stories:
            epic_id = story["epic"]
            label = epic_id
            issue = create_issue(
                client,
                owner_login,
                repo,
                epic_id,
                story["title"],
                story.get("acceptance") or [],
                label,
            )
            add_to_project(
                client,
                project["id"],
                issue.get("node_id", ""),
                fields,
                epic_id,
                epic_name_by_id.get(epic_id, epic_id),
                story.get("priority", "Medium"),
                int(story.get("sprint", 1)),
            )

        print()
        log_ok(f"Project URL: {project['url']}")
        if args.dry_run:
            log_ok("Dry-run completed — no API calls were made")
        return 0
    except Exception as exc:  # noqa: BLE001 — top-level CLI boundary
        log_err(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
