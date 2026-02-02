#!/usr/bin/env python3
"""
YouTube Video Downloader - No external dependencies
Uses YouTube's innertube API with anti-bot measures
"""

import json
import sys
import os
import re
import urllib.request
import urllib.parse
import urllib.error
import time
import random
import gzip


class YouTubeDownloader:
    def __init__(self):
        # Rotate between multiple realistic user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Use Android client - typically has fewer restrictions
        self.innertube_context = {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "19.09.36",
                "androidSdkVersion": 30,
                "hl": "en",
                "gl": "US",
                "utcOffsetMinutes": 0
            }
        }
        
        # Fallback contexts to try
        self.fallback_contexts = [
            {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20240201.00.00",
                    "hl": "en",
                    "gl": "US"
                }
            },
            {
                "client": {
                    "clientName": "IOS",
                    "clientVersion": "19.09.3",
                    "deviceModel": "iPhone14,3",
                    "hl": "en",
                    "gl": "US"
                }
            }
        ]
    
    def _get_headers(self):
        """Get randomized headers to avoid bot detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _make_request(self, url, data=None, headers=None, max_retries=3):
        """Make HTTP request with retry logic"""
        if headers is None:
            headers = self._get_headers()
        
        for attempt in range(max_retries):
            try:
                if data:
                    data = json.dumps(data).encode('utf-8')
                    headers['Content-Type'] = 'application/json'
                
                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read()
                    
                    # Handle gzip encoding
                    if response.headers.get('Content-Encoding') == 'gzip':
                        content = gzip.decompress(content)
                    
                    # Decode bytes to string
                    if isinstance(content, bytes):
                        content = content.decode('utf-8')
                    
                    return content
            except urllib.error.HTTPError as e:
                if e.code == 403 and attempt < max_retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    sys.stderr.write(f"\nReceived 403, retrying in {wait_time:.1f}s...\n")
                    time.sleep(wait_time)
                    continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise
    
    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Could not extract video ID from URL")
    
    def get_video_info(self, url):
        """Extract video information using innertube API"""
        try:
            video_id = self.extract_video_id(url)
            
            # Use innertube API - more reliable than HTML scraping
            api_url = "https://www.youtube.com/youtubei/v1/player"
            
            # Try primary context first
            contexts_to_try = [self.innertube_context] + self.fallback_contexts
            
            for context in contexts_to_try:
                payload = {
                    "videoId": video_id,
                    "context": context
                }
                
                try:
                    response_text = self._make_request(api_url, data=payload)
                    player_response = json.loads(response_text)
                    
                    if 'playabilityStatus' in player_response:
                        status = player_response['playabilityStatus'].get('status')
                        if status == 'OK':
                            # Success! Process and return
                            break
                        elif status == 'UNPLAYABLE':
                            # Try next context
                            continue
                        else:
                            reason = player_response['playabilityStatus'].get('reason', 'Unknown error')
                            # Don't return error yet, try next context
                            if context == contexts_to_try[-1]:  # Last context
                                return {'error': f'Video not available: {reason}'}
                            continue
                except Exception as e:
                    if context == contexts_to_try[-1]:  # Last context
                        raise
                    continue
            
            video_details = player_response.get('videoDetails', {})
            streaming_data = player_response.get('streamingData', {})
            
            formats = []
            
            # Process formats
            for fmt in streaming_data.get('formats', []):
                if fmt.get('url'):
                    formats.append({
                        'itag': fmt.get('itag'),
                        'quality': fmt.get('qualityLabel', fmt.get('quality')),
                        'mimeType': fmt.get('mimeType'),
                        'url': fmt.get('url'),
                        'hasAudio': True,
                        'hasVideo': True
                    })
            
            # Process adaptive formats
            for fmt in streaming_data.get('adaptiveFormats', []):
                if fmt.get('url'):
                    mime_type = fmt.get('mimeType', '')
                    formats.append({
                        'itag': fmt.get('itag'),
                        'quality': fmt.get('qualityLabel', fmt.get('quality')),
                        'mimeType': mime_type,
                        'url': fmt.get('url'),
                        'hasAudio': 'audio' in mime_type,
                        'hasVideo': 'video' in mime_type,
                        'bitrate': fmt.get('bitrate')
                    })
            
            info = {
                'id': video_id,
                'title': video_details.get('title', 'Unknown'),
                'duration': video_details.get('lengthSeconds', '0'),
                'author': video_details.get('author', 'Unknown'),
                'viewCount': video_details.get('viewCount', '0'),
                'description': video_details.get('shortDescription', ''),
                'formats': formats,
                'thumbnail': video_details.get('thumbnail', {}).get('thumbnails', [{}])[-1].get('url', '')
            }
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def download_video(self, url, output_path='.', quality='best', audio_only=False):
        """Download video from YouTube"""
        try:
            info = self.get_video_info(url)
            
            if 'error' in info:
                return info
            
            formats = info['formats']
            
            if not formats:
                return {'error': 'No formats available with direct URLs'}
            
            # Filter formats
            if audio_only:
                formats = [f for f in formats if f.get('hasAudio') and not f.get('hasVideo')]
            else:
                # Prefer formats with both audio and video
                formats = [f for f in formats if f.get('hasAudio') and f.get('hasVideo')]
            
            if not formats:
                return {'error': 'No suitable format found. Video may require signature decryption.'}
            
            # Sort by quality/bitrate
            if audio_only:
                formats.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
            else:
                # Sort by quality (try to get highest quality)
                def quality_key(f):
                    quality_str = f.get('quality', '')
                    if isinstance(quality_str, str) and 'p' in quality_str:
                        try:
                            return int(quality_str.replace('p', ''))
                        except:
                            pass
                    return 0
                formats.sort(key=quality_key, reverse=True)
            
            selected_format = formats[0]
            
            # Ensure output directory exists
            os.makedirs(output_path, exist_ok=True)
            
            # Generate safe filename
            safe_title = re.sub(r'[^\w\s-]', '', info['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)[:100]  # Limit length
            extension = 'mp3' if audio_only else 'mp4'
            filename = f"{safe_title}_{info['id']}.{extension}"
            filepath = os.path.join(output_path, filename)
            
            # Download the file
            download_url = selected_format['url']
            
            # Use custom headers for download
            headers = self._get_headers()
            req = urllib.request.Request(download_url, headers=headers)
            
            sys.stderr.write(f"Downloading: {info['title']}\n")
            sys.stderr.write(f"Quality: {selected_format.get('quality', 'unknown')}\n")
            
            with urllib.request.urlopen(req, timeout=60) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192
                
                with open(filepath, 'wb') as out_file:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            sys.stderr.write(f"\rProgress: {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                            sys.stderr.flush()
            
            sys.stderr.write("\n✓ Download completed!\n")
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'title': info['title']
            }
            
        except Exception as e:
            return {'error': str(e)}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Usage: python yt_downloader.py <command> <url> [options]'}))
        sys.exit(1)
    
    command = sys.argv[1]
    url = sys.argv[2]
    
    downloader = YouTubeDownloader()
    
    if command == 'info':
        info = downloader.get_video_info(url)
        print(json.dumps(info, indent=2))
    
    elif command == 'download':
        output_path = sys.argv[3] if len(sys.argv) > 3 else './downloads'
        audio_only = '--audio-only' in sys.argv
        
        result = downloader.download_video(url, output_path, audio_only=audio_only)
        print(json.dumps(result, indent=2))
    
    else:
        print(json.dumps({'error': f'Unknown command: {command}'}))
        sys.exit(1)


if __name__ == '__main__':
    main()
