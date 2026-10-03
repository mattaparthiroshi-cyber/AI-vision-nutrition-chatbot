import os
import urllib.parse
import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="AI Vision Nutrition Chatbot",
    page_icon="🥗",
    layout="centered"
)

# 2. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY dorakaledhu! .env file check cheyyandi.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "image_analyzed" not in st.session_state:
    st.session_state.image_analyzed = False
if "latest_summary" not in st.session_state:
    st.session_state.latest_summary = ""

# Header
st.title("🥗 AI Vision Nutrition Chatbot")
st.caption("Upload your meal photo, receive nutrition metrics, chat, and share to WhatsApp instantly!")

# 4. Meal Image Upload Section
uploaded_file = st.file_uploader("Upload a photo of your meal (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Meal", use_container_width=True)

    if not st.session_state.image_analyzed:
        if st.button("🔍 Analyze Meal & Nutrition", type="primary"):
            with st.spinner("Gemini AI mee meal ni analyze chesthondi..."):
                prompt = """
                You are an expert AI Nutritionist. 
                Analyze the meal in the image and provide:
                1. 🍲 Food Items Identified
                2. 🔥 Estimated Total Calories
                3. 📊 Macronutrients Breakdown (Protein, Carbs, Fats)
                4. 💡 Quick Health Verdict / Diet Advice
                Format the answer cleanly using markdown and bullet points.
                """
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=[prompt, img]
                    )
                    analysis_text = response.text
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": analysis_text
                    })
                    st.session_state.image_analyzed = True
                    st.session_state.latest_summary = analysis_text
                    st.rerun()
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")

# 5. Display Conversation History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Direct WhatsApp Share Section
if st.session_state.image_analyzed:
    st.markdown("---")
    st.subheader("📲 Send / Share to WhatsApp")
    
    phone_number = st.text_input(
        "Mee WhatsApp Number enter cheyyandi (with country code):",
        value="+919110526999",
        help="Country code tho paatu enter cheyyandi (e.g. +91XXXXXXXXXX)"
    )

    clean_phone = phone_number.replace("+", "").replace(" ", "").strip()
    
    # Message formatting for WhatsApp
    wa_text = f"🥗 *AI Vision Nutrition Report*\n\n{st.session_state.latest_summary}\n\n_Generated via AI Vision Nutrition Bot_"
    encoded_text = urllib.parse.quote(wa_text)
    
    wa_url = f"https://wa.me/{clean_phone}?text={encoded_text}"
    
    st.link_button("👉 Open in WhatsApp & Send Report", wa_url, type="primary")

    # Follow-up Chat Input
    user_question = st.chat_input("Ask a follow-up question about this meal...")
    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_context = "You are an expert AI Nutritionist helping the user with their analyzed meal.\n"
                for m in st.session_state.messages:
                    chat_context += f"{m['role'].capitalize()}: {m['content']}\n"
                
                try:
                    chat_response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=[chat_context]
                    )
                    reply = chat_response.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error generating reply: {e}")