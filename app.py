"""
OmniMeet: AI Smart Meeting Recorder & Point-Wise NLP Summarizer
Built with Python, Streamlit, Web Audio Dual-Stream Capture, and Local NLP.
"""

import os
import sys
import json
import time
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

# Import local processing engines
from audio_recorder import (
    get_dual_recorder_html,
    save_uploaded_file,
    get_audio_duration_seconds,
    ensure_local_audio_receiver,
    RECORDINGS_DIR
)
from transcription_engine import (
    transcribe_audio_file,
    get_sample_meeting,
    SAMPLE_MEETINGS
)
from nlp_summarizer import generate_point_wise_summary
from report_generator import (
    generate_pdf_mom,
    generate_markdown_mom,
    generate_email_draft,
    EXPORTS_DIR
)

# Streamlit Page Configuration
st.set_page_config(
    page_title="OmniMeet | AI Meeting Recorder & Point-Wise NLP Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Start background local receiver so live recordings auto-save directly to disk
receiver_port = ensure_local_audio_receiver()

# Custom Dark Glassmorphism Styling
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    /* Metrics & Cards */
    div[data-testid="metric-container"] {
        background-color: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Custom Container Cards */
    .mom-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    
    .action-card {
        background: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    
    .decision-card {
        background: rgba(6, 78, 59, 0.3);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    
    .risk-card {
        background: rgba(120, 53, 15, 0.3);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }

    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: rgba(15, 23, 42, 0.6);
        border-radius: 8px;
        padding: 0 20px;
        color: #94a3b8;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(14, 165, 233, 0.2) !important;
        border: 1px solid #38bdf8 !important;
        color: #38bdf8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "meeting_data" not in st.session_state:
    # Check if a real user recording exists; if so, load it immediately!
    user_recs = [f for f in os.listdir(RECORDINGS_DIR) if f.startswith("live_meeting_") and f.endswith(('.wav', '.mp3', '.webm'))]
    user_recs.sort(key=lambda f: os.path.getmtime(os.path.join(RECORDINGS_DIR, f)), reverse=True)
    
    if user_recs:
        latest_rec_file = user_recs[0]
        latest_rec_path = os.path.join(RECORDINGS_DIR, latest_rec_file)
        try:
            cached_tr = transcribe_audio_file(latest_rec_path)
            cached_mom = generate_point_wise_summary(cached_tr, f"Live Meeting Session ({latest_rec_file})")
            st.session_state.meeting_data = {
                "title": f"Live Meeting Recording ({latest_rec_file})",
                "date": datetime.now().strftime("%B %d, %Y"),
                "attendees": ["You (Speaker 1)", "Meeting Attendees"],
                "transcript": cached_tr,
                "mom": cached_mom,
                "audio_path": latest_rec_path
            }
        except Exception:
            user_recs = []

    if "meeting_data" not in st.session_state:
        # Default to preloaded rich product sync
        sample = get_sample_meeting("product_strategy")
        st.session_state.meeting_data = {
            "title": sample["title"],
            "date": sample["date"],
            "attendees": sample["attendees"],
            "transcript": {
                "source": "Pre-Loaded High-Fidelity Dataset",
                "full_text": " ".join([seg["text"] for seg in sample["transcript_segments"]]),
                "segments": sample["transcript_segments"]
            },
            "mom": generate_point_wise_summary(sample, sample["title"]),
            "audio_path": os.path.join(os.path.dirname(__file__), "sample_meetings", "quarterly_sync.wav")
        }

# Sidebar: Controls & Live Demo Triggers
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/microphone.png", width=64)
    st.title("OmniMeet NLP")
    st.caption("Dual-Audio Meeting Recorder & Point-Wise MoM Generator")
    st.divider()

    st.subheader("⚡ Instant Demo Presets")
    st.caption("Test point-wise summarization instantly without recording:")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🚀 Q3 Tech Sync", use_container_width=True):
            sample = get_sample_meeting("product_strategy")
            st.session_state.meeting_data = {
                "title": sample["title"],
                "date": sample["date"],
                "attendees": sample["attendees"],
                "transcript": {
                    "source": "Sample Architecture Sync",
                    "full_text": " ".join([s["text"] for s in sample["transcript_segments"]]),
                    "segments": sample["transcript_segments"]
                },
                "mom": generate_point_wise_summary(sample, sample["title"]),
                "audio_path": os.path.join(os.path.dirname(__file__), "sample_meetings", "quarterly_sync.wav")
            }
            st.rerun()

    with col_s2:
        if st.button("💼 Client SLA", use_container_width=True):
            sample = get_sample_meeting("client_onboarding")
            st.session_state.meeting_data = {
                "title": sample["title"],
                "date": sample["date"],
                "attendees": sample["attendees"],
                "transcript": {
                    "source": "Sample Enterprise Onboarding",
                    "full_text": " ".join([s["text"] for s in sample["transcript_segments"]]),
                    "segments": sample["transcript_segments"]
                },
                "mom": generate_point_wise_summary(sample, sample["title"]),
                "audio_path": os.path.join(os.path.dirname(__file__), "sample_meetings", "quarterly_sync.wav")
            }
            st.rerun()

    st.divider()
    st.subheader("⚙️ Meeting Metadata")
    custom_title = st.text_input("Meeting Subject / Title:", value=st.session_state.meeting_data.get("title", "Executive Meeting"))
    custom_attendees = st.text_area("Participants / Attendees (comma-separated):", value=", ".join(st.session_state.meeting_data.get("attendees", ["Team Lead", "Product Owner"])))

    st.divider()
    st.subheader("💾 Recording Storage Folders")
    st.caption("Live voice recordings & exported MoM PDFs are saved directly to:")
    st.markdown(f"**📁 Audio Recordings:**<br>`{RECORDINGS_DIR}`", unsafe_allow_html=True)
    st.markdown(f"**📄 PDF / Markdown Exports:**<br>`{EXPORTS_DIR}`", unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button("📂 Open Recordings", key="btn_open_rec", use_container_width=True):
            try:
                os.startfile(RECORDINGS_DIR)
            except Exception:
                pass
    with col_f2:
        if st.button("📂 Open Exports", key="btn_open_exp", use_container_width=True):
            try:
                os.startfile(EXPORTS_DIR)
            except Exception:
                pass

    st.divider()
    st.info("💡 **Tip**: When using the **Live Dual-Sound Recorder**, select your meeting window or screen with **'Share system audio'** enabled to capture both your voice and remote participants!")

# Top Header
st.title("🎙️ OmniMeet: Dual-Sound Meeting Recorder & Point-Wise NLP Summarizer")
st.caption("Captures both sound sources (Microphone + Zoom/Teams/Meet audio) → Transcribes speech → Extracts point-wise Minutes of Meeting (MoM).")

# Telemetry Overview Bar
mom = st.session_state.meeting_data.get("mom", {})
telemetry = mom.get("telemetry", {})

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Sound Capture Source", "Dual-Channel (Mic + Sys)", "Stereo Mixed")
with col2:
    st.metric("Words Transcribed", f"{telemetry.get('total_words', 0)} Words", f"{telemetry.get('sentence_count', 0)} Sentences")
with col3:
    st.metric("NLP Compression", telemetry.get("compression_ratio", "75%"), "Point-Wise Distillation")
with col4:
    st.metric("Tone / Sentiment", telemetry.get("tone", "Action-Oriented"), "Productive Consensus")

# Main Navigation Tabs
tab_recorder, tab_upload, tab_mom, tab_transcript = st.tabs([
    "🎙️ Live Dual-Sound Meeting Recorder",
    "📁 Upload Meeting Audio File",
    "📋 Point-Wise Minutes of Meeting (MoM)",
    "📝 Timestamped Verbatim Transcript"
])

# -------------------------------------------------------------
# TAB 1: Live Dual-Sound Meeting Recorder
# -------------------------------------------------------------
with tab_recorder:
    st.subheader("Record Live Virtual or In-Person Meeting (Both Audio Channels)")
    st.markdown("""
    **How Dual-Sound Capture Works:**
    1. Click **'Start Dual-Sound Meeting Recording'** below.
    2. The browser captures your **Microphone** (your voice) AND prompts to share your **Meeting Window / Screen with Audio** (attendees' voices from Zoom, Teams, Google Meet, or Slack).
    3. Both sound streams are mixed into a synchronized high-fidelity meeting audio recording!
    """)

    # HTML5 Dual Audio Recorder Component with direct auto-save to disk
    components.html(get_dual_recorder_html(receiver_port), height=460, scrolling=False)

    st.markdown("---")
    st.markdown("#### ⚡ Transcribe & Convert Meeting Audio into Point-Wise MoM")
    
    # Check recordings directory and sort by newest first
    saved_recordings = [f for f in os.listdir(RECORDINGS_DIR) if f.endswith(('.wav', '.mp3', '.webm', '.m4a'))]
    saved_recordings.sort(key=lambda f: os.path.getmtime(os.path.join(RECORDINGS_DIR, f)), reverse=True)

    if saved_recordings:
        latest_file = saved_recordings[0]
        latest_path = os.path.join(RECORDINGS_DIR, latest_file)
        latest_size_kb = round(os.path.getsize(latest_path) / 1024, 1)
        
        st.info(f"🎙️ **Latest Recording Auto-Saved:** `{latest_file}` ({latest_size_kb} KB) — *Ready to convert to points!*")
        
        if st.button(f"⚡ 1-Click: Transcribe & Convert Latest Recording ('{latest_file}') into Points", type="primary", use_container_width=True):
            with st.spinner(f"Transcribing '{latest_file}' and extracting point-wise summary with NLP..."):
                transcript = transcribe_audio_file(latest_path)
                mom_result = generate_point_wise_summary(transcript, custom_title or f"Meeting Recording ({latest_file})")
                
                st.session_state.meeting_data = {
                    "title": custom_title or f"Meeting Recording ({latest_file})",
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "attendees": [a.strip() for a in custom_attendees.split(",") if a.strip()],
                    "transcript": transcript,
                    "mom": mom_result,
                    "audio_path": latest_path
                }
                st.success(f"✅ Transcribed what you said and converted into point-wise MoM below!")
                st.rerun()

    st.caption("Or choose from all saved recordings:")
    rec_options = [os.path.join(RECORDINGS_DIR, r) for r in saved_recordings] + ["sample_meetings/quarterly_sync.wav"]
    rec_col1, rec_col2 = st.columns([3, 1])
    with rec_col1:
        selected_rec = st.selectbox("Select saved recording to process:", rec_options, index=0 if saved_recordings else 0)
    with rec_col2:
        if st.button("🚀 Process Selected Recording", use_container_width=True):
            with st.spinner("Processing audio, transcribing dialogue, and extracting point-wise summary..."):
                transcript = transcribe_audio_file(selected_rec)
                mom_result = generate_point_wise_summary(transcript, custom_title)
                
                st.session_state.meeting_data = {
                    "title": custom_title,
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "attendees": [a.strip() for a in custom_attendees.split(",") if a.strip()],
                    "transcript": transcript,
                    "mom": mom_result,
                    "audio_path": selected_rec
                }
                st.success("✅ Meeting transcribed and point-wise MoM generated!")
                st.rerun()

    # Instant Point-Wise Preview on Tab 1 so the user immediately sees the converted points
    cur_mom_preview = st.session_state.meeting_data.get("mom", {})
    cur_audio_name = os.path.basename(st.session_state.meeting_data.get("audio_path", "sample"))
    
    st.markdown("---")
    st.markdown(f"### 📋 Converted Points for: `{cur_audio_name}`")
    st.caption("What you said has been processed and converted into the following structured points:")
    
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        st.markdown("**🎯 Executive Summary:**")
        st.markdown(f"""
        <div class="mom-card" style="margin-bottom:10px;">
            <p style="font-size: 13px; line-height: 1.5; color: #f1f5f9; margin: 0;">
                {cur_mom_preview.get('executive_summary', 'No summary available.')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**📌 Key Discussion Points:**")
        for dp in cur_mom_preview.get("discussion_points", []):
            st.markdown(f"**{dp.get('topic')}:**")
            for b in dp.get("bullets", []):
                st.markdown(f"- {b}")
                
    with col_p2:
        st.markdown("**📋 Action Items Matrix:**")
        actions_list = cur_mom_preview.get("action_items", [])
        if not actions_list:
            st.info("No action items assigned in this recording segment.")
        else:
            for ai in actions_list:
                st.markdown(f"- **{ai.get('owner')}** ({ai.get('deadline')}): {ai.get('task')} `[{ai.get('priority')} Priority]`")
                
        st.markdown("**✅ Decisions & Agreements:**")
        decisions_list = cur_mom_preview.get("decisions", [])
        for d in decisions_list:
            st.markdown(f"""
            <div class="decision-card" style="margin-bottom:6px;">
                <span style="font-size: 12px; color: #a7f3d0;">• {d}</span>
            </div>
            """, unsafe_allow_html=True)
            
    st.info("💡 **Looking for the full view & export options?** Switch to **Tab 3: '📋 Point-Wise Minutes of Meeting (MoM)'** above to download the executive PDF, Markdown file, or email draft!")

# -------------------------------------------------------------
# TAB 2: Upload Audio File
# -------------------------------------------------------------
with tab_upload:
    st.subheader("Upload an Existing Meeting Audio or Video File")
    st.caption("Supports Zoom, Microsoft Teams, Google Meet, and dictaphone recordings (.wav, .mp3, .m4a, .webm, .mp4).")

    uploaded_file = st.file_uploader("Drop meeting recording here:", type=["wav", "mp3", "m4a", "webm", "mp4"])

    if uploaded_file is not None:
        saved_path = save_uploaded_file(uploaded_file)
        st.audio(uploaded_file)
        st.write(f"**File Size:** `{round(uploaded_file.size / (1024*1024), 2)} MB` | **Saved Location:** `{saved_path}`")

        if st.button("🎯 Transcribe & Generate Point-Wise MoM", key="btn_transcribe_upload", use_container_width=True):
            with st.spinner("Transcribing speech and extracting key discussion points & action items..."):
                transcript = transcribe_audio_file(saved_path)
                mom_result = generate_point_wise_summary(transcript, custom_title)

                st.session_state.meeting_data = {
                    "title": custom_title,
                    "date": datetime.now().strftime("%B %d, %Y"),
                    "attendees": [a.strip() for a in custom_attendees.split(",") if a.strip()],
                    "transcript": transcript,
                    "mom": mom_result,
                    "audio_path": saved_path
                }
                st.success("✅ Audio transcribed & point-wise MoM ready!")
                st.rerun()

# -------------------------------------------------------------
# TAB 3: Point-Wise Minutes of Meeting (MoM)
# -------------------------------------------------------------
with tab_mom:
    cur_mom = st.session_state.meeting_data.get("mom", {})
    
    # Header & Export Toolbar
    st.subheader(f"📋 {st.session_state.meeting_data.get('title', 'Minutes of Meeting')}")
    st.caption(f"**Date:** {st.session_state.meeting_data.get('date')} | **Attendees:** {', '.join(st.session_state.meeting_data.get('attendees', []))}")

    # Action Toolbar for 1-Click Exports
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        pdf_path = generate_pdf_mom(cur_mom)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download Executive PDF MoM",
                data=f.read(),
                file_name=f"Minutes_of_Meeting_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
    with exp_col2:
        md_content = generate_markdown_mom(cur_mom)
        st.download_button(
            "📝 Download Markdown (.md)",
            data=md_content,
            file_name="Meeting_Minutes.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    with exp_col3:
        email_draft = generate_email_draft(cur_mom)
        with st.popover("✉️ Preview Team Email Draft", use_container_width=True):
            st.text_area("Ready to Copy & Paste into Outlook/Gmail/Slack:", value=email_draft, height=280)

    st.divider()

    # SECTION 1: Executive Summary
    st.markdown("### 🎯 1. Executive Summary")
    st.markdown(f"""
    <div class="mom-card">
        <p style="font-size: 14px; line-height: 1.6; color: #e2e8f0; margin: 0;">
            {cur_mom.get('executive_summary', 'No summary available.')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 2: Point-Wise Key Discussions (Thematic Categories)
    st.markdown("### 📌 2. Point-Wise Key Discussions (Grouped by Topic)")
    discussion_groups = cur_mom.get("discussion_points", [])
    
    if not discussion_groups:
        st.info("No distinct discussion categories extracted.")
    else:
        for group in discussion_groups:
            with st.expander(f"🔹 {group.get('topic')}", expanded=True):
                for bullet in group.get("bullets", []):
                    st.markdown(f"- {bullet}")

    # SECTION 3: Action Items & Deliverables Matrix
    st.markdown("### 📌 3. Action Items & Deliverables Matrix")
    action_items = cur_mom.get("action_items", [])
    
    if not action_items:
        st.info("No explicit action items detected in transcript.")
    else:
        for item in action_items:
            priority_color = "#ef4444" if item.get("priority") == "High" else "#38bdf8"
            st.markdown(f"""
            <div class="action-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 13px; font-weight: 700; color: #f8fafc;">
                        👤 Assigned to: <b style="color: #38bdf8;">{item.get('owner')}</b>
                    </span>
                    <span style="font-size: 11px; background: rgba(56, 189, 248, 0.15); border: 1px solid {priority_color}; color: {priority_color}; padding: 2px 8px; border-radius: 4px; font-weight: bold;">
                        {item.get('priority').upper()} PRIORITY
                    </span>
                </div>
                <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 4px;">
                    {item.get('task')}
                </div>
                <div style="font-size: 11px; color: #94a3b8;">
                    📅 Target Completion: <b style="color: #34d399;">{item.get('deadline')}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # SECTION 4: Key Decisions Made
    st.markdown("### ✅ 4. Key Decisions & Agreements")
    decisions = cur_mom.get("decisions", [])
    if not decisions:
        st.info("No explicit decisions identified.")
    else:
        for d in decisions:
            st.markdown(f"""
            <div class="decision-card">
                <span style="font-size: 13px; color: #a7f3d0;">
                    <b>Agreement:</b> {d}
                </span>
            </div>
            """, unsafe_allow_html=True)

    # SECTION 5: Identified Risks & Blockers
    risks = cur_mom.get("risks_and_blockers", [])
    if risks:
        st.markdown("### ⚠️ 5. Identified Risks, Blockers & Questions")
        for r in risks:
            st.markdown(f"""
            <div class="risk-card">
                <span style="font-size: 13px; color: #fde68a;">
                    <b>Risk / Item:</b> {r}
                </span>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 4: Full Verbatim Transcript
# -------------------------------------------------------------
with tab_transcript:
    st.subheader("Verbatim Timestamped Meeting Transcript")
    
    transcript_info = st.session_state.meeting_data.get("transcript", {})
    segments = transcript_info.get("segments", [])
    
    search_kw = st.text_input("🔍 Search within transcript:", placeholder="Type a keyword e.g. 'indexing', 'budget', 'Sarah'...")

    if not segments:
        st.write(transcript_info.get("full_text", "No transcript available."))
    else:
        for seg in segments:
            text = seg.get("text", "")
            if search_kw and search_kw.lower() not in text.lower() and search_kw.lower() not in seg.get("speaker", "").lower():
                continue
                
            speaker = seg.get("speaker", "Speaker")
            role = seg.get("role", "")
            time_tag = seg.get("time", "")

            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                    <b style="color: #38bdf8;">🗣️ {speaker} <span style="color:#64748b; font-weight:normal;">({role})</span></b>
                    <code style="color: #94a3b8;">⏱️ {time_tag}</code>
                </div>
                <div style="font-size: 13px; color: #e2e8f0; line-height: 1.5;">
                    {text}
                </div>
            </div>
            """, unsafe_allow_html=True)
