#!/usr/bin/env python3
import json
import os
import re
import yaml
from pathlib import Path

AGENCY_ROOT = Path(__file__).parent.parent / "agency-agents"
AGENTS_DIR = Path(__file__).parent / "agents"
CATEGORIES = [
    "engineering",
    "design",
    "marketing",
    "sales",
    "product",
    "project-management",
    "testing",
    "support",
    "specialized",
    "strategy",
    "finance",
    "academic",
    "game-development",
    "paid-media",
    "spatial-computing",
]


def parse_agent_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not frontmatter:
            return None
        return {
            "name": frontmatter.get("name", file_path.stem),
            "description": frontmatter.get("description", ""),
            "category": file_path.parent.name,
        }
    except:
        return None


def sync_agents():
    agents = []
    integrations_dir = AGENCY_ROOT / "integrations" / "opencode" / "agents"

    for category in CATEGORIES:
        category_dir = AGENCY_ROOT / category
        if not category_dir.exists():
            continue

        for md_file in category_dir.glob("*.md"):
            agent = parse_agent_file(md_file)
            if agent:
                agents.append(agent)

    for md_file in integrations_dir.glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
                name = frontmatter.get("name", md_file.stem)
                if not any(a["name"] == name for a in agents):
                    agents.append(
                        {
                            "name": name,
                            "description": frontmatter.get("description", ""),
                            "category": "specialized",
                        }
                    )
            except:
                pass

    agents.sort(key=lambda x: x.get("name", "").lower())

    output = {"version": "1.0", "total": len(agents), "agents": agents}

    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(AGENTS_DIR / "agent_index.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Synced {len(agents)} agents from The Agency")
    return agents


if __name__ == "__main__":
    sync_agents()
