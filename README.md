# FriendlyPyYtScrapper

A Node.js project with Python code to download YouTube videos, mimicking yt-dlp functionality without using it as a dependency.

## Features

- Download YouTube videos in various qualities
- Extract video information (title, duration, formats)
- Download audio only
- Simple CLI interface
- Node.js and Python hybrid architecture

## Prerequisites

- Node.js (v14 or higher)
- Python 3.7+
- pip packages: `requests`, `beautifulsoup4`

## Installation

```bash
npm install
pip install requests beautifulsoup4
```

## Usage

### As a CLI tool

```bash
# Download a video
node src/cli.js download <youtube-url>

# Get video info
node src/cli.js info <youtube-url>

# Download audio only
node src/cli.js download <youtube-url> --audio-only
```

### As a Node.js module

```javascript
import YtScrapper from './src/index.js';

const scrapper = new YtScrapper();

// Get video info
const info = await scrapper.getInfo('https://www.youtube.com/watch?v=VIDEO_ID');
console.log(info);

// Download video
await scrapper.download('https://www.youtube.com/watch?v=VIDEO_ID', './downloads');
```

## How it works

This project uses:
- **Python scripts** to handle YouTube video extraction and downloading
- **Node.js** as the main interface and orchestration layer
- Direct HTTP requests to YouTube's player API and video streams

## Disclaimer

This tool is for educational purposes only. Please respect YouTube's Terms of Service and copyright laws.

# Setup
npm install
pip3 install requests beautifulsoup4

# Usage Examples

## Get video info
node src/cli.js info "https://www.youtube.com/watch?v=VIDEO_ID"

## Download video
node src/cli.js download "https://www.youtube.com/watch?v=VIDEO_ID"

## Download audio only
node src/cli.js download "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only

## List formats
node src/cli.js formats "https://www.youtube.com/watch?v=VIDEO_ID"

E.g. -
https://www.youtube.com/watch?v=DTgrzlQtOd0