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
import subprocess
import tempfile


class YouTubeDownloader:
    def __init__(self):
        # Rotate between multiple realistic user agents (updated to latest versions)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
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
        
        # Fallback contexts to try (prioritize iOS and Android)
        self.fallback_contexts = [
            {
                "client": {
                    "clientName": "IOS",
                    "clientVersion": "19.09.3",
                    "deviceModel": "iPhone14,3",
                    "hl": "en",
                    "gl": "US",
                    "utcOffsetMinutes": 0
                }
            },
            {
                "client": {
                    "clientName": "ANDROID_EMBEDDED_PLAYER",
                    "clientVersion": "19.09.36",
                    "androidSdkVersion": 30,
                    "hl": "en",
                    "gl": "US"
                }
            },
            {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20240201.00.00",
                    "hl": "en",
                    "gl": "US"
                }
            }
        ]
    
    def _get_headers(self, for_api=False):
        """Get randomized headers to avoid bot detection"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        if for_api:
            headers.update({
                'Accept': 'application/json',
                'Origin': 'https://www.youtube.com',
                'Referer': 'https://www.youtube.com/',
                'X-Youtube-Client-Name': '1',
                'X-Youtube-Client-Version': '2.20240201.00.00',
            })
        else:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            })
        
        return headers
    
    def _make_request(self, url, data=None, headers=None, max_retries=3, is_api=False):
        """Make HTTP request with retry logic"""
        if headers is None:
            headers = self._get_headers(for_api=is_api)
        
        for attempt in range(max_retries):
            try:
                # Add small random delay between retries to appear more human-like
                if attempt > 0:
                    delay = random.uniform(1.0, 3.0)
                    sys.stderr.write(f"Waiting {delay:.1f}s before retry...\n")
                    time.sleep(delay)
                
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
            
            for idx, context in enumerate(contexts_to_try):
                # Add delay between context attempts to avoid rate limiting
                if idx > 0:
                    time.sleep(random.uniform(0.5, 1.5))
                payload = {
                    "videoId": video_id,
                    "context": context
                }
                
                try:
                    response_text = self._make_request(api_url, data=payload, is_api=True)
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
    
    def _download_stream(self, url, filepath, description=""):
        """Helper method to download a single stream"""
        headers = self._get_headers()
        req = urllib.request.Request(url, headers=headers)
        
        if description:
            sys.stderr.write(f"{description}\n")
        
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
                        sys.stderr.write(f"\r  Progress: {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                        sys.stderr.flush()
        
        sys.stderr.write("\n")
    
    def download_video(self, url, output_path='.', quality='best', audio_only=False, merge=True):
        """Download video from YouTube
        
        Args:
            url: YouTube video URL
            output_path: Directory to save video
            quality: Resolution (e.g., '720p', '1080p', '480p', 'best', 'worst')
            audio_only: Download audio only
            merge: Merge separate video and audio streams (requires ffmpeg)
        """
        try:
            info = self.get_video_info(url)
            
            if 'error' in info:
                return info
            
            formats = info['formats']
            
            if not formats:
                return {'error': 'No formats available with direct URLs'}
            
            # Ensure output directory exists
            os.makedirs(output_path, exist_ok=True)
            
            # Generate safe filename
            safe_title = re.sub(r'[^\w\s-]', '', info['title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)[:100]  # Limit length
            
            # Handle audio-only download
            if audio_only:
                audio_formats = [f for f in formats if f.get('hasAudio') and not f.get('hasVideo')]
                if not audio_formats:
                    return {'error': 'No audio-only formats found'}
                
                audio_formats.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
                selected_format = audio_formats[0]
                
                extension = 'mp3'
                filename = f"{safe_title}_{info['id']}.{extension}"
                filepath = os.path.join(output_path, filename)
                
                sys.stderr.write(f"Downloading: {info['title']}\n")
                sys.stderr.write(f"Audio bitrate: {selected_format.get('bitrate', 'unknown')}\n\n")
                
                self._download_stream(selected_format['url'], filepath, "Downloading audio...")
                
                sys.stderr.write("✓ Download completed!\n")
                
                return {
                    'success': True,
                    'filename': filename,
                    'filepath': filepath,
                    'title': info['title']
                }
            
            # Helper function to extract resolution number
            def get_resolution(f):
                quality_str = f.get('quality', '')
                if isinstance(quality_str, str) and 'p' in quality_str:
                    try:
                        return int(quality_str.replace('p', ''))
                    except:
                        pass
                return 0
            
            # Check if we should merge (high quality video + audio)
            video_formats = [f for f in formats if f.get('hasVideo')]
            audio_formats = [f for f in formats if f.get('hasAudio') and not f.get('hasVideo')]
            combined_formats = [f for f in formats if f.get('hasAudio') and f.get('hasVideo')]
            
            # Select video format based on quality
            if quality == 'best':
                video_formats.sort(key=get_resolution, reverse=True)
                selected_video = video_formats[0] if video_formats else None
            elif quality == 'worst':
                video_formats.sort(key=get_resolution)
                selected_video = video_formats[0] if video_formats else None
            elif quality.endswith('p'):
                try:
                    target_res = int(quality.replace('p', ''))
                    exact_match = [f for f in video_formats if get_resolution(f) == target_res]
                    if exact_match:
                        selected_video = exact_match[0]
                    else:
                        video_formats.sort(key=lambda f: abs(get_resolution(f) - target_res))
                        selected_video = video_formats[0] if video_formats else None
                        if selected_video:
                            actual_res = get_resolution(selected_video)
                            sys.stderr.write(f"Requested {quality} not available, using closest: {actual_res}p\n")
                except ValueError:
                    return {'error': f'Invalid quality format: {quality}. Use format like "720p" or "best"'}
            else:
                return {'error': f'Invalid quality: {quality}. Use "best", "worst", or a resolution like "720p"'}
            
            if not selected_video:
                return {'error': 'No suitable video format found'}
            
            # Check if selected video has audio
            has_audio = selected_video.get('hasAudio', False)
            
            # Decide whether to merge
            if merge and not has_audio and audio_formats:
                # Need to download and merge separate streams
                sys.stderr.write(f"Downloading: {info['title']}\n")
                sys.stderr.write(f"Video quality: {selected_video.get('quality', 'unknown')}\n")
                sys.stderr.write(f"Mode: Separate video + audio (will merge with FFmpeg)\n\n")
                
                # Select best audio
                audio_formats.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
                selected_audio = audio_formats[0]
                
                # Create temporary files
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_temp:
                    video_temp_path = video_temp.name
                
                with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as audio_temp:
                    audio_temp_path = audio_temp.name
                
                try:
                    # Download video stream
                    self._download_stream(selected_video['url'], video_temp_path, "Downloading video stream...")
                    
                    # Download audio stream
                    self._download_stream(selected_audio['url'], audio_temp_path, "Downloading audio stream...")
                    
                    # Merge with FFmpeg
                    sys.stderr.write("\nMerging video and audio with FFmpeg...\n")
                    
                    filename = f"{safe_title}_{info['id']}.mp4"
                    filepath = os.path.join(output_path, filename)
                    
                    # Use FFmpeg to merge
                    ffmpeg_cmd = [
                        'ffmpeg', '-y',
                        '-i', video_temp_path,
                        '-i', audio_temp_path,
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-strict', 'experimental',
                        filepath
                    ]
                    
                    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        return {'error': f'FFmpeg merge failed: {result.stderr}'}
                    
                    sys.stderr.write("✓ Merge completed!\n")
                    sys.stderr.write("✓ Download completed!\n")
                    
                    return {
                        'success': True,
                        'filename': filename,
                        'filepath': filepath,
                        'title': info['title'],
                        'merged': True
                    }
                
                finally:
                    # Clean up temp files
                    if os.path.exists(video_temp_path):
                        os.unlink(video_temp_path)
                    if os.path.exists(audio_temp_path):
                        os.unlink(audio_temp_path)
            
            else:
                # Download single stream (has audio or merge disabled)
                filename = f"{safe_title}_{info['id']}.mp4"
                filepath = os.path.join(output_path, filename)
                
                sys.stderr.write(f"Downloading: {info['title']}\n")
                sys.stderr.write(f"Quality: {selected_video.get('quality', 'unknown')}\n")
                
                if not has_audio:
                    sys.stderr.write("⚠️  Warning: Video has no audio (merge disabled or no audio stream available)\n")
                
                sys.stderr.write("\n")
                
                self._download_stream(selected_video['url'], filepath, "Downloading...")
                
                sys.stderr.write("✓ Download completed!\n")
                
                return {
                    'success': True,
                    'filename': filename,
                    'filepath': filepath,
                    'title': info['title'],
                    'merged': False
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
        merge = '--no-merge' not in sys.argv  # Merge by default
        
        # Extract quality parameter
        quality = 'best'
        if '--quality' in sys.argv:
            quality_idx = sys.argv.index('--quality')
            if quality_idx + 1 < len(sys.argv):
                quality = sys.argv[quality_idx + 1]
        
        result = downloader.download_video(url, output_path, quality=quality, audio_only=audio_only, merge=merge)
        print(json.dumps(result, indent=2))
    
    else:
        print(json.dumps({'error': f'Unknown command: {command}'}))
        sys.exit(1)


if __name__ == '__main__':
    main()
