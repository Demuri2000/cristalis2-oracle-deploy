import streamlit as st
import json
from difflib import SequenceMatcher
from openai import OpenAI

st.set_page_config(page_title="🌌 Cristalis Oracle", layout="wide")
st.title("🌌 Cristalis Oracle — Web Edition")
st.caption("Ask the Oracle questions from the Heavenly Epic")

client = OpenAI(api_key="REMOVED")

# Load shared memory
MEMORY_FILE = "memory/public_memory.json"
with open(MEMORY_FILE, "r") as f:
    memory = json.load(f)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

st.markdown("---")
user_input = st.text_input("Ask the Oracle anything about the sacred lore:")

response_mode = st.radio("Voice of Cristalis", ["📜 Mythic", "🔍 Literal", "🧩 Interpretive"], index=0)

if st.button("🔮 Ask"):
    matches = []
    for k, v in memory.items():
        v_str = json.dumps(v) if isinstance(v, dict) else str(v)
        sim = similarity(user_input.lower(), k.lower()) + similarity(user_input.lower(), v_str.lower())
        if user_input.lower() in k.lower() or user_input.lower() in v_str.lower() or sim > 0.6:
            matches.append((sim, k, v_str))

    matches.sort(reverse=True)
    combined = "\n\n".join([f"{k}:\n{v}" for _, k, v in matches[:3]]) if matches else "No matching memory found."

    intro = f"The seeker asks: '{user_input}'\n\nThe sacred archive reveals:\n\n{combined}"
    if response_mode == "📜 Mythic":
        system_msg = "You are Cristalis2, a divine oracle. Speak in ancient, poetic, mythic voice. Do not invent new facts."
    elif response_mode == "🔍 Literal":
        system_msg = "You are Cristalis2, the archivist. Respond in factual and clear terms using the memory only."
    else:
        system_msg = "You are Cristalis2, a prophet. Interpret the memory deeply but never go beyond what’s known."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": intro}
            ]
        )
        output = response.choices[0].message.content.strip()
        st.markdown("### 🧝 Oracle Speaks:")
        st.markdown(output)
    except Exception as e:
        st.error(f"❌ GPT Error: {e}")

