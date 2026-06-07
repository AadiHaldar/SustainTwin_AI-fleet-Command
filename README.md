# SustainTwin AI 

**Agentic Edge Intelligence for Sustainable Heavy Machinery Fleets**

SustainTwin AI is a full-stack, production-grade platform that enables autonomous fleet orchestration for industrial heavy machinery. By combining **Agentic AI, Edge AI, Digital Twins, Predictive Maintenance, and Sustainability Intelligence**, the platform transforms raw telemetry into actionable, explainable insights.

Designed for the modern industrial enterprise (construction, mining, logistics, manufacturing), SustainTwin is scalable, modular, and visually stunning.

---

## 🚀 Key Features

*   **Fleet Command Center**: A centralized, glassmorphism-styled dashboard built with Next.js, Recharts, and Framer Motion for real-time fleet oversight.
*   **Agentic Edge AI**: Simulated edge nodes run localized anomaly detection before syncing payloads to the cloud, reducing bandwidth and ensuring offline resilience.
*   **Predictive Maintenance (RUL)**: Machine health tracking that predicts Remaining Useful Life (RUL) using realistic telemetry datasets (HuggingFace/Kaggle).
*   **Sustainability Intelligence**: Carbon footprint tracking and agent-driven emission reduction recommendations (e.g., optimizing idle times, route adjustments).
*   **Explainable AI (XAI)**: Demystifies predictions using SHAP feature importance and Google Gemini LLM reasoning, providing natural language root-cause analysis.
*   **Enterprise Security**: Role-Based Access Control (RBAC) and JWT authentication built into the FastAPI backend.

---

## 🏗️ Architecture Stack

### Frontend (The "Wow" Factor)
*   **Framework**: Next.js 15 (App Router), React, TypeScript
*   **Styling**: Tailwind CSS, ShadCN UI (Dark mode, Glassmorphism aesthetics)
*   **Animations & Charts**: Framer Motion, Recharts
*   **Icons**: Lucide React

### Backend (The "Brain")
*   **Framework**: FastAPI (Python)
*   **Database**: SQLite (Development/MVP) -> Easily scalable to PostgreSQL
*   **ORM**: SQLAlchemy
*   **Agentic Framework**: LangGraph (for multi-agent reasoning)
*   **LLM Integration**: Google Gemini (for XAI)
*   **Security**: Passlib (Bcrypt), python-jose (JWT)

---

## 🛠️ Local Setup & Installation

Follow these steps to run the platform locally on your machine.

### Prerequisites
*   Node.js 18+
*   Python 3.10+
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/AadiHaldar/SustainTwin_AI-fleet-Command.git
cd SustainTwin_AI-fleet-Command
```

### 2. Backend Setup
The backend serves the API and the AI agent logic.
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

**Seed the Database:**
We use a public HuggingFace dataset to simulate realistic machinery telemetry.
```bash
python app/core/ingest_data.py
```

**Run the FastAPI Server:**
```bash
uvicorn app.main:app --reload --port 8000
```
*The API will be available at `http://localhost:8000`. You can view the interactive Swagger docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup
The frontend is the glassmorphism UI for fleet orchestration.
```bash
# Open a new terminal
cd frontend
npm install
npm run dev
```
*The dashboard will be available at `http://localhost:3000`.*

### 4. Edge Simulator (Optional)
To test the cloud-sync and edge-anomaly detection capabilities, run the simulated Edge node.
```bash
# Open a new terminal
cd edge
python main.py
```
*This script will generate telemetry and send it to the FastAPI backend every 5 seconds.*

---

## 📂 Project Structure

```text
SustainTwin/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── agents/           # LangGraph Agent logic
│   │   ├── api/              # API Routers (auth, telemetry)
│   │   ├── core/             # Config, Security, DB session
│   │   ├── models/           # SQLAlchemy DB Models
│   │   └── schemas/          # Pydantic schemas
│   └── requirements.txt
├── edge/                     # Edge Node Simulation
│   └── main.py
├── frontend/                 # Next.js Application
│   ├── src/
│   │   ├── app/              # Routes (health, sustainability, xai)
│   │   ├── components/       # UI Components (Shadcn, Sidebar)
│   │   └── lib/              # Utilities
│   └── package.json
└── README.md
```

---

## 🛡️ License

This project was built for the Tata Hackathon. All rights reserved by the creators.
