# 🏛️ WaveSync AI — System Architecture

WaveSync AI follows a modular, package-based architecture that separates concerns into a clean, scalable hierarchy. The system is divided into three primary "Member" roles, each responsible for a critical layer of the migration pipeline.

## 📦 Package Hierarchy (`src/wavesync/`)

The core logic is organized into specialized sub-packages:

### 💾 1. API & Persistence (`api/`)
Handles the "Skeleton" and state persistence using a lightweight, high-performance SQLite engine and FastAPI.
- **Ingestion**: Bulk manifest uploads.
- **Monitoring**: Real-time migration metrics.

### 📐 2. Graph & Orchestration (`engine/`)
The "Brain" of the project. Ensures deterministic execution and constraint satisfaction using advanced Graph Theory.
- **DAG Builder**: Constructs and validates the dependency graph.
- **Scheduler**: Calculates migration scores and sequences services.

### 🤖 3. AI Intelligence (`agents/`)
The "Solution Architect." Rectifies legacy configurations into cloud-ready AWS plans using LLM agents.
- **Service Classifier**: Determines the service type (Stateful, Stateless, etc.).
- **AWS Architect**: Maps legacy tech to AWS services.
- **Risk Agent**: Evaluates migration difficulty.

### 🚀 4. Execution Layer
- **Simulation**: A demo dashboard for real-time visualization.
- **Deployment**: The final stage for AWS Lambda/ECS provisioning.
