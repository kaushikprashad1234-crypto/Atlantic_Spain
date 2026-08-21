# 🎵 Atlantic Spain Top 50 — Song Lifecycle & Playlist Rotation Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)]()
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-blue)]()
[![Plotly](https://img.shields.io/badge/Plotly-Visualization-purple)]()

## 📌 Project Overview

**Atlantic Spain Top 50** is a data analytics and Streamlit dashboard project designed to analyze **song lifecycle, playlist rotation, content maturity, and popularity patterns** within Spain's Top 50 music playlist.

The project examines how songs move through the playlist ecosystem:

```text
New Entry
   ↓
Growth
   ↓
Peak
   ↓
Maturity
   ↓
Decline
   ↓
Exit
```

The analysis transforms longitudinal playlist observations into actionable insights that can support **music release strategy, promotional planning, playlist optimization, and content investment decisions**.

---

# 🎯 Business Problem

Atlantic Recording Corporation has access to daily Spain Top 50 playlist data but requires deeper insight into how songs perform over time.

Key business questions include:

- How long do songs remain in Spain's Top 50?
- Do playlists favor fresh releases or mature content?
- How quickly do songs reach their best positions?
- How intensive is playlist rotation?
- Do explicit and non-explicit songs behave differently?
- Do singles and album tracks have different lifecycles?
- Is popularity associated with playlist longevity?
- Which songs demonstrate strong momentum?
- Which songs are entering decline?

Without lifecycle intelligence, release and marketing strategies may rely too heavily on approaches developed for other music markets.

This project develops a **Spain-specific analytical framework** for understanding playlist behavior.

---

# 🎯 Project Objectives

## Primary Objectives

1. Measure song lifecycle duration.
2. Identify playlist entry, peak, and exit patterns.
3. Analyze playlist churn and rotation.
4. Classify songs by lifecycle stage.
5. Compare explicit and non-explicit content.
6. Compare singles and album tracks.
7. Analyze popularity versus playlist longevity.

## Secondary Objectives

- Identify high-performing durable songs.
- Detect rapidly growing songs.
- Identify declining content.
- Support release-timing decisions.
- Improve promotional allocation.
- Develop Spain-specific playlist strategies.
- Identify opportunities for predictive modeling.

---

# 📊 Dataset

The project uses daily observations from Spain's Top 50 music playlist.

## Dataset Columns

| Column | Description |
|---|---|
| `date` | Playlist snapshot date |
| `position` | Playlist rank from 1–50 |
| `song` | Song title |
| `artist` | Artist name |
| `popularity` | Popularity score |
| `duration_ms` | Song duration in milliseconds |
| `album_type` | Single or Album |
| `total_tracks` | Number of tracks in the album |
| `is_explicit` | Explicit content indicator |
| `album_cover_url` | Album artwork URL |

## Dataset Scale

- **27,800 observations**
- **583 unique songs**
- Daily Top 50 playlist structure
- Longitudinal song-level observations
- Historical ranking trajectories

The longitudinal nature of the dataset allows each song to be analyzed across its observed playlist lifecycle.

---

# 🔬 Methodology

## 1. Data Validation & Normalization

The preprocessing pipeline performs the following operations:

- Validates date values
- Checks playlist positions
- Removes invalid records
- Normalizes song names
- Normalizes artist names
- Converts numeric fields
- Handles explicit-content flags
- Identifies unique song/artist combinations
- Detects missing values
- Checks duplicate observations

The goal is to create a reliable dataset for lifecycle and playlist rotation analysis.

---

## 2. Song Lifecycle Construction

Each song is analyzed across its observed playlist journey.

```text
Entry Date
     ↓
Growth
     ↓
Peak
     ↓
Maturity
     ↓
Decline
     ↓
Exit Date
```

### Core Lifecycle Metrics

#### Lifecycle Days

```text
Exit Date − Entry Date + 1
```

This measures the observed duration of a song's presence within the playlist dataset.

#### Peak Position

```text
Minimum observed playlist position
```

Because lower playlist positions represent better rankings, position `1` is the strongest possible peak.

#### Time to Peak

```text
Peak Date − Entry Date
```

This measures how quickly a song reaches its best observed playlist position.

#### Entry Position

The playlist rank when a song first appears in the Top 50.

#### Exit Position

The final observed rank before the song leaves the playlist or the dataset observation period ends.

---

# 🧭 Lifecycle Classification

Songs are categorized into five analytical lifecycle stages.

| Stage | Definition |
|---|---|
| 🆕 **New Entry** | Song has recently entered the playlist, typically ≤ 7 days |
| 📈 **Growth Phase** | Song demonstrates significant rank improvement |
| 🏆 **Peak Phase** | Song reaches strong performance, typically Top 10 |
| 🎯 **Mature Phase** | Song demonstrates relatively stable playlist performance |
| 📉 **Decline Phase** | Song demonstrates deteriorating rank performance |

Lifecycle classification allows the dashboard to move beyond static rankings and identify **momentum and trajectory**.

---

# 🔄 Playlist Churn Analysis

Playlist rotation is measured through daily entries and exits.

## Churn Rate

```text
(Entries + Exits) / 50 × 100
```

Higher churn indicates stronger playlist volatility.

Lower churn suggests greater playlist stability.

The churn framework helps identify periods of:

- High playlist volatility
- Strong release competition
- Rapid content replacement
- Greater playlist stability
- Seasonal rotation patterns

Daily metrics are also aggregated into monthly trends to identify longer-term changes in playlist behavior.

---

# 🔞 Content Maturity Analysis

The project compares:

### Explicit Content

vs.

### Non-Explicit Content

The following metrics are evaluated:

- Average lifecycle duration
- Median lifecycle duration
- Average peak position
- Time to peak
- Playlist retention
- Retention stability

This analysis provides an evidence-based framework for understanding whether content classification is associated with different playlist trajectories.

---

# 💿 Single vs Album Analysis

The project compares:

- **Singles**
- **Album tracks**

using:

- Lifecycle duration
- Peak position
- Time to peak
- Playlist retention
- Retention stability
- Top-10 performance

This helps determine whether dedicated single releases demonstrate different playlist behavior compared with tracks originating from larger albums.

---

# 📈 Popularity vs Playlist Longevity

The dashboard evaluates the relationship between popularity and lifecycle duration.

Songs are segmented into four strategic groups:

| Popularity | Lifecycle | Interpretation |
|---|---|---|
| High | Long | 🏆 Durable Winners |
| High | Short | ⚡ Potential Under-Monetization |
| Low | Long | 🎯 Stable or Niche Content |
| Low | Short | 📉 Low-Priority Content |

This framework helps identify songs that may deserve:

- Additional promotion
- Playlist retention efforts
- Catalog investment
- Reactivation campaigns
- Reduced marketing allocation

---

# 📊 Key Performance Indicators

The dashboard provides executive-level KPIs, including:

- **Average Days on Playlist**
- **Median Lifecycle**
- **Average Peak Position**
- **Average Entry Position**
- **Entry-to-Peak Time**
- **Playlist Churn Rate**
- **Retention Stability Index**
- **Content Maturity Score**
- **Top-10 Rate**
- **Single vs Album Longevity**
- **Explicit vs Non-Explicit Lifecycle**

These KPIs provide a high-level view of playlist dynamics while supporting deeper song-level analysis.

---

# 🖥️ Streamlit Dashboard

The project includes an interactive Streamlit application for exploring Spain's Top 50 playlist ecosystem.

## 🎛️ Interactive Filters

Users can filter the analysis by:

- Date range
- Lifecycle stage
- Explicit / Non-explicit content
- Album type
- Song
- Artist

---

## 📊 KPI Cards

The dashboard provides an executive-level overview of the selected dataset.

Example metrics include:

```text
Average Lifecycle
Median Lifecycle
Average Peak Position
Top-10 Rate
Playlist Churn
Average Time to Peak
```

---

## 🎯 Lifecycle Timeline

Visualizes song lifecycles from entry to exit.

This allows users to identify:

- Long-running songs
- Short-lived entries
- Rapid climbers
- Durable performers
- Declining content

---

## 🔄 Churn Dashboard

Displays:

- Daily entries
- Daily exits
- Daily churn
- Monthly churn rate
- Playlist stability trends

---

## 🔞 Content Comparison

Compares:

```text
Explicit
     vs
Non-Explicit
```

across lifecycle, peak performance, retention, and time-to-peak metrics.

---

## 💿 Album Analysis

Compares:

```text
Singles
    vs
Album Tracks
```

to identify differences in longevity and ranking performance.

---

## 📈 Popularity Analysis

Visualizes the relationship between:

```text
Popularity Score
       vs
Lifecycle Duration
```

This helps identify durable high-popularity songs and unusual outliers.

---

## 🔎 Song Drill-Down

Users can select an individual song and inspect:

- Entry date
- Peak date
- Exit date
- Lifecycle stage
- Lifecycle duration
- Peak position
- Time to peak
- Popularity
- Retention stability
- Daily ranking trajectory

This enables detailed song-level strategic analysis.

---

# 🖼️ Dashboard Preview

Add your dashboard screenshot to:

```text
screenshots/dashboard.png
```

Then display it in the README:

```markdown
![Atlantic Spain Top 50 Dashboard](screenshots/dashboard.png)
```

Example:

![Atlantic Spain Top 50 Dashboard](screenshots/dashboard.png)

---

# 💡 Business Insights Framework

The project enables Atlantic Recording Corporation to identify several important song categories.

## 🏆 Durable Winners

Characteristics:

- High popularity
- Long lifecycle
- Strong peak positions
- Stable retention

### Strategic Action

Maintain playlist visibility and maximize catalog monetization.

---

## 🚀 Rapid Growth Songs

Characteristics:

- Short time to peak
- Significant rank improvement
- Strong early momentum

### Strategic Action

Increase promotional investment while momentum is strongest.

---

## 🎯 Mature Stable Songs

Characteristics:

- Long playlist retention
- Stable rankings
- Consistent visibility

### Strategic Action

Focus on efficient retention and long-tail consumption.

---

## 📉 Declining Songs

Characteristics:

- Worsening playlist positions
- Reduced momentum
- Potential exit risk

### Strategic Action

Evaluate:

- Reactivation campaigns
- Remix opportunities
- Alternative marketing
- Playlist repositioning
- Transition to the next release

---

# 🎯 Strategic Recommendations

Based on the lifecycle framework, Atlantic can implement a dynamic content strategy.

## 🆕 New Entry

**Strategy: Monitor**

Focus on:

- Early playlist acceptance
- Entry position
- Initial rank movement
- Early popularity signals

---

## 📈 Growth Phase

**Strategy: Invest**

Increase:

- Promotional support
- Social media activity
- Marketing visibility
- Artist content activity

Songs demonstrating strong positive momentum may justify additional investment.

---

## 🏆 Peak Phase

**Strategy: Maximize**

Focus on:

- Maximum exposure
- Promotional amplification
- Cross-platform visibility
- Commercial monetization

This is the period of strongest playlist visibility.

---

## 🎯 Mature Phase

**Strategy: Retain Efficiently**

Focus on:

- Long-tail streaming
- Catalog value
- Efficient marketing
- Stable audience engagement

---

## 📉 Decline Phase

**Strategy: Evaluate or Transition**

Consider:

- Reactivation
- Remix releases
- Alternative playlist opportunities
- Reduced promotional spending
- Launch preparation for the next release

---

# 🗂️ Project Structure

```text
Atlantic-Spain-Top50/
│
├── Atlantic_Spain.csv
├── song_lifecycle_analysis.csv
├── app.py
│
├── notebooks/
│   └── Data Validation & Normalization.py
│
├── research/
│   ├── research_paper.md
│   └── executive_summary.md
│
├── screenshots/
│   └── dashboard.png
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/<username>/Atlantic-Spain-Top50.git
cd Atlantic-Spain-Top50
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install the core packages directly:

```bash
pip install streamlit pandas numpy plotly
```

---

# ▶️ Run the Application

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

The application will open automatically in your default browser.

---

# 📦 Requirements

Recommended Python version:

```text
Python 3.10+
```

Core dependencies:

```text
streamlit
pandas
numpy
plotly
```

Example `requirements.txt`:

```text
streamlit
pandas
numpy
plotly
```

---

# ❓ Example Business Questions

The dashboard can answer questions such as:

## Lifecycle

- How long do songs typically survive in Spain's Top 50?
- Which songs have the longest observed lifecycle?
- Which songs exit the playlist quickly?

## Release Strategy

- Which songs reach their peak fastest?
- Which songs show the strongest early momentum?
- When should promotional investment increase?

## Playlist Rotation

- When does playlist churn increase?
- Which periods demonstrate the highest content turnover?
- Is the playlist becoming more or less stable?

## Content

- Do explicit songs have different lifecycle patterns?
- Do explicit songs peak faster?
- Do non-explicit songs demonstrate stronger retention?

## Format

- Do singles remain on the playlist longer than album tracks?
- Do singles achieve better peak positions?
- Do album tracks demonstrate different retention patterns?

## Popularity

- Does higher popularity correspond to longer playlist retention?
- Which high-popularity songs have unexpectedly short lifecycles?
- Which lower-popularity songs demonstrate strong durability?

## Song-Level Strategy

- Which songs are currently growing?
- Which songs are at peak performance?
- Which songs are declining?
- Which songs may require additional promotion?

---

# 🔮 Future Improvements

Potential project extensions include:

- Spotify streaming data integration
- Actual commercial release dates
- Social media engagement data
- TikTok trend data
- Radio airplay
- Genre classification
- Artist-level analysis
- Spanish vs international artist comparison
- Regional-language analysis
- Collaborative playlist analysis
- Automated weekly reporting

---

# 🤖 Future Machine Learning Models

The project can be extended from descriptive analytics into predictive music-market intelligence.

Potential prediction targets include:

## Top-10 Prediction

```text
Probability of a song reaching the Top 10
```

Potential input features:

- Entry position
- Early rank improvement
- Popularity
- Explicit content
- Album type
- Historical artist performance

---

## Playlist Survival Prediction

```text
Expected number of playlist days
```

Potential models could estimate the expected longevity of a song based on its early performance characteristics.

This would allow Atlantic to identify promising songs earlier in their lifecycle.

---

# ⚠️ Limitations

This analysis should be interpreted within the limitations of the dataset.

- Playlist presence does not represent total streaming consumption.
- First observed playlist appearance is not necessarily the commercial release date.
- Final observed playlist appearance may be affected by the dataset observation window.
- Popularity scores are relative indicators.
- Correlation does not establish causation.
- Editorial and algorithmic playlist decisions are not directly observed.
- The dataset represents one playlist environment rather than the entire Spanish music market.
- Playlist performance may be influenced by external events not included in the dataset.

These limitations are important when translating descriptive patterns into business decisions.

---

# 📚 Research Deliverables

This project includes:

- **Exploratory Data Analysis**
- **Song Lifecycle Analysis**
- **Playlist Churn Analysis**
- **Content Maturity Analysis**
- **Single vs Album Analysis**
- **Popularity Analysis**
- **Research Paper**
- **Executive Summary**
- **Interactive Streamlit Dashboard**

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical operations |
| Plotly | Interactive visualizations |
| Streamlit | Interactive dashboard |
| GitHub | Version control and project hosting |

---

# 👤 Author

**Kaushik Prasad**

### Project

**Content Maturity, Release Lifecycle & Playlist Rotation Analysis of Spain Top 50 Songs**

### Organization / Mentor

**Atlantic Recording Corporation / Unified Mentor**

---

# 📄 License

This project is intended for **educational, analytical, and research purposes**.

Dataset ownership and third-party content rights remain with their respective owners.

---

# ⭐ Project Impact

This project demonstrates how longitudinal playlist data can be transformed into a structured **music analytics framework**.

Instead of treating playlist rankings as isolated daily observations, the project analyzes each song as a dynamic lifecycle:

```text
Entry
  ↓
Growth
  ↓
Peak
  ↓
Maturity
  ↓
Decline
  ↓
Exit
```

The resulting framework can support:

- Release strategy
- Marketing optimization
- Promotional investment
- Playlist intelligence
- Content portfolio management
- Artist strategy
- Lifecycle forecasting

Ultimately, the project provides a foundation for moving from **descriptive playlist analytics** toward **predictive music-market intelligence**.