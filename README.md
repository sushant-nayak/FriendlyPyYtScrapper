# FriendlyPyYtScrapper

A Node.js project with Python code to download YouTube videos without external dependencies like yt-dlp.

## Features

- ✅ Download YouTube videos in various qualities (144p to 1080p)
- ✅ Choose specific resolutions (360p, 480p, 720p, 1080p, etc.)
- ✅ Extract video information (title, duration, formats)
- ✅ Download audio only
- ✅ No external dependencies - uses YouTube's internal API
- ✅ Anti-bot measures with retry logic
- ✅ Simple CLI interface
- ✅ Node.js and Python hybrid architecture

## Prerequisites

- Node.js (v14 or higher)
- Python 3.7+
- No pip packages required (uses standard library only)

## Installation

```bash
npm install
```

## Usage

### As a CLI tool

```bash
# Download a video (best quality)
node src/cli.js download <youtube-url>

# Download with specific resolution
node src/cli.js download <youtube-url> --quality 720p
node src/cli.js download <youtube-url> --quality 480p
node src/cli.js download <youtube-url> --quality 360p

# Download worst quality (smallest file)
node src/cli.js download <youtube-url> --quality worst

# Get video info
node src/cli.js info <youtube-url>

# List all available formats
node src/cli.js formats <youtube-url>

# Download audio only
node src/cli.js download <youtube-url> --audio-only

# Specify output directory
node src/cli.js download <youtube-url> --output ./my-videos --quality 1080p
```

### As a Node.js module

```javascript
import YtScrapper from './src/index.js';

const scrapper = new YtScrapper();

// Get video info
const info = await scrapper.getInfo('https://www.youtube.com/watch?v=VIDEO_ID');
console.log(info);

// Download video with specific quality
await scrapper.download('https://www.youtube.com/watch?v=VIDEO_ID', './downloads', {
    quality: '720p'
});

// Download best quality
await scrapper.download('https://www.youtube.com/watch?v=VIDEO_ID', './downloads', {
    quality: 'best'
});
```

## Available Quality Options

- `best` - Highest available resolution (default)
- `worst` - Lowest available resolution
- `1080p` - Full HD
- `720p` - HD
- `480p` - Standard Definition
- `360p` - Low Definition
- `240p` - Very Low
- `144p` - Minimal

Note: If the exact resolution is not available, the closest match will be automatically selected.

## How it works

This project uses:
- **Python scripts** to handle YouTube video extraction and downloading
- **YouTube's innertube API** with multiple client contexts (Android, iOS, Web)
- **Anti-bot measures**: User agent rotation, retry logic, gzip handling
- **Node.js** as the main interface and orchestration layer
- **Zero external dependencies** - only Python standard library

## Disclaimer

This tool is for educational purposes only. Please respect YouTube's Terms of Service and copyright laws.

## Usage Examples


### Get video info
```bash
node src/cli.js info "https://www.youtube.com/watch?v=vZdbbN3FCzE"
```

### Download video (best quality)
```bash
node src/cli.js download "https://www.youtube.com/watch?v=vZdbbN3FCzE" --quality best
```

### Download 720p version
```bash
node src/cli.js download "https://www.youtube.com/watch?v=vZdbbN3FCzE" --quality 720p
```

### Download audio only
```bash
node src/cli.js download "https://www.youtube.com/watch?v=vZdbbN3FCzE" --audio-only
```

### List all available formats
```bash
node src/cli.js formats "https://www.youtube.com/watch?v=vZdbbN3FCzE"
```

### Download with custom output directory and quality
```bash
node src/cli.js download "https://www.youtube.com/watch?v=vZdbbN3FCzE" --output ./my-videos --quality 480p
```