import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(layout="wide")
st.title("🐰 Bad Bunny Spotify Music Data")
# Custom CSS for custom width
st.markdown("""
<style>
    .main {
        max-width: 980px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

photo, welcome_msg = st.columns((1, 2.5), vertical_alignment="center")
with photo:
    st.image("bb.jpeg")
with welcome_msg:
    st.write(""" 🎬 add later """)

# ----------------------------
# Load data
# ----------------------------
@st.cache_data
def load_data():
    
    df = pd.read_csv("data/track_data_final.csv")

    df = df.rename(columns={
        "album_release_date": "release_date"
    })

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year

    df["track_popularity"] = pd.to_numeric(df["track_popularity"], errors="coerce")
    df["artist_followers"] = pd.to_numeric(df["artist_followers"], errors="coerce")
    df["artist_popularity"] = pd.to_numeric(df["artist_popularity"], errors="coerce")

    df = df[df["artist_name"].str.lower() == "bad bunny"]
    df = df.drop_duplicates(subset=["track_id"])

    all_genres = (
        df["artist_genres"]
        .dropna()
        .apply(lambda x: [g.strip().lower() for g in x.split(",")])
        .explode()
    )

    primary_genre = all_genres.value_counts().idxmax().title()  # Most frequent genre

    # Assign the same genre to all tracks
    df["primary_genre"] = primary_genre
    top_genre = df["primary_genre"].mode()[0]  # Just the string

    return df


df = load_data()


# ----------------------------
# Overview Metrics
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.info("🌍 **#1 Global Artist in 2025** - only artist to make the Global Top Artist list 4 times!")

with col2:
    st.info("🎵 **82 Million Monthly Listeners** & most streamed artist in Spotify history.")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.info(f"🎵 **Total Tracks**\n\n{df.shape[0]}")
with col2:
    st.info(f"💿 **Albums**\n\n{df['album_name'].nunique()}")
with col3:
    st.info(f"📅 **Years Covered**\n\n{int(df['release_year'].min())} – {int(df['release_year'].max())}")
with col4:
    followers_millions = df['artist_followers'].max() / 1_000_000
    st.info(f"👥 **Followers**\n\n{followers_millions:.0f}\nmillion")
with col5:
    genres_str = df['artist_genres'].mode()[0].replace("'", "").replace('"', "").strip("[]")
    top_genre_only = genres_str.split(",")[0].strip()
    st.info(f"🎸 **Top Genre**\n\n{top_genre_only}")

    

# ============================
# 📈 Yearly Popularity
# ============================
st.markdown("## 📈 Yearly Popularity")

df_timeline = df[["release_date", "track_popularity"]].sort_values("release_date")
df_timeline["cumulative_avg"] = df_timeline["track_popularity"].expanding().mean()

fig_growth = go.Figure()

fig_growth.add_trace(go.Scatter(
    x=df_timeline["release_date"],
    y=df_timeline["cumulative_avg"],
    mode="lines+markers",
    line=dict(color="#ff1493", width=4),
    marker=dict(size=8, symbol="star"),
    fill="tozeroy",
    fillcolor="rgba(255, 20, 147, 0.15)",
    hovertemplate=(
        "<b>Date:</b> %{x|%Y}<br>"
        "<b>Cumulative Avg Popularity:</b> %{y:.1f}"
        "<extra></extra>"
    )
))

fig_growth.update_layout(
    template="plotly_dark",
    height=450,
    showlegend=False,
    hovermode="x unified",
    yaxis=dict(
        title="Spotify Popularity Score (0–100)",
        range=[0, 100]
    ),
    annotations=[
        dict(
            xref="paper",
            yref="paper",
            x=0.99,
            y=1.0,
            xanchor="right",
            showarrow=False,
            text=(
                "<b>What is Spotify Popularity?</b><br>"
                "A 0–100 score based on recent streams,<br>"
                "listener engagement, and growth velocity."
            ),
            bgcolor="rgba(0,0,0,0.6)",
            font=dict(size=12)
        ),
        dict(
            xref="paper",
            yref="paper",
            x=0.7,
            y=0.2,
            showarrow=False,
            text="📈 Popularity compounds over time, not just hit releases",
            font=dict(size=11, color="#d1d5db")
        )
    ]
)

st.plotly_chart(fig_growth, use_container_width=True)

# ============================
# 🔥 Most Popular Tracks
# ============================
st.markdown("## 🎤 Most Popular Songs")

top_n = st.slider("Number of tracks to display", 5, 20, 10)

top_tracks = (
    df.sort_values("track_popularity", ascending=False)
      .head(top_n)
      .sort_values("track_popularity")
)

fig_tracks = go.Figure(go.Bar(
    x=top_tracks["track_popularity"],
    y=top_tracks["track_name"],
    orientation="h",
    text=top_tracks["track_popularity"],
    textposition="outside",
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Spotify Popularity Score: %{x}"
        "<extra></extra>"
    )
))

fig_tracks.update_layout(
    template="plotly_dark",
    xaxis_title="Spotify Popularity Score",
    yaxis_title="Songs",
    height=450
)

st.plotly_chart(fig_tracks, use_container_width=True)

# ============================
# 🧠 Key Insights
# ============================
st.markdown("## 🧠 Key Takeaway: \n Bad Bunny's dominance isn't built on one era, it compounded with every release and this artist is only getting started.")
st.markdown("### So what should you listen to first?")

st.markdown(f"""
- **🎤 Most Popular Album:** {df.groupby("album_name")["track_popularity"].mean().idxmax()}  
- **🔥 Most Popular Track:** {df.loc[df["track_popularity"].idxmax(), "track_name"]}  
- **📅 Peak Popularity Year:** {int(df.groupby("release_year")["track_popularity"].mean().idxmax())}
""")

# ============================
# Footer
# ============================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a0aec0; margin-top: 2rem;">
    <p style="font-size: 0.9rem;">🎵 Data powered by Spotify API | Last Updated: 2025</p>
    <p style="font-size: 0.85rem; color: #718096;">Evelyn's Entertainment Data 🔥</p>
</div>
""", unsafe_allow_html=True)

# --- STATCOUNTER ---
st.html(
    """
<!-- Statcounter Code -->
<script type="text/javascript">
var sc_project=13141013;
var sc_invisible=1;
var sc_security="1e0c10d8";
</script>
<script type="text/javascript"
src="https://www.statcounter.com/counter/counter.js"
async></script>
<noscript><div class="statcounter"><a title="web counter"
href="https://statcounter.com/" target="_blank"><img
class="statcounter"
src="https://c.statcounter.com/13141013/0/1e0c10d8/1/"
alt="web counter"
referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
""",
)