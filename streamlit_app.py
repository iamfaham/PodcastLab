import streamlit as st
import os
import time
import uuid
import base64
import io
from datetime import datetime, timedelta
from pathlib import Path
from main import PodcastAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PodcastLab",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .loading-spinner {
        text-align: center;
        padding: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def create_download_link(file_data, filename, mime_type):
    """Create a download link for file data."""
    b64 = base64.b64encode(file_data).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href


def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🎙️ PodcastLab</h1>
        <p>AI-powered podcast creator using Google's Imagen, Gemini, and Veo models</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Initialize session state for file storage
    if "generated_files" not in st.session_state:
        st.session_state.generated_files = {}

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        api_key = st.text_input(
            "Google AI API Key",
            type="password",
            help="Enter your Google AI API key. You can also set it as GOOGLE_AI_API_KEY environment variable.",
            value=os.getenv("GOOGLE_AI_API_KEY", ""),
        )

        if not api_key:
            st.warning("⚠️ Please enter your Google AI API key to use the application.")
            return

        st.markdown("---")
        st.markdown("### 📋 Instructions")
        st.markdown(
            """
        1. Enter a topic for your podcast episode
        2. Click 'Generate Podcast' to start the process
        3. Wait for the AI to generate the image, script, and video
        4. View and download your generated content
        """
        )

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown(
            """
        This app uses:
        - **Imagen** for image generation
        - **Gemini** for script generation  
        - **Veo 3** for video generation
        """
        )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🎯 Create Your Podcast Episode")

        # Topic input
        topic = st.text_input(
            "Enter the topic for your podcast episode:",
            placeholder="e.g., The Future of Artificial Intelligence",
            help="Enter any topic you'd like to create a podcast episode about",
        )

        # Search grounding toggle
        use_search = st.checkbox(
            "🔍 Use Google Search for factual data",
            value=False,
            help="Enable this to have Gemini search the web for current, factual information about your topic. This will make the podcast more accurate and up-to-date.",
        )

        # Generate button
        generate_button = st.button(
            "🎬 Generate Podcast", type="primary", disabled=not topic.strip()
        )

        if generate_button and topic.strip():
            # Initialize the agent
            try:
                agent = PodcastAgent(api_key=api_key)

                # Create progress containers
                progress_container = st.container()
                status_container = st.container()
                result_container = st.container()

                with progress_container:
                    st.markdown("### 🚀 Generation Progress")
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                # Step 1: Generate image
                with status_container:
                    status_text.text("🖼️ Step 1/5: Generating podcast image...")
                    progress_bar.progress(10)

                try:
                    # Generate unique ID for this session
                    unique_id = str(uuid.uuid4())[:8]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    session_key = f"{timestamp}_{unique_id}"

                    image = agent.generate_podcast_image()
                    progress_bar.progress(20)

                    # Step 2: Generate script (3 parts)
                    status_text.text("📝 Step 2/5: Generating 3-part podcast script...")
                    progress_bar.progress(30)

                    script_parts, grounding_metadata = agent.generate_podcast_script(
                        topic, use_search
                    )
                    progress_bar.progress(40)

                    # Step 3: Generate 3 individual videos
                    status_text.text("🎬 Step 3/5: Generating 3 individual videos...")
                    progress_bar.progress(50)

                    # For HF Spaces, we'll generate videos in memory
                    video_data_list = []
                    for i, script_part in enumerate(script_parts, 1):
                        status_text.text(f"🎬 Generating video part {i}/3...")
                        try:
                            # Generate video to temporary location
                            temp_video_path = f"/tmp/temp_video_{i}.mp4"
                            video_path = agent.generate_podcast_video(
                                script=script_part,
                                image=image,
                                output_filename=temp_video_path,
                            )

                            # Read video data into memory
                            with open(video_path, "rb") as f:
                                video_data = f.read()
                            video_data_list.append(video_data)

                            # Clean up temp file
                            os.remove(video_path)

                        except Exception as e:
                            st.error(f"Failed to generate video part {i}: {e}")
                            raise

                    progress_bar.progress(70)

                    # Step 4: Combine videos
                    status_text.text(
                        "🔗 Step 4/5: Combining videos into final 24-second video..."
                    )
                    progress_bar.progress(80)

                    # For HF Spaces, we'll combine videos in memory
                    try:
                        from moviepy import VideoFileClip, concatenate_videoclips
                        import tempfile

                        # Create temporary files for combining
                        temp_files = []
                        clips = []

                        for i, video_data in enumerate(video_data_list):
                            # Create temporary file
                            temp_file = tempfile.NamedTemporaryFile(
                                suffix=f"_part_{i}.mp4", delete=False
                            )
                            temp_file.write(video_data)
                            temp_file.close()
                            temp_files.append(temp_file.name)

                            # Load as video clip
                            clip = VideoFileClip(temp_file.name)
                            clips.append(clip)

                        # Combine videos
                        final_clip = concatenate_videoclips(clips)

                        # Write to bytes
                        final_video_buffer = io.BytesIO()
                        final_clip.write_videofile(
                            final_video_buffer,
                            codec="libx264",
                            audio_codec="aac",
                            temp_audiofile="temp-audio.m4a",
                            remove_temp=True,
                            verbose=False,
                            logger=None,
                        )

                        final_video_data = final_video_buffer.getvalue()

                        # Clean up
                        for clip in clips:
                            clip.close()
                        final_clip.close()

                        for temp_file in temp_files:
                            os.unlink(temp_file)

                    except Exception as e:
                        st.error(f"Failed to combine videos: {e}")
                        # Fallback: use first video
                        final_video_data = (
                            video_data_list[0] if video_data_list else b""
                        )

                    progress_bar.progress(90)

                    # Step 5: Save image to memory
                    status_text.text("💾 Step 5/5: Preparing files for download...")
                    progress_bar.progress(95)

                    # Convert image to bytes
                    img_buffer = io.BytesIO()
                    image.save(img_buffer, format="PNG")
                    image_data = img_buffer.getvalue()

                    # Save combined script
                    combined_script = "\n\n---PART---\n\n".join(script_parts)
                    script_data = combined_script.encode("utf-8")

                    # Store in session state
                    st.session_state.generated_files[session_key] = {
                        "topic": topic,
                        "image_data": image_data,
                        "script_data": script_data,
                        "video_data": final_video_data,
                        "script_parts": script_parts,
                        "grounding_metadata": grounding_metadata,
                        "timestamp": timestamp,
                    }

                    # Complete
                    progress_bar.progress(100)
                    status_text.text("✅ Podcast generation completed!")

                    # Display results
                    with result_container:
                        st.markdown("### 🎉 Your Podcast Episode is Ready!")

                        # Success message
                        st.markdown(
                            f"""
                        <div class="success-box">
                            <h4>✅ Successfully generated podcast episode about: <strong>{topic}</strong></h4>
                            <p>📁 Session ID: <code>{session_key}</code></p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        # Display image
                        st.markdown("#### 🖼️ Generated Image")
                        st.image(
                            image,
                            caption="Generated podcast studio image",
                            use_container_width=True,
                        )

                        # Display script parts
                        st.markdown(
                            "#### 📝 Generated Script (3 parts, complete podcast segments)"
                        )

                        # Create tabs for each script part
                        tab1, tab2, tab3 = st.tabs(
                            [
                                "Part 1 (Intro)",
                                "Part 2 (Main Content)",
                                "Part 3 (Conclusion)",
                            ]
                        )

                        with tab1:
                            st.text_area(
                                "Script Part 1:",
                                value=script_parts[0],
                                height=100,
                                disabled=True,
                                key="script_part_1",
                            )

                        with tab2:
                            st.text_area(
                                "Script Part 2:",
                                value=script_parts[1],
                                height=100,
                                disabled=True,
                                key="script_part_2",
                            )

                        with tab3:
                            st.text_area(
                                "Script Part 3:",
                                value=script_parts[2],
                                height=100,
                                disabled=True,
                                key="script_part_3",
                            )

                        # Show combined script
                        st.markdown("#### 📄 Combined Script")
                        st.text_area(
                            "Full Script:",
                            value=combined_script,
                            height=150,
                            disabled=True,
                            key="combined_script",
                        )

                        # Display grounding metadata if search was used
                        if use_search and grounding_metadata:
                            st.markdown("#### 🔍 Search Sources & Citations")

                            # Show search queries
                            if grounding_metadata.get("web_search_queries"):
                                st.markdown("**Search Queries Used:**")
                                for i, query in enumerate(
                                    grounding_metadata["web_search_queries"], 1
                                ):
                                    st.markdown(f"{i}. {query}")

                            # Show sources
                            if grounding_metadata.get("grounding_chunks"):
                                st.markdown("**Sources Found:**")
                                for i, chunk in enumerate(
                                    grounding_metadata["grounding_chunks"], 1
                                ):
                                    # Handle GroundingChunk object attributes
                                    if hasattr(chunk, "web"):
                                        web_info = chunk.web
                                        title = getattr(
                                            web_info, "title", "Unknown Title"
                                        )
                                        uri = getattr(web_info, "uri", "")
                                        if uri:
                                            st.markdown(f"{i}. [{title}]({uri})")

                            # Show script with citations
                            if grounding_metadata.get("grounding_supports"):
                                st.markdown("**Script with Citations:**")
                                script_with_citations = agent.add_citations(
                                    combined_script, grounding_metadata
                                )
                                st.markdown(script_with_citations)

                        # Display video
                        st.markdown("#### 🎬 Generated Video")
                        if final_video_data:
                            st.video(final_video_data)

                            # Download buttons
                            st.markdown("#### 📥 Download Files")

                            col_download1, col_download2, col_download3 = st.columns(3)

                            with col_download1:
                                st.markdown(
                                    create_download_link(
                                        image_data,
                                        f"podcast_image_{session_key}.png",
                                        "image/png",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            with col_download2:
                                st.markdown(
                                    create_download_link(
                                        script_data,
                                        f"podcast_script_{session_key}.txt",
                                        "text/plain",
                                    ),
                                    unsafe_allow_html=True,
                                )

                            with col_download3:
                                st.markdown(
                                    create_download_link(
                                        final_video_data,
                                        f"podcast_video_{session_key}.mp4",
                                        "video/mp4",
                                    ),
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.error("Video generation failed. Please try again.")

                except Exception as e:
                    st.markdown(
                        f"""
                    <div class="error-box">
                        <h4>❌ Error during generation:</h4>
                        <p>{str(e)}</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    st.error(f"Failed to generate podcast episode: {e}")

            except Exception as e:
                st.markdown(
                    f"""
                <div class="error-box">
                    <h4>❌ Error initializing agent:</h4>
                    <p>{str(e)}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.error(f"Failed to initialize PodcastAgent: {e}")

    with col2:
        st.header("📊 Generation Info")

        st.markdown(
            """
        ### ⏱️ Expected Timeline
        - **Image Generation**: ~10-30 seconds
        - **Script Generation**: ~5-15 seconds  
        - **Video Generation**: ~33 seconds to 18 minutes
          - 3 individual videos (8s each)
          - Video combining: ~5-10 seconds
        - **Total Duration**: 24 seconds (3 × 8s videos)
        """
        )

        # Show recent generations
        if st.session_state.generated_files:
            st.markdown("### 📁 Recent Generations")
            for session_key, files in list(st.session_state.generated_files.items())[
                -3:
            ]:
                with st.expander(f"Session {session_key[:8]} - {files['topic']}"):
                    st.write(f"**Topic:** {files['topic']}")
                    st.write(f"**Generated:** {files['timestamp']}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(
                            create_download_link(
                                files["image_data"],
                                f"image_{session_key[:8]}.png",
                                "image/png",
                            ),
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.markdown(
                            create_download_link(
                                files["script_data"],
                                f"script_{session_key[:8]}.txt",
                                "text/plain",
                            ),
                            unsafe_allow_html=True,
                        )
                    with col3:
                        st.markdown(
                            create_download_link(
                                files["video_data"],
                                f"video_{session_key[:8]}.mp4",
                                "video/mp4",
                            ),
                            unsafe_allow_html=True,
                        )


if __name__ == "__main__":
    main()
