---
title: PodcastLab
emoji: 🎙️
colorFrom: blue
colorTo: purple
sdk: streamlit
pinned: false
license: mit
short_description: AI podcast creator using Google's Imagen, Gemini, and Veo.
---

# PodcastLab - AI-Powered Podcast Creator

🎙️ **Create professional podcasts with AI using Google's Imagen, Gemini, and Veo models**

## Demo

https://github.com/user-attachments/assets/30e09cfd-ade6-4911-9ae2-9f8c5c2ead6b

## Features

- **AI-Generated Content**: Create complete, end-to-end podcast scripts using Google's Gemini AI
- **Google Search Grounding**: Access real-time, factual information with Google Search integration
- **Visual Storytelling**: Generate custom podcast cover images with Google's Imagen
- **Video Podcasts**: Create square video podcasts using Google's Veo model
- **Professional Quality**: High-quality audio and video output
- **Easy to Use**: Simple Streamlit interface for seamless podcast creation
- **Source Citations**: Automatic citation generation for factual claims

## How to Use

1. **Enter Your Topic**: Input any topic you want to create a podcast about
2. **Enable Search Grounding**: Toggle the "Use Google Search for factual data" option for current information
3. **Configure Settings**: Choose the number of parts, duration, and other preferences
4. **Generate Content**: Let AI create the script, images, and video content
5. **Download Results**: Get your complete podcast package ready for publishing

## Google Search Grounding

The podcast agent now supports Google Search grounding, which allows Gemini to access real-time web information for more accurate and up-to-date content. When enabled:

- **Real-time Information**: Get current facts and data about your topic
- **Source Citations**: Automatic generation of citations for factual claims
- **Search Queries**: See what search queries were used to gather information
- **Source Links**: Access the original sources used in the podcast script

This is particularly useful for topics involving:

- Current events and news
- Recent technological developments
- Up-to-date statistics and data
- Latest trends and developments

## Script Structure

Each podcast episode is generated as 3 complete segments:

1. **Part 1 (Introduction)**: Welcome message, topic introduction, and what listeners will learn
2. **Part 2 (Main Content)**: Key insights, facts, and detailed discussion with host interactions
3. **Part 3 (Conclusion)**: Key takeaways, wrap-up, and call-to-action

Each part is designed to feel like a complete segment of a real podcast episode with natural host conversations and smooth transitions.

## Requirements

- Google AI API Key (set in Streamlit Cloud secrets or as `GOOGLE_AI_API_KEY` environment variable)
- Internet connection for AI model access

## Deployment on Streamlit Cloud

### Option 1: Using Streamlit Cloud Secrets (Recommended)

1. **Fork this repository** to your GitHub account
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Click "New app"** and connect your GitHub repository
4. **Set up secrets** in the Streamlit Cloud dashboard:
   - Go to your app's settings
   - Navigate to "Secrets" section
   - Add your Google AI API key:
     ```toml
     [secrets]
     GOOGLE_AI_API_KEY = "your-google-ai-api-key-here"
     ```
5. **Deploy** your app

### Option 2: Using Environment Variables

1. **Fork this repository** to your GitHub account
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Click "New app"** and connect your GitHub repository
4. **Set environment variables** in the Streamlit Cloud dashboard:
   - Go to your app's settings
   - Navigate to "Environment variables" section
   - Add: `GOOGLE_AI_API_KEY` = `your-google-ai-api-key-here`
5. **Deploy** your app

## Getting Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Navigate to the API section
4. Create a new API key
5. Copy the key and add it to your Streamlit Cloud secrets or environment variables

## Technical Details

- **Framework**: Streamlit
- **AI Models**: Google Gemini, Imagen, Veo
- **Video Processing**: MoviePy
- **Image Processing**: Pillow
- **Aspect Ratio**: Square (1:1) for videos
- **Deployment**: Streamlit Cloud

## License

MIT License - feel free to use and modify for your projects!

---

**Note**: This application requires a valid Google AI API key to function. The key is not included in the repository for security reasons. The cost may range between $5 to $9 per video creation. Use it at your own risk.
