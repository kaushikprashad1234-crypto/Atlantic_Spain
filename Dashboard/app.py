# Atlantic Spain Top 50 — Streamlit Dashboard

# ============================================================
# ATLANTIC SPAIN TOP 50
# Content Maturity, Release Lifecycle & Playlist Rotation
#
# Streamlit Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Atlantic Spain Top 50",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f8fafc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-title {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 5px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
    }

    .metric-subtitle {
        font-size: 12px;
        color: #94a3b8;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "outputs" / "song_lifecycle_analysis.csv"


@st.cache_data
def load_data():

    if not DATA_FILE.exists():

        st.error(
            f"Could not find {DATA_FILE.name}. "
            "Please ensure the CSV exists in the project's outputs folder."
        )

        st.stop()

    data = pd.read_csv(DATA_FILE)

    # Normalize column names
    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # ... keep the rest of your existing function exactly as it is

    # Normalize column names
    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Date conversion
    for column in [
        "entry_date",
        "exit_date",
        "peak_date"
    ]:

        if column in data.columns:

            data[column] = pd.to_datetime(
                data[column],
                errors="coerce"
            )

    # Numeric columns
    numeric_columns = [
        "lifecycle_days",
        "time_to_peak_days",
        "peak_position",
        "entry_position",
        "peak_popularity",
        "popularity",
        "duration_minutes",
        "duration_ms",
        "total_tracks",
        "retention_stability_index",
        "content_maturity_score"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    # Boolean normalization
    if "is_explicit" in data.columns:

        data["is_explicit"] = (
            data["is_explicit"]
            .astype(str)
            .str.lower()
            .map(
                {
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False
                }
            )
        )

    # Text normalization
    for column in [
        "song",
        "artist",
        "album_type",
        "lifecycle_stage"
    ]:

        if column in data.columns:

            data[column] = (
                data[column]
                .astype("string")
                .str.strip()
            )

    return data


df = load_data()


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "song",
    "artist",
    "entry_date",
    "exit_date",
    "lifecycle_days",
    "peak_position"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The lifecycle CSV is missing required columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("🎵 Atlantic Spain Top 50")

st.markdown(
    """
    ### Content Maturity, Release Lifecycle & Playlist Rotation

    Interactive analytics dashboard for understanding how songs
    enter, mature, peak, and exit the Spanish Top 50 playlist.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🎛️ Dashboard Filters")


# -----------------------------
# Date range
# -----------------------------

min_date = df["entry_date"].min()
max_date = df["entry_date"].max()

if pd.isna(min_date) or pd.isna(max_date):

    st.error("No valid entry dates were found.")
    st.stop()

date_range = st.sidebar.date_input(
    "Entry Date Range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date()
)

if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

else:

    start_date = min_date
    end_date = max_date


# -----------------------------
# Lifecycle stage
# -----------------------------

if "lifecycle_stage" in df.columns:

    stage_options = sorted(
        df["lifecycle_stage"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_stages = st.sidebar.multiselect(
        "Lifecycle Stage",
        options=stage_options,
        default=stage_options
    )

else:

    selected_stages = []


# -----------------------------
# Explicit filter
# -----------------------------

explicit_filter = st.sidebar.radio(
    "Content Type",
    [
        "All",
        "Explicit",
        "Non-Explicit"
    ],
    index=0
)


# -----------------------------
# Album type
# -----------------------------

if "album_type" in df.columns:

    album_options = sorted(
        df["album_type"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_album_types = st.sidebar.multiselect(
        "Album Type",
        options=album_options,
        default=album_options
    )

else:

    selected_album_types = []


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


filtered_df = filtered_df[
    (filtered_df["entry_date"] >= start_date) &
    (filtered_df["entry_date"] <= end_date)
]


if "lifecycle_stage" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["lifecycle_stage"]
        .isin(selected_stages)
    ]


if explicit_filter == "Explicit":

    filtered_df = filtered_df[
        filtered_df["is_explicit"] == True
    ]

elif explicit_filter == "Non-Explicit":

    filtered_df = filtered_df[
        filtered_df["is_explicit"] == False
    ]


if "album_type" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["album_type"]
        .isin(selected_album_types)
    ]


# ============================================================
# FILTER SUMMARY
# ============================================================

st.sidebar.divider()

st.sidebar.metric(
    "Filtered Songs",
    f"{len(filtered_df):,}"
)

st.sidebar.caption(
    f"Showing entries from "
    f"{start_date.strftime('%d %b %Y')} "
    f"to "
    f"{end_date.strftime('%d %b %Y')}"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

song_count = filtered_df["song"].nunique()

artist_count = filtered_df["artist"].nunique()

avg_lifecycle = filtered_df[
    "lifecycle_days"
].mean()

median_lifecycle = filtered_df[
    "lifecycle_days"
].median()

avg_peak = filtered_df[
    "peak_position"
].mean()

avg_time_peak = filtered_df[
    "time_to_peak_days"
].mean()

max_lifecycle = filtered_df[
    "lifecycle_days"
].max()


if "retention_stability_index" in filtered_df.columns:

    avg_stability = filtered_df[
        "retention_stability_index"
    ].mean()

else:

    avg_stability = np.nan


if "content_maturity_score" in filtered_df.columns:

    avg_maturity = filtered_df[
        "content_maturity_score"
    ].mean()

else:

    avg_maturity = np.nan


# ============================================================
# KPI CARDS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Executive KPIs</div>',
    unsafe_allow_html=True
)

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)


with kpi1:

    st.metric(
        "Songs",
        f"{song_count:,}"
    )


with kpi2:

    st.metric(
        "Artists",
        f"{artist_count:,}"
    )


with kpi3:

    st.metric(
        "Avg. Lifecycle",
        f"{avg_lifecycle:.1f} days"
        if not pd.isna(avg_lifecycle)
        else "N/A"
    )


with kpi4:

    st.metric(
        "Median Lifecycle",
        f"{median_lifecycle:.1f} days"
        if not pd.isna(median_lifecycle)
        else "N/A"
    )


with kpi5:

    st.metric(
        "Avg. Peak Position",
        f"{avg_peak:.1f}"
        if not pd.isna(avg_peak)
        else "N/A"
    )


with kpi6:

    st.metric(
        "Avg. Time to Peak",
        f"{avg_time_peak:.1f} days"
        if not pd.isna(avg_time_peak)
        else "N/A"
    )


# ============================================================
# SECOND KPI ROW
# ============================================================

st.markdown("")

kpi7, kpi8, kpi9, kpi10 = st.columns(4)


with kpi7:

    st.metric(
        "Longest Lifecycle",
        f"{max_lifecycle:.0f} days"
        if not pd.isna(max_lifecycle)
        else "N/A"
    )


with kpi8:

    st.metric(
        "Retention Stability",
        f"{avg_stability * 100:.1f}%"
        if not pd.isna(avg_stability)
        else "N/A"
    )


with kpi9:

    st.metric(
        "Content Maturity",
        f"{avg_maturity:.2f}"
        if not pd.isna(avg_maturity)
        else "N/A"
    )


with kpi10:

    if len(filtered_df) > 0:

        top10_share = (
            filtered_df["peak_position"] <= 10
        ).mean() * 100

    else:

        top10_share = np.nan

    st.metric(
        "Reached Top 10",
        f"{top10_share:.1f}%"
        if not pd.isna(top10_share)
        else "N/A"
    )


st.divider()


# ============================================================
# LIFECYCLE STAGE ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🔄 Lifecycle Stage Analysis</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# -----------------------------
# Stage distribution
# -----------------------------

with col1:

    if "lifecycle_stage" in filtered_df.columns:

        stage_counts = (
            filtered_df[
                "lifecycle_stage"
            ]
            .value_counts()
            .reset_index()
        )

        stage_counts.columns = [
            "Lifecycle Stage",
            "Songs"
        ]

        fig = px.bar(
            stage_counts,
            x="Lifecycle Stage",
            y="Songs",
            title="Songs by Lifecycle Stage",
            text="Songs"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            height=430,
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# -----------------------------
# Lifecycle duration distribution
# -----------------------------

with col2:

    fig = px.histogram(
        filtered_df,
        x="lifecycle_days",
        nbins=30,
        title="Distribution of Playlist Longevity",
        labels={
            "lifecycle_days":
            "Days on Top 50"
        }
    )

    fig.update_layout(
        height=430
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# LIFECYCLE STAGE SUMMARY
# ============================================================

if "lifecycle_stage" in filtered_df.columns:

    stage_summary = (
        filtered_df
        .groupby("lifecycle_stage")
        .agg(
            Songs=("song", "nunique"),
            Avg_Lifecycle=("lifecycle_days", "mean"),
            Avg_Peak_Position=("peak_position", "mean"),
            Avg_Time_to_Peak=("time_to_peak_days", "mean")
        )
        .reset_index()
    )

    stage_summary = stage_summary.round(2)

    st.dataframe(
        stage_summary,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SONG LIFECYCLE TIMELINE
# ============================================================

st.markdown(
    '<div class="section-title">📅 Song Lifecycle Timeline</div>',
    unsafe_allow_html=True
)

timeline_limit = st.slider(
    "Number of songs shown",
    min_value=5,
    max_value=50,
    value=20,
    step=5
)

timeline_df = (
    filtered_df
    .sort_values(
        "lifecycle_days",
        ascending=False
    )
    .head(timeline_limit)
    .copy()
)

timeline_df["Song Label"] = (
    timeline_df["song"]
    + " — "
    + timeline_df["artist"]
)

fig = px.timeline(
    timeline_df,
    x_start="entry_date",
    x_end="exit_date",
    y="Song Label",
    color="lifecycle_stage"
    if "lifecycle_stage" in timeline_df.columns
    else None,
    hover_data=[
        "lifecycle_days",
        "peak_position",
        "time_to_peak_days",
        "peak_popularity"
    ]
    if "peak_popularity" in timeline_df.columns
    else [
        "lifecycle_days",
        "peak_position",
        "time_to_peak_days"
    ],
    title="Top Song Lifecycle Timelines"
)

fig.update_yaxes(
    autorange="reversed"
)

fig.update_layout(
    height=max(
        500,
        timeline_limit * 28
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# POPULARITY VS LONGEVITY
# ============================================================

st.markdown(
    '<div class="section-title">📈 Popularity vs Lifecycle</div>',
    unsafe_allow_html=True
)

if "peak_popularity" in filtered_df.columns:

    fig = px.scatter(
        filtered_df,
        x="peak_popularity",
        y="lifecycle_days",
        size="peak_popularity",
        color="lifecycle_stage"
        if "lifecycle_stage" in filtered_df.columns
        else None,
        hover_name="song",
        hover_data=[
            "artist",
            "peak_position",
            "time_to_peak_days"
        ],
        title="Popularity vs Playlist Longevity",
        labels={
            "peak_popularity": "Peak Popularity",
            "lifecycle_days": "Lifecycle (Days)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# EXPLICIT VS NON-EXPLICIT
# ============================================================

st.markdown(
    '<div class="section-title">🔞 Content Maturity: Explicit vs Non-Explicit</div>',
    unsafe_allow_html=True
)

if "is_explicit" in filtered_df.columns:

    explicit_summary = (
        filtered_df
        .groupby("is_explicit")
        .agg(
            Songs=("song", "nunique"),
            Avg_Lifecycle=("lifecycle_days", "mean"),
            Median_Lifecycle=("lifecycle_days", "median"),
            Avg_Peak_Position=("peak_position", "mean"),
            Avg_Time_to_Peak=("time_to_peak_days", "mean")
        )
        .reset_index()
    )

    explicit_summary["Content"] = (
        explicit_summary["is_explicit"]
        .map({
            True: "Explicit",
            False: "Non-Explicit"
        })
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.box(
            filtered_df,
            x="is_explicit",
            y="lifecycle_days",
            color="is_explicit",
            title="Lifecycle by Explicit Content",
            labels={
                "is_explicit": "Explicit",
                "lifecycle_days": "Days on Playlist"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        display_df = explicit_summary[
            [
                "Content",
                "Songs",
                "Avg_Lifecycle",
                "Median_Lifecycle",
                "Avg_Peak_Position",
                "Avg_Time_to_Peak"
            ]
        ].round(2)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SINGLE VS ALBUM
# ============================================================

st.markdown(
    '<div class="section-title">💿 Single vs Album Tracks</div>',
    unsafe_allow_html=True
)

if "album_type" in filtered_df.columns:

    album_summary = (
        filtered_df
        .groupby("album_type")
        .agg(
            Songs=("song", "nunique"),
            Avg_Lifecycle=("lifecycle_days", "mean"),
            Median_Lifecycle=("lifecycle_days", "median"),
            Avg_Peak_Position=("peak_position", "mean"),
            Avg_Time_to_Peak=("time_to_peak_days", "mean")
        )
        .reset_index()
        .round(2)
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.box(
            filtered_df,
            x="album_type",
            y="lifecycle_days",
            color="album_type",
            title="Lifecycle by Album Type",
            labels={
                "album_type": "Album Type",
                "lifecycle_days": "Days on Playlist"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.dataframe(
            album_summary,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# MONTHLY CHURN ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">🔁 Playlist Churn & Rotation</div>',
    unsafe_allow_html=True
)

# Reconstruct daily entries/exits from lifecycle data
# based on entry and exit dates.

all_dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)

daily_rotation = []

for current_date in all_dates:

    entries = (
        filtered_df["entry_date"]
        .dt.normalize()
        .eq(current_date)
        .sum()
    )

    exits = (
        filtered_df["exit_date"]
        .dt.normalize()
        .eq(current_date)
        .sum()
    )

    daily_rotation.append(
        {
            "date": current_date,
            "entries": entries,
            "exits": exits,
            "churn": entries + exits
        }
    )


daily_rotation = pd.DataFrame(
    daily_rotation
)

daily_rotation["churn_rate"] = (
    daily_rotation["churn"] / 50 * 100
)

daily_rotation["month"] = (
    daily_rotation["date"]
    .dt.to_period("M")
    .astype(str)
)


col1, col2 = st.columns(2)


# -----------------------------
# Daily entries/exits
# -----------------------------

with col1:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=daily_rotation["date"],
            y=daily_rotation["entries"],
            mode="lines",
            name="Entries"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=daily_rotation["date"],
            y=daily_rotation["exits"],
            mode="lines",
            name="Exits"
        )
    )

    fig.update_layout(
        title="Daily Playlist Entries vs Exits",
        xaxis_title="Date",
        yaxis_title="Songs",
        height=430
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# Monthly churn
# -----------------------------

with col2:

    monthly_churn = (
        daily_rotation
        .groupby("month")
        .agg(
            Average_Entries=("entries", "mean"),
            Average_Exits=("exits", "mean"),
            Average_Churn_Rate=("churn_rate", "mean")
        )
        .reset_index()
    )

    fig = px.line(
        monthly_churn,
        x="month",
        y="Average_Churn_Rate",
        markers=True,
        title="Monthly Playlist Churn Rate",
        labels={
            "month": "Month",
            "Average_Churn_Rate":
                "Average Daily Churn (%)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CHURN TABLE
# ============================================================

st.markdown("### Monthly Rotation Summary")

st.dataframe(
    monthly_churn.round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SONG-LEVEL DRILL DOWN
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Song-Level Drill-Down</div>',
    unsafe_allow_html=True
)

song_options = (
    filtered_df[
        ["song", "artist"]
    ]
    .drop_duplicates()
    .sort_values(["song", "artist"])
)

song_labels = (
    song_options["song"]
    + " — "
    + song_options["artist"]
)

selected_song_label = st.selectbox(
    "Select a song",
    song_labels.tolist()
)


selected_song_name = (
    selected_song_label
    .split(" — ")[0]
)

selected_artist_name = (
    selected_song_label
    .split(" — ", 1)[1]
)


song_record = filtered_df[
    (filtered_df["song"] == selected_song_name) &
    (filtered_df["artist"] == selected_artist_name)
].copy()


if not song_record.empty:

    song = song_record.iloc[0]

    # --------------------------------
    # Song summary
    # --------------------------------

    st.markdown(
        f"### 🎵 {selected_song_name}"
    )

    st.caption(
        f"Artist: {selected_artist_name}"
    )

    info1, info2, info3, info4, info5 = st.columns(5)

    with info1:

        st.metric(
            "Lifecycle",
            f"{song['lifecycle_days']:.0f} days"
        )

    with info2:

        st.metric(
            "Peak Position",
            f"{song['peak_position']:.0f}"
        )

    with info3:

        st.metric(
            "Time to Peak",
            f"{song['time_to_peak_days']:.0f} days"
        )

    with info4:

        if "peak_popularity" in song_record.columns:

            st.metric(
                "Peak Popularity",
                f"{song['peak_popularity']:.0f}"
            )

    with info5:

        if "retention_stability_index" in song_record.columns:

            st.metric(
                "Stability",
                f"{song['retention_stability_index'] * 100:.1f}%"
            )


    # --------------------------------
    # Metadata
    # --------------------------------

    metadata = {
        "Song": song["song"],
        "Artist": song["artist"],
        "Entry Date": song["entry_date"],
        "Exit Date": song["exit_date"],
        "Peak Date": song.get("peak_date", "N/A"),
        "Peak Position": song["peak_position"],
        "Lifecycle Days": song["lifecycle_days"],
        "Time to Peak": song["time_to_peak_days"],
        "Album Type": song.get("album_type", "N/A"),
        "Explicit": song.get("is_explicit", "N/A"),
        "Duration": (
            f"{song['duration_minutes']:.2f} min"
            if "duration_minutes" in song_record.columns
            and not pd.isna(song["duration_minutes"])
            else "N/A"
        )
    }

    metadata_df = pd.DataFrame(
        metadata.items(),
        columns=["Attribute", "Value"]
    )

    st.dataframe(
        metadata_df,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------
    # Rank trajectory
    # --------------------------------

    st.markdown("### 📉 Playlist Rank Trajectory")

    # The lifecycle dataset contains summary data,
    # so if rank history is unavailable we show
    # the entry-to-peak movement.

    rank_data = pd.DataFrame(
        {
            "Stage": [
                "Entry",
                "Peak"
            ],
            "Position": [
                song["entry_position"],
                song["peak_position"]
            ]
        }
    )

    fig = px.line(
        rank_data,
        x="Stage",
        y="Position",
        markers=True,
        title="Entry-to-Peak Rank Movement"
    )

    fig.update_yaxes(
        autorange="reversed"
    )

    fig.update_layout(
        height=400,
        yaxis_title="Playlist Position"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------
    # Lifecycle timeline
    # --------------------------------

    st.markdown("### ⏳ Lifecycle Timeline")

    timeline_events = pd.DataFrame(
        {
            "Event": [
                "Entry",
                "Peak",
                "Exit"
            ],
            "Date": [
                song["entry_date"],
                song.get("peak_date", song["entry_date"]),
                song["exit_date"]
            ]
        }
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=timeline_events["Date"],
            y=[1, 1, 1],
            mode="lines+markers+text",
            text=timeline_events["Event"],
            textposition="top center",
            marker=dict(size=12),
            line=dict(width=4)
        )
    )

    fig.update_yaxes(
        visible=False
    )

    fig.update_layout(
        title="Song Lifecycle",
        height=250,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TOP LONGEST-LIVED SONGS
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Longest-Lived Songs</div>',
    unsafe_allow_html=True
)

top_songs = (
    filtered_df
    .sort_values(
        "lifecycle_days",
        ascending=False
    )
    .head(20)
)

display_columns = [
    "song",
    "artist",
    "lifecycle_days",
    "peak_position",
    "time_to_peak_days"
]

if "peak_popularity" in top_songs.columns:
    display_columns.append(
        "peak_popularity"
    )

if "lifecycle_stage" in top_songs.columns:
    display_columns.append(
        "lifecycle_stage"
    )

st.dataframe(
    top_songs[display_columns]
    .round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

st.markdown(
    '<div class="section-title">⬇️ Export</div>',
    unsafe_allow_html=True
)

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Lifecycle Data",
    data=csv_data,
    file_name="atlantic_spain_filtered_lifecycle.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Atlantic Spain Top 50 | Content Maturity, Release Lifecycle "
    "& Playlist Rotation Analysis"
)

st.caption(
    "Note: playlist entry date represents the first observed "
    "appearance in the dataset and should not be interpreted as "
    "the original commercial release date."
)
