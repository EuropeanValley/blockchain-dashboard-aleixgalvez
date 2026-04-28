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
| M1 | Proof of Work Monitor | Done |
| M2 | Block Header Analyzer | Done |
| M3 | Difficulty History | Done |
| M4 | AI Component | Done |
| M5 | Merkle Proof Verifier | Done |
| M6 | Security Score | Done |
| M7 | Second AI Approach | Done |

## Current Progress

- GitHub Classroom repository accepted and project structure reviewed successfully.
- The blockchain API client was implemented and tested with real Bitcoin data from public APIs.
- M1 was completed with live Proof of Work metrics such as block height, difficulty, transaction count, hash, nonce, bits, and leading zeros.
- M2 was completed with block header analysis and local Proof of Work verification using reconstructed 80-byte headers and double SHA-256.
- M3 was completed with difficulty history visualizations across adjustment periods and block-time ratio analysis against the 600-second target.
- M4 was completed with an anomaly detector for unusual inter-block times based on an exponential baseline, including timestamp anomaly handling.
- M5 was completed with a Merkle proof verifier that reconstructs the proof path step by step and checks whether the computed Merkle root matches the official block Merkle root.
- M6 was completed with a security score module that estimates the cost of a 51% attack and visualizes attack success probability as the number of confirmations increases.
- M7 was completed with a second AI approach based on a regression model that predicts the next Bitcoin difficulty adjustment and compares its performance against a naive baseline.

## Next Step

- Finalize the report PDF, review the dashboard presentation, and make a final full test of all modules before submission.

## Main Problem or Blocker

- No major blocker at the moment. The current focus is polishing the final delivery and documentation.

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
|-- modules/
|   |-- m1_pow_monitor.py
|   |-- m2_block_header.py
|   |-- m3_difficulty_history.py
|   |-- m4_ai_component.py
|   |-- m5_merkle_proof.py
|   |-- m6_security_score.py
|   `-- m7_difficulty_predictor.py
`-- report/
    `-- final_report.pdf
```

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-20 13:31 CEST  
Status: Green

Strength:
- Your repository keeps the expected classroom structure.

Improve now:
- The kickoff evidence is strong and aligned with the session goals.

Next step:
- Keep building on this start and prepare the next milestone.
<!-- student-repo-auditor:teacher-feedback:end -->