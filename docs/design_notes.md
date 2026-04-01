# 📝 WaveSync AI — Design Notes

## 🧠 Solution Architect Role
The agent is prompted as a **Senior Cloud Migration Architect** with strict decision-mapping rules:

> [!IMPORTANT]
> **AI Mapping Rules:**
> - Local MySQL / PostgreSQL → **AWS RDS**
> - Local Files → **AWS S3**
> - Cron Jobs → **AWS EventBridge**
> - Queue → **AWS SQS**
> - Cache → **AWS ElastiCache**
> - Docker → **AWS ECS / EKS**

### 🧮 Priority-Weighted DAG Heuristic
To determine the perfect migration order, the engine calculates a **Migration Score (S)** for each service:

$$S = (BusinessPriority \times 0.7) + (OutDegree \times 0.3)$$

- **Business Priority (0.7):** Directs focus to mission-critical services.
- **Out-Degree (0.3):** Prioritizes foundational services that many others depend on (bottleneck resolution).

### 🛡️ Defensive Parsing & Token Management
*   **Balanced Brace Extraction:** A robust JSON parser ensures that even if the LLM includes markdown or conversational noise, the final architecture plan is correctly extracted.
*   **Zero-Rupee Optimization:** Implements global rate-limiting (`GLOBAL_RATE_LIMIT_DELAY`) to process 50+ consecutive services without triggering API throttling or exceeding quota limits on the **Groq (Llama 3.3)** platform.
