import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components


# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(layout="wide")

st.title("🐰 Bad Bunny Spotify Music Data")
st.caption("🌐 Explore my full data portfolio → https://evelyntc.streamlit.app/")


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
    st.write(""" 🎶 The announcement of Bad Bunny as the 2026 Super Bowl Halftime Show performer surprised some people but the data shows it shouldn’t have.
            \n This dashboard is designed to contextualize Bad Bunny’s career through data highlighting yearly growth and global popularity.""")

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
import plotly.graph_objects as go

st.markdown("## 📈 Bad Bunny's Yearly Growth")

# ----------------------------
# Prepare data
# ----------------------------
df_yearly = (
    df.groupby(df["release_date"].dt.year)["track_popularity"]
    .mean()
    .reset_index()
    .rename(columns={"release_date": "year", "track_popularity": "avg_popularity"})
)

# Year-over-year growth
df_yearly["pop_growth"] = df_yearly["avg_popularity"].diff()

# Find biggest jump
max_growth_idx = df_yearly["pop_growth"].idxmax()
max_growth_year = df_yearly.loc[max_growth_idx, "year"]
max_growth_value = df_yearly.loc[max_growth_idx, "pop_growth"]
max_growth_pop = df_yearly.loc[max_growth_idx, "avg_popularity"]

# Cumulative average for reference (optional trace)
df_yearly["cumulative_avg"] = df_yearly["avg_popularity"].expanding().mean()

# ----------------------------
# Create Plotly figure
# ----------------------------
fig_growth = go.Figure()

# Line: cumulative average (optional, light background)
fig_growth.add_trace(go.Scatter(
    x=df_yearly["year"],
    y=df_yearly["cumulative_avg"],
    mode="lines",
    line=dict(color="rgba(255,20,147,0.3)", width=3, dash="dot"),
    name="Cumulative Avg",
    hovertemplate="<b>Year:</b> %{x}<br><b>Cumulative Avg:</b> %{y:.1f}<extra></extra>"
))

# Line + markers: yearly avg popularity
fig_growth.add_trace(go.Scatter(
    x=df_yearly["year"],
    y=df_yearly["avg_popularity"],
    mode="lines+markers",
    line=dict(color="#ff1493", width=4),
    marker=dict(size=10, symbol="circle"),
    name="Yearly Avg",
    hovertemplate="<b>Year:</b> %{x}<br><b>Avg Popularity:</b> %{y:.1f}<extra></extra>"
))

# Highlight biggest jump
fig_growth.add_trace(go.Scatter(
    x=[max_growth_year],
    y=[max_growth_pop],
    mode="markers+text",
    marker=dict(size=18, color="gold", symbol="star"),
    text=[f"⬆️ Biggest Jump (+{max_growth_value:.1f})"],
    textposition="top center",
    showlegend=False,
    hovertemplate="<b>Year:</b> %{x}<br><b>Growth:</b> +%{text}<extra></extra>"
))

# ----------------------------
# Layout
# ----------------------------
fig_growth.update_layout(
    template="plotly_dark",
    height=500,
    title="Bad Bunny's popularity drastically increased in 2020 and while it plateaued a bit, he continued to grow in 2025!",
    xaxis=dict(title="Year", dtick=1),
    yaxis=dict(title="Popularity Score (0–100)", range=[0, 100]),
    hovermode="x unified",
    showlegend=True,
)

# Optional annotations
fig_growth.add_annotation(
    x=max_growth_year,
    y=max_growth_pop,
    text=f"Biggest jump here!",
    showarrow=True,
    arrowhead=2,
    arrowcolor="gold",
    ax=0,
    ay=-40,
    font=dict(color="gold", size=12)
)

# Display in Streamlit
st.plotly_chart(fig_growth, use_container_width=True)


# ============================
# 🔥 Most Popular Tracks
# ============================
st.markdown("## 🎤 Most Popular Songs")
st.write("Bad Bunny's top 3 most popular songs come from his 2025 album DeBÍ TiRAR MáS FOToS. ")

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
st.markdown("## 🧠 Key Takeaway: \n Bad Bunny's dominance isn't built on one era, it compounded with every release and this artist is only getting started." \
"\n His latest album garnering his biggest hits. So if you haven't heard his music first where should you get started? ⬇️")

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
    <p style="font-size: 0.85rem; color: #718096;">
        Built by Evelyn | 
        <a href="https://evelyntc.streamlit.app" target="_blank" style="color:#ff4b4b; text-decoration:none;">
            View Full Portfolio
        </a>
    </p>
</div>
""", unsafe_allow_html=True)


# --- STATCOUNTER ---
st.html(
"""<!-- Default Statcounter code for badbunnydashboard
https://badbunnydashboard.streamlit.app/ -->
<script type="text/javascript">
var sc_project=13202887; 
var sc_invisible=1; 
var sc_security="31bf5360"; 
</script>
<script type="text/javascript"
src="https://www.statcounter.com/counter/counter.js"
async></script>
<noscript><div class="statcounter"><a title="Web Analytics"
href="https://statcounter.com/" target="_blank"><img
class="statcounter"
src="https://c.statcounter.com/13202887/0/31bf5360/1/"
alt="Web Analytics"
referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
<!-- End of Statcounter Code -->
""",
)
