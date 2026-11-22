# AI OFFICE
## Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** November 2026  
**Product Type:** Personal Hybrid Multi-Agent AI Workspace  
**Development Status:** Planning / Pre-MVP  
**Initial Platform:** Windows Desktop + Web Browser  
**Primary Language:** Indonesian and English

---

# 1. PRODUCT OVERVIEW

## 1.1 Product Description

AI Office adalah aplikasi personal berbasis Multi-Agent AI yang menggabungkan konsep virtual office dengan sistem produktivitas berbasis AI agents.

Aplikasi ini memungkinkan pengguna memiliki sebuah kantor virtual yang terdiri dari beberapa AI agent dengan tanggung jawab dan kemampuan berbeda.

Setiap agent memiliki:
- Identitas dan role.
- Instruksi atau system prompt.
- Model AI yang digunakan.
- Status aktivitas.
- Daftar pekerjaan.
- Riwayat aktivitas.
- Hak akses terhadap tools tertentu.

Pengguna bertindak sebagai CEO atau pemilik kantor yang dapat memberikan instruksi, membuat pekerjaan, memantau aktivitas agent, dan memberikan persetujuan terhadap tindakan tertentu.

AI Office bukan sekadar chatbot dengan beberapa persona. Sistem harus memiliki kemampuan untuk mengatur workflow, mendelegasikan pekerjaan, menggunakan tools, menyimpan hasil, dan menghasilkan laporan.

## 1.2 Product Vision

"Build a personal AI-powered virtual company where intelligent agents collaborate, execute real tasks, and assist users in managing their digital work."

Membangun perusahaan virtual pribadi yang memungkinkan berbagai AI agent bekerja sama secara terstruktur untuk membantu menyelesaikan pekerjaan nyata.

## 1.3 Product Philosophy

Prinsip utama pengembangan:

1. Functionality over Animation: fungsi agent lebih penting daripada animasi karakter.
2. Local-first, Cloud-capable: utamakan model lokal, tetapi tetap mendukung model cloud.
3. Human-in-the-loop: pengguna tetap memiliki kendali atas keputusan dan tindakan penting.
4. Modular Architecture: model, agent, dan tools dapat diganti tanpa membangun ulang keseluruhan aplikasi.
5. Cost-conscious AI: penggunaan model dan token harus dapat dipantau dan dikontrol.
6. Incremental Development: pembangunan dilakukan secara bertahap berdasarkan MVP.

---

# 2. PROBLEM STATEMENT

Penggunaan AI saat ini sering kali masih berbentuk interaksi satu lawan satu antara pengguna dan chatbot.

Beberapa keterbatasannya:

- Pengguna harus memberikan instruksi secara manual untuk setiap pekerjaan.
- Pekerjaan kompleks memerlukan banyak interaksi berulang.
- Pembagian pekerjaan berdasarkan spesialisasi belum terorganisasi dalam satu workspace.
- Penggunaan berbagai model AI dapat menjadi sulit dikelola.
- Biaya penggunaan model cloud dapat meningkat tanpa monitoring.
- Riwayat pekerjaan dan aktivitas AI tersebar di berbagai aplikasi.

AI Office dirancang untuk mengatasi permasalahan tersebut melalui sistem multi-agent yang terorganisasi.

---

# 3. PRODUCT OBJECTIVES

Tujuan utama:

1. Membuat virtual office yang dapat menampilkan agent dan aktivitasnya.
2. Menyediakan sistem multi-agent dengan pembagian role yang jelas.
3. Menghubungkan agent dengan model AI lokal dan cloud.
4. Memungkinkan agent menerima, membagi, dan menyelesaikan pekerjaan.
5. Menyediakan mekanisme approval untuk tindakan penting.
6. Menyimpan task, laporan, dan riwayat aktivitas.
7. Menyediakan monitoring penggunaan model dan biaya.
8. Menyiapkan arsitektur yang dapat dikembangkan dan di-deploy ke VPS.

## 3.1 Success Metrics

Target keberhasilan MVP:

- Pengguna dapat mengirim instruksi melalui dashboard.
- Manager dapat membuat dan mengalokasikan task kepada agent.
- Developer dapat memproses task menggunakan model AI.
- QA dapat mengevaluasi hasil pekerjaan.
- Manager dapat menggabungkan hasil menjadi laporan akhir.
- Semua aktivitas dapat dilihat melalui dashboard.
- Pengguna dapat menyetujui atau menolak tindakan yang membutuhkan approval.
- Sistem dapat berjalan menggunakan model lokal tanpa API berbayar.
- Penggunaan API cloud dapat dicatat apabila integrasi cloud diaktifkan.

---

# 4. TARGET USER

## 4.1 Primary User

Personal user / individual developer.

Karakteristik:
- Memiliki pengetahuan dasar software development.
- Menggunakan Windows PC atau laptop.
- Memiliki GPU NVIDIA GTX Series.
- Tertarik pada AI automation dan multi-agent systems.
- Ingin menggunakan AI untuk produktivitas dan pengembangan software.
- Memiliki keterbatasan anggaran operasional.

## 4.2 User Role

Untuk MVP hanya terdapat satu jenis pengguna:

**CEO / Owner**

Hak akses:
- Mengelola kantor virtual.
- Memberikan instruksi.
- Membuat dan mengelola task.
- Mengatur agent.
- Memilih model AI.
- Memantau aktivitas.
- Menyetujui atau menolak tindakan agent.
- Melihat laporan dan penggunaan biaya.

Multi-user dan role management tidak termasuk MVP.

---

# 5. PRODUCT SCOPE

## 5.1 MVP Scope

Fitur yang wajib tersedia:

1. Virtual Office Dashboard.
2. Agent Management.
3. Task Management.
4. Agent Orchestration.
5. Local AI Integration.
6. Model Configuration.
7. Human Approval System.
8. Activity Logs.
9. Execution Reports.
10. Basic Cost Monitoring.

## 5.2 Future Scope

Fitur yang ditunda:

- Multi-user access.
- Public SaaS platform.
- WhatsApp integration.
- Voice assistant.
- Advanced autonomous scheduling.
- Advanced memory and knowledge base.
- Multiple virtual office locations.
- Real-time agent meetings.
- Complex parallel agent orchestration.
- Advanced analytics.
- Cloud GPU hosting.

---

# 6. AGENT STRUCTURE

MVP menggunakan tiga agent utama.

## 6.1 Manager Agent

Role: AI Team Manager.

Responsibilities:
- Menerima instruksi dari CEO.
- Menganalisis tujuan pekerjaan.
- Membuat task breakdown.
- Menentukan agent yang sesuai.
- Mengalokasikan task.
- Memantau hasil pekerjaan.
- Menggabungkan hasil dari agent.
- Menghasilkan laporan akhir.

Input:
- User instruction.
- Project context.
- Available agents.
- Available tools.

Output:
- Task breakdown.
- Task assignments.
- Execution instructions.
- Final report.

Manager tidak boleh melakukan tindakan berisiko tanpa persetujuan pengguna.

## 6.2 Developer Agent

Role: AI Software Engineer.

Responsibilities:
- Menerima task dari Manager.
- Menganalisis kebutuhan teknis.
- Membaca source code yang diizinkan.
- Membuat atau mengubah kode.
- Membuat dokumentasi teknis.
- Menjalankan pengujian yang diizinkan.
- Melaporkan hasil pekerjaan.

Initial capabilities:
- Code analysis.
- Code generation.
- Bug investigation.
- Basic debugging.
- Documentation generation.

Developer Agent tidak memiliki akses bebas ke seluruh filesystem.

## 6.3 QA Agent

Role: AI Quality Assurance Engineer.

Responsibilities:
- Mengevaluasi hasil Developer.
- Memeriksa perubahan kode.
- Membuat test cases.
- Menjalankan pengujian yang diizinkan.
- Mengidentifikasi bug.
- Memberikan hasil evaluasi.
- Mengirimkan feedback untuk perbaikan.

Output:
- Test report.
- Identified issues.
- Pass/fail status.
- Recommendations.

QA tidak boleh menyatakan pekerjaan berhasil apabila pengujian belum benar-benar dilakukan.

## 6.4 Agent Status

Setiap agent memiliki status:

- Idle
- Thinking
- Working
- Reviewing
- Waiting Approval
- Completed
- Failed
- Offline

Status harus mencerminkan proses yang benar-benar terjadi, bukan animasi acak.

---

# 7. FUNCTIONAL REQUIREMENTS

## FR-01: Virtual Office Dashboard

Description:

Sistem menampilkan kantor virtual sebagai antarmuka utama.

Requirements:
- Menampilkan karakter Manager, Developer, dan QA.
- Menampilkan nama dan role agent.
- Menampilkan status aktivitas.
- Menampilkan indikator pekerjaan aktif.
- Menampilkan akses menuju task management.
- Menampilkan ringkasan aktivitas kantor.

Acceptance Criteria:
- Pengguna dapat melihat seluruh agent yang terdaftar.
- Status agent berubah mengikuti aktivitas backend.
- Status tidak dibuat secara acak hanya untuk visual.
- Pengguna dapat membuka detail masing-masing agent.

## FR-02: Agent Management

Description:

Sistem menyediakan pengelolaan agent.

Requirements:
- Melihat daftar agent.
- Melihat detail agent.
- Mengatur nama dan deskripsi.
- Mengatur role.
- Mengatur system prompt.
- Memilih model yang digunakan.
- Mengaktifkan atau menonaktifkan agent.

Acceptance Criteria:
- Setiap agent memiliki identitas unik.
- Setiap agent memiliki konfigurasi tersendiri.
- Perubahan konfigurasi tersimpan di database.
- Agent yang dinonaktifkan tidak menerima task baru.

## FR-03: Task Management

Description:

Pengguna dapat membuat dan memantau pekerjaan.

Requirements:
- Membuat task melalui dashboard.
- Menampilkan task list.
- Melihat detail task.
- Menampilkan agent yang bertanggung jawab.
- Melihat status task.
- Melihat hasil pekerjaan.
- Menyimpan riwayat eksekusi.

Task status:
- Pending
- Assigned
- In Progress
- Waiting Approval
- Under Review
- Completed
- Failed
- Cancelled

Acceptance Criteria:
- Setiap task memiliki ID unik.
- Task memiliki deskripsi dan status.
- Setiap perubahan status tercatat.
- Task dapat ditelusuri hingga laporan akhirnya.

## FR-04: Agent Orchestration

Description:

Sistem mengatur komunikasi dan alur kerja antar-agent.

Initial workflow:

1. User memberikan instruksi.
2. Manager menganalisis instruksi.
3. Manager membuat task breakdown.
4. Manager menentukan agent.
5. Developer mengerjakan task.
6. QA melakukan evaluasi.
7. Manager menggabungkan hasil.
8. Sistem menampilkan laporan kepada pengguna.

Acceptance Criteria:
- Workflow dapat berjalan secara berurutan.
- Agent menerima input sesuai tanggung jawabnya.
- Hasil agent disimpan.
- Kegagalan agent dapat dicatat.
- Pengguna dapat menghentikan task.
- Sistem tidak menjalankan loop tanpa batas.

## FR-05: Local AI Integration

Description:

Sistem dapat berkomunikasi dengan model AI lokal melalui Ollama.

Requirements:
- Menghubungkan backend ke Ollama API.
- Mengirim prompt ke model lokal.
- Menerima response.
- Menangani timeout dan error.
- Menampilkan status koneksi.
- Mengidentifikasi model yang tersedia.

Initial model candidates:
- Qwen3 1.7B.
- Qwen3 4B.
- Qwen2.5-Coder 3B.

Final model selection must depend on actual hardware testing.

Acceptance Criteria:
- Backend berhasil mengirim request ke Ollama.
- Model menghasilkan response.
- Error ditampilkan dengan jelas apabila Ollama tidak tersedia.
- Sistem dapat digunakan tanpa cloud API.

## FR-06: Cloud AI Integration

Description:

Sistem mendukung model cloud secara modular.

Candidate providers:
- DeepSeek API.
- OpenRouter.

Requirements:
- Menyimpan API credentials secara aman.
- Memilih provider.
- Memilih model.
- Mengirim request melalui backend.
- Mencatat token usage.
- Mencatat estimasi biaya.
- Menangani provider errors.

Cloud integration merupakan fitur setelah local engine berhasil.

Acceptance Criteria:
- Model cloud dapat dipilih melalui konfigurasi.
- API key tidak terekspos di frontend.
- Usage dicatat berdasarkan request.
- Sistem dapat kembali menggunakan model lokal apabila fallback diaktifkan.

## FR-07: Model Router

Description:

Sistem menentukan model yang digunakan berdasarkan konfigurasi agent dan karakteristik task.

Requirements:
- Mendukung local model.
- Mendukung cloud model.
- Menentukan model berdasarkan agent.
- Memungkinkan pemilihan model manual.
- Mencatat provider dan model yang digunakan.
- Memiliki aturan fallback yang dapat dikonfigurasi.

Initial routing:
- Manager: Qwen lokal / DeepSeek Flash.
- Developer: Qwen lokal / DeepSeek Flash.
- QA: Qwen lokal / DeepSeek Flash.

Model Pro atau model premium dapat digunakan pada pekerjaan kompleks apabila diperlukan.

Acceptance Criteria:
- Setiap eksekusi mencatat model yang digunakan.
- Model dapat diganti tanpa mengubah business logic agent.
- Fallback tidak boleh menimbulkan request berulang tanpa batas.

## FR-08: Human Approval System

Description:

Pengguna memiliki kontrol terhadap tindakan agent.

Approval diperlukan untuk:
- Menghapus file.
- Mengubah atau menghapus data penting.
- Menjalankan perintah terminal yang berisiko.
- Mengakses resource di luar workspace yang diizinkan.
- Melakukan deployment production.
- Mengirim komunikasi eksternal.
- Melakukan transaksi atau tindakan yang tidak dapat dibatalkan.

Approval states:
- Pending
- Approved
- Rejected
- Expired

Acceptance Criteria:
- Agent tidak dapat melewati approval.
- Pengguna dapat menyetujui atau menolak.
- Setiap keputusan tercatat.
- Penolakan menghentikan tindakan terkait.

## FR-09: Activity Logs

Description:

Sistem mencatat aktivitas seluruh agent.

Data:
- Agent ID.
- Task ID.
- Action.
- Timestamp.
- Model provider.
- Model name.
- Execution status.
- Error information.

Acceptance Criteria:
- Pengguna dapat melihat aktivitas agent.
- Aktivitas dapat difilter berdasarkan agent dan task.
- Log tidak boleh menampilkan API keys atau credentials.

## FR-10: Cost Monitoring

Description:

Sistem memonitor penggunaan model AI.

Requirements:
- Mencatat input tokens.
- Mencatat output tokens.
- Mencatat provider.
- Mencatat model.
- Menghitung estimasi biaya cloud.
- Memisahkan penggunaan local dan cloud.
- Menampilkan ringkasan penggunaan.

Acceptance Criteria:
- Setiap cloud request memiliki usage record apabila provider memberikan datanya.
- Estimasi biaya berdasarkan harga model yang dikonfigurasi.
- Local inference tidak dicatat sebagai tagihan token API.
- Sistem memberikan peringatan ketika budget tercapai.

---

# 8. NON-FUNCTIONAL REQUIREMENTS

## NFR-01: Performance

- Dashboard harus responsif.
- Agent execution harus berjalan secara asynchronous.
- UI tidak boleh membeku ketika model sedang memproses.
- Status pekerjaan harus dapat diperbarui tanpa refresh halaman secara manual.
- Sistem mendukung satu task aktif pada tahap awal.

## NFR-02: Reliability

- Error model harus ditangani.
- Task yang gagal harus memiliki informasi penyebab.
- Backend harus dapat mendeteksi Ollama yang tidak tersedia.
- Riwayat pekerjaan tidak boleh hilang ketika aplikasi direstart.

## NFR-03: Security

- API keys disimpan di backend.
- Gunakan environment variables.
- Batasi filesystem access.
- Gunakan command allowlist untuk terminal.
- Jangan mengekspos Ollama API ke internet publik.
- Gunakan autentikasi meskipun aplikasi awal bersifat personal.
- Approval wajib untuk tindakan berisiko.

## NFR-04: Cost Efficiency

- Local model menjadi pilihan utama.
- Cloud API bersifat opsional.
- Terapkan batas penggunaan.
- Batasi jumlah agent iteration.
- Batasi context size sesuai kemampuan hardware.
- Jangan mengirim seluruh conversation history tanpa kebutuhan.

## NFR-05: Maintainability

- Gunakan modular architecture.
- Pisahkan agent logic dan model provider.
- Pisahkan frontend dan backend.
- Gunakan dokumentasi.
- Gunakan struktur konfigurasi yang konsisten.

---

# 9. TECHNICAL ARCHITECTURE

## 9.1 Proposed Technology Stack

Frontend:
- Next.js
- React
- TypeScript
- Tailwind CSS

Backend:
- Python
- FastAPI

AI:
- Ollama
- Qwen family models
- DeepSeek API (future)
- OpenRouter (future)

Orchestration:
- Simple sequential orchestration for MVP.
- LangGraph may be introduced when workflow complexity requires it.

Database:
- SQLite for MVP.
- PostgreSQL for production.

Future infrastructure:
- Redis.
- Docker.
- VPS.
- Tailscale.

## 9.2 High-Level Architecture

User
  |
  v
Next.js Virtual Office
  |
  v
FastAPI Backend
  |
  +---- Task Management
  |
  +---- Agent Management
  |
  +---- Approval Management
  |
  +---- Activity Logging
  |
  +---- Model Router
          |
          +---- Ollama Local
          |
          +---- DeepSeek API
          |
          +---- OpenRouter
  |
  v
SQLite Database

## 9.3 Local Development Architecture

Initial execution:

- Windows PC hosts Ollama.
- Windows PC hosts FastAPI.
- Windows PC hosts Next.js.
- SQLite stores application data.

No VPS is required for the initial MVP.

## 9.4 Future VPS Architecture

When the MVP is stable:

- VPS hosts frontend.
- VPS hosts backend.
- VPS hosts PostgreSQL.
- Local PC provides inference through secure private networking.
- Cloud AI providers remain optional.

The system must not expose local Ollama endpoints publicly.

---

# 10. DATA MODEL — INITIAL PROPOSAL

## Agents

- id
- name
- role
- description
- system_prompt
- provider
- model
- is_active
- created_at
- updated_at

## Tasks

- id
- title
- description
- status
- priority
- assigned_agent_id
- parent_task_id
- created_at
- updated_at
- completed_at

## Executions

- id
- task_id
- agent_id
- provider
- model
- status
- input_tokens
- output_tokens
- estimated_cost
- started_at
- completed_at
- error_message

## Approvals

- id
- task_id
- agent_id
- action_type
- action_payload
- status
- approved_at
- rejected_at

## Activity Logs

- id
- agent_id
- task_id
- event_type
- description
- metadata
- created_at

This schema is an initial proposal and should be refined during implementation.

---

# 11. UI/UX REQUIREMENTS

## 11.1 Design Direction

The interface combines:
- Virtual office simulation.
- Productivity dashboard.
- Agent management workspace.

The interface should feel like a digital company headquarters.

## 11.2 Main Pages

### Dashboard / Office
- Virtual office environment.
- Agent characters.
- Current agent activities.
- Active task summary.
- Office overview.

### Agents
- Agent list.
- Agent details.
- Role configuration.
- Model configuration.
- Agent activity history.

### Tasks
- Task list.
- Task detail.
- Assignment.
- Progress tracking.
- Execution results.

### Approvals
- Pending approval requests.
- Action details.
- Approve / reject controls.
- Approval history.

### Activity
- Activity feed.
- Execution logs.
- Error history.

### Settings
- Model provider configuration.
- Ollama connection.
- Cloud API configuration.
- Budget limits.
- Application settings.

## 11.3 Interaction Principles

- User must understand what each agent is doing.
- Agent status must reflect actual backend state.
- Task progress must be visible.
- Approval requests must be clear.
- Error messages must be understandable.
- Avoid unnecessary animations.
- Prioritize clarity and usability.

---

# 12. DEVELOPMENT ROADMAP

## Phase 0 — Environment Preparation

- Inspect Windows hardware.
- Identify GPU and VRAM.
- Identify available RAM.
- Install Ollama.
- Test Qwen3 1.7B.
- Verify local API.

Deliverable:
Working local AI engine.

## Phase 1 — Backend Foundation

- Initialize FastAPI.
- Configure SQLite.
- Implement Ollama client.
- Implement basic agent service.
- Implement task management.
- Implement activity logging.

Deliverable:
Backend capable of executing a single AI agent task.

## Phase 2 — Multi-Agent MVP

- Implement Manager.
- Implement Developer.
- Implement QA.
- Implement task assignment.
- Implement sequential orchestration.
- Implement final reporting.

Deliverable:
Three agents successfully collaborate on one task.

## Phase 3 — Virtual Office Frontend

- Initialize Next.js.
- Build dashboard.
- Build virtual office scene.
- Display agent characters.
- Connect real-time activity status.
- Build task interface.

Deliverable:
Functional virtual office dashboard.

## Phase 4 — Approval and Monitoring

- Implement approval workflow.
- Implement activity history.
- Implement execution logs.
- Implement token tracking.
- Implement basic cost monitoring.

Deliverable:
Controlled and observable AI Office.

## Phase 5 — Hybrid Model Integration

- Integrate DeepSeek API.
- Integrate OpenRouter.
- Implement model router.
- Implement provider fallback.
- Implement budget limits.

Deliverable:
Multi-provider AI Office.

## Phase 6 — Deployment

- Dockerize services when appropriate.
- Configure VPS.
- Configure private networking.
- Configure domain and HTTPS.
- Implement backup.
- Implement monitoring.

Deliverable:
AI Office accessible through the internet.

---

# 13. MVP ACCEPTANCE CRITERIA

MVP is considered successful when:

1. Ollama runs successfully on the local computer.
2. FastAPI can communicate with Ollama.
3. The application can create and store tasks.
4. Manager can assign tasks to Developer and QA.
5. Developer can process an assigned task.
6. QA can review the result.
7. Manager can generate a final report.
8. Frontend displays real agent statuses.
9. User can approve or reject important actions.
10. Activity logs are persisted.
11. Application works without paid API credentials.
12. Local model usage does not require cloud token billing.

---

# 14. DEVELOPMENT CONSTRAINTS

Initial budget:
- Rp0–100.000 for the simulation phase.
- No mandatory VPS subscription.
- No mandatory paid API credits.
- Use existing Windows hardware.

Hardware:
- NVIDIA GTX Series.
- Exact GPU and VRAM must be verified.
- Model size must be selected based on actual performance tests.

Development:
- Work incrementally.
- Avoid unnecessary dependencies.
- Avoid premature abstraction.
- Do not implement features outside MVP without approval.
- Do not invent test results.
- Do not execute destructive operations without approval.

---

# 15. OUT OF SCOPE FOR VERSION 1.0

The following are intentionally excluded:

- Public SaaS platform.
- Multi-tenant infrastructure.
- Autonomous financial transactions.
- Unrestricted computer control.
- Unrestricted terminal access.
- Automatic production deployment.
- Voice-based agent interaction.
- Complex agent-to-agent social simulation.
- Multiple concurrent GPU inference workloads.
- Paid cloud GPU infrastructure.

---

# 16. FINAL PRODUCT DEFINITION

AI Office v1.0 is a personal, local-first, hybrid-capable multi-agent workspace with a virtual office interface.

It enables a user to assign work to AI agents, observe their activity, review results, and approve important actions.

The first version must prove that the agents can perform real work using a local model before introducing additional infrastructure or paid cloud services.

**Core principle: Build a functional AI company first. Expand its capabilities only after the foundation works reliably.**