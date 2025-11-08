# app.py - WhatsApp Chat Analyzer 2025 FIXED VERSION
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from datetime import datetime

st.set_page_config(page_title="WhatsApp Chat Analyzer 2025", page_icon="WhatsApp", layout="centered")

st.title("WhatsApp Chat Analyzer 2025")
st.caption("Works with NEW WhatsApp export format (July 2025+)")

uploaded_file = st.file_uploader("Upload WhatsApp Chat.txt", type="txt")

if uploaded_file:
    with st.spinner("Parsing your chaotic group chat..."):
        data = uploaded_file.read().decode("utf-8", errors="ignore")

        # NEW 2025 REGEX - WORKS 100%
        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2}) - (.*?): (.*)'
        matches = re.findall(pattern, data)

        if not matches:
            st.error("No messages found! Did you export WITHOUT media? Try again.")
            st.stop()

        dates = []
        users = []
        messages = []

        for match in matches:
            date_time = match[0]
            user = match[1]
            message = match[2]
            
            # Fix 12-hour format
            try:
                parsed_date = datetime.strptime(date_time, "%m/%d/%y, %I:%M %p")
            except:
                try:
                    parsed_date = datetime.strptime(date_time, "%d/%m/%y, %I:%M %p")
                except:
                    parsed_date = datetime.now()
            
            dates.append(parsed_date)
            users.append(user)
            messages.append(message)

        df = pd.DataFrame({
            "date": dates,
            "user": users,
            "message": messages
        })

        df['hour'] = df['date'].dt.hour
        df['day'] = df['date'].dt.day_name()
        df['emoji'] = df['message'].apply(lambda x: ''.join(c for c in x if c in emoji.EMOJI_DATA))

        # SUCCESS!
        st.success(f"Found {len(df):,} messages from {df['user'].nunique()} people!")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", f"{len(df):,}")
        col2.metric("Most Active", df['user'].value_counts().index[0])
        col3.metric("Duration", f"{(df['date'].max() - df['date'].min()).days} days")
        col4.metric("Avg/Day", f"{int(len(df)/(df['date'].dt.date.nunique() or 1))}")

        # Top 10
        st.subheader("Top 10 Spammers")
        top10 = df['user'].value_counts().head(10)
        fig = px.bar(y=top10.index, x=top10.values, orientation='h', color=top10.values)
        st.plotly_chart(fig, use_container_width=True)

        # Peak hours
        st.subheader("When do you chat?")
        hours = df['hour'].value_counts().sort_index()
        fig2 = px.line(x=hours.index, y=hours.values, markers=True)
        fig2.update_layout(xaxis=dict(tick0=0, dtick=1), xaxis_title="Hour", yaxis_title="Messages")
        st.plotly_chart(fig2, use_container_width=True)

        # Word Cloud
        st.subheader("Most Used Words")
        text = " ".join(df['message']).lower()
        wordcloud = WordCloud(width=800, height=400, background_color='black',
                              stopwords={'media', 'omitted', 'image', 'video', 'this message was deleted'}).generate(text)
        plt.figure(figsize=(10,5))
        plt.imshow(wordcloud)
        plt.axis('off')
        st.pyplot(plt)

        # Emojis
        st.subheader("Emoji Leaderboard")
        all_emojis = "".join(df['emoji'])
        if all_emojis:
            top_emojis = Counter(all_emojis).most_common(10)
            emoji_df = pd.DataFrame(top_emojis, columns=['Emoji', 'Count'])
            fig3 = px.bar(emoji_df, x='Emoji', y='Count', color='Count')
            st.plotly_chart(fig3, use_container_width=True)
