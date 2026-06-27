import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="c Game Analytics Dashboard",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Wolfee Aka Amit's Game Analytics Dashboard")

# ---------------- DATABASE CONNECTION ----------------
try:
    engine = create_engine("mysql+pymysql://root:@localhost/game_login")
except Exception as e:
    st.error("Database connection failed")
    st.stop()

# ---------------- LOAD DATA ----------------
try:
    users_query = "SELECT * FROM users"

    stats_query = """
    SELECT users.username, game_name, high_score, total_plays, total_time, avg_time
    FROM game_stats
    JOIN users ON users.id = game_stats.user_id
    """

    users_df = pd.read_sql(users_query, engine)
    stats_df = pd.read_sql(stats_query, engine)

except Exception as e:
    st.error("Error loading data from database")
    st.stop()

# ---------------- KPI CARDS ----------------
total_users = len(users_df)

if not stats_df.empty:
    total_games = stats_df["total_plays"].sum()
    highest_score = stats_df["high_score"].max()
    avg_time = stats_df["avg_time"].mean()
else:
    total_games = 0
    highest_score = 0
    avg_time = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", total_users)
col2.metric("Total Games Played", int(total_games))
col3.metric("Highest Score", int(highest_score))
col4.metric("Average Play Time", round(avg_time, 2))

st.divider()

# ---------------- GAME POPULARITY CHART ----------------
st.subheader("📊 Game Popularity")

if not stats_df.empty:

    game_chart = px.bar(
        stats_df,
        x="game_name",
        y="total_plays",
        color="game_name",
        title="Games Played Per Game"
    )

    st.plotly_chart(game_chart, width="stretch")

else:
    st.warning("No game statistics available")

# ---------------- LEADERBOARD ----------------
st.subheader("🏆 Top Players")

if not stats_df.empty:

    top_players = stats_df.sort_values(
        by="high_score",
        ascending=False
    ).head(10)

    leader_chart = px.bar(
        top_players,
        x="username",
        y="high_score",
        color="username",
        title="Top 10 Players"
    )

    st.plotly_chart(leader_chart, width="stretch")

# ---------------- PLAY TIME ANALYSIS ----------------
st.subheader("⏱ Play Time Distribution")

if not stats_df.empty:

    time_chart = px.pie(
        stats_df,
        names="game_name",
        values="avg_time",
        title="Average Play Time by Game"
    )

    st.plotly_chart(time_chart, width="stretch")

# ---------------- DATA TABLES ----------------
st.subheader("👤 Users Table")
st.dataframe(users_df, width="stretch")

st.subheader("🎮 Game Statistics")
st.dataframe(stats_df, width="stretch")
