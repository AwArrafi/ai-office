# PROJECT HANDOFF — AI OFFICE

## 1. Project Overview

Saya ingin membangun sebuah aplikasi bernama **AI Office**, yaitu virtual office berbasis multi-agent AI.

Tujuan proyek ini adalah membuat sebuah kantor virtual yang memiliki beberapa AI agent dengan tanggung jawab berbeda. Agent bukan hanya ditampilkan sebagai karakter animasi, tetapi benar-benar dapat menerima instruksi, mengerjakan task, menggunakan tools, dan melaporkan hasil pekerjaan.

Saya ingin membangun sistem ini secara bertahap, dimulai dari simulasi lokal dengan biaya seminimal mungkin.

Target awal adalah membuktikan bahwa beberapa agent dengan role berbeda dapat bekerja sama menggunakan model AI lokal.

## 2. Project Objectives

Target utama:

1. Memiliki dashboard virtual office yang dapat diakses melalui browser.
2. Memiliki beberapa AI agent dengan role berbeda.
3. Agent dapat menerima dan membagi pekerjaan.
4. Agent dapat berkomunikasi melalui backend.
5. Agent dapat menggunakan model AI lokal melalui Ollama.
6. Agent dapat menjalankan task dan menghasilkan laporan.
7. Memiliki opsi integrasi model cloud seperti DeepSeek dan OpenRouter.
8. Memiliki sistem pencatatan aktivitas, penggunaan token, dan biaya.
9. Nantinya dapat di-deploy ke VPS.

## 3. AI Agent Structure

Untuk MVP, gunakan tiga agent utama:

### Manager Agent
- Menerima instruksi dari user.
- Menganalisis tujuan pekerjaan.
- Membagi pekerjaan menjadi beberapa task.
- Menentukan agent yang bertanggung jawab.
- Menggabungkan hasil pekerjaan.
- Memberikan laporan akhir.

### Developer Agent
- Menerima task dari Manager.
- Menganalisis kebutuhan teknis.
- Membuat atau mengubah kode.
- Membaca project repository.
- Melaporkan hasil implementasi.

### QA Agent
- Memeriksa hasil pekerjaan Developer.
- Menyusun test case.
- Menjalankan pengujian yang diizinkan.
- Mengidentifikasi bug.
- Memberikan laporan hasil testing.

Untuk MVP, ketiga agent boleh menggunakan satu model lokal yang sama, tetapi memiliki system prompt dan konteks masing-masing.

Jangan langsung membuat sistem multi-agent yang kompleks atau paralel. Prioritaskan workflow berurutan yang dapat berjalan dengan baik.

## 4. AI Model Strategy

Gunakan pendekatan hybrid dengan local-first untuk tahap simulasi.

### Local AI
Primary runtime: Ollama.

Model awal yang ingin diuji:
- Qwen3 1.7B.
- Qwen3 4B jika hardware mencukupi.
- Qwen2.5-Coder 3B untuk eksperimen coding.

Model harus dipilih berdasarkan hasil pengujian hardware, terutama VRAM GPU dan RAM.

### Cloud AI
Provider yang akan dipertimbangkan:
- DeepSeek API.
- OpenRouter.

Cloud model bersifat opsional dan belum perlu diintegrasikan pada tahap pertama.

### Claude
Saya memiliki langganan Claude Pro.

Claude Code digunakan sebagai coding assistant untuk membantu membangun dan memelihara proyek ini.

Jangan mengasumsikan Claude Pro memberikan akses Anthropic API untuk backend aplikasi.

## 5. Technology Stack

Stack yang direncanakan:

| Layer | Technology |
|---|---|
| Frontend | Next.js |
| Language | TypeScript |
| Backend | Python + FastAPI |
| Local AI Runtime | Ollama |
| Initial Database | SQLite |
| Agent Orchestration | Implementasi sederhana terlebih dahulu |
| Future Orchestration | LangGraph |
| Future Database | PostgreSQL |
| Future Queue | Redis |
| Future Deployment | Docker + VPS |

Hindari menambahkan dependency atau infrastruktur yang belum dibutuhkan.

## 6. Initial Architecture

User
  |
  v
Next.js Virtual Office
  |
  v
FastAPI Backend
  |
  v
Manager Agent
  |
  +---- Developer Agent
  |
  +---- QA Agent
  |
  v
Ollama Local API
  |
  v
Qwen Local Model
  |
  v
Agent Results
  |
  v
Final Report to User

SQLite digunakan untuk menyimpan:
- Tasks.
- Agent activities.
- Task status.
- Execution history.
- Agent reports.

## 7. Hardware and Environment

Current environment:
- Operating System: Windows PC / Laptop.
- GPU: NVIDIA GTX Series.
- Exact GPU model: Not yet confirmed.
- RAM: Not yet confirmed.
- Budget: Rp300.000–750.000/month for future operation.
- Initial simulation budget: Ideally Rp0, maximum Rp100.000.

Hardware must be checked before selecting the final local model.

Use:
- `nvidia-smi` to inspect NVIDIA GPU.
- `ollama ps` to inspect model execution and GPU/CPU allocation.

Do not assume that a particular model will fit in VRAM without checking hardware.

## 8. Development Phases

### Phase 1 — Local AI Engine
- Install Ollama on Windows.
- Download Qwen3 1.7B.
- Run a local inference test.
- Verify GPU utilization.
- Test the Ollama API.

### Phase 2 — Backend
- Create FastAPI project.
- Connect FastAPI to Ollama.
- Implement basic agent service.
- Implement Manager, Developer, and QA roles.
- Store task and activity history using SQLite.

### Phase 3 — Multi-Agent Workflow
- User submits a task.
- Manager analyzes and creates subtasks.
- Developer processes assigned tasks.
- QA evaluates results.
- Manager generates final report.

### Phase 4 — Virtual Office Frontend
- Create Next.js dashboard.
- Display agent characters.
- Display agent status.
- Display task progress.
- Display activity logs.
- Display final reports.

### Phase 5 — Hybrid Model Integration
- Add DeepSeek API as an optional provider.
- Add OpenRouter as an optional multi-model gateway.
- Implement model routing.
- Track input/output token usage and cost.
- Implement model fallback.

### Phase 6 — VPS Deployment
Only after local MVP is functional:
- Deploy frontend and backend.
- Configure database.
- Connect local AI engine through a secure private network.
- Configure HTTPS and domain.
- Implement monitoring and backup.

## 9. Security Requirements

Important:
- Never expose API keys in frontend code.
- Never expose Ollama's local API directly to the public internet.
- Restrict agent access to approved project directories.
- Do not allow unrestricted terminal execution.
- Require user approval before destructive actions.
- Require approval before production deployment.
- Record agent activities.
- Protect `.env` files and credentials.

## 10. Budget Constraints

Initial target: Rp0–100.000.

Do not purchase VPS, GPU cloud, or API credits during the initial phase.

Use existing hardware and free software first.

Cloud API integration can be added later with strict spending limits.

## 11. Development Instructions

Before writing code:

1. Inspect the current development environment.
2. Explain the proposed project structure.
3. Identify missing hardware or software dependencies.
4. Propose a minimal implementation plan.
5. Do not generate the entire application in one step.

Implement incrementally and test each phase.

Do not invent successful test results.

Keep the architecture modular so local and cloud models can be switched without rewriting agent logic.

Prioritize a working MVP over unnecessary abstraction or visual complexity.

## 12. First Task

Start with Phase 1.

Help me prepare the Windows environment for Ollama and Qwen3 1.7B.

First inspect the available environment and guide me through hardware verification.

Do not start implementing the complete AI Office yet.

The immediate objective is to successfully run a local AI model and verify that the Ollama API can be accessed from the computer.
