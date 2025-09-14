import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


class PodcastAgent:
    """AI-powered podcast creator using Google's Imagen, Gemini, and Veo models."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the PodcastAgent with Google AI client.

        Args:
            api_key: Google AI API key. If not provided, will use GOOGLE_AI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google AI API key is required. Set GOOGLE_AI_API_KEY environment variable or pass api_key parameter."
            )

        # Load model names from environment variables with defaults
        self.imagen_model = os.getenv("IMAGEN_MODEL", "imagen-3.0-generate-002")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-205-flash-exp")
        self.veo_model = os.getenv("VEO_MODEL", "veo-3")

        self.client = genai.Client(api_key=self.api_key)
        logger.info(
            f"PodcastAgent initialized successfully with models: Imagen={self.imagen_model}, Gemini={self.gemini_model}, Veo={self.veo_model}"
        )

    def generate_podcast_image(
        self, custom_prompt: Optional[str] = None
    ) -> Image.Image:
        """Generate a podcast image using Imagen.

        Args:
            custom_prompt: Custom prompt for image generation. If not provided, uses default.

        Returns:
            PIL Image object of the generated podcast photo.
        """
        prompt = custom_prompt or (
            "Two professional podcast hosts: Alex (male, 30s, friendly smile) and Sarah (female, 30s, warm expression) "
            "sitting across from each other in a modern podcast studio, with microphones, headphones, and recording equipment. "
            "Professional lighting, warm and inviting atmosphere, high quality photography style. "
            "Both hosts look engaged and ready to discuss topics."
        )

        logger.info(f"Generating podcast image with prompt: {prompt}")

        try:
            response = self.client.models.generate_images(
                model=self.imagen_model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    include_rai_reason=True,
                ),
            )

            generated_image = response.generated_images[0]
            image = Image.open(BytesIO(generated_image.image.image_bytes))

            logger.success("Podcast image generated successfully")
            return image

        except Exception as e:
            logger.error(f"Failed to generate podcast image: {e}")
            raise

    def generate_podcast_script(
        self, topic: str, use_search: bool = False
    ) -> tuple[list[str], dict]:
        """Generate a podcast script with 3 parts using Gemini.

        Args:
            topic: The topic for the podcast episode.
            use_search: Whether to use Google Search grounding for factual data.

        Returns:
            Tuple of (List of 3 script parts, grounding metadata dict).
        """
        prompt = (
            f"Write a complete podcast script about '{topic}' with exactly 3 parts, each designed for 8-second video segments. "
            f"Hosts are Alex (male) and Sarah (female). Create a full podcast experience with proper introduction, main content, and conclusion. "
            f"Each part should be conversational and engaging, with natural host interactions and smooth transitions. "
            f"Format: 'Alex: [dialogue] Sarah: [response]' for each part. "
            f"Separate parts with '---PART---'. "
            f"Include current, factual information when relevant. "
            f"Make each part feel like a complete segment of a real podcast episode. "
            f"Example structure:\n"
            f"Part 1 (Introduction): Welcome, topic introduction, what listeners will learn\n"
            f"Alex: Welcome to TechTalk! I'm Alex, and I'm here with Sarah.\n"
            f"Sarah: Hey everyone! Today we're diving deep into {topic}.\n"
            f"Alex: This is going to be fascinating because it affects all of us.\n"
            f"Sarah: Absolutely! Let's break down what you need to know.\n"
            f"---PART---\n"
            f"Part 2 (Main Content): Key insights, facts, and detailed discussion\n"
            f"Alex: So here's what's really interesting about this topic...\n"
            f"Sarah: That's a great point, and I think what's even more important is...\n"
            f"Alex: Exactly! And when you consider the implications...\n"
            f"Sarah: Right, which brings us to the next crucial aspect...\n"
            f"---PART---\n"
            f"Part 3 (Conclusion): Key takeaways, wrap-up, and call-to-action\n"
            f"Alex: So to summarize what we've learned today...\n"
            f"Sarah: Those are some really important points to remember.\n"
            f"Alex: Thanks for listening! What are your thoughts on this topic?\n"
            f"Sarah: We'd love to hear from you! Until next time, keep learning!"
        )

        logger.info(
            f"Generating 3-part podcast script for topic: {topic} (search: {use_search})"
        )

        # Configure tools based on search preference
        tools = []
        if use_search:
            tools.append(types.Tool(google_search=types.GoogleSearch()))

        try:
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=600,
                    tools=tools if tools else None,
                ),
            )

            full_script = response.text.strip()

            # Split the script into 3 parts
            parts = full_script.split("---PART---")
            if len(parts) != 3:
                # Fallback: try to split by double newlines or other separators
                parts = [
                    part.strip() for part in full_script.split("\n\n") if part.strip()
                ]
                if len(parts) < 3:
                    # If still not 3 parts, create equal divisions
                    words = full_script.split()
                    words_per_part = len(words) // 3
                    parts = [
                        " ".join(words[:words_per_part]),
                        " ".join(words[words_per_part : words_per_part * 2]),
                        " ".join(words[words_per_part * 2 :]),
                    ]
                elif len(parts) > 3:
                    # If more than 3 parts, combine the extras
                    parts = [parts[0], parts[1], " ".join(parts[2:])]

            # Ensure we have exactly 3 parts
            while len(parts) < 3:
                parts.append("")

            parts = parts[:3]  # Take only first 3 parts
            parts = [part.strip() for part in parts]

            # Clean up each part - remove any markdown formatting and extra whitespace
            cleaned_parts = []
            for part in parts:
                # Remove markdown formatting like **text** and *text*
                cleaned_part = part.replace("**", "").replace("*", "")
                # Remove extra whitespace and newlines
                cleaned_part = " ".join(cleaned_part.split())
                cleaned_parts.append(cleaned_part)

            parts = cleaned_parts

            # Extract grounding metadata if available
            grounding_metadata = {}
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if (
                    hasattr(candidate, "grounding_metadata")
                    and candidate.grounding_metadata
                ):
                    grounding_metadata = {
                        "web_search_queries": getattr(
                            candidate.grounding_metadata, "web_search_queries", []
                        ),
                        "grounding_chunks": getattr(
                            candidate.grounding_metadata, "grounding_chunks", []
                        ),
                        "grounding_supports": getattr(
                            candidate.grounding_metadata, "grounding_supports", []
                        ),
                    }

            logger.success(
                f"Podcast script generated successfully: 3 parts, {sum(len(part) for part in parts)} total characters"
            )
            return parts, grounding_metadata

        except Exception as e:
            logger.error(f"Failed to generate podcast script: {e}")
            raise

    def add_citations(self, text: str, grounding_metadata: dict) -> str:
        """Add inline citations to text based on grounding metadata.

        Args:
            text: The text to add citations to
            grounding_metadata: Grounding metadata from Gemini response

        Returns:
            Text with inline citations added
        """
        if not grounding_metadata or not grounding_metadata.get("grounding_supports"):
            return text

        supports = grounding_metadata["grounding_supports"]
        chunks = grounding_metadata.get("grounding_chunks", [])

        # Sort supports by end_index in descending order to avoid shifting issues
        sorted_supports = sorted(
            supports,
            key=lambda s: (
                getattr(s.segment, "end_index", 0) if hasattr(s, "segment") else 0
            ),
            reverse=True,
        )

        for support in sorted_supports:
            # Handle GroundingSupport object attributes
            if hasattr(support, "segment") and hasattr(support.segment, "end_index"):
                end_index = support.segment.end_index
            else:
                continue

            if hasattr(support, "grounding_chunk_indices"):
                chunk_indices = support.grounding_chunk_indices
            else:
                continue

            if end_index is None or not chunk_indices:
                continue

            # Create citation links
            citation_links = []
            for i in chunk_indices:
                if i < len(chunks):
                    chunk = chunks[i]
                    # Handle GroundingChunk object attributes
                    if hasattr(chunk, "web") and hasattr(chunk.web, "uri"):
                        uri = chunk.web.uri
                        if uri:
                            citation_links.append(f"[{i + 1}]({uri})")

            if citation_links:
                citation_string = ", ".join(citation_links)
                text = text[:end_index] + citation_string + text[end_index:]

        return text

    def generate_podcast_video(
        self,
        script: str,
        image: Optional[Image.Image] = None,
        output_filename: str = "podcast_video.mp4",
    ) -> str:
        """Generate a single podcast video using Veo.

        Args:
            script: The podcast script to base the video on.
            image: Optional starting image for the video. If provided, will use image-to-video generation.
            output_filename: Name of the output video file.

        Returns:
            Path to the generated video file.
        """
        # Create a detailed prompt that incorporates the script
        prompt = (
            f"A professional podcast recording session with Alex (male host, 30s) and Sarah (female host, 30s) "
            f"in a modern studio setting. The hosts are engaged in conversation about the following content: {script}. "
            f"Show natural gestures, professional lighting, microphones, and recording equipment. "
            f"Cinematic quality, smooth camera movement, realistic expressions and movements. "
            f"Both hosts should look engaged and natural while speaking their lines. "
            f"Create this video in square aspect ratio (1:1) format."
        )

        logger.info(
            f"Generating podcast video with script length: {len(script)} characters"
        )

        try:
            # Generate video with or without starting image
            if image:
                # Convert PIL Image to bytes for the API
                img_bytes = BytesIO()
                image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                operation = self.client.models.generate_videos(
                    model=self.veo_model,
                    prompt=prompt,
                    image=types.Image(
                        image_bytes=img_bytes.getvalue(), mime_type="image/png"
                    ),
                )
                logger.info("Generating video with starting image")
            else:
                operation = self.client.models.generate_videos(
                    model=self.veo_model,
                    prompt=prompt,
                )
                logger.info("Generating video from text prompt only")

            # Poll the operation status until the video is ready
            logger.info("Waiting for video generation to complete...")
            while not operation.done:
                logger.info("Video generation in progress...")
                time.sleep(10)
                operation = self.client.operations.get(operation)

            # Check if the operation was successful
            if not operation.done:
                raise Exception("Video generation operation did not complete")

            logger.info(f"Operation completed. Response: {operation.response}")

            if not operation.response:
                raise Exception(
                    "Video generation operation completed but no response received"
                )

            if not hasattr(operation.response, "generated_videos"):
                raise Exception(
                    f"Video generation response missing 'generated_videos' attribute. Response: {operation.response}"
                )

            if not operation.response.generated_videos:
                raise Exception(
                    "Video generation operation completed but no videos were generated"
                )

            logger.info(
                f"Found {len(operation.response.generated_videos)} generated videos"
            )

            # Download the generated video
            generated_video = operation.response.generated_videos[0]
            self.client.files.download(file=generated_video.video)

            # Save to specified filename
            output_path = Path(output_filename)
            generated_video.video.save(str(output_path))

            logger.success(f"Podcast video generated and saved to: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate podcast video: {e}")
            raise

    def generate_multiple_podcast_videos(
        self,
        script_parts: list[str],
        image: Optional[Image.Image] = None,
        output_dir: str = "output",
    ) -> list[str]:
        """Generate multiple podcast videos from script parts.

        Args:
            script_parts: List of script parts for each video segment.
            image: Optional starting image for the videos.
            output_dir: Directory to save the video files.

        Returns:
            List of paths to the generated video files.
        """
        video_paths = []
        output_path = Path(output_dir)

        for i, script_part in enumerate(script_parts, 1):
            logger.info(f"Generating video segment {i}/{len(script_parts)}")
            video_filename = output_path / f"podcast_video_part_{i}.mp4"

            try:
                video_path = self.generate_podcast_video(
                    script=script_part, image=image, output_filename=str(video_filename)
                )
                video_paths.append(video_path)
                logger.success(f"Video segment {i} completed: {video_path}")
            except Exception as e:
                logger.error(f"Failed to generate video segment {i}: {e}")
                raise

        return video_paths

    def combine_videos(self, video_paths: list[str], output_filename: str) -> str:
        """Combine multiple video files into one using moviepy.

        Args:
            video_paths: List of paths to video files to combine.
            output_filename: Path for the combined video file.

        Returns:
            Path to the combined video file.
        """
        try:
            from moviepy import VideoFileClip, concatenate_videoclips

            logger.info(f"Combining {len(video_paths)} videos into one")

            # Load video clips
            clips = []
            for video_path in video_paths:
                if os.path.exists(video_path):
                    clip = VideoFileClip(video_path)
                    clips.append(clip)
                    logger.info(f"Loaded video: {video_path}")
                else:
                    logger.warning(f"Video file not found: {video_path}")

            if not clips:
                raise Exception("No valid video clips found to combine")

            # Concatenate videos
            final_clip = concatenate_videoclips(clips)

            # Write the combined video
            final_clip.write_videofile(
                output_filename,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
            )

            # Close clips to free memory
            for clip in clips:
                clip.close()
            final_clip.close()

            logger.success(f"Videos combined successfully: {output_filename}")
            return output_filename

        except ImportError:
            logger.error(
                "moviepy is required for video combining. Install with: pip install moviepy"
            )
            raise Exception(
                "moviepy is required for video combining. Please install it with: pip install moviepy"
            )
        except Exception as e:
            logger.error(f"Failed to combine videos: {e}")
            raise

    def create_podcast_episode(
        self,
        topic: str,
        output_dir: str = "/tmp/podcast_output",
        custom_image_prompt: Optional[str] = None,
        use_search: bool = False,
    ) -> dict:
        """Create a complete podcast episode with image, script, and 3 combined videos.

        Args:
            topic: The topic for the podcast episode.
            output_dir: Directory to save output files.
            custom_image_prompt: Optional custom prompt for image generation.
            use_search: Whether to use Google Search grounding for factual data.

        Returns:
            Dictionary containing paths to generated files and metadata.
        """
        logger.info(f"Creating complete podcast episode for topic: '{topic}'")

        # Create timestamped subfolder with unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
        subfolder_name = f"{timestamp}_{unique_id}"

        output_path = Path(output_dir) / subfolder_name
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: Generate podcast image
            logger.info("Step 1/5: Generating podcast image...")
            image = self.generate_podcast_image(custom_image_prompt)
            image_path = output_path / "podcast_image.png"
            image.save(image_path)

            # Step 2: Generate podcast script (3 parts)
            logger.info("Step 2/5: Generating 3-part podcast script...")
            script_parts, grounding_metadata = self.generate_podcast_script(
                topic, use_search
            )

            # Save individual script parts
            script_paths = []
            for i, script_part in enumerate(script_parts, 1):
                script_part_path = output_path / f"podcast_script_part_{i}.txt"
                with open(script_part_path, "w", encoding="utf-8") as f:
                    f.write(script_part)
                script_paths.append(str(script_part_path))

            # Save combined script
            combined_script = "\n\n---PART---\n\n".join(script_parts)
            script_path = output_path / "podcast_script.txt"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(combined_script)

            # Step 3: Generate 3 individual videos
            logger.info("Step 3/5: Generating 3 individual podcast videos...")
            video_paths = self.generate_multiple_podcast_videos(
                script_parts=script_parts, image=image, output_dir=str(output_path)
            )

            # Step 4: Combine videos into one final video
            logger.info("Step 4/5: Combining videos into final 24-second video...")
            final_video_path = output_path / "podcast_video.mp4"
            combined_video_path = self.combine_videos(
                video_paths=video_paths, output_filename=str(final_video_path)
            )

            # Step 5: Clean up individual video parts (optional)
            logger.info("Step 5/5: Cleaning up individual video parts...")
            for video_path in video_paths:
                try:
                    os.remove(video_path)
                    logger.info(f"Cleaned up: {video_path}")
                except Exception as e:
                    logger.warning(f"Could not clean up {video_path}: {e}")

            result = {
                "topic": topic,
                "image_path": str(image_path),
                "script_path": str(script_path),
                "script_parts": script_parts,
                "script_part_paths": script_paths,
                "video_path": combined_video_path,
                "individual_video_paths": video_paths,
                "script_content": combined_script,
                "grounding_metadata": grounding_metadata,
            }

            logger.success(
                f"Podcast episode created successfully! Files saved in: {output_path} (subfolder: {subfolder_name})"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to create podcast episode: {e}")
            raise


def main():
    """Example usage of the PodcastAgent."""
    try:
        # Initialize the agent
        agent = PodcastAgent()

        # Get topic input from user
        print("🎙️ Welcome to Podcast Agent! 🎙️")
        print(
            "This tool will generate a complete podcast episode with image, script, and video."
        )
        print()

        topic = input("Enter the topic for your podcast episode: ").strip()

        if not topic:
            print("No topic provided. Exiting...")
            return

        logger.info(f"Creating podcast episode about: {topic}")

        result = agent.create_podcast_episode(topic)

        print("\n🎙️ Podcast Episode Created Successfully! 🎙️")
        print(f"Topic: {result['topic']}")
        print(f"Image: {result['image_path']}")
        print(f"Script: {result['script_path']}")
        print(f"Video: {result['video_path']}")
        print(f"\nGenerated Script (3 parts, 24 seconds total):")
        for i, part in enumerate(result["script_parts"], 1):
            print(f"\nPart {i} (8 seconds):\n{part}")

    except Exception as e:
        logger.error(f"Failed to create podcast episode: {e}")
        print(f"Error: {e}")
        print("\nMake sure to set your GOOGLE_AI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
