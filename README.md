💊 Prescription-to-Life

An AI-powered multi-agent application that helps users understand and organize information from prescription images.

🚀 Project Overview

Prescription-to-Life allows a user to upload a prescription image and select either English or Urdu.

The system:

1. Reads the prescription.
2. Checks whether the extracted information is reliable.
3. Stops when important handwriting is unclear.
4. Organizes medicines into a schedule.
5. Provides a simple explanation of each medicine's general purpose.
6. Presents the final information in English or Urdu.

The main goal is to reduce hallucinations when prescription handwriting is unclear.

---

🤖 Multi-Agent System

Agent 1 — Prescription Vision Agent

Uses a vision-capable Groq model to read the uploaded prescription.

Model:

qwen/qwen3.8-27b

It extracts:

- Medicine name
- Dosage
- Frequency
- Timing
- Duration

It marks unreadable information as "UNCLEAR" instead of guessing.

Agent 2 — Safety Verification Agent

Uses:

openai/gpt-oss-120b

Checks the extracted prescription information and decides whether it is safe to continue.

If important information is unclear, the pipeline stops.

Agent 3 — Medicine Schedule Agent

Uses:

openai/gpt-oss-120b

Creates a simple schedule containing:

- Morning
- Afternoon
- Evening
- Night

The agent does not invent missing timings.

Agent 4 — Medicine Explanation Agent

Uses:

openai/gpt-oss-120b

Provides a short, simple explanation of a medicine's general purpose when it can be determined reliably.

Agent 5 — Language Agent

Uses:

openai/gpt-oss-120b

Provides the final output in:

- English
- Urdu

It must not change medicine names, dosage, frequency, timing, or duration.

---

🏗️ Architecture

Prescription Image
       │
       ▼
┌───────────────────────┐
│ Agent 1               │
│ Vision / OCR          │
│ Qwen 3.8 27B          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Agent 2               │
│ Safety Verification   │
│ GPT-OSS 120B          │
└───────────┬───────────┘
            │
       Reliable?
       /       \
     NO         YES
     │           │
     ▼           ▼
   STOP    ┌───────────────┐
           │ Agent 3       │
           │ Schedule      │
           │ GPT-OSS 120B  │
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │ Agent 4       │
           │ Explanation   │
           │ GPT-OSS 120B  │
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │ Agent 5       │
           │ Language      │
           │ GPT-OSS 120B  │
           └───────┬───────┘
                   │
                   ▼
             Streamlit UI

---

🛠️ Technology Stack

- Python
- Streamlit
- Groq API
- OpenAI GPT-OSS 120B
- Qwen 3.8 27B
- Pandas
- GitHub
- Streamlit Cloud

---

📁 Project Structure

Prescription-to-Life/
│
├── app.py
├── agent.py
├── requirements.txt
├── README.md
└── .gitignore

---

⚙️ Installation

Clone the repository:

git clone YOUR_GITHUB_REPOSITORY_URL

Install the dependencies:

pip install -r requirements.txt

Create:

.streamlit/secrets.toml

Add:

GROQ_API_KEY = "YOUR_GROQ_API_KEY"

Run:

streamlit run app.py

---

☁️ Streamlit Cloud Deployment

1. Upload the project to GitHub.
2. Create a new Streamlit Cloud application.
3. Select the GitHub repository.
4. Select "app.py".
5. Open the application's Secrets settings.
6. Add:

GROQ_API_KEY = "YOUR_GROQ_API_KEY"

7. Deploy.

Never upload your API key to GitHub.

---

🔐 Hallucination Prevention

The application uses a verification gate.

Unreadable prescription
        ↓
UNCLEAR
        ↓
Safety Agent
        ↓
STOP

The system should never invent:

- Medicine names
- Dosages
- Frequencies
- Timings
- Durations

---

⚠️ Disclaimer

Prescription-to-Life is an educational AI project.

It does not replace a doctor, pharmacist, or other qualified healthcare professional.

Users should confirm unclear prescription information with a healthcare professional.

The application is not intended to independently diagnose diseases or prescribe medicines.

---

🔮 Future Improvements

- Verified medicine database
- Medicine interaction checking
- Prescription history
- Downloadable schedules
- Voice output
- Improved Urdu support
- Medicine reminders
- RAG-based medicine information
- Doctor/pharmacist verification workflow

---

👩‍💻 Project Type

Generative AI + Multi-Agent AI + Computer Vision + Healthcare

Built with Python, Streamlit, Groq API, GPT-OSS 120B, and Qwen 3.8 27B.
