# WhatsApp Chat Analyzer

**Instant online version (Streamlit):**  
https://whatsappproanalyze.streamlit.app/

**Your own 24×7 AWS cloud version (Fargate - serverless):**  
http://13.49.125.74:8501/

---

## 📊 What Does This Project Do?

WhatsApp Chat Analyzer is a powerful tool that transforms your WhatsApp chat exports into comprehensive visual analytics and insights. Upload any WhatsApp chat export file and get:

- **📈 Detailed Statistics**: Total messages, words, media shared, links, and more
- **☁️ Word Clouds**: Visual representation of most-used words by each participant
- **😂 Emoji Analysis**: Emoji usage statistics and battles between participants
- **📅 Timeline Insights**: Activity patterns over time, busiest days and months
- **⏰ Active Hours**: Heatmap showing when conversations are most active
- **👥 Contributor Analysis**: Who sends the most messages, words, and media
- **📄 PDF Report**: Downloadable comprehensive report with all analytics

---

## 🛠️ Technology Stack

### Frontend & Processing
- **Streamlit** - Web interface and interactive dashboards
- **Pandas** - Data manipulation and analysis
- **Matplotlib** - Static visualizations and charts
- **Seaborn** - Statistical data visualization
- **Plotly** - Interactive plots and graphs

### Text & Emoji Processing
- **Emoji** - Emoji extraction and analysis
- **urlextract** - URL detection from messages
- **WordCloud** - Word cloud generation

### PDF Generation
- **FPDF** - PDF report creation

### Deployment
- **Docker** - Containerization for consistent environments
- **AWS ECR** - Container image storage
- **AWS ECS Fargate** - Serverless container orchestration
- **Python 3.11** - Base runtime environment

---

## 🔍 How It Works

1. **Upload**: User uploads WhatsApp chat export (`.txt` file)
2. **Parse**: Application parses the chat format (supports multiple date formats)
3. **Extract**: Extracts messages, timestamps, users, emojis, URLs, and media references
4. **Analyze**: Processes data to generate statistics and insights
5. **Visualize**: Creates interactive charts, word clouds, and heatmaps
6. **Generate**: Compiles everything into a downloadable PDF report

---

## How to Use (30 seconds)

1. Open WhatsApp → any chat (personal or group)
2. Tap contact/group name → **Export chat** → **Without media**
3. Save the `.txt` file
4. Upload here → get beautiful PDF report + word clouds + emoji battles + active hours + more!
5. Roast your friends

---

## I Hosted This on AWS in 27 Minutes (100% Replicable)

### 1. Local Files

```
whatsapp-docker/
├── app.py              ← Full Streamlit code
├── requirements.txt    ← 9 exact packages
└── Dockerfile          ← python:3.11-slim + plot libraries
```

### 2. Build Docker Image (1 click)

- Open folder in **VS Code**
- Install **Docker** extension
- Right-click `Dockerfile` → **Build Image…**
- Tag: `whatsappdocker:latest`

### 3. AWS ECR – Store Image Forever

1. AWS Console → ECR → **Create repository**
2. Visibility: **Private**
3. Name: `whatsapp-analyzer` → Create

### 4. Push Image (PowerShell – 4 lines)

```powershell
aws configure
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin YOUR-ACCOUNT.dkr.ecr.eu-north-1.amazonaws.com
docker tag whatsappdocker:latest YOUR-ACCOUNT.dkr.ecr.eu-north-1.amazonaws.com/whatsapp-analyzer:latest
docker push YOUR-ACCOUNT.dkr.ecr.eu-north-1.amazonaws.com/whatsapp-analyzer:latest
```

### 5. ECS Fargate – Go Live (5 clicks)

1. **Cluster** → Fargate → Name: `whatsapp-cluster`
2. **Task Definition** → Name: `whatsapp-task` → Image: your ECR URI → Port: `8501` → CPU: `0.5 vCPU` | Memory: `1 GB`
3. **Service** → Name: `whatsapp-live` → Tasks: `1` → Public IP: `ENABLED` → Subnets: `ALL 6` → Security group: `TCP 8501` → `0.0.0.0/0`

### 6. Live URL

- Tasks tab → wait for `RUNNING`
- Click task → copy Public IP
- `http://YOUR-IP:8501` → **LIVE WORLDWIDE!**

**First load:** 30–40 sec (cold start)  
**After that:** instant forever

