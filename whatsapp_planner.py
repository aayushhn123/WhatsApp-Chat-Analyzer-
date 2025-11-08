# app.py - WhatsApp Chat Analyzer (AWS Ready)
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="centered")
st.title("WhatsApp Chat Analyzer")
st.caption("Export any chat → Upload → Get insane stats!")

uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type="txt")

if uploaded_file:
    # Read the chat
    bytes_data = uploaded_file.read()
    data = bytes_data.decode("utf-8")
    
    # Parse WhatsApp format
    messages = []
    dates = []
    users = []
    
    for line in data.split("\n"):
        if line.strip() and ("AM" in line or "PM" in line) and "] " in line:
            try:
                # Example: 12/25/23, 10:30 PM - Aayush: Hello bro
                datetime_part = line.split("] ")[0][1:]  # remove first [
                message_part = line.split("] ")[1]
                if ": " in message_part:
                    user = message_part.split(": ")[0]
                    message = message_part.split(": ")[1]
                    
                    users.append(user)
                    messages.append(message)
                    dates.append(datetime_part)
            except:
                pass
    
    df = pd.DataFrame({"user": users, "message": messages, "date": dates})
    df['date'] = pd.to_datetime(df['date'], format='mixed')
    df['hour'] = df['date'].dt.hour
    df['day'] = df['date'].dt.day_name()
    df['emoji'] = df['message'].apply(lambda x: ''.join(c for c in x if c in emoji.EMOJI_DATA))

    # === STATS ===
    st.success(f"Analysis Complete! Found {len(df):,} messages from {df['user'].nunique()} people")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", len(df))
    with col2:
        st.metric("Most Active", df['user'].mode()[0])
    with col3:
        st.metric("Chat Duration", f"{df['date'].dt.date.nunique()} days")

    # Top 10 speakers
    st.subheader("Who talks the most?")
    top_users = df['user'].value_counts().head(10)
    fig = px.bar(x=top_users.values, y=top_users.index, orientation='h', 
                 color=top_users.values, color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)

    # Peak hours
    st.subheader("When do you spam?")
    hours = df['hour'].value_counts().sort_index()
    fig2 = px.line(x=hours.index, y=hours.values, markers=True)
    fig2.update_layout(xaxis_title="Hour", yaxis_title="Messages", xaxis=dict(tick0=0, dtick=1))
    st.plotly_chart(fig2, use_container_width=True)

    # Word Cloud
    st.subheader("Most Used Words")
    all_words = ' '.join(df['message']).lower()
    wordcloud = WordCloud(width=800, height=400, background_color='black', 
                          stopwords=['media', 'omitted', 'this', 'message', 'deleted']).generate(all_words)
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

    # Emoji leaderboard
    st.subheader("Emoji Leaderboard")
    all_emojis = ''.join(df['emoji'])
    emoji_count = Counter(all_emojis).most_common(10)
    if emoji_count:
        emoji_df = pd.DataFrame(emoji_count, columns=['Emoji', 'Count'])
        fig3 = px.bar(emoji_df, x='Emoji', y='Count', color='Count')
        st.plotly_chart(fig3, use_container_width=True)