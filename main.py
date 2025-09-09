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
        self.imagen_model = os.getenv("IMAGEN_MODEL", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "")
        self.veo_model = os.getenv("VEO_MODEL", "")

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
            "Two professional podcast hosts sitting across from each other in a modern podcast studio, "
            "with microphones, headphones, and recording equipment. Professional lighting, "
            "warm and inviting atmosphere, high quality photography style."
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

    def generate_podcast_script(self, topic: str) -> str:
        """Generate a podcast script using Gemini.

        Args:
            topic: The topic for the podcast episode.

        Returns:
            Generated script text optimized for 8-second video.
        """
        prompt = (
            f"Write a brief, engaging podcast script about '{topic}' that is suitable for an 8-second video. "
            f"The script should be conversational, mention the topic clearly, and sound natural when spoken. "
            f"Include dialogue for two podcast hosts. Keep it concise but compelling. "
            f"Format it as natural speech that would work well with video narration."
        )

        logger.info(f"Generating podcast script for topic: {topic}")

        try:
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=200,
                ),
            )

            script = response.text.strip()
            logger.success(
                f"Podcast script generated successfully: {len(script)} characters"
            )
            return script

        except Exception as e:
            logger.error(f"Failed to generate podcast script: {e}")
            raise

    def generate_podcast_video(
        self,
        script: str,
        image: Optional[Image.Image] = None,
        output_filename: str = "podcast_video.mp4",
    ) -> str:
        """Generate a podcast video using Veo.

        Args:
            script: The podcast script to base the video on.
            image: Optional starting image for the video. If provided, will use image-to-video generation.
            output_filename: Name of the output video file.

        Returns:
            Path to the generated video file.
        """
        # Create a detailed prompt that incorporates the script
        prompt = (
            f"A professional podcast recording session with two hosts in a modern studio setting. "
            f"The hosts are engaged in conversation about the following content: {script}. "
            f"Show natural gestures, professional lighting, microphones, and recording equipment. "
            f"Cinematic quality, smooth camera movement, realistic expressions and movements."
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

    def create_podcast_episode(
        self,
        topic: str,
        output_dir: str = "output",
        custom_image_prompt: Optional[str] = None,
    ) -> dict:
        """Create a complete podcast episode with image, script, and video.

        Args:
            topic: The topic for the podcast episode.
            output_dir: Directory to save output files.
            custom_image_prompt: Optional custom prompt for image generation.

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
            logger.info("Step 1/3: Generating podcast image...")
            image = self.generate_podcast_image(custom_image_prompt)
            image_path = output_path / "podcast_image.png"
            image.save(image_path)

            # Step 2: Generate podcast script
            logger.info("Step 2/3: Generating podcast script...")
            script = self.generate_podcast_script(topic)
            script_path = output_path / "podcast_script.txt"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script)

            # Step 3: Generate podcast video
            logger.info("Step 3/3: Generating podcast video...")
            video_filename = output_path / "podcast_video.mp4"
            video_path = self.generate_podcast_video(
                script=script, image=image, output_filename=str(video_filename)
            )

            result = {
                "topic": topic,
                "image_path": str(image_path),
                "script_path": str(script_path),
                "video_path": video_path,
                "script_content": script,
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
        print(f"\nGenerated Script:\n{result['script_content']}")

    except Exception as e:
        logger.error(f"Failed to create podcast episode: {e}")
        print(f"Error: {e}")
        print("\nMake sure to set your GOOGLE_AI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
