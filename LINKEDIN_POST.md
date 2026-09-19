# 🎙️ LinkedIn Post: OmniMeet (AI Smart Meeting Recorder & NLP Summarizer)

*Ready to copy and paste directly to LinkedIn.*

---

🚀 Excited to unveil **OmniMeet** — an AI-powered Dual-Audio Meeting Recorder & Point-Wise NLP Summarization Engine built entirely with Python! 🎙️🤖

Ever sat through a 60-minute sprint sync or client kickoff, only to spend another 30 minutes manually typing out Minutes of the Meeting (MoM) and chasing down who owns which action item? 

Existing bot recorders often get blocked by enterprise IT security, and capturing both your voice AND your colleagues' voices from Zoom, Microsoft Teams, or Google Meet without messy virtual audio cables has always been a major headache.

I built **OmniMeet** to solve this end-to-end with a seamless local-first architecture:

### 💡 What OmniMeet Does:
1. 🎧 **Dual-Sound Audio Mixer**: Simultaneously records **BOTH sound sources** — your microphone (your voice) AND remote attendees' voices (Zoom / Teams / Meet / Slack audio) mixed into a high-fidelity synchronized stream with zero external software or virtual cables.
2. 🗣️ **Local Speech-to-Text (STT)**: Transcribes the meeting into timestamped speaker turns using local OpenAI Whisper.
3. 🧠 **Point-Wise NLP Distillation**: Converts raw conversational dialogue into a crisp, structured Minutes of the Meeting (MoM):
   - 🎯 **Executive Summary** (Core takeaways in 2–3 sentences)
   - 📌 **Categorized Discussion Topics** (Grouped by themes)
   - 📋 **Action Items Matrix** (Automatically extracts: *Task, Owner, Deadline, and Priority*)
   - ✅ **Key Decisions Reached** (Consensus & business sign-offs)
   - ⚠️ **Risks & Blockers**
4. 📄 **1-Click Executive PDF & Email Generation**: Generates executive-ready PDFs via ReportLab, formatted Markdown archives, and pre-composed email drafts ready to paste into Outlook, Gmail, or Slack.
5. ⚡ **76% Information Compression**: Distills 45-minute meetings into high-density, actionable bullet points in seconds!

### 🛠️ The Tech Stack:
- **Backend**: Python 3.12, NumPy
- **Audio Capture**: Web Audio API & WebRTC stream mixer (Microphone + System Display loopback)
- **Transcription**: Local OpenAI Whisper & SpeechRecognition
- **NLP Engine**: TextRank summarization, regex heuristic entity extraction, sentiment telemetry
- **Frontend & UI**: Streamlit with custom Dark Glassmorphism aesthetic
- **Document Engine**: ReportLab for executive corporate PDF reporting

All running locally with zero cloud API dependency required! 🔒

Check out the full repository and code below 👇
GitHub: [https://github.com/your-username/smart-meeting-summarizer-nlp]

Would love to hear your thoughts on how your teams currently capture and track meeting action items! 💬

---

#Python #ArtificialIntelligence #NLP #MachineLearning #SpeechToText #OpenAIWhisper #Streamlit #Productivity #SoftwareEngineering #Automation #DataScience #WebRTC
