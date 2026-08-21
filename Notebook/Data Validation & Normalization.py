# ============================================================
# ATLANTIC SPAIN TOP 50
# Content Maturity, Release Lifecycle & Playlist Rotation
# ============================================================

# -----------------------------
# 1. IMPORT LIBRARIES
# -----------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


# -----------------------------
# 2. LOAD DATA
# -----------------------------
FILE_PATH = "E:\\power bi\\Atlantic_Spain\\Data\\Atlantic_Spain.csv"

df = pd.read_csv(FILE_PATH)

print("=" * 70)
print("DATASET LOADED")
print("=" * 70)
print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]}")
print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 3. DATA VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("DATA VALIDATION")
print("=" * 70)

# Basic information
print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

missing_df = pd.DataFrame({
    "Missing_Count": missing,
    "Missing_Percentage": missing_pct
})

print(missing_df)


# Duplicate rows
duplicate_count = df.duplicated().sum()

print(f"\nDuplicate rows: {duplicate_count:,}")


# -----------------------------
# Date conversion
# -----------------------------
df["date"] = pd.to_datetime(
    df["date"],
    format="%d-%m-%Y",
    errors="coerce"
)

print("\nDate range:")
print("Start:", df["date"].min())
print("End  :", df["date"].max())

print("\nInvalid dates:")
print(df["date"].isna().sum())


# -----------------------------
# Check daily record count
# -----------------------------
daily_counts = (
    df.groupby("date")
      .size()
      .reset_index(name="records")
)

print("\nDaily record statistics:")
print(daily_counts["records"].describe())

invalid_days = daily_counts[daily_counts["records"] != 50]

print(f"\nDays with != 50 records: {len(invalid_days)}")

if len(invalid_days) > 0:
    print(invalid_days.head(20))


# -----------------------------
# Check position range
# -----------------------------
print("\nPosition range:")
print(df["position"].min(), "to", df["position"].max())

invalid_positions = df[
    ~df["position"].between(1, 50)
]

print("Invalid positions:", len(invalid_positions))


# -----------------------------
# Check duplicate positions per day
# -----------------------------
duplicate_positions = (
    df.groupby(["date", "position"])
      .size()
      .reset_index(name="count")
)

duplicate_positions = duplicate_positions[
    duplicate_positions["count"] > 1
]

print(
    "\nDuplicate date-position combinations:",
    len(duplicate_positions)
)


# ============================================================
# 4. DATA NORMALIZATION
# ============================================================

print("\n" + "=" * 70)
print("DATA NORMALIZATION")
print("=" * 70)

text_columns = ["song", "artist", "album_type"]

for col in text_columns:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

# Normalize album type
df["album_type"] = df["album_type"].str.lower()

# Normalize boolean field
df["is_explicit"] = (
    df["is_explicit"]
    .astype(str)
    .str.lower()
    .map({
        "true": True,
        "false": False,
        "1": True,
        "0": False
    })
)

# Duration in seconds
df["duration_seconds"] = df["duration_ms"] / 1000

# Duration in minutes
df["duration_minutes"] = df["duration_ms"] / 60000

print("\nNormalized data preview:")
print(df.head())


# ============================================================
# 5. BASIC DATASET EDA
# ============================================================

print("\n" + "=" * 70)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 70)

print("\nUnique songs:", df["song"].nunique())
print("Unique artists:", df["artist"].nunique())

print("\nAlbum type distribution:")
print(df["album_type"].value_counts())

print("\nExplicit content distribution:")
print(df["is_explicit"].value_counts())

print("\nPopularity statistics:")
print(df["popularity"].describe())

print("\nDuration statistics:")
print(df["duration_minutes"].describe())


# ============================================================
# 6. SONG LIFECYCLE CONSTRUCTION
# ============================================================

print("\n" + "=" * 70)
print("SONG LIFECYCLE ANALYSIS")
print("=" * 70)

# Sort chronologically
df = df.sort_values(["song", "artist", "date"])

# First appearance
first_appearance = (
    df.groupby(["song", "artist"])
      .agg(
          entry_date=("date", "min"),
          exit_date=("date", "max"),
          days_observed=("date", "nunique"),
          peak_position=("position", "min"),
          peak_popularity=("popularity", "max")
      )
      .reset_index()
)

# Calculate lifecycle duration
first_appearance["lifecycle_days"] = (
    first_appearance["exit_date"]
    - first_appearance["entry_date"]
).dt.days + 1

# Avoid zero/negative values
first_appearance["lifecycle_days"] = (
    first_appearance["lifecycle_days"].clip(lower=1)
)

print("\nLifecycle dataset:")
print(first_appearance.head(10))


# ============================================================
# 7. TIME TO PEAK
# ============================================================

# Position at first appearance
entry_position = (
    df.sort_values("date")
      .groupby(["song", "artist"])
      .first()
      .reset_index()[
          ["song", "artist", "date", "position"]
      ]
      .rename(columns={
          "date": "entry_date_check",
          "position": "entry_position"
      })
)

lifecycle = first_appearance.merge(
    entry_position,
    on=["song", "artist"],
    how="left"
)

# Find date of peak position
peak_rows = (
    df.sort_values(["song", "artist", "position", "date"])
      .groupby(["song", "artist"])
      .first()
      .reset_index()[
          ["song", "artist", "date", "position"]
      ]
      .rename(columns={
          "date": "peak_date",
          "position": "peak_position_check"
      })
)

lifecycle = lifecycle.merge(
    peak_rows,
    on=["song", "artist"],
    how="left"
)

lifecycle["time_to_peak_days"] = (
    lifecycle["peak_date"] -
    lifecycle["entry_date"]
).dt.days

lifecycle["time_to_peak_days"] = (
    lifecycle["time_to_peak_days"].clip(lower=0)
)


# ============================================================
# 8. ADD SONG ATTRIBUTES
# ============================================================

song_attributes = (
    df.sort_values("date")
      .groupby(["song", "artist"])
      .first()
      .reset_index()[
          [
              "song",
              "artist",
              "album_type",
              "total_tracks",
              "is_explicit",
              "duration_ms",
              "duration_minutes"
          ]
      ]
)

lifecycle = lifecycle.merge(
    song_attributes,
    on=["song", "artist"],
    how="left"
)

print("\nFinal lifecycle dataset:")
print(lifecycle.head())


# ============================================================
# 9. LIFECYCLE STAGE CLASSIFICATION
# ============================================================

print("\n" + "=" * 70)
print("LIFECYCLE STAGE CLASSIFICATION")
print("=" * 70)


def classify_lifecycle_stage(row):

    days = row["lifecycle_days"]
    peak = row["peak_position"]
    entry = row["entry_position"]

    # New entry
    if days <= 7:
        return "New Entry"

    # Peak phase
    elif peak <= 10:
        return "Peak Phase"

    # Growth
    elif entry - peak >= 10:
        return "Growth Phase"

    # Mature
    elif peak <= 30:
        return "Mature Phase"

    # Decline
    else:
        return "Decline Phase"


lifecycle["lifecycle_stage"] = lifecycle.apply(
    classify_lifecycle_stage,
    axis=1
)

print(
    lifecycle["lifecycle_stage"]
    .value_counts()
)


# ============================================================
# 10. LIFECYCLE KPI SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("LIFECYCLE KPIs")
print("=" * 70)

kpis = {
    "Average Days on Playlist":
        lifecycle["lifecycle_days"].mean(),

    "Median Days on Playlist":
        lifecycle["lifecycle_days"].median(),

    "Maximum Days on Playlist":
        lifecycle["lifecycle_days"].max(),

    "Average Entry-to-Peak Time":
        lifecycle["time_to_peak_days"].mean(),

    "Median Entry-to-Peak Time":
        lifecycle["time_to_peak_days"].median(),

    "Average Peak Position":
        lifecycle["peak_position"].mean(),

    "Songs Analyzed":
        lifecycle.shape[0]
}

kpi_df = pd.DataFrame(
    kpis.items(),
    columns=["KPI", "Value"]
)

print(kpi_df)


# ============================================================
# 11. DAILY ENTRY / EXIT ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("PLAYLIST ROTATION & CHURN")
print("=" * 70)

# Song-date presence
song_daily = (
    df[["date", "song", "artist"]]
    .drop_duplicates()
    .sort_values(["song", "artist", "date"])
)

# Previous date for each song
song_daily["previous_date"] = (
    song_daily
    .groupby(["song", "artist"])["date"]
    .shift(1)
)

# Next date
song_daily["next_date"] = (
    song_daily
    .groupby(["song", "artist"])["date"]
    .shift(-1)
)

# Entry = no previous observation
song_daily["is_entry"] = (
    song_daily["previous_date"].isna()
)

# Exit = no next observation
song_daily["is_exit"] = (
    song_daily["next_date"].isna()
)


daily_rotation = (
    song_daily.groupby("date")
    .agg(
        entries=("is_entry", "sum"),
        exits=("is_exit", "sum")
    )
    .reset_index()
)

daily_rotation["churn"] = (
    daily_rotation["entries"] +
    daily_rotation["exits"]
)

daily_rotation["churn_rate"] = (
    daily_rotation["churn"] / 50 * 100
)

print("\nDaily rotation:")
print(daily_rotation.head())


# ============================================================
# 12. MONTHLY CHURN
# ============================================================

daily_rotation["month"] = (
    daily_rotation["date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_churn = (
    daily_rotation.groupby("month")
    .agg(
        avg_entries=("entries", "mean"),
        avg_exits=("exits", "mean"),
        avg_churn=("churn", "mean"),
        avg_churn_rate=("churn_rate", "mean")
    )
    .reset_index()
)

print("\nMonthly churn:")
print(monthly_churn)


# ============================================================
# 13. RETENTION STABILITY INDEX
# ============================================================

# Definition:
# Percentage of observed lifecycle days where the song
# remains in the Top 50 without interruption.

# Calculate actual consecutive presence
song_daily["date_diff"] = (
    song_daily
    .groupby(["song", "artist"])["date"]
    .diff()
    .dt.days
)

song_daily["continuous_day"] = (
    song_daily["date_diff"].isna() |
    (song_daily["date_diff"] == 1)
)

continuity = (
    song_daily
    .groupby(["song", "artist"])
    .agg(
        observed_days=("date", "nunique"),
        continuous_days=("continuous_day", "sum")
    )
    .reset_index()
)

continuity["retention_stability_index"] = (
    continuity["continuous_days"] /
    continuity["observed_days"]
)

lifecycle = lifecycle.merge(
    continuity[
        [
            "song",
            "artist",
            "retention_stability_index"
        ]
    ],
    on=["song", "artist"],
    how="left"
)

print("\nRetention Stability Index:")
print(
    lifecycle["retention_stability_index"].describe()
)


# ============================================================
# 14. EXPLICIT VS NON-EXPLICIT ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("EXPLICIT CONTENT ANALYSIS")
print("=" * 70)

explicit_analysis = (
    lifecycle
    .groupby("is_explicit")
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        median_lifecycle_days=("lifecycle_days", "median"),
        avg_peak_position=("peak_position", "mean"),
        avg_time_to_peak=("time_to_peak_days", "mean"),
        avg_popularity=("peak_popularity", "mean"),
        avg_retention_stability=(
            "retention_stability_index",
            "mean"
        )
    )
    .reset_index()
)

print(explicit_analysis)


# Explicit Lifecycle Score
explicit_lifecycle_score = (
    lifecycle
    .groupby("is_explicit")["lifecycle_days"]
    .mean()
)

print("\nExplicit Lifecycle Score:")
print(explicit_lifecycle_score)


# ============================================================
# 15. SINGLE VS ALBUM ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("SINGLE VS ALBUM ANALYSIS")
print("=" * 70)

album_analysis = (
    lifecycle
    .groupby("album_type")
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        median_lifecycle_days=("lifecycle_days", "median"),
        avg_peak_position=("peak_position", "mean"),
        avg_time_to_peak=("time_to_peak_days", "mean"),
        avg_popularity=("peak_popularity", "mean"),
        avg_stability=(
            "retention_stability_index",
            "mean"
        )
    )
    .reset_index()
)

print(album_analysis)


# ============================================================
# 16. SINGLE VS ALBUM LONGEVITY RATIO
# ============================================================

single_life = lifecycle.loc[
    lifecycle["album_type"].str.lower() == "single",
    "lifecycle_days"
].mean()

album_life = lifecycle.loc[
    lifecycle["album_type"].str.lower() == "album",
    "lifecycle_days"
].mean()

if album_life != 0:
    single_album_ratio = single_life / album_life
else:
    single_album_ratio = np.nan

print("\nSingle vs Album Longevity Ratio:")
print(round(single_album_ratio, 3))


# ============================================================
# 17. DURATION VS RETENTION
# ============================================================

print("\n" + "=" * 70)
print("DURATION VS RETENTION")
print("=" * 70)

duration_corr = lifecycle[
    [
        "duration_minutes",
        "lifecycle_days"
    ]
].corr()

print(duration_corr)


# Duration buckets
lifecycle["duration_group"] = pd.cut(
    lifecycle["duration_minutes"],
    bins=[0, 2.5, 3.0, 3.5, 4.0, 100],
    labels=[
        "<2.5 min",
        "2.5–3 min",
        "3–3.5 min",
        "3.5–4 min",
        ">4 min"
    ]
)

duration_analysis = (
    lifecycle
    .groupby("duration_group", observed=True)
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        avg_peak_position=("peak_position", "mean"),
        avg_popularity=("peak_popularity", "mean")
    )
    .reset_index()
)

print(duration_analysis)


# ============================================================
# 18. ALBUM SIZE VS LIFECYCLE
# ============================================================

album_size_corr = lifecycle[
    [
        "total_tracks",
        "lifecycle_days"
    ]
].corr()

print("\nAlbum size vs lifecycle correlation:")
print(album_size_corr)


# Album size buckets
lifecycle["album_size_group"] = pd.cut(
    lifecycle["total_tracks"],
    bins=[0, 1, 5, 10, 15, 100],
    labels=[
        "Single",
        "2–5 tracks",
        "6–10 tracks",
        "11–15 tracks",
        "16+ tracks"
    ]
)

album_size_analysis = (
    lifecycle
    .groupby("album_size_group", observed=True)
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        avg_peak_position=("peak_position", "mean")
    )
    .reset_index()
)

print(album_size_analysis)


# ============================================================
# 19. POPULARITY VS LIFECYCLE
# ============================================================

print("\n" + "=" * 70)
print("POPULARITY VS LIFECYCLE")
print("=" * 70)

popularity_corr = lifecycle[
    [
        "peak_popularity",
        "lifecycle_days",
        "time_to_peak_days",
        "peak_position"
    ]
].corr()

print(popularity_corr)


# Popularity groups
lifecycle["popularity_group"] = pd.cut(
    lifecycle["peak_popularity"],
    bins=[0, 40, 60, 70, 80, 90, 100],
    labels=[
        "<40",
        "40–60",
        "60–70",
        "70–80",
        "80–90",
        "90+"
    ]
)

popularity_analysis = (
    lifecycle
    .groupby("popularity_group", observed=True)
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        avg_peak_position=("peak_position", "mean"),
        avg_time_to_peak=("time_to_peak_days", "mean")
    )
    .reset_index()
)

print(popularity_analysis)


# ============================================================
# 20. TOP 20 LONGEST-LIVED SONGS
# ============================================================

print("\n" + "=" * 70)
print("TOP 20 LONGEST-LIVED SONGS")
print("=" * 70)

top_lifecycle = (
    lifecycle
    .sort_values(
        "lifecycle_days",
        ascending=False
    )
    .head(20)
)

print(
    top_lifecycle[
        [
            "song",
            "artist",
            "lifecycle_days",
            "peak_position",
            "time_to_peak_days",
            "is_explicit",
            "album_type",
            "peak_popularity"
        ]
    ]
)


# ============================================================
# 21. TOP 20 FASTEST SONGS TO PEAK
# ============================================================

print("\n" + "=" * 70)
print("FASTEST SONGS TO PEAK")
print("=" * 70)

fastest_peak = (
    lifecycle
    .sort_values(
        "time_to_peak_days",
        ascending=True
    )
    .head(20)
)

print(
    fastest_peak[
        [
            "song",
            "artist",
            "entry_position",
            "peak_position",
            "time_to_peak_days",
            "lifecycle_days"
        ]
    ]
)


# ============================================================
# 22. LIFECYCLE STAGE DISTRIBUTION
# ============================================================

stage_distribution = (
    lifecycle["lifecycle_stage"]
    .value_counts()
    .reset_index()
)

stage_distribution.columns = [
    "Lifecycle Stage",
    "Songs"
]

stage_distribution["Percentage"] = (
    stage_distribution["Songs"] /
    stage_distribution["Songs"].sum() * 100
)

print("\nLifecycle stage distribution:")
print(stage_distribution)


# ============================================================
# 23. VISUALIZATIONS
# ============================================================

sns.set_theme(style="whitegrid")


# -----------------------------
# Chart 1: Lifecycle distribution
# -----------------------------
plt.figure(figsize=(10, 6))

sns.histplot(
    lifecycle["lifecycle_days"],
    bins=30,
    kde=True
)

plt.title("Distribution of Song Lifecycle Length")
plt.xlabel("Days on Spain Top 50")
plt.ylabel("Number of Songs")
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 2: Lifecycle stages
# -----------------------------
plt.figure(figsize=(10, 6))

sns.countplot(
    data=lifecycle,
    x="lifecycle_stage",
    order=[
        "New Entry",
        "Growth Phase",
        "Peak Phase",
        "Mature Phase",
        "Decline Phase"
    ]
)

plt.title("Song Lifecycle Stage Distribution")
plt.xlabel("Lifecycle Stage")
plt.ylabel("Number of Songs")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 3: Explicit comparison
# -----------------------------
plt.figure(figsize=(8, 6))

sns.boxplot(
    data=lifecycle,
    x="is_explicit",
    y="lifecycle_days"
)

plt.title("Lifecycle Length: Explicit vs Non-Explicit")
plt.xlabel("Explicit Content")
plt.ylabel("Days on Playlist")
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 4: Single vs Album
# -----------------------------
plt.figure(figsize=(8, 6))

sns.boxplot(
    data=lifecycle,
    x="album_type",
    y="lifecycle_days"
)

plt.title("Lifecycle Length: Single vs Album")
plt.xlabel("Album Type")
plt.ylabel("Days on Playlist")
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 5: Duration vs lifecycle
# -----------------------------
plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=lifecycle,
    x="duration_minutes",
    y="lifecycle_days",
    alpha=0.5
)

plt.title("Song Duration vs Playlist Longevity")
plt.xlabel("Duration (Minutes)")
plt.ylabel("Lifecycle (Days)")
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 6: Popularity vs lifecycle
# -----------------------------
plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=lifecycle,
    x="peak_popularity",
    y="lifecycle_days",
    alpha=0.5
)

plt.title("Popularity vs Playlist Longevity")
plt.xlabel("Peak Popularity")
plt.ylabel("Lifecycle (Days)")
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 7: Monthly churn
# -----------------------------
plt.figure(figsize=(12, 6))

sns.lineplot(
    data=monthly_churn,
    x="month",
    y="avg_churn_rate",
    marker="o"
)

plt.title("Monthly Playlist Churn Rate")
plt.xlabel("Month")
plt.ylabel("Average Daily Churn (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 8: Daily entries/exits
# -----------------------------
plt.figure(figsize=(14, 6))

plt.plot(
    daily_rotation["date"],
    daily_rotation["entries"],
    label="Entries"
)

plt.plot(
    daily_rotation["date"],
    daily_rotation["exits"],
    label="Exits"
)

plt.title("Daily Playlist Entries and Exits")
plt.xlabel("Date")
plt.ylabel("Number of Songs")
plt.legend()
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 9: Lifecycle vs popularity
# -----------------------------
plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=lifecycle,
    x="time_to_peak_days",
    y="peak_popularity",
    size="lifecycle_days",
    alpha=0.6
)

plt.title("Time to Peak vs Popularity")
plt.xlabel("Time to Peak (Days)")
plt.ylabel("Peak Popularity")
plt.tight_layout()
plt.show()


# ============================================================
# 24. CORRELATION MATRIX
# ============================================================

numeric_columns = [
    "popularity",
    "duration_minutes",
    "total_tracks",
    "position"
]

lifecycle_numeric = [
    "lifecycle_days",
    "time_to_peak_days",
    "peak_position",
    "peak_popularity",
    "duration_minutes",
    "total_tracks",
    "retention_stability_index"
]

corr = lifecycle[
    lifecycle_numeric
].corr()

plt.figure(figsize=(11, 8))

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0
)

plt.title("Lifecycle Correlation Matrix")
plt.tight_layout()
plt.show()


# ============================================================
# 25. RETENTION STABILITY ANALYSIS
# ============================================================

stability_analysis = (
    lifecycle
    .groupby("lifecycle_stage")
    .agg(
        songs=("song", "count"),
        avg_stability=(
            "retention_stability_index",
            "mean"
        ),
        avg_lifecycle=("lifecycle_days", "mean")
    )
    .reset_index()
)

print("\nRetention Stability by Lifecycle Stage:")
print(stability_analysis)


# ============================================================
# 26. MONTHLY LIFECYCLE ANALYSIS
# ============================================================

lifecycle["entry_month"] = (
    lifecycle["entry_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_lifecycle = (
    lifecycle
    .groupby("entry_month")
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        median_lifecycle_days=("lifecycle_days", "median"),
        avg_time_to_peak=("time_to_peak_days", "mean"),
        avg_peak_position=("peak_position", "mean")
    )
    .reset_index()
)

print("\nMonthly lifecycle analysis:")
print(monthly_lifecycle)


# ============================================================
# 27. MONTHLY EXPLICIT ANALYSIS
# ============================================================

monthly_explicit = (
    lifecycle
    .groupby(
        ["entry_month", "is_explicit"]
    )
    .agg(
        songs=("song", "count"),
        avg_lifecycle_days=("lifecycle_days", "mean"),
        avg_time_to_peak=("time_to_peak_days", "mean"),
        avg_peak_position=("peak_position", "mean")
    )
    .reset_index()
)

print("\nMonthly explicit-content analysis:")
print(monthly_explicit)


# ============================================================
# 28. CONTENT MATURITY SCORE
# ============================================================

# Normalize lifecycle-related metrics
def minmax(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0.5, index=series.index)

    return (series - minimum) / (maximum - minimum)


lifecycle["longevity_score"] = minmax(
    lifecycle["lifecycle_days"]
)

lifecycle["stability_score"] = (
    lifecycle["retention_stability_index"]
)

# Higher peak performance = better
lifecycle["peak_score"] = (
    1 - minmax(lifecycle["peak_position"])
)

lifecycle["content_maturity_score"] = (
    lifecycle["longevity_score"] * 0.4 +
    lifecycle["stability_score"] * 0.3 +
    lifecycle["peak_score"] * 0.3
)

print("\nContent Maturity Score:")
print(
    lifecycle[
        [
            "song",
            "artist",
            "content_maturity_score"
        ]
    ]
    .sort_values(
        "content_maturity_score",
        ascending=False
    )
    .head(20)
)


# ============================================================
# 29. SONG RANK TRAJECTORY FUNCTION
# ============================================================

def get_song_trajectory(song_name, artist_name=None):

    temp = df[
        df["song"].str.lower() ==
        song_name.lower()
    ].copy()

    if artist_name:
        temp = temp[
            temp["artist"].str.lower() ==
            artist_name.lower()
        ]

    if temp.empty:
        print("Song not found.")
        return

    temp = temp.sort_values("date")

    plt.figure(figsize=(12, 6))

    plt.plot(
        temp["date"],
        temp["position"],
        marker="o"
    )

    plt.gca().invert_yaxis()

    plt.title(
        f"Playlist Rank Trajectory: {song_name}"
    )

    plt.xlabel("Date")
    plt.ylabel("Playlist Position")

    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()


# Example:
# get_song_trajectory("Supernova", "Saiko")


# ============================================================
# 30. EXPORT ANALYTICAL DATASETS
# ============================================================

OUTPUT_DIR = Path("E:\\power bi\\Atlantic_Spain\\outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Clean dataset
df.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\atlantic_spain_cleaned.csv",
    index=False
)

# Lifecycle dataset
lifecycle.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\song_lifecycle_analysis.csv",
    index=False
)

# Daily rotation
daily_rotation.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\daily_playlist_rotation.csv",
    index=False
)

# Monthly churn
monthly_churn.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\monthly_churn_analysis.csv",
    index=False
)

# Explicit analysis
explicit_analysis.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\explicit_content_analysis.csv",
    index=False
)

# Album analysis
album_analysis.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\single_vs_album_analysis.csv",
    index=False
)

# Duration analysis
duration_analysis.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\duration_analysis.csv",
    index=False
)

# Popularity analysis
popularity_analysis.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\popularity_lifecycle_analysis.csv",
    index=False
)

# Stage distribution
stage_distribution.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\lifecycle_stage_distribution.csv",
    index=False
)

print("\n" + "=" * 70)
print("FILES EXPORTED")
print("=" * 70)

for file in OUTPUT_DIR.iterdir():
    print(file.name)


# ============================================================
# 31. FINAL KPI REPORT
# ============================================================

final_kpis = pd.DataFrame({
    "KPI": [
        "Total Dataset Rows",
        "Unique Songs",
        "Unique Artists",
        "Number of Days",
        "Average Days on Playlist",
        "Median Days on Playlist",
        "Maximum Days on Playlist",
        "Average Entry-to-Peak Time",
        "Average Peak Position",
        "Average Churn Rate",
        "Average Retention Stability",
        "Single/Album Longevity Ratio"
    ],
    "Value": [
        len(df),
        df["song"].nunique(),
        df["artist"].nunique(),
        df["date"].nunique(),
        lifecycle["lifecycle_days"].mean(),
        lifecycle["lifecycle_days"].median(),
        lifecycle["lifecycle_days"].max(),
        lifecycle["time_to_peak_days"].mean(),
        lifecycle["peak_position"].mean(),
        daily_rotation["churn_rate"].mean(),
        lifecycle["retention_stability_index"].mean(),
        single_album_ratio
    ]
})

print("\nFINAL KPI REPORT")
print(final_kpis)

final_kpis.to_csv(
    OUTPUT_DIR / "E:\\power bi\\Atlantic_Spain\\outputs\\final_kpi_report.csv",
    index=False
)

print("\nAnalysis completed successfully.")