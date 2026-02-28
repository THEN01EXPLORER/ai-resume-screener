import streamlit as st
import requests
import pandas as pd
import threading
import uvicorn
import time

# ─── AUTO-START FASTAPI BACKEND ─────────────────────────────────────────────
@st.cache_resource
def start_fastapi_server():
    """Starts the FastAPI backend in a background thread (runs only once)."""
    thread = threading.Thread(
        target=lambda: uvicorn.run("main:app", host="0.0.0.0", port=8000),
        daemon=True
    )
    thread.start()
    time.sleep(2)  # Give the server a moment to boot
    return True

start_fastapi_server()

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Matchmaker",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App Background ── */
.stApp {
    background: #0f1117;
    color: #e0e0e0;
}

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a1f36 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0 0 8px 0;
    background: linear-gradient(90deg, #818cf8, #c4b5fd, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 1rem;
    color: #94a3b8;
    margin: 0;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    border: 1px solid rgba(99,102,241,0.4);
    color: #818cf8;
    padding: 4px 14px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* ── Section Header ── */
.section-header {
    font-size: 1rem;
    font-weight: 600;
    color: #c4b5fd;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom: 1px solid rgba(99,102,241,0.25);
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

/* ── Candidate Card ── */
.candidate-card {
    background: linear-gradient(135deg, #1e2235 0%, #1a1f36 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    transition: border-color 0.2s;
}
.candidate-card:hover {
    border-color: rgba(99,102,241,0.5);
}
.card-rank {
    position: absolute;
    top: 20px;
    right: 24px;
    font-size: 0.7rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.card-name {
    font-size: 1.15rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 0 0 4px 0;
}
.card-meta {
    font-size: 0.8rem;
    color: #64748b;
    margin: 0 0 20px 0;
}
.score-main {
    font-size: 2.4rem;
    font-weight: 700;
    line-height: 1;
    margin: 0 0 4px 0;
}
.score-label {
    font-size: 0.7rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0;
}

/* ── Progress Bar Container ── */
.metric-row {
    margin: 6px 0;
}
.metric-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    color: #94a3b8;
    margin-bottom: 4px;
}
.progress-bg {
    background: rgba(255,255,255,0.05);
    border-radius: 99px;
    height: 6px;
    overflow: hidden;
}
.progress-fill-semantic {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
}
.progress-fill-skills {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #34d399, #10b981);
}
.progress-fill-exp {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

/* ── Badge ── */
.badge-pass {
    display: inline-block;
    background: rgba(52,211,153,0.15);
    border: 1px solid rgba(52,211,153,0.35);
    color: #34d399;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-fail {
    display: inline-block;
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.3);
    color: #f87171;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
}

/* ── Stats Row ── */
.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 28px;
}
.stat-card {
    flex: 1;
    background: linear-gradient(135deg, #1e2235, #1a1f36);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}
.stat-number {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
}
.stat-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0;
}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {
    background: #0d1019 !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
}
[data-testid="stSidebar"] * {
    color: #94a3b8 !important;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #c4b5fd !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: #1e2235 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(99,102,241,0.7) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Primary Button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #818cf8) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.88 !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(99,102,241,0.12) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    border-radius: 10px !important;
    color: #818cf8 !important;
    font-weight: 600 !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #818cf8 !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #334155;
    font-size: 0.75rem;
    margin-top: 56px;
    padding-top: 16px;
    border-top: 1px solid rgba(99,102,241,0.1);
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid rgba(99,102,241,0.12);
    margin: 24px 0;
}
</style>
""", unsafe_allow_html=True)


# ─── HERO BANNER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">🚀 AI Resume Matchmaker</h1>
    <p class="hero-subtitle">Upload candidate resumes, define the role, and let AI surface the best matches — instantly.</p>
</div>
""", unsafe_allow_html=True)


# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Resume Ingestion")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Drop PDF resumes here",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload multiple resumes at once."
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)}** file(s) ready to upload")

    st.markdown("")
    ingest_btn = st.button("⚡ Ingest Resumes", type="primary", width='stretch')

    if ingest_btn:
        if uploaded_files:
            progress = st.progress(0, text="Starting ingestion...")
            status_box = st.empty()
            status_lines = []
            total = len(uploaded_files)
            success_count = 0
            for i, file in enumerate(uploaded_files):
                # Phase 1: immediately update progress BEFORE the blocking network call
                progress.progress(i / total, text=f"📄 Parsing {file.name}…")
                # Show a live "thinking" placeholder in the status card
                thinking_html = (
                    f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(99,102,241,0.15);border-radius:10px;padding:10px 14px;margin-top:8px;">'
                    + "".join(status_lines)
                    + f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
                    f'<span style="width:8px;height:8px;border-radius:50%;background:#818cf8;flex-shrink:0;opacity:0.6;"></span>'
                    f'<span style="font-size:0.8rem;color:#64748b;font-style:italic;">🤖 AI extracting data from {file.name}…</span>'
                    f'</div></div>'
                )
                status_box.markdown(thinking_html, unsafe_allow_html=True)

                files_payload = {"file": (file.name, file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(
                        "http://127.0.0.1:8000/upload/",
                        files=files_payload,
                        timeout=120  # allow up to 2 min per file (Gemini can be slow)
                    )
                    # Phase 2: update progress after response
                    progress.progress((i + 1) / total, text=f"✅ Done: {file.name}" if response.status_code == 200 else f"❌ Failed: {file.name}")
                    if response.status_code == 200:
                        status_lines.append(
                            f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                            f'<span style="width:8px;height:8px;border-radius:50%;background:#34d399;flex-shrink:0;"></span>'
                            f'<span style="font-size:0.8rem;color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{file.name}</span>'
                            f'</div>'
                        )
                        success_count += 1
                    else:
                        try:
                            err_detail = response.json().get("detail", "Upload failed")
                        except Exception:
                            err_detail = "Upload failed"
                        status_lines.append(
                            f'<div style="display:flex;flex-direction:column;gap:2px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                            f'<div style="display:flex;align-items:center;gap:8px;">'
                            f'<span style="width:8px;height:8px;border-radius:50%;background:#f87171;flex-shrink:0;"></span>'
                            f'<span style="font-size:0.8rem;color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{file.name}</span>'
                            f'</div>'
                            f'<span style="font-size:0.72rem;color:#f87171;padding-left:16px;">{err_detail}</span>'
                            f'</div>'
                        )
                except requests.exceptions.Timeout:
                    status_lines.append(
                        f'<div style="display:flex;flex-direction:column;gap:2px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                        f'<div style="display:flex;align-items:center;gap:8px;">'
                        f'<span style="width:8px;height:8px;border-radius:50%;background:#f87171;flex-shrink:0;"></span>'
                        f'<span style="font-size:0.8rem;color:#94a3b8;">{file.name}</span>'
                        f'</div>'
                        f'<span style="font-size:0.72rem;color:#f87171;padding-left:16px;">Request timed out — AI took too long</span>'
                        f'</div>'
                    )
                except Exception:
                    status_lines.append(
                        f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                        f'<span style="width:8px;height:8px;border-radius:50%;background:#f87171;flex-shrink:0;"></span>'
                        f'<span style="font-size:0.8rem;color:#f87171;">Server unreachable</span>'
                        f'</div>'
                    )
                status_box.markdown(
                    f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(99,102,241,0.15);border-radius:10px;padding:10px 14px;margin-top:8px;">{"".join(status_lines)}</div>',
                    unsafe_allow_html=True
                )
            progress.progress(1.0, text="Done!")
            st.markdown(f'<span style="font-size:0.82rem;color:#34d399;">✓ {success_count}/{total} resumes ingested</span>', unsafe_allow_html=True)
        else:
            st.warning("Please upload at least one PDF first.")

    st.markdown("---")
    st.markdown("### ℹ️ How it works")
    st.markdown("""
1. **Upload** candidate PDFs
2. **Define** the job role below
3. **Click Rank** — AI scores & ranks all candidates
""")
    st.markdown("---")
    st.caption("AI Resume Matchmaker · Built with FastAPI + ChromaDB + Gemini")


# ─── MAIN: JOB DESCRIPTION ──────────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 Define the Role</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")
with col1:
    job_title = st.text_input("Job Title", "Backend AI Engineer", placeholder="e.g. Senior ML Engineer")
    skills = st.text_input(
        "Required Skills",
        "Python, FastAPI, Docker",
        placeholder="Comma-separated: Python, React, AWS",
        help="Separate each skill with a comma."
    )
with col2:
    exp = st.number_input("Minimum Experience (Years)", value=3.0, step=0.5, min_value=0.0)
    desc = st.text_area(
        "Job Description",
        "Looking for a backend engineer to build scalable AI infrastructure using Python and FastAPI.",
        height=120,
        placeholder="Paste the full job description here…"
    )

st.markdown("")
rank_btn = st.button("🔍 Rank Candidates", type="primary", width='content')


# ─── RESULTS ────────────────────────────────────────────────────────────────
if rank_btn:
    with st.spinner("AI is calculating matches…"):
        payload = {
            "title": job_title,
            "required_skills": [s.strip() for s in skills.split(",")],
            "minimum_experience_years": exp,
            "text_description": desc
        }
        try:
            response = requests.post("http://127.0.0.1:8000/match/", json=payload)
        except Exception:
            st.error("❌ Could not reach the AI Engine. Make sure the backend is running on port 8000.")
            st.stop()

    if response.status_code == 200:
        data = response.json()
        rankings = data.get("rankings", [])
        total = data.get("total_candidates_scored", 0)

        if not rankings:
            st.info("No candidates found in the database. Please ingest some resumes first.")
        else:
            # ── Summary Stats ──
            top_score = rankings[0]["scoring_report"]["final_percentage"] if rankings else 0
            avg_score = round(sum(r["scoring_report"]["final_percentage"] for r in rankings) / len(rankings), 1)
            exp_passed = sum(1 for r in rankings if r["scoring_report"]["experience_passed"])

            st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)
            st.markdown(f"""
<div class="stats-row">
    <div class="stat-card">
        <p class="stat-number" style="color:#818cf8;">{total}</p>
        <p class="stat-label">Candidates Scored</p>
    </div>
    <div class="stat-card">
        <p class="stat-number" style="color:#34d399;">{top_score}%</p>
        <p class="stat-label">Top Match Score</p>
    </div>
    <div class="stat-card">
        <p class="stat-number" style="color:#38bdf8;">{avg_score}%</p>
        <p class="stat-label">Average Score</p>
    </div>
    <div class="stat-card">
        <p class="stat-number" style="color:#fbbf24;">{exp_passed}</p>
        <p class="stat-label">Meet Experience Bar</p>
    </div>
</div>
""", unsafe_allow_html=True)

            # ── Candidate Cards ──
            for i, item in enumerate(rankings):
                report = item["scoring_report"]
                final   = report["final_percentage"]
                semantic = report["semantic_score"]
                skill_sc = report["skill_match_score"]
                exp_ok   = report["experience_passed"]
                candidate = item["candidate_id"]

                # Score color
                if final >= 75:
                    score_color = "#34d399"
                elif final >= 50:
                    score_color = "#fbbf24"
                else:
                    score_color = "#f87171"

                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                exp_badge = '<span class="badge-pass">✓ Meets Experience</span>' if exp_ok else '<span class="badge-fail">✗ Under-experienced</span>'

                st.markdown(f"""
<div class="candidate-card">
    <span class="card-rank">{medal} Rank {i+1}</span>
    <p class="card-name">📄 {candidate}</p>
    <p class="card-meta">Candidate Resume · {exp_badge}</p>
    <div style="display:flex; align-items:flex-end; gap:32px; margin-bottom:18px;">
        <div>
            <p class="score-main" style="color:{score_color};">{final}%</p>
            <p class="score-label">Overall Match</p>
        </div>
    </div>
    <div class="metric-row">
        <div class="metric-label"><span>🔷 Semantic Match</span><span>{semantic}%</span></div>
        <div class="progress-bg"><div class="progress-fill-semantic" style="width:{semantic}%;"></div></div>
    </div>
    <div class="metric-row" style="margin-top:10px;">
        <div class="metric-label"><span>🟢 Skills Match</span><span>{skill_sc}%</span></div>
        <div class="progress-bg"><div class="progress-fill-skills" style="width:{skill_sc}%;"></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

            # ── Export Table ──
            st.markdown('<div class="section-header">📋 Full Table View</div>', unsafe_allow_html=True)
            df_data = []
            for item in rankings:
                r = item["scoring_report"]
                df_data.append({
                    "Candidate": item["candidate_id"],
                    "Overall Match (%)": r["final_percentage"],
                    "Skills Match (%)": r["skill_match_score"],
                    "Semantic Score (%)": r["semantic_score"],
                    "Experience Met": "✅ Yes" if r["experience_passed"] else "❌ No",
                })
            df = pd.DataFrame(df_data)
            table_height = (len(df) + 1) * 38 + 10  # 38px per row + header, no inner scroll
            st.dataframe(df, width='stretch', hide_index=True, height=table_height)

            # ── CSV Download ──
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Results as CSV",
                data=csv,
                file_name=f"rankings_{job_title.replace(' ', '_')}.csv",
                mime="text/csv",
            )
    else:
        st.error(f"❌ Backend returned an error (status {response.status_code}). Check the FastAPI logs.")

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">AI Resume Matchmaker · FastAPI + ChromaDB + Gemini 2.5 Flash · Made with ❤️</div>', unsafe_allow_html=True)