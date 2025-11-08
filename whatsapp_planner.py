# app.py - ULTIMATE WhatsApp Chat Analyzer 2025+ (PDF Export + Time Labels)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from datetime import datetime
import base64
from io import BytesIO

# PDF Generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(page_title="WhatsApp Analyzer Pro", page_icon="Chart", layout="wide")

# Title
st.title("WhatsApp Chat Analyzer Pro")
st.markdown("**Export chats → Get deep insights → Download PDF report**")

# File uploader
uploaded_file = st.file_uploader("Upload WhatsApp Chat.txt (export without media)", type="txt")

def parse_chat(data):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2}) - (.*?): (.*)'
    matches = re.findall(pattern, data)
    
    dates, users, messages = [], [], []
    for match in matches:
        dt_str = match[0]
        user = match[1]
        msg = match[2]
        
        try:
            dt = datetime.strptime(dt_str, "%m/%d/%y, %I:%M %p")
        except:
            try:
                dt = datetime.strptime(dt_str, "%d/%m/%y, %I:%M %p")
            except:
                continue
        
        dates.append(dt)
        users.append(user)
        messages.append(msg)
    
    df = pd.DataFrame({"date": dates, "user": users, "message": messages})
    df['hour'] = df['date'].dt.hour
    df['time_12h'] = df['date'].dt.strftime("%I:%M %p")
    df['day'] = df['date'].dt.day_name()
    df['date_only'] = df['date'].dt.date
    
    # Part of day
    def get_part_of_day(h):
        if 5 <= h < 12:
            return "Morning (5AM-12PM)"
        elif 12 <= h < 17:
            return "Afternoon (12PM-5PM)"
        elif 17 <= h < 21:
            return "Evening (5PM-9PM)"
        else:
            return "Night (9PM-5AM)"
    
    df['part_of_day'] = df['hour'].apply(get_part_of_day)
    df['emoji'] = df['message'].apply(lambda x: ''.join(c for c in x if c in emoji.EMOJI_DATA))
    
    return df

def create_pdf_report(df, figs):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("WhatsApp Chat Analysis Report", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Total Messages: {len(df):,}", styles['Normal']))
    story.append(Paragraph(f"Active Users: {df['user'].nunique()}", styles['Normal']))
    story.append(Paragraph(f"Duration: {(df['date'].max() - df['date'].min()).days} days", styles['Normal']))
    story.append(Spacer(1, 20))
    
    for i, fig in enumerate(figs):
        img_data = BytesIO()
        fig.write_image(img_data, format="PNG")
        img_data.seek(0)
        story.append(Image(img_data, width=500, height=300))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    return buffer.getvalue()

if uploaded_file:
    data = uploaded_file.read().decode("utf-8", errors="ignore")
    df = parse_chat(data)
    
    if len(df) == 0:
        st.error("No messages found! Make sure you exported chat WITHOUT media.")
        st.stop()
    
    st.success(f"Analyzed {len(df):,} messages from {df['user'].nunique()} users!")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Messages", f"{len(df):,}")
    col2.metric("Most Active", df['user'].value_counts().head(1).index[0])
    col3.metric("Duration", f"{(df['date'].max() - df['date'].min()).days} days")
    col4.metric("Avg/Day", f"{int(len(df)/df['date_only'].nunique())}")
    
    # === CHARTS WITH LABELS ===
    st.subheader("Most Active Users")
    top10 = df['user'].value_counts().head(10)
    fig1 = px.bar(y=top10.index, x=top10.values, orientation='h',
                  text=top10.values, color=top10.values)
    fig1.update_traces(textposition='outside')
    fig1.update_layout(height=500, xaxis_title="Messages", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("Most Active Time of Day")
    part_counts = df['part_of_day'].value_counts()
    fig2 = px.pie(values=part_counts.values, names=part_counts.index,
                  color_discrete_sequence=px.colors.sequential.Plasma)
    fig2.update_traces(textinfo='percent+label+value')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Peak Hours (12-Hour Format)")
    hour_counts = df['time_12h'].value_counts().head(15)
    fig3 = px.bar(x=hour_counts.index, y=hour_counts.values,
                  text=hour_counts.values, color=hour_counts.values)
    fig3.update_traces(textposition='outside')
    fig3.update_layout(xaxis_title="Time", yaxis_title="Messages", height=500)
    st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("Word Cloud")
    text = " ".join(df['message']).lower()
    wordcloud = WordCloud(width=800, height=400, background_color='black',
                          stopwords={'media', 'omitted', 'image', 'video', 'deleted'}).generate(text)
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud)
    plt.axis('off')
    wordcloud_fig = plt
    st.pyplot(plt)
    
    st.subheader("Top Emojis")
    all_emojis = "".join(df['emoji'])
    if all_emojis:
        top_emojis = Counter(all_emojis).most_common(10)
        emoji_df = pd.DataFrame(top_emojis, columns=['Emoji', 'Count'])
        fig4 = px.bar(emoji_df, x='Emoji', y='Count', text='Count', color='Count')
        fig4.update_traces(textposition='outside')
        st.plotly_chart(fig4, use_container_width=True)
    
    # === PDF EXPORT ===
    if st.button("Export Full Report as PDF"):
        with st.spinner("Generating PDF..."):
            figs = [fig1, fig2, fig3, fig4]
            pdf_data = create_pdf_report(df, figs)
            
            b64 = base64.b64encode(pdf_data).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="WhatsApp_Analysis_Report.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("PDF Ready! Click above to download")
