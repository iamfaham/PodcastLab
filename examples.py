#!/usr/bin/env python3
"""
Example usage of the Podcast Creator Agent
"""

import os
from main import PodcastAgent
from loguru import logger


def example_basic_usage():
    """Basic example: Create a complete podcast episode."""
    print("🎙️ Example 1: Basic Usage")
    print("=" * 50)

    agent = PodcastAgent()

    topic = "The Future of Renewable Energy"
    result = agent.create_podcast_episode(topic)

    print(f"✅ Created podcast episode about: {topic}")
    print(f"📁 Files saved in: output/")
    print(f"🖼️ Image: {result['image_path']}")
    print(f"📝 Script: {result['script_path']}")
    print(f"🎬 Video: {result['video_path']}")
    print(f"\n📋 Generated Script Preview:\n{result['script_content'][:200]}...")
    print("\n")


def example_custom_image_prompt():
    """Example with custom image prompt."""
    print("🎙️ Example 2: Custom Image Prompt")
    print("=" * 50)

    agent = PodcastAgent()

    topic = "Space Exploration"
    custom_prompt = (
        "Two astronauts in a futuristic space station podcast studio, "
        "with Earth visible through a large window, professional lighting, "
        "space-themed microphones and equipment"
    )

    result = agent.create_podcast_episode(
        topic=topic, custom_image_prompt=custom_prompt, output_dir="output/space_themed"
    )

    print(f"✅ Created space-themed podcast about: {topic}")
    print(f"📁 Files saved in: output/space_themed/")
    print(f"🖼️ Custom image generated with space theme")
    print("\n")


def example_individual_components():
    """Example using individual components separately."""
    print("🎙️ Example 3: Individual Components")
    print("=" * 50)

    agent = PodcastAgent()

    # Generate just an image
    print("🖼️ Generating podcast image...")
    image = agent.generate_podcast_image()
    image.save("output/standalone_image.png")
    print("✅ Image saved to: output/standalone_image.png")

    # Generate just a script
    print("📝 Generating podcast script...")
    topic = "Digital Privacy in 2024"
    script = agent.generate_podcast_script(topic)
    with open("output/standalone_script.txt", "w", encoding="utf-8") as f:
        f.write(script)
    print("✅ Script saved to: output/standalone_script.txt")
    print(f"📋 Script preview: {script[:150]}...")

    # Generate just a video (using the image and script)
    print("🎬 Generating podcast video...")
    video_path = agent.generate_podcast_video(
        script=script, image=image, output_filename="output/standalone_video.mp4"
    )
    print(f"✅ Video saved to: {video_path}")
    print("\n")


def example_batch_creation():
    """Example: Create multiple podcast episodes on different topics."""
    print("🎙️ Example 4: Batch Creation")
    print("=" * 50)

    agent = PodcastAgent()

    topics = ["Cryptocurrency Trends", "Remote Work Revolution", "Sustainable Fashion"]

    results = []
    for i, topic in enumerate(topics, 1):
        print(f"🔄 Creating episode {i}/{len(topics)}: {topic}")

        try:
            result = agent.create_podcast_episode(
                topic=topic, output_dir=f"output/batch_episode_{i}"
            )
            results.append(result)
            print(f"✅ Episode {i} completed!")

        except Exception as e:
            print(f"❌ Episode {i} failed: {e}")

    print(f"\n🎉 Batch creation completed! Created {len(results)} episodes.")
    print("\n")


def main():
    """Run all examples."""
    try:
        # Check if API key is set
        if not os.getenv("GOOGLE_AI_API_KEY"):
            print("❌ Error: GOOGLE_AI_API_KEY environment variable not set!")
            print("Please set your Google AI API key before running examples.")
            print("Example: export GOOGLE_AI_API_KEY='your_api_key_here'")
            return

        print("🚀 Podcast Creator Agent Examples")
        print("=" * 60)
        print("This will demonstrate various ways to use the PodcastAgent.")
        print("Note: Video generation can take several minutes per episode.\n")

        # Create output directory
        os.makedirs("output", exist_ok=True)

        # Run examples
        example_basic_usage()
        example_custom_image_prompt()
        example_individual_components()

        # Uncomment the next line to run batch creation (takes longer)
        # example_batch_creation()

        print("🎉 All examples completed successfully!")
        print("Check the 'output/' directory for generated files.")

    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user.")
    except Exception as e:
        logger.error(f"Examples failed: {e}")
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    main()
