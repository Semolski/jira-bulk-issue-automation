import csv
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv


# -----------------------------
# CONFIG: Map CSV columns -> Jira fields
# -----------------------------
# Update these keys to match your CSV headers.
# Update values to match Jira field IDs.
#
# Built-in Jira fields:
#   summary, labels, issuetype, project, assignee, parent, fixVersions, components
#
# Custom fields:
#   customfield_XXXXX
#
FIELD_MAP: Dict[str, str] = {
    "Summary": "summary",
    "Labels": "labels",
    "Description": "description",
    # Example custom field mapping:
    # "ClientFieldValue": "customfield_XXXXX",
}

# If you use a Jira custom select field that expects a stored string value,
# you may need to pass a list of strings or an object. This depends on your Jira config.
CUSTOM_FIELD_AS_LIST: List[str] = [
    # "customfield_XXXXX"
]


def env_required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


def to_adf_doc(text: str) -> Dict[str, Any]:
    """
    Convert plain text into Atlassian Document Format (ADF).
    Jira Cloud often requires ADF for 'description'.
    """
    lines = (text or "").splitlines() or [""]
    content: List[Dict[str, Any]] = []
    for line in lines:
        content.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": line}],
            }
        )
    return {"type": "doc", "version": 1, "content": content}


def parse_labels(value: str) -> List[str]:
    """
    Labels can be comma-separated in CSV.
    """
    if not value:
        return []
    # split by comma and strip whitespace
    return [v.strip() for v in value.split(",") if v.strip()]


def jira_auth() -> Tuple[str, str]:
    return (env_required("JIRA_EMAIL"), env_required("JIRA_API_TOKEN"))


def jira_base_url() -> str:
    return env_required("JIRA_BASE_URL").rstrip("/")


def create_issue_payload(
    row: Dict[str, str],
    project_key: str,
    issue_type: str,
    epic_key: Optional[str],
    assignee_account_id: Optional[str],
) -> Dict[str, Any]:
    fields: Dict[str, Any] = {
        "project": {"key": project_key},
        "issuetype": {"name": issue_type},
    }

    # Map CSV columns into Jira fields
    for csv_col, jira_field in FIELD_MAP.items():
        val = (row.get(csv_col) or "").strip()

        if not val and jira_field in ("summary",):
            continue

        if jira_field == "labels":
            fields["labels"] = parse_labels(val)
            continue

        if jira_field == "description":
            fields["description"] = to_adf_doc(val)
            continue

        # Custom field handling
        if jira_field.startswith("customfield_"):
            if jira_field in CUSTOM_FIELD_AS_LIST:
                fields[jira_field] = [val] if val else []
            else:
                fields[jira_field] = val
            continue

        # Default: pass through as a string
        fields[jira_field] = val

    # Optional: set assignee by accountId
    if assignee_account_id:
        fields["assignee"] = {"accountId": assignee_account_id}

    # Optional: link to epic (Jira Cloud instances differ; this may require a custom field)
    # Many Jira Cloud setups use a custom field for "Epic Link" (varies).
    # If your instance supports parent linking for issues under an epic, you can set "parent":
    if epic_key:
        # In company-managed projects, Epic is a parent for child issues in some configurations.
        fields["parent"] = {"key": epic_key}

    return {"fields": fields}


def create_issue(row: Dict[str, str]) -> str:
    base = jira_base_url()
    url = f"{base}/rest/api/3/issue"

    project_key = env_required("JIRA_PROJECT_KEY")
    issue_type = os.getenv("JIRA_ISSUE_TYPE", "Task")

    epic_key = os.getenv("EPIC_KEY")
    assignee_account_id = os.getenv("ASSIGNEE_ACCOUNT_ID")

    payload = create_issue_payload(row, project_key, issue_type, epic_key, assignee_account_id)

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, auth=jira_auth(), json=payload, timeout=60)
    if resp.status_code >= 300:
        raise RuntimeError(f"{resp.status_code} {resp.text}")

    data = resp.json()
    return data["key"]


def main() -> None:
    load_dotenv()

    csv_path = env_required("CSV_PATH")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise RuntimeError("CSV has no headers.")

        print("DEBUG: CSV headers detected:")
        for h in reader.fieldnames:
            print(f" - {repr(h)}")

        created = 0
        for i, row in enumerate(reader, start=1):
            try:
                key = create_issue(row)
                created += 1
                print(f"[{i}] Created {key}")
            except Exception as e:
                print(f"[{i}] ERROR {e}")

        print(f"\nDone. Created {created} issues.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C).")
        sys.exit(1)
