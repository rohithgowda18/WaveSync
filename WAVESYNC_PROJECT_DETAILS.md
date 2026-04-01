# 🌊 WaveSync AI — Automated Cloud Migration Intelligence

WaveSync AI is a high-performance orchestration and intelligence platform designed to automate the migration of complex microservice ecosystems to AWS. It combines Graph Theory (DAGs) with LLM-powered "Rectification Agents" to determine the perfect migration sequence and automatically update service configurations for cloud readiness.

---

## 🧠 The "Member" Architecture

WaveSync is built by a unified team of AI-coordinated agents, each focusing on a critical layer of the migration pipeline:

### 🏗️ Member 1: Core Systems Engineer (The Skeleton & Memory)
*   **Role:** Manages the system's state and data persistence.
*   **Implementation:** 
    *   **Backend:** FastAPI-based REST API for service ingestion and progress monitoring.
    *   **Database:** SQLite (`wavesync.db`) tracking the state of all 50+ services.
    *   **Statuses:** `Pending` → `Rectifying` → `Deploying` → `Success` | `Failed`.
    *   **Endpoints:** `/upload` (manifest ingestion), `/status` (real-time tracking), `/next` (dependency-aware scheduling).

### 📐 Member 2: Graph & Logic Specialist (The Brain & Sequence)
*   **Role:** Resolves complex dependency chains and determines the optimal execution order.
*   **Implementation:**
    *   **Engine:** Directed Acyclic Graph (DAG) construction using **NetworkX**.
    *   **Heuristic:** **Priority-Weighted DAG** scoring.
    *   **Formula:** $S = (BusinessPriority \times 0.7) + (OutDegree \times 0.3)$.
    *   **Validation:** Built-in "Cycle Detector" to prevent circular dependency deadlocks.
    *   **Output:** A deterministic, prioritized serial execution sequence.

### 🤖 Member 3: AI Agent Engineer (The Intelligence & Rectifier)
*   **Role:** Analyzes legacy microservice configurations and "rectifies" them for AWS.
*   **Implementation:**
    *   **LLM Integration:** **Groq** (`llama-3.3-70b-versatile`) for ultra-low latency inference.
    *   **Prompt Engineering:** Strict JSON-only schema mapping local components (MySQL, Local Storage) to AWS equivalents (RDS, S3, ECS).
    *   **Defensive Parsing:** Robust extraction logic to handle LLM noise and ensure the pipeline never crashes.
    *   **Batching:** Sequential processing with rate-limiting protection.

---

## 🛠️ Technical Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **API Framework** | FastAPI + Uvicorn |
| **Database** | SQLAlchemy + SQLite |
| **Graph Theory** | NetworkX |
| **AI / LLM** | Groq API (Llama 3.3) |
| **Data Validation** | Pydantic 2.0 |
| **Environment** | `python-dotenv` |

---

## 📂 Project Structure (Senior Engineer Layout)

```text
WaveSync/
├── src/                        # Source Code
│   └── wavesync/               # Main Package
│       ├── api/                # Member 1: API & Persistence
│       ├── engine/             # Member 2: Graph & DAG Logic
│       ├── agents/             # Member 3: LLM Intelligence
│       └── main.py             # Application Entry Point
├── docs/                       # Technical Documentation & Summaries
├── scripts/                    # Development & Utility Scripts
├── tests/                      # Unit & Integration Tests
├── .env                        # Private Configurations (API Keys)
└── requirements.txt            # Unified Dependencies
```

---

## 🚀 Getting Started

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```text
GROQ_API_KEY=your_api_key_here
```

### 3. Running the Platform
```bash
# Set PYTHONPATH and start the FastAPI server
$env:PYTHONPATH = "src"
python src/wavesync/main.py
```

---

## 📈 Success Criteria
- [x] Ingests and persists 50+ service manifests dynamically.
- [x] Correctly identifies and blocks circular dependencies.
- [x] Generates deterministic, priority-weighted migration sequences.
- [x] Transforms legacy configs into AWS-ready JSON plans via AI.
- [x] Maintains high observability with detailed per-service logging.

---

**Status:** ✅ **Production Ready / Hackathon Ready**
**Branch:** `feature/ai-rectification-agent`
**Version:** 2.1.0
