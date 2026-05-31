import os
import subprocess

from database.db import get_alerts
import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.report_generator import generate_pdf_report
import plotly.graph_objects as go
from database.db import (
    get_events,
    get_sessions,
    create_session,
    get_tracking_points,
    get_dwell_times,
    get_session_summary
)

st.set_page_config(
    page_title="VisionOps AI",
    page_icon="🧠",
    layout="wide"
)


# ---------------- UI CSS ----------------
st.markdown("""
<style>
.stApp {
    background:
    radial-gradient(circle at top left, #4b0082 0%, transparent 35%),
    radial-gradient(circle at top right, #00e5ff33 0%, transparent 28%),
    linear-gradient(135deg, #050510, #0b0618 55%, #020204);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.hero {
    padding: 38px;
    border-radius: 30px;
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    box-shadow: 0 0 55px rgba(170, 70, 255, 0.45);
    animation: float 4s ease-in-out infinite;
    border: 1px solid rgba(255,255,255,0.14);
}

.card {
    padding: 24px;
    border-radius: 24px;
    background: rgba(255,255,255,0.09);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.13);
    box-shadow: 0 0 32px rgba(120, 80, 255, 0.28);
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-7px) scale(1.015);
    box-shadow: 0 0 45px rgba(0, 229, 255, 0.35);
}

.metric-title {
    color: #cfc7ff;
    font-size: 15px;
}

.metric-value {
    font-size: 40px;
    font-weight: 900;
}

.glow {
    color: #00e5ff;
    text-shadow: 0 0 18px #00e5ff;
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}
</style>
""", unsafe_allow_html=True)


# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <h1>🧠 VisionOps AI Command Center</h1>
    <h3>Real-time CCTV Intelligence · Visitor Tracking · Event Analytics · Retail AI</h3>
    <p class="glow">AI-powered store intelligence from raw CCTV footage</p>
</div>
""", unsafe_allow_html=True)

st.write("")


# ---------------- UPLOAD VIDEO ----------------
st.subheader("📤 Upload CCTV / Store Video")

uploaded_video = st.file_uploader(
    "Upload video for AI analysis",
    type=["mp4", "avi", "mov", "mpeg4"]
)

if uploaded_video is not None:
    os.makedirs("sample_data", exist_ok=True)

    video_path = os.path.join("sample_data", uploaded_video.name)

    with open(video_path, "wb") as f:
        f.write(uploaded_video.read())

    st.success("Video uploaded successfully ✅")
    st.video(video_path)

    if st.button("🚀 Analyze Uploaded Video"):
        session_id = create_session(uploaded_video.name)

        with st.spinner("Processing video with YOLO + ByteTrack..."):
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "cv_pipeline.video_processor",
                    video_path,
                    str(session_id)
                ],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:
            st.success("Analysis completed ✅ Dashboard updated.")
        else:
            st.error("Processing failed ❌")

        with st.expander("🔍 View Processing Logs"):
            st.code(result.stdout)
            if result.stderr:
                st.code(result.stderr)


# ---------------- SESSION FILTER ----------------
st.subheader("🎥 Video Session Analytics")

sessions = get_sessions()

if sessions:
    session_options = {
        f"{s['id']} - {s['video_name']}": s["id"]
        for s in sessions
    }

    selected_session_label = st.selectbox(
        "Select video session",
        list(session_options.keys())
    )

    selected_session_id = session_options[selected_session_label]
    events = get_events(selected_session_id)
else:
    selected_session_id = None
    events = []
    st.warning("No video sessions found yet. Upload and analyze a video first.")


events_df = pd.DataFrame(events)


# ---------------- METRICS ----------------
if events_df.empty:
    total_events = 0
    high_alerts = 0
    medium_alerts = 0
    latest_event = "No events yet"
    latest_zone = "N/A"
else:
    total_events = len(events_df)
    high_alerts = len(events_df[events_df["severity"] == "high"])
    medium_alerts = len(events_df[events_df["severity"] == "medium"])
    latest_event = events_df.iloc[0]["event_type"]
    latest_zone = events_df.iloc[0]["zone"]


st.subheader("⚡ Live Intelligence Overview")

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("Total Events", total_events, "📊"),
    ("High Alerts", high_alerts, "🚨"),
    ("Medium Alerts", medium_alerts, "⚠️"),
    ("Latest Zone", latest_zone, "📍"),
]

for col, item in zip([c1, c2, c3, c4], cards):
    title, value, icon = item
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="metric-title">{icon} {title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------- ALERT CENTER ----------------
st.subheader("🚨 Smart Alert Center")

alerts = get_alerts()
alerts_df = pd.DataFrame(alerts)

if alerts_df.empty:
    st.success("No alerts generated yet.")
else:
    st.dataframe(alerts_df, use_container_width=True)

    fig = px.bar(
        alerts_df,
        x="severity",
        title="Alert Severity Distribution",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------- CHARTS ----------------
st.write("")
st.subheader("📈 Futuristic Analytics")

if events_df.empty:
    st.info("No events found for this selected session yet.")
else:
    events_df["timestamp"] = pd.to_datetime(events_df["timestamp"])
    events_df["minute"] = events_df["timestamp"].dt.strftime("%H:%M")

    col1, col2 = st.columns(2)

    with col1:
        event_count = events_df["event_type"].value_counts().reset_index()
        event_count.columns = ["event_type", "count"]

        fig = px.bar(
            event_count,
            x="event_type",
            y="count",
            title="Event Distribution",
            template="plotly_dark",
            text="count"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        zone_count = events_df["zone"].value_counts().reset_index()
        zone_count.columns = ["zone", "count"]

        fig = px.pie(
            zone_count,
            names="zone",
            values="count",
            title="Zone-wise Activity",
            template="plotly_dark",
            hole=0.55
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        timeline = events_df.groupby("minute").size().reset_index(name="events")

        fig = px.line(
            timeline,
            x="minute",
            y="events",
            markers=True,
            title="Event Timeline",
            template="plotly_dark"
        )
        fig.update_traces(line=dict(width=4))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        severity_count = events_df["severity"].value_counts().reset_index()
        severity_count.columns = ["severity", "count"]

        fig = px.funnel(
            severity_count,
            x="count",
            y="severity",
            title="Alert Severity Funnel",
            template="plotly_dark"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)


st.subheader(" Real Visitor Movement Heatmap")

tracking_points = get_tracking_points(selected_session_id)
tracking_df = pd.DataFrame(tracking_points)

if tracking_df.empty:
    st.info("No tracking points found for this session.")
else:

    # Density Heatmap
    fig = px.density_heatmap(
        tracking_df,
        x="x",
        y="y",
        nbinsx=50,
        nbinsy=30,
        title="Visitor Density Heatmap",
        template="plotly_dark",
        color_continuous_scale="Turbo"
    )

    fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader(" Visitor Movement Paths")

    fig2 = px.scatter(
        tracking_df,
        x="x",
        y="y",
        color="track_id",
        title="Tracked Visitor Paths",
        template="plotly_dark",
        opacity=0.7
    )

    fig2.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig2.update_yaxes(autorange="reversed")

    st.plotly_chart(fig2, use_container_width=True)


    st.subheader(" Live Event Feed")
    st.dataframe(events_df, use_container_width=True)



st.subheader(" Dwell Time Analytics")

dwell_data = get_dwell_times(selected_session_id)
dwell_df = pd.DataFrame(dwell_data)

if dwell_df.empty:
    st.info("No dwell time data found yet.")
else:
    avg_dwell = round(dwell_df["dwell_seconds"].mean(), 2)
    max_dwell = round(dwell_df["dwell_seconds"].max(), 2)
    top_visitor = dwell_df.iloc[0]["track_id"]

    d1, d2, d3 = st.columns(3)

    d1.markdown(f"""
    <div class="card">
        <div class="metric-title">Average Dwell Time</div>
        <div class="metric-value">{avg_dwell}s</div>
    </div>
    """, unsafe_allow_html=True)

    d2.markdown(f"""
    <div class="card">
        <div class="metric-title">Max Dwell Time</div>
        <div class="metric-value">{max_dwell}s</div>
    </div>
    """, unsafe_allow_html=True)

    d3.markdown(f"""
    <div class="card">
        <div class="metric-title">Top Visitor ID</div>
        <div class="metric-value">#{top_visitor}</div>
    </div>
    """, unsafe_allow_html=True)

    fig = px.bar(
        dwell_df,
        x="track_id",
        y="dwell_seconds",
        title="Visitor-wise Dwell Time",
        template="plotly_dark",
        text="dwell_seconds"
    )

    fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(dwell_df, use_container_width=True)


st.subheader(" AI Recommendation Engine")

st.markdown(f"""
<div class="card">
    <h3>Store Insight</h3>
    <p>
    Latest detected activity: <b>{latest_event}</b>.  
    The system recommends monitoring <b>{latest_zone}</b> closely.
    If footfall continues increasing, allocate staff near checkout or high-traffic zones.
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader(" AI Recommendation Engine")

recommendations = []

if not events_df.empty:
    total_events = len(events_df)
    latest_event = events_df.iloc[0]["event_type"]
    medium_alerts = len(events_df[events_df["severity"] == "medium"])
    high_alerts = len(events_df[events_df["severity"] == "high"])

    if total_events >= 2:
        recommendations.append("Footfall is repeatedly increasing. Keep monitoring this zone closely.")

    if medium_alerts > 0:
        recommendations.append("Medium-level crowd activity detected. Add temporary staff near active zones.")

    if high_alerts > 0:
        recommendations.append("High-risk crowd alert detected. Immediate action recommended.")

    if latest_event == "footfall_spike":
        recommendations.append("Footfall spike detected. Check checkout, entrance, or high-traffic areas.")

if "dwell_df" in locals() and not dwell_df.empty:
    avg_dwell = dwell_df["dwell_seconds"].mean()
    max_dwell = dwell_df["dwell_seconds"].max()

    if avg_dwell > 5:
        recommendations.append("Average dwell time is high. Visitors may be waiting or moving slowly.")

    if max_dwell > 15:
        recommendations.append("One visitor stayed unusually long. Possible loitering or slow service zone.")

if not recommendations:
    recommendations.append("Store activity looks stable. Continue normal monitoring.")

recommendation_html = "".join([f"<li>{r}</li>" for r in recommendations])

st.markdown(f"""
<div class="card" id="store-insight">
    <h3>Store Insight</h3>
    <p>Based on visitor movement, events, and dwell-time analytics:</p>
    <ul>
        {recommendation_html}
    </ul>
</div>
""", unsafe_allow_html=True)


st.subheader(" Session Comparison Dashboard")

summary_data = get_session_summary()
summary_df = pd.DataFrame(summary_data)

if summary_df.empty:
    st.info("No session comparison data available yet.")
else:
    best_session = summary_df.sort_values(
        by="unique_visitors",
        ascending=False
    ).iloc[0]

    s1, s2, s3 = st.columns(3)

    s1.markdown(f"""
    <div class="card">
        <div class="metric-title">Most Active Video</div>
        <div class="metric-value">{best_session["video_name"]}</div>
    </div>
    """, unsafe_allow_html=True)

    s2.markdown(f"""
    <div class="card">
        <div class="metric-title">Peak Visitors</div>
        <div class="metric-value">{best_session["unique_visitors"]}</div>
    </div>
    """, unsafe_allow_html=True)

    s3.markdown(f"""
    <div class="card">
        <div class="metric-title">Sessions Compared</div>
        <div class="metric-value">{len(summary_df)}</div>
    </div>
    """, unsafe_allow_html=True)

    fig = px.bar(
        summary_df,
        x="video_name",
        y="unique_visitors",
        title="Unique Visitors by Video",
        template="plotly_dark",
        text="unique_visitors"
    )
    fig.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(
        summary_df,
        x="unique_visitors",
        y="avg_dwell_seconds",
        size="total_events",
        color="video_name",
        title="Visitor Engagement Matrix",
        template="plotly_dark",
        hover_data=["video_name", "total_events", "max_dwell_seconds"]
    )
    fig2.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(summary_df, use_container_width=True)


st.subheader(" Download Analytics Report")

if st.button("Generate PDF Report"):

    pdf_path = generate_pdf_report(
        session_name="road_traffic",
        total_events=len(events_df) if not events_df.empty else 0,
        unique_visitors=unique_visitors if "unique_visitors" in locals() else 0,
        avg_dwell=round(dwell_df["dwell_seconds"].mean(), 2) if not dwell_df.empty else 0,
        max_dwell=round(dwell_df["dwell_seconds"].max(), 2) if not dwell_df.empty else 0
    )

    with open(pdf_path, "rb") as file:
        st.download_button(
            label="⬇️ Download PDF Report",
            data=file,
            file_name="visionops_report.pdf",
            mime="application/pdf"
        )