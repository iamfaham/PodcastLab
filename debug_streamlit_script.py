#!/usr/bin/env python3
"""
Debug script to test the generate_podcast_script method in a Streamlit-like environment.

This script helps identify why the method works in tests but returns empty strings in Streamlit.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import PodcastAgent
from loguru import logger


def test_script_generation():
    """Test script generation with detailed debugging."""
    print("🔍 Debug: Testing generate_podcast_script in Streamlit-like environment")
    print("=" * 70)

    # Check for API key
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY environment variable not set!")
        return False

    print(f"✅ API Key found: {api_key[:10]}...")

    try:
        # Initialize agent
        print("\n🔧 Initializing PodcastAgent...")
        agent = PodcastAgent(api_key=api_key)
        print("✅ Agent initialized successfully")

        # Test basic script generation
        print("\n📝 Testing basic script generation...")
        topic = "Artificial Intelligence"
        script_parts, grounding_metadata = agent.generate_podcast_script(
            topic, use_search=False
        )

        print(f"✅ Script generation completed")
        print(f"   - Number of parts: {len(script_parts)}")
        print(f"   - Grounding metadata keys: {list(grounding_metadata.keys())}")

        # Check each part
        for i, part in enumerate(script_parts, 1):
            print(f"   - Part {i}: {len(part)} characters")
            if len(part) == 0:
                print(f"     ❌ WARNING: Part {i} is empty!")
            else:
                print(f"     ✅ Part {i} preview: {part[:100]}...")

        # Test with search
        print("\n🔍 Testing script generation with search...")
        script_parts_search, grounding_metadata_search = agent.generate_podcast_script(
            topic, use_search=True
        )

        print(f"✅ Search script generation completed")
        print(f"   - Number of parts: {len(script_parts_search)}")
        print(f"   - Grounding metadata keys: {list(grounding_metadata_search.keys())}")

        # Check each part
        for i, part in enumerate(script_parts_search, 1):
            print(f"   - Part {i}: {len(part)} characters")
            if len(part) == 0:
                print(f"     ❌ WARNING: Part {i} is empty!")
            else:
                print(f"     ✅ Part {i} preview: {part[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_different_topics():
    """Test with different topics to see if it's topic-specific."""
    print("\n🌍 Testing with different topics...")

    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY environment variable not set!")
        return False

    agent = PodcastAgent(api_key=api_key)

    topics = ["Climate Change", "Space Exploration", "Machine Learning"]

    for topic in topics:
        print(f"\n📝 Testing topic: {topic}")
        try:
            script_parts, grounding_metadata = agent.generate_podcast_script(
                topic, use_search=False
            )

            print(f"   ✅ Generated {len(script_parts)} parts")
            for i, part in enumerate(script_parts, 1):
                print(
                    f"   - Part {i}: {len(part)} chars - {'✅' if len(part) > 0 else '❌ EMPTY'}"
                )

        except Exception as e:
            print(f"   ❌ Error with topic '{topic}': {e}")


def main():
    """Main debug function."""
    print("🧪 Streamlit Script Generation Debug Tool 🧪")
    print("This tool helps debug why script generation might fail in Streamlit")
    print()

    # Test basic functionality
    success = test_script_generation()

    if success:
        # Test different topics
        test_different_topics()

        print("\n" + "=" * 70)
        print("✅ Debug completed successfully!")
        print("If this works but Streamlit doesn't, the issue is likely:")
        print("1. Streamlit session state management")
        print("2. API client initialization in Streamlit context")
        print("3. Response parsing differences in Streamlit environment")
        print("\nNote: Output files are now saved to the 'tmp' folder")
    else:
        print("\n" + "=" * 70)
        print("❌ Debug failed - there's a fundamental issue with the API call")
        print("Check your API key and network connection")


if __name__ == "__main__":
    main()
