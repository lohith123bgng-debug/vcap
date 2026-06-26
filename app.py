import streamlit as st
import google.generativeai as genai
import tempfile
import time

# Page configuration
st.set_page_config(page_title="AI Video Caption Generator", page_icon="🎬", layout="centered")

st.title("🎬 AI Video Caption & Hashtag Generator")
st.write("Upload your video and get matching captions and trending hashtags using Gemini 1.5 Flash AI!")

# Get API key from Streamlit secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found in settings! Please add GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Video Uploader
uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    # Button to generate captions
    if st.button("✨ Generate Captions & Hashtags", type="primary"):
        with st.spinner("🤖 AI is watching your video... Please wait..."):
            try:
                # Save uploaded file to a temporary file because Gemini API needs a file path or bytes
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name

                # Upload to Gemini File API
                st.info("Uploading video to Gemini AI Studio...")
                video_file = genai.upload_file(path=tmp_file_path)
                
                # Wait for video processing
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    raise Exception("Video processing failed on Gemini servers.")

                # Prompt for the AI
                prompt = (
                    "Watch this video carefully. Generate 3 creative, engaging, and catchy social media captions "
                    "(appropriate for Instagram/Reels/TikTok) based on the visual content, actions, and mood of the video. "
                    "Also, provide a set of 10 highly relevant and trending hashtags. Format the output beautifully with emojis."
                )

                # Initialize model and generate content
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                response = model.generate_content([video_file, prompt])

                # Clear video from Gemini server after processing
                genai.delete_file(video_file.name)

                # Display Results
                st.success("🎉 Done!")
                st.subheader("📝 Generated Captions & Hashtags")
                st.write(response.text)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
