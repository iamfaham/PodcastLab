#!/usr/bin/env python3
"""
Test script for the generate_podcast_script method from PodcastAgent class.

This script tests the generate_podcast_script method with real API calls
to verify actual functionality with Google AI API.

Usage:
    python test_podcast_script.py

Requirements:
    - GOOGLE_AI_API_KEY environment variable set
    - The main.py file with PodcastAgent class
    - Internet connection for API calls
"""

import os
import sys
import unittest
from typing import List, Dict, Any

# Add the current directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import PodcastAgent


class TestPodcastScriptGeneration(unittest.TestCase):
    """Test cases for the generate_podcast_script method with real API calls."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Check for API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            self.skipTest("GOOGLE_AI_API_KEY environment variable not set")

        # Initialize the agent with real API key
        self.agent = PodcastAgent(api_key=api_key)

    def test_generate_podcast_script_basic(self):
        """Test basic podcast script generation without search using real API."""
        print("\n🧪 Testing basic podcast script generation (no search)...")

        # Test the method with real API call
        topic = "Artificial Intelligence"
        script_parts, grounding_metadata = self.agent.generate_podcast_script(
            topic, use_search=False
        )

        # Assertions
        self.assertIsInstance(script_parts, list)
        self.assertEqual(len(script_parts), 3)
        self.assertIsInstance(grounding_metadata, dict)

        # Check that each part contains expected content
        for i, part in enumerate(script_parts):
            self.assertIsInstance(part, str)
            self.assertGreater(len(part), 0)
            print(f"✅ Part {i+1} ({len(part)} chars): {part[:100]}...")

        print(f"✅ Basic test passed - Generated 3 script parts for topic: {topic}")

    def test_generate_podcast_script_with_search(self):
        """Test podcast script generation with search enabled using real API."""
        print("\n🔍 Testing podcast script generation with search enabled...")

        # Test the method with search enabled using real API call
        topic = "Machine Learning"
        script_parts, grounding_metadata = self.agent.generate_podcast_script(
            topic, use_search=True
        )

        # Assertions
        self.assertIsInstance(script_parts, list)
        self.assertEqual(len(script_parts), 3)
        self.assertIsInstance(grounding_metadata, dict)

        # Check that each part contains expected content
        for i, part in enumerate(script_parts):
            self.assertIsInstance(part, str)
            self.assertGreater(len(part), 0)
            print(f"✅ Part {i+1} ({len(part)} chars): {part[:100]}...")

        # Check grounding metadata
        print(f"✅ Grounding metadata keys: {list(grounding_metadata.keys())}")
        if grounding_metadata.get("web_search_queries"):
            print(f"✅ Search queries: {grounding_metadata['web_search_queries']}")

        print(f"✅ Search test passed - Generated 3 script parts for topic: {topic}")

    def test_generate_podcast_script_different_topics(self):
        """Test script generation with different topics using real API."""
        print("\n🌍 Testing script generation with different topics...")

        # Test with a different topic to verify variety
        topic = "Climate Change"
        script_parts, grounding_metadata = self.agent.generate_podcast_script(topic)

        # Assertions
        self.assertEqual(len(script_parts), 3)
        self.assertIsInstance(grounding_metadata, dict)

        # Check that each part contains expected content
        for i, part in enumerate(script_parts):
            self.assertIsInstance(part, str)
            self.assertGreater(len(part), 0)
            print(f"✅ Part {i+1} ({len(part)} chars): {part[:100]}...")

        print(
            f"✅ Different topics test passed - Generated 3 script parts for topic: {topic}"
        )


def run_tests():
    """Run all tests and display results."""
    print("🧪 Running Podcast Script Generation Tests with Real API Calls 🧪")
    print("=" * 70)
    print("⚠️  WARNING: This will make 2 real API calls to Google AI")
    print("⚠️  Make sure GOOGLE_AI_API_KEY is set and you have API quota")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPodcastScriptGeneration)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun
    ) * 100
    print(f"Success rate: {success_rate:.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    # Check for API key before running
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("❌ ERROR: GOOGLE_AI_API_KEY environment variable not set!")
        print("Please set your Google AI API key before running tests.")
        print("Example: export GOOGLE_AI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Check if pytest is available for more advanced testing
    try:
        import pytest

        print("pytest is available. You can also run: pytest test_podcast_script.py -v")
    except ImportError:
        print("pytest not available. Running with unittest.")

    # Run the tests
    success = run_tests()

    if success:
        print("\n✅ All tests passed! Real API calls completed successfully.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
