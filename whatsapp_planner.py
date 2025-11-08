# app.py - WhatsApp Analyzer PRO v7 (ANDROID + IPHONE 100% FIXED)
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from datetime import datetime
import base64
from io import BytesIO

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

st.set_page_config(page_title="WhatsApp Analyzer PRO", page_icon="WhatsApp", layout="wide")

# CSS
st.markdown("""
<style>
    .big-font {font-size:50px !important; font-weight:bold; color:#FF6B6B;}
    .step-box {background-color:#262730; padding:20px; border-radius:12px; border-left:6px solid #FF4B4B;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">WhatsApp Analyzer PRO</p>', unsafe_allow_html=True)
st.markdown("**Works 100% with Android & iPhone • Made by Aayush Nayak**")

with st.expander("How to Export Chat (Android & iPhone)", expanded=True):
    st.markdown("""
    <div class="step-box">
    <strong>Step 1:</strong> Open WhatsApp → Chat → 3 dots → More → Export chat<br>
    <strong>Step 2:</strong> Choose <strong>Without Media</strong><br>
    <strong>Step 3:</strong> Save file → Upload here!
    </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("**Upload your WhatsApp chat.txt**", type="txt")

def parse_whatsapp_chat(text):
    dates, users, messages = [], [], []
    
    # SUPER ROBUST REGEX - WORKS WITH ALL FORMATS
    patterns = [
        # iPhone: [8/6/25, 19:48:10] Leisha: hello
        r'\[(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:\d{2})\] (.*?): (.*)',
        
        # Android - ALL POSSIBLE VARIATIONS
        r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} ?[APMapm]{2}) - (.*?): (.*)',  # space or no space after :
        r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [APMapm]{2}) - (.*?): (.*)',
        r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}[APMapm]{2}) - (.*?): (.*)',
    ]
    
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        matched = False
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                date_str = match.group(1)
                user = match.group(2).strip()
                msg = match.group(3).strip()
                
                # Parse date - TRY ALL FORMATS
                parsed = False
                for fmt in [
                    "%d/%m/%y, %H:%M:%S", "%m/%d/%y, %H:%M:%S",
                    "%d/%m/%Y, %H:%M:%S", "%m/%d/%Y, %H:%M:%S",
                    "%d/%m/%y, %I:%M %p", "%m/%d/%y, %I:%M %p",
                    "%d/%m/%y, %I:%M%p", "%m/%d/%y, %I:%M%p"
                ]:
                    try:
                        dt = datetime.strptime(date_str.strip(), fmt)
                        dates.append(dt)
                        users.append(user)
                        messages.append(msg)
                        parsed = True
                        matched = True
                        break
                    except:
                        continue
                if parsed:
                    break
        
        # Multi-line message continuation
        if matched:
            i += 1
            while i < len(lines) and not re.match(r'\d{1,2}/\d{1,2}/\d{2,4},', lines[i]) and not re.match(r'\[\d{1,2}/', lines[i]):
                if messages:
                    messages[-1] += " " + lines[i].strip()
                i += 1
            continue
            
        i += 1
    
    if not dates:
        return None
    
    df = pd.DataFrame({'date': dates, 'user': users, 'message': messages})
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = df['date'].dt.hour
    df['time_12h'] = df['date'].dt.strftime("%I:%M %p")
    df['day'] = df['date'].dt.day_name()
    df['date_only'] = df['date'].dt.date
    
    def part_of_day(h):
        if 5 <= h < 12: return "Morning (5AM-12PM)"
        if 12 <= h < 17: return "Afternoon (12PM-5PM)"
        if 17 <= h < 21: return "Evening (5PM-9PM)"
        return "Night (9PM-5AM)"
    
    df['part_of_day'] = df['hour'].apply(part_of_day)
    df['emoji'] = df['message'].apply(lambda x: ''.join(c for c in x if c in emoji.EMOJI_DATA))
    
    return df

# PDF function (same as before)
def create_pdf(df, figs):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("WhatsApp Chat Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    summary = [
        ["Total Messages", f"{len(df):,}"],
        ["Users", df['user'].nunique()],
        ["Most Active", df['user'].value_counts().index[0]],
        ["Duration", f"{(df['date'].max() - df['date'].min()).days} days"]
    ]
    table = Table(summary)
    table.setStyle([('GRID', (0,0), (-1,-1), 1, colors.grey)])
    story.append(table)
    story.append(Spacer(1, 20))
    
    for fig, title in zip(figs, ["Top Users", "Time of Day", "Peak Hours", "Emojis", "Word Cloud"]):
        img_data = BytesIO()
        if hasattr(fig, 'write_image'):
            fig.write_image(img_data, format="PNG")
        else:
            fig.savefig(img_data, format='PNG', bbox_inches='tight')
            plt.close()
        img_data.seek(0)
        story.append(Image(img_data, width=500, height=300))
        story.append(Paragraph(title, styles['Heading3']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    return buffer.getvalue()

# MAIN
if uploaded_file:
    raw = uploaded_file.read().decode("utf-8", errors="ignore")
    df = parse_whatsapp_chat(raw)
    
    if df is None or len(df) == 0:
        st.error("No messages found! Try exporting again WITHOUT media.")
        st.stop()
    
    st.success(f"Analyzed {len(df):,} messages from {df['user'].nunique()} people!")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Messages", f"{len(df):,}")
    col2.metric("Most Active", df['user'].value_counts().head(1).index[0])
    col3.metric("Duration", f"{(df['date'].max()-df['date'].min()).days} days")
    col4.metric("Avg/Day", f"{int(len(df)/df['date_only'].nunique())}")
    
    # Charts
    fig1 = px.bar(y=df['user'].value_counts().head(10).index, 
                  x=df['user'].value_counts().head(10).values, 
                  orientation='h', text=df['user'].value_counts().head(10).values)
    fig1.update_traces(textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.pie(values=df['part_of_day'].value_counts().values, 
                  names=df['part_of_day'].value_counts().index)
    fig2.update_traces(textinfo='percent+label+value')
    st.plotly_chart(fig2, use_container_width=True)
    
    fig3 = px.bar(x=df['time_12h'].value_counts().head(15).index, 
                  y=df['time_12h'].value_counts().head(15).values,
                  text=df['time_12h'].value_counts().head(15).values)
    st.plotly_chart(fig3, use_container_width=True)
    
    wc = WordCloud(width=800, height=400, background_color='black').generate(" ".join(df['message']))
    plt.figure(figsize=(10,5), facecolor='black')
    plt.imshow(wc)
    plt.axis('off')
    wordcloud_fig = plt
    st.pyplot(plt)
    
    # PDF
    if st.button("Download PDF Report", type="primary"):
        with st.spinner("Generating PDF..."):
            figs = [fig1, fig2, fig3, wordcloud_fig]
            pdf = create_pdf(df, figs)
            b64 = base64.b64encode(pdf).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="WhatsApp_Report.pdf">Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.balloons()

else:
    st.info("Upload your chat file to begin!")
