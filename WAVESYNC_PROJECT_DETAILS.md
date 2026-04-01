# 🌊 WaveSync AI — Project Technical Architecture

WaveSync AI is a production-grade orchestration and intelligence platform designed to automate the migration of complex microservice ecosystems to AWS. It leverages Directed Acyclic Graphs (DAGs) for deterministic sequencing and LLM agents for automated infrastructure rectification.

---

## 🏛️ System Architecture (`src/` layout)

The project follows a modular, package-based architecture that separates concerns into a clean, scalable hierarchy.

```text
WaveSync/
├── src/                        # Source Code
│   └── wavesync/               # Main Package
│       ├── api/                # Member 1: Persistence & API Layer
│       ├── engine/             # Member 2: Graph & Orchestration Layer
│       ├── agents/             # Member 3: AI Intelligence Layer
│       └── main.py             # Application Entry Point
├── docs/                       # Technical Documentation
├── tests/                      # Unit & Integration Tests
└── .env                        # Configuration / Secrets
```

---

## 🏗️ Member 1: Core Systems Engineer (Data & Memory)

Responsible for the platform's "Skeleton" and state persistence using a lightweight, high-performance SQLite engine.

### 💾 Database Schema (`wavesync.db`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary Key (Auto-increment) |
| `name` | String(255) | Unique service identifier |
| `status` | String(50) | State (Pending, Rectifying, Success, Failed) |
| `priority` | Integer | Business urgency (1-10) |
| `dependencies` | String(255) | Comma-separated list of dependent service names |
| `tech_stack` | String(255) | Service technology (e.g., Python Flask, Go) |
| `database_type`| String(255) | Local database type (e.g., Local MySQL) |

### 🌐 FastAPI Implementation
*   **Ingestion:** `@app.post("/upload")` handles bulk manifest uploads of 50+ services.
*   **Orchestration:** `@app.get("/next")` provides the next available service based on dependency satisfaction.
*   **Monitoring:** `@app.get("/progress")` provides real-time migration metrics (percentage complete).

---

## 📐 Member 2: Graph & Logic Specialist (The Brain)

Ensures deterministic execution and constraint satisfaction using advanced Graph Theory.

### 🧮 Priority-Weighted DAG Heuristic
To determine the perfect migration order, the engine calculates a **Migration Score (S)** for each service:

$$S = (BusinessPriority \times 0.7) + (OutDegree \times 0.3)$$

- **Business Priority (0.7):** Directs focus to mission-critical services.
- **Out-Degree (0.3):** Prioritizes foundational services that many others depend on (bottleneck resolution).

### 🔄 Cycle Detection & Topological Sort
*   **Validation:** Uses `networkx.is_directed_acyclic_graph` to detect circular dependencies before execution.
*   **Sequence:** Implements **Modified Kahn’s Algorithm** with a priority-weighted max-heap to generate a deterministic "Serial Push List."

---

## 🤖 Member 3: AI Agent Engineer (The Intelligence)

Acts as the "Solution Architect" to rectify legacy configurations into cloud-ready AWS plans.

### 🧠 Solution Architect Role
The agent is prompted as a **Senior Cloud Migration Architect** with strict decision-mapping rules:

> [!IMPORTANT]
> **AI Mapping Rules:**
> - Local MySQL / PostgreSQL → **AWS RDS**
> - Local Files → **AWS S3**
> - Cron Jobs → **AWS EventBridge**
> - Queue → **AWS SQS**
> - Cache → **AWS ElastiCache**
> - Docker → **AWS ECS / EKS**

### 🛡️ Defensive Parsing & Token Management
*   **Balanced Brace Extraction:** A robust JSON parser ensures that even if the LLM includes markdown or conversational noise, the final architecture plan is correctly extracted.
*   **Zero-Rupee Optimization:** Implements global rate-limiting (`GLOBAL_RATE_LIMIT_DELAY`) to process 50+ consecutive services without triggering API throttling or exceeding quota limits on the **Groq (Llama 3.3)** platform.

---

## 🚀 Execution Guide

### 🔧 Setup
```powershell
# 1. Environment
python -m venv venv
.\venv\Scripts\activate

# 2. Dependencies
pip install -r requirements.txt
```

### 🏃 Start Service
```powershell
$env:PYTHONPATH = "src"
python src/wavesync/main.py
```

---

**Status:** ✅ **Production Ready**
**Author:** Senior AI Agent Team
**Target:** Hackathon - Cloud Migration Track
