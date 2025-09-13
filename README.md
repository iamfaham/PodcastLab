---
title: PodcastLab
emoji: 🎙️
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# PodcastLab - AI-Powered Podcast Creator

🎙️ **Create professional podcasts with AI using Google's Imagen, Gemini, and Veo models**

## Features

- **AI-Generated Content**: Create engaging podcast scripts using Google's Gemini AI
- **Visual Storytelling**: Generate custom podcast cover images with Google's Imagen
- **Video Podcasts**: Create video podcasts using Google's Veo model
- **Professional Quality**: High-quality audio and video output
- **Easy to Use**: Simple Streamlit interface for seamless podcast creation

## How to Use

1. **Enter Your Topic**: Input any topic you want to create a podcast about
2. **Configure Settings**: Choose the number of parts, duration, and other preferences
3. **Generate Content**: Let AI create the script, images, and video content
4. **Download Results**: Get your complete podcast package ready for publishing

## Requirements

- Google AI API Key (set as `GOOGLE_AI_API_KEY` environment variable)
- Internet connection for AI model access

## Environment Variables

Make sure to set the following environment variable in your Hugging Face Space:

- `GOOGLE_AI_API_KEY`: Your Google AI API key for accessing Gemini, Imagen, and Veo models

## Getting Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Navigate to the API section
4. Create a new API key
5. Copy the key and add it to your Hugging Face Space environment variables

## Technical Details

- **Framework**: Streamlit
- **AI Models**: Google Gemini, Imagen, Veo
- **Video Processing**: MoviePy
- **Image Processing**: Pillow
- **Deployment**: Docker on Hugging Face Spaces

## License

MIT License - feel free to use and modify for your projects!

---

**Note**: This application requires a valid Google AI API key to function. The key is not included in the repository for security reasons.
