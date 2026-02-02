# Installation Guide

## Prerequisites

1. **Node.js**: Version 14 or higher
   ```bash
   node --version
   ```

2. **Python 3**: Version 3.7 or higher
   ```bash
   python3 --version
   ```

3. **pip**: Python package manager
   ```bash
   pip3 --version
   ```

## Setup Steps

### 1. Install Node.js Dependencies

```bash
npm install
```

### 2. Install Python Dependencies

```bash
pip3 install -r python/requirements.txt
```

Or install manually:
```bash
pip3 install requests beautifulsoup4
```

### 3. Make Python Script Executable (Optional)

```bash
chmod +x python/yt_downloader.py
```

### 4. Make CLI Executable (Optional)

```bash
chmod +x src/cli.js
```

## Verify Installation

Test that everything is working:

```bash
# Test info command
node src/cli.js info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Troubleshooting

### Python not found
If you get a "python3 not found" error, you might need to:
- Install Python 3 from python.org
- Update the spawn command in `src/index.js` to use `python` instead of `python3`

### Module import errors
Make sure you're using Node.js with ES modules support (v14+) and that `"type": "module"` is in package.json.

### Permission denied
Run the chmod commands above or use `node` explicitly:
```bash
node src/cli.js download <url>
```

## Alternative: Using npm scripts

You can also use the npm scripts defined in package.json:

```bash
npm run cli info "https://www.youtube.com/watch?v=VIDEO_ID"
```
