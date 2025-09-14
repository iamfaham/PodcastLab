import streamlit as st
import os
import time
import uuid
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


def cleanup_old_files(output_dir: str = "tmp", max_age_hours: int = 24) -> dict:
    """
    Clean up files older than specified hours in the output directory.

    Args:
        output_dir: Directory to clean up
        max_age_hours: Maximum age in hours before files are deleted

    Returns:
        Dictionary with cleanup statistics
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return {"deleted_files": 0, "deleted_dirs": 0, "freed_space": 0}

    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    deleted_files = 0
    deleted_dirs = 0
    freed_space = 0

    try:
        # Get all subdirectories in output folder
        for item in output_path.iterdir():
            if item.is_dir():
                # Check if directory is older than cutoff time
                dir_creation_time = datetime.fromtimestamp(item.stat().st_ctime)

                if dir_creation_time < cutoff_time:
                    # Calculate space before deletion
                    dir_size = sum(
                        f.stat().st_size for f in item.rglob("*") if f.is_file()
                    )
                    freed_space += dir_size

                    # Delete the entire directory and its contents
                    import shutil

                    shutil.rmtree(item)
                    deleted_dirs += 1

                    # Count files in the deleted directory
                    deleted_files += sum(1 for f in item.rglob("*") if f.is_file())

        return {
            "deleted_files": deleted_files,
            "deleted_dirs": deleted_dirs,
            "freed_space": freed_space,
            "cutoff_time": cutoff_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        st.error(f"Error during cleanup: {e}")
        return {
            "deleted_files": 0,
            "deleted_dirs": 0,
            "freed_space": 0,
            "error": str(e),
        }


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


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

    # Auto-cleanup on app start (only run once per session)
    if "cleanup_done" not in st.session_state:
        with st.spinner("🧹 Cleaning up old files (24+ hours)..."):
            cleanup_stats = cleanup_old_files()
            st.session_state.cleanup_done = True

            if cleanup_stats["deleted_files"] > 0:
                st.success(
                    f"✅ Cleanup completed! Deleted {cleanup_stats['deleted_files']} files from {cleanup_stats['deleted_dirs']} directories, freed {format_file_size(cleanup_stats['freed_space'])}"
                )

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        # Try to get API key from Streamlit secrets first, then from environment
        try:
            default_api_key = st.secrets.get(
                "GOOGLE_AI_API_KEY", os.getenv("GOOGLE_AI_API_KEY", "")
            )
        except:
            default_api_key = os.getenv("GOOGLE_AI_API_KEY", "")

        api_key = st.text_input(
            "Google AI API Key",
            type="password",
            help="Enter your Google AI API key. You can also set it in Streamlit Cloud secrets or as GOOGLE_AI_API_KEY environment variable.",
            value=default_api_key,
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
                    # Create timestamped subfolder with unique ID
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
                    subfolder_name = f"{timestamp}_{unique_id}"

                    output_dir = Path("tmp") / subfolder_name
                    output_dir.mkdir(parents=True, exist_ok=True)

                    image = agent.generate_podcast_image()
                    progress_bar.progress(20)

                    # Step 2: Generate script (3 parts)
                    status_text.text("📝 Step 2/5: Generating 3-part podcast script...")
                    progress_bar.progress(30)

                    # Refresh client connection before script generation (Streamlit fix)
                    agent.refresh_client()

                    script_parts, grounding_metadata = agent.generate_podcast_script(
                        topic, use_search
                    )
                    progress_bar.progress(40)

                    # Step 3: Generate 3 individual videos
                    status_text.text("🎬 Step 3/5: Generating 3 individual videos...")
                    progress_bar.progress(50)

                    video_paths = agent.generate_multiple_podcast_videos(
                        script_parts=script_parts,
                        image=image,
                        output_dir=str(output_dir),
                    )
                    progress_bar.progress(70)

                    # Step 4: Combine videos
                    status_text.text(
                        "🔗 Step 4/5: Combining videos into final 24-second video..."
                    )
                    progress_bar.progress(80)

                    final_video_path = output_dir / "podcast_video.mp4"
                    combined_video_path = agent.combine_videos(
                        video_paths=video_paths, output_filename=str(final_video_path)
                    )
                    progress_bar.progress(90)

                    # Step 5: Clean up
                    status_text.text(
                        "🧹 Step 5/5: Cleaning up individual video parts..."
                    )
                    progress_bar.progress(95)

                    # Save image
                    image_path = output_dir / "podcast_image.png"
                    image.save(image_path)

                    # Save individual script parts
                    script_part_paths = []
                    for i, script_part in enumerate(script_parts, 1):
                        script_part_path = output_dir / f"podcast_script_part_{i}.txt"
                        with open(script_part_path, "w", encoding="utf-8") as f:
                            f.write(script_part)
                        script_part_paths.append(str(script_part_path))

                    # Save combined script
                    combined_script = "\n\n---PART---\n\n".join(script_parts)
                    script_path = output_dir / "podcast_script.txt"
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(combined_script)

                    # Clean up individual video parts
                    for video_path in video_paths:
                        try:
                            os.remove(video_path)
                        except Exception as e:
                            st.warning(f"Could not clean up {video_path}: {e}")

                    video_path = combined_video_path

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
                            <p>📁 Files saved in: <code>tmp/{subfolder_name}/</code></p>
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
                            st.markdown("#### 🔍 Search Sources")

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

                        # Display video
                        st.markdown("#### 🎬 Generated Video")
                        if os.path.exists(video_path):
                            st.video(video_path)

                            # Download buttons
                            st.markdown("#### 📥 Download Files")

                            col_download1, col_download2, col_download3 = st.columns(3)

                            with col_download1:
                                with open(image_path, "rb") as img_file:
                                    st.download_button(
                                        label="📷 Download Image",
                                        data=img_file.read(),
                                        file_name=image_path.name,
                                        mime="image/png",
                                    )

                            with col_download2:
                                with open(script_path, "rb") as script_file:
                                    st.download_button(
                                        label="📄 Download Script",
                                        data=script_file.read(),
                                        file_name=script_path.name,
                                        mime="text/plain",
                                    )

                            with col_download3:
                                with open(video_path, "rb") as video_file:
                                    st.download_button(
                                        label="🎬 Download Video",
                                        data=video_file.read(),
                                        file_name=Path(video_path).name,
                                        mime="video/mp4",
                                    )
                        else:
                            st.error(
                                "Video file not found. Please check the generation process."
                            )

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


if __name__ == "__main__":
    main()
