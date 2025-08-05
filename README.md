# VisionVerseAI

# 🚦 VisionVerseAI - Visual Understanding Chat Assistant

**VisionVerseAI** is an agentic chat assistant that analyzes short video clips (up to 2 minutes), recognizes important events, summarizes them, and allows users to have natural, multi-turn conversations about what occurred in the video.

---

## 📌 Project Overview

The core goal of VisionVerseAI is to demonstrate a functional prototype of a visual understanding system that can:

- Accept video input
- Detect key events like vehicle motion, pedestrian crossings, and traffic signals
- Summarize those events with timestamps and guideline adherence/violations
- Allow multi-turn chat-based interaction with memory of past queries

🛠️ This solution highlights how AI can support real-time decision-making by extracting actionable insights from video content.

---

## 🧱 Architecture Diagram

Below is a high-level diagram that illustrates the key components of VisionVerseAI and their interaction.

<img src="https://github.com/user-attachments/assets/398fd3aa-86a6-4d82-9eaf-027367fbd3ea" alt="Architecture Diagram" width="600"/>

**Explanation:**

1. **Frontend (HTML/CSS/JS)** – Takes video input and allows users to chat  
2. **Backend (Flask)** – Handles video processing, chat logic, and state  
3. **Frame Extractor (OpenCV)** – Converts video into frames  
4. **Event Detection Module** – Detects objects/events from frames  
5. **Summarization Engine** – Produces a textual summary  
6. **Conversation Handler** – Maintains multi-turn context for queries  
7. **Chat Interface** – Displays summary and handles user interactions

---

## 🧠 Tech Stack Justification

| Component         | Technology             | Justification |
|------------------|-------------------------|----------------|
| **Backend**       | Python + Flask          | Fast prototyping, RESTful API support |
| **Frontend**      | HTML, CSS, JavaScript   | Lightweight UI to upload videos and chat |
| **Video Processing** | OpenCV              | Powerful library for real-time computer vision tasks |
| **Event/Violation Detection** | Rule-based + Visual Parsing | Custom logic and frame-level parsing to highlight red light violations, crossings |
| **Chat Handling** | Python logic            | Retains chat history for multi-turn interactions |
| **Deployment**    | Localhost / Flask Server| Simple to run and test locally |

---

## ⚙️ Setup and Installation Instructions

### 🔧 Clone the repository
```bash
git clone https://github.com/saipraneeth88/VisionVerseAI.git
cd VisionVerseAI
```

## 🐍 Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

## Create a .env file in the project root with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## 📦 Install dependencies
pip install -r requirements.txt

## ▶️ Run the application
python app.py

The application will be available at `http://localhost:5000`

## 💬 Usage Instructions

### 1️⃣ Upload a video (Max 2 minutes)

- Allowed formats: `.mp4`
- Example: Upload a traffic video showing cars at a signal

### 2️⃣ System will:

- Extract frames from the video using OpenCV
- Detect events like:
  - Vehicles crossing stop line
  - Pedestrians crossing
  - Traffic light changes
- Generate a **natural language summary** with timestamped violations

### 3️⃣ Ask follow-up questions in the chat window:

#### 💡 Examples:

- “What happened at 00:15?”
- “Did any vehicle run a red light?”
- “Was there a pedestrian crossing?”
- “Who violated traffic rules?”

The assistant will respond based on video summary context and chat history.

---

## 📹 Demo Video

## 📺 Watch our demo here:  
👉 [Demo Link (Google Drive)](https://drive.google.com/file/d/1namVG2kEP4Fy2VfdSG4Rz15GIuaSdHN1/view?usp=sharing&t=2)

## 📁 Folder Structure

```
VisionVerseAI/
├── app.py                      # Flask backend
├── templates/
│   └── index.html              # Frontend
├── static/
│   ├── css/                    # Chat & UI styling
│   ├── js/                     # Chatbot interaction
│   └── frames/                 # Extracted video frames
├── temp_video.mp4              # Temp storage for uploaded video
├── requirements.txt            # Python dependencies
├── architecture_diagram.png    # Architecture image (upload manually)
└── README.md                   # This file
```


## 🙋 Contact
Gorla Sai Praneeth Reddy - saipraneeth1806@gmail.com  
Polisetty Surya Teja - suryateja2031@gmail.com  
Nabajyoti Chandra Deb - nabadeb2017@gmail.com
