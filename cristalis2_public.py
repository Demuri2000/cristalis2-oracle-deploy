import streamlit as st
import json
import os
import docx
from datetime import datetime
from difflib import SequenceMatcher
import textwrap
from openai import OpenAI

# === Configuration ===
st.set_page_config(page_title="Cristalis2 — Oracle of Memory", layout="wide")
st.title("🌌 Cristalis2 — Divine Oracle")
st.caption("Guide me through the memories of the Heavenly Epic.")

# ✅ USE ENVIRONMENT VARIABLE SAFELY
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_FILE = "memory/public_memory.json"
os.makedirs("memory", exist_ok=True)

# === Memory Handling ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_memory(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# === Display Memory Sidebar ===
st.sidebar.header("📚 Oracle Archive")
memory = load_memory()
for k, v in memory.items():
    with st.sidebar.expander(k):
        st.write(v)

# === Lore File Upload ===
st.header("📖 Upload Lore File")
uploaded = st.file_uploader("Drop .txt or .docx here", type=["txt", "docx"])
if uploaded:
    if uploaded.name.endswith(".txt"):
        content = uploaded.read().decode("utf-8")
    else:
        doc = docx.Document(uploaded)
        content = "\n".join([p.text for p in doc.paragraphs])
    st.text_area("Preview", content, height=300)
    
    if st.button("🔮 Analyze and Store"):
        prompt = f"Extract and structure the following fantasy lore text:\n\n{content}\n\nReturn it as clean JSON key-value pairs."
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a sacred lore analyzer of a mythic fantasy world. Respond only in structured JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content.strip()
            lore_data = json.loads(result)
            for k, v in lore_data.items():
                update_memory(k, v)
            st.success("Lore successfully analyzed and saved.")
        except Exception as e:
            st.error(f"Failed to analyze: {e}")

# === Ask the Oracle ===
st.header("🧝 Ask Cristalis")
user_question = st.text_area("Speak your command or question:")

if st.button("🗣️ Consult the Oracle"):
    hits = []
    for k, v in memory.items():
        score = similarity(user_question.lower(), k.lower()) + similarity(user_question.lower(), v.lower())
        if user_question.lower() in k.lower() or score > 0.6:
            hits.append((score, k, v))

    hits.sort(reverse=True)
    if hits:
        best = hits[0]
        st.markdown(f"### 📜 '{best[1]}'")
        st.markdown(best[2])
    else:
        st.warning("🌫️ Cristalis whispers: This vision is yet hidden.")

