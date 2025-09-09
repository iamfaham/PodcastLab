# 🎙️ Podcast Lab (Podcast Creator Agent)

An AI-powered podcast creator that uses Google's cutting-edge AI models to generate complete podcast episodes with images, scripts, and videos.

## ✨ Features

- **🖼️ Image Generation**: Creates professional podcast studio photos using Google's Imagen
- **📝 Script Generation**: Generates engaging podcast scripts using Gemini AI
- **🎬 Video Generation**: Produces 8-second podcast videos using Google's Veo 3
- **🔄 Complete Workflow**: Seamlessly integrates all three models for end-to-end podcast creation

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Google AI API key (get yours at [ai.google.dev](https://ai.google.dev/))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/iamfaham/PodcastLab
cd podcast-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your API key:

```bash
# Option 1: Environment variable
export GOOGLE_AI_API_KEY="your_api_key_here"

# Option 2: Create a .env file
echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env
```

### Basic Usage

```python
from main import PodcastAgent

# Initialize the agent
agent = PodcastAgent()

# Create a complete podcast episode
result = agent.create_podcast_episode("The Future of Artificial Intelligence")

print(f"Generated files:")
print(f"- Image: {result['image_path']}")
print(f"- Script: {result['script_path']}")
print(f"- Video: {result['video_path']}")
```

### Command Line Usage

```bash
# Run the example
python main.py
```

### Streamlit Web Interface

For a user-friendly web interface, use the Streamlit app:

```bash
# Install Streamlit if not already installed
pip install streamlit

# Run the Streamlit app
streamlit run streamlit_app.py

# Or use the convenience script
python run_streamlit.py
```

The web interface provides:

- 🎯 Simple topic input
- 📊 Real-time progress tracking
- 🖼️ Image preview
- 📝 Script display
- 🎬 Video player
- 📥 Download buttons for all generated files

## 📖 API Reference

### PodcastAgent Class

#### `__init__(api_key: Optional[str] = None)`

Initialize the podcast agent with your Google AI API key.

#### `generate_podcast_image(custom_prompt: Optional[str] = None) -> Image.Image`

Generate a professional podcast studio image using Imagen.

**Parameters:**

- `custom_prompt`: Optional custom prompt for image generation

**Returns:** PIL Image object

#### `generate_podcast_script(topic: str) -> str`

Generate an 8-second podcast script using Gemini.

**Parameters:**

- `topic`: The topic for the podcast episode

**Returns:** Generated script text

#### `generate_podcast_video(script: str, image: Optional[Image.Image] = None, output_filename: str = "podcast_video.mp4") -> str`

Generate a podcast video using Veo 3.

**Parameters:**

- `script`: The podcast script to base the video on
- `image`: Optional starting image for the video
- `output_filename`: Name of the output video file

**Returns:** Path to the generated video file

#### `create_podcast_episode(topic: str, output_dir: str = "output", custom_image_prompt: Optional[str] = None) -> dict`

Create a complete podcast episode with image, script, and video.

**Parameters:**

- `topic`: The topic for the podcast episode
- `output_dir`: Directory to save output files
- `custom_image_prompt`: Optional custom prompt for image generation

**Returns:** Dictionary with paths to generated files and metadata

## 🎯 Examples

### Custom Image Prompt

```python
agent = PodcastAgent()

# Use a custom image prompt
custom_prompt = "Two tech entrepreneurs discussing AI in a futuristic podcast studio with holographic displays"

result = agent.create_podcast_episode(
    topic="AI in Business",
    custom_image_prompt=custom_prompt
)
```

### Individual Components

```python
agent = PodcastAgent()

# Generate just an image
image = agent.generate_podcast_image()
image.show()

# Generate just a script
script = agent.generate_podcast_script("Climate Change Solutions")
print(script)

# Generate just a video
video_path = agent.generate_podcast_video(script, image)
print(f"Video saved to: {video_path}")
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_AI_API_KEY`: Your Google AI API key (required)

### Model Configuration

The agent uses the following Google AI models:

- **Imagen**: `imagen-3.0-generate-002` for image generation
- **Gemini**: `gemini-2.0-flash-exp` for script generation
- **Veo**: `veo-3.0-generate-preview` for video generation

## 📁 Output Structure

Generated files are saved in the following structure:

```
output/
├── podcast_image_[topic].png     # Generated podcast studio image
├── podcast_script_[topic].txt    # Generated podcast script
└── podcast_video_[topic].mp4     # Generated podcast video
```

## ⚠️ Limitations

- **Video Length**: Maximum 8 seconds (Veo 3 limitation)
- **Generation Time**: Video generation can take 11 seconds to 6 minutes
- **API Costs**: Each generation uses API credits
- **File Retention**: Generated videos are stored on Google's servers for 2 days

## 🛠️ Technical Details

### Dependencies

- `google-genai>=0.8.0`: Google AI SDK
- `pillow>=10.0.0`: Image processing
- `python-dotenv>=1.0.0`: Environment variable management
- `loguru>=0.7.0`: Logging

### Error Handling

The agent includes comprehensive error handling and logging:

- API authentication errors
- Model generation failures
- File I/O errors
- Network timeouts

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:

1. Check the [Google AI documentation](https://ai.google.dev/gemini-api/docs)
2. Review the error logs generated by the agent
3. Ensure your API key has the necessary permissions

## 🔗 Related Links

- [Google AI for Developers](https://ai.google.dev/)
- [Imagen API Documentation](https://ai.google.dev/gemini-api/docs/imagen)
- [Veo API Documentation](https://ai.google.dev/gemini-api/docs/video)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
