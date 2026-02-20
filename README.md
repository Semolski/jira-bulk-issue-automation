# jira-bulk-issue-automation

# 🚀 Jira CSV Bulk Issue Creator (Python + Jira Cloud API)

Create Jira issues in bulk from a CSV file — designed for repeatable, standardized workflows (ex: remediation, migrations, QA checklists, compliance tasks).

This is a **sanitized, reusable template** intended for public sharing. Configure it for your Jira project by updating `.env` and the field mapping.

---

## ✅ What it does

- Creates Jira issues from CSV rows
- Supports configurable field mapping (including custom fields)
- Assigns issues automatically (optional)
- Adds labels
- Adds/updates description in Atlassian Document Format (ADF) so it works with Jira Cloud
- Optional: links issues to an Epic (if your Jira instance supports it)

---

## 🏷 Tech Stack

- Python 3.10+
- Jira Cloud REST API
- `requests`
- `python-dotenv`

---

## 📦 Install

```bash
pip install -r requirements.txt
```

---

## Windows (recommended)

Create a .env file in the project root:
```
JIRA_BASE_URL=https://company.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=your_token_here

JIRA_PROJECT_KEY=PROJ
JIRA_ISSUE_TYPE=Task

CSV_PATH=sample.csv
```

## Optional
```
EPIC_KEY=PROJ-123
ASSIGNEE_ACCOUNT_ID=your_account_id_here
```

🔒 Never commit .env to git. Use .env.example as a template.

## 📄 CSV Format
Required columns (minimum)
```
Summary

Description

Recommended columns

Labels (comma-separated)
```

any additional columns you want to map into Jira fields

Example headers:
```
Summary,Description,Labels,ClientFieldValue
```

Example row:
```
Demo University - Template Updates,"Line 1
Line 2
Line 3","automation,accessibility","123;demo-client;Demo University"
```

## ⚡ 1-minute Quick Start

Export your spreadsheet as CSV

Update .env

Run:
```
py create_issues_from_csv.py
```
You’ll see output like:
```
[1] Created PROJ-101
[2] Created PROJ-102
...
```

## 🧩 Field Mapping (important)

Jira fields vary by instance. This repo uses a simple mapping layer:

Built-in fields like ```summary, description, labels```

Custom fields like ```customfield_XXXXX```

To map CSV columns to Jira fields, edit the FIELD_MAP in create_issues_from_csv.py.

Example:
```
FIELD_MAP = {
  "Summary": "summary",
  "Labels": "labels",
  "ClientFieldValue": "customfield_XXXXX"
}
```

## 🛡 Safety

✅ Test with 2–3 rows first

✅ Verify issue type + required fields

✅ Use a dedicated test project if possible

## 🛠 Troubleshooting

### Python not recognized (Windows)

Use:
```
py --version
py create_issues_from_csv.py
```

### 401 Unauthorized

Check:

- token

- email

- base URL

### “Operation value must be an Atlassian Document”

Your Jira Cloud requires ADF for description — this script already uses ADF. If you modify description handling, keep it ADF.

### Custom field not set

Custom fields differ per Jira instance. Confirm:

- field ID (ex: customfield_12345)

- field exists on the Create screen

- your user has permission to set it

## License

#### This project is licensed under the MIT License.
