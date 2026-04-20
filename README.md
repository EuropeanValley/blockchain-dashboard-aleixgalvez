[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/N3kLi3ZO)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23640742&assignment_repo_type=AssignmentRepo)

# Blockchain Dashboard Project

Use this repository to build your blockchain dashboard project.  
Update this README every week.

## Student Information

| Field | Value |
|---|---|
| Student Name | Alex Galvez |
| GitHub Username | aleixgalvez |
| Project Title | CryptoChain Analyzer Dashboard |
| Chosen AI Approach | Anomaly detector for abnormal inter-block times |

## Module Tracking

Use one of these values: `Not started`, `In progress`, `Done`

| Module | What it should include | Status |
|---|---|---|
| M1 | Proof of Work Monitor | In progress |
| M2 | Block Header Analyzer | Not started |
| M3 | Difficulty History | Not started |
| M4 | AI Component | Not started |

## Current Progress

- GitHub Classroom repository accepted successfully.
- Project template reviewed and repository structure checked.
- README updated with initial project information.
- First blockchain API call tested successfully with real Bitcoin block data.

## Next Step

- Integrate the API data into the dashboard and start Module M1.

## Main Problem or Blocker

- No major blocker at the moment.

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```text
template-blockchain-dashboard/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- app.py
|-- api/
|   `-- blockchain_client.py
`-- modules/
    |-- m1_pow_monitor.py
    |-- m2_block_header.py
    |-- m3_difficulty_history.py
    `-- m4_ai_component.py
```