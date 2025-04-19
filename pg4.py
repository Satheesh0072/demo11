import streamlit as st
import pandas as pd
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

# Load emotion data
emotion_df = pd.read_csv("emotion_lookup_table.csv")

st.set_page_config(page_title="Emotion Voice Chatbot", layout="centered")
st.title("🧠 Emotion Voice-Based Assistant")
st.caption("🎙️ Talk to the bot or select an emotion and then click Submit.")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_emotion" not in st.session_state:
    st.session_state.selected_emotion = None

# Voice Input Function
def listen_to_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Please speak your emotion.")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            st.success(f"You said: {text}")
            return text.capitalize()
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand your voice.")
        except sr.RequestError:
            st.error("Network error. Try again.")
    return None

# Voice Output Function
def speak_response(text):
    tts = gTTS(text)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmpfile.name)
    tmpfile.close()
    st.audio(tmpfile.name, format="audio/mp3")
    os.remove(tmpfile.name)

# Voice Input Button (outside form)
if st.button("🎤 Use Voice Input"):
    voice_emotion = listen_to_user()
    if voice_emotion and voice_emotion in emotion_df["Emotion"].values:
        st.session_state.selected_emotion = voice_emotion
    else:
        st.warning("Emotion not recognized. Try again or use dropdown.")

# Dropdown + Submit form
with st.form("input_form"):
    selected = st.selectbox("⬇️ Or select an emotion", ["Choose..."] + list(emotion_df["Emotion"]))
    if selected != "Choose...":
        st.session_state.selected_emotion = selected

    submit = st.form_submit_button("✅ Submit")

# Response logic
if submit and st.session_state.selected_emotion:
    emotion = st.session_state.selected_emotion
    row = emotion_df[emotion_df["Emotion"] == emotion].iloc[0]
    suggestion = row["Suggested Action"]
    explanation = row["Psychological Insight"]

    user_msg = f"**User:** I feel {emotion.lower()}."
    bot_msg = f"**Assistant:** You can try: **{suggestion}**\n\n_Why this helps_: {explanation}"
    st.session_state.chat_history.append((user_msg, bot_msg))

    speak_response(f"You can try: {suggestion}. Because {explanation}")

# Display chat
st.subheader("🗨️ Chat History")
for user_msg, bot_msg in st.session_state.chat_history[::-1]:
    st.markdown(user_msg)
    st.markdown(bot_msg)
    st.markdown("---")

# Export option
if st.session_state.chat_history:
    history_df = pd.DataFrame(st.session_state.chat_history, columns=["User", "Assistant"])
    st.download_button("📥 Download Chat History", data=history_df.to_csv(index=False),
                       file_name="emotion_chat_history.csv", mime="text/csv")
