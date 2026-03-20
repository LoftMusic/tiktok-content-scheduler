#!/usr/bin/env python3
"""
Splice.com Audio Preview Downloader
Downloads preview audio files from Splice.com samples
"""

import requests
import re
import os
import sys
import json
from pathlib import Path
from urllib.parse import urljoin

def get_sample_id(url):
    """Extract sample ID from Splice URL"""
    # URL format: https://splice.com/sounds/sample/{ID}/...
    match = re.search(r'/sounds/sample/([a-f0-9]+)', url)
    if match:
        return match.group(1)
    return None

def extract_audio_from_page(url):
    """Extract audio URL from the Splice page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        
        sample_id = get_sample_id(url)
        
        # Method 1: Look for preview URL in embedded JSON data
        # Splice often embeds data in script tags
        json_patterns = [
            r'"previewUrl"\s*:\s*"([^"]+)"',
            r'"preview_url"\s*:\s*"([^"]+)"',
            r'"mp3Url"\s*:\s*"([^"]+)"',
            r'"audioUrl"\s*:\s*"([^"]+)"',
            r'"url"\s*:\s*"(https://[^"]*\.mp3[^"]*)"',
            r'"soundPreviewUrl"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, html)
            if match:
                audio_url = match.group(1)
                # Clean URL - remove trailing backslash and escape chars
                audio_url = audio_url.rstrip('\\').strip()
                if audio_url.startswith('//'):
                    audio_url = 'https:' + audio_url
                elif not audio_url.startswith('http'):
                    audio_url = 'https://splice.com' + audio_url
                return audio_url, f'sample_{sample_id}'
        
        # Method 2: Look for .mp3 URLs directly
        mp3_matches = re.findall(r'(https?://[^\s"\'<>]+\.mp3[^\s"\'<>]*)', html)
        if mp3_matches:
            # Filter for splice CDN URLs
            for mp3_url in mp3_matches:
                if 'splice' in mp3_url.lower() or 'cdn' in mp3_url.lower():
                    return mp3_url.split('"')[0].split("'")[0], f'sample_{sample_id}'
        
        # Method 3: Look for audio tags
        audio_match = re.search(r'<audio[^>]*src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if audio_match:
            audio_url = audio_match.group(1)
            if not audio_url.startswith('http'):
                audio_url = urljoin(url, audio_url)
            return audio_url, f'sample_{sample_id}'
        
        # Method 4: Try the Splice GraphQL API
        # Splice uses GraphQL for many operations
        graphql_url = "https://splice.com/graphql"
        
        query = """
        query GetSound($id: ID!) {
            sound(id: $id) {
                id
                name
                previewUrl
                mp3Url
            }
        }
        """
        
        graphql_response = requests.post(
            graphql_url,
            headers={
                **headers,
                'Content-Type': 'application/json',
            },
            json={
                'query': query,
                'variables': {'id': sample_id}
            }
        )
        
        if graphql_response.status_code == 200:
            data = graphql_response.json()
            if 'data' in data and 'sound' in data['data']:
                sound = data['data']['sound']
                for field in ['previewUrl', 'mp3Url', 'audioUrl']:
                    if field in sound and sound[field]:
                        return sound[field], sound.get('name', f'sample_{sample_id}')
        
        # Method 5: Direct preview API endpoint
        preview_api = f"https://api.splice.com/v2/sounds/{sample_id}"
        api_response = requests.get(preview_api, headers=headers)
        if api_response.status_code == 200:
            try:
                data = api_response.json()
                for field in ['previewUrl', 'preview_url', 'mp3Url', 'audioUrl']:
                    if field in data and data[field]:
                        return data[field], data.get('name', f'sample_{sample_id}')
            except:
                pass
        
        # Method 6: Try to construct preview URL pattern
        # Splice often uses CDN URLs with the sample ID
        cdn_patterns = [
            f"https://s3.amazonaws.com/splice-preview/sounds/{sample_id}.mp3",
            f"https://cdn.splice.com/sounds/preview/{sample_id}.mp3",
            f"https://splice-preview.s3.amazonaws.com/{sample_id}.mp3",
        ]
        
        for cdn_url in cdn_patterns:
            test_resp = requests.head(cdn_url, headers=headers, allow_redirects=True)
            if test_resp.status_code == 200:
                return cdn_url, f'sample_{sample_id}'
        
        return None, None
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def download_audio(url, filename, output_dir='.'):
    """Download audio file"""
    output_path = Path(output_dir) / f"{filename}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://splice.com/',
        'Accept': '*/*',
    }
    
    print(f"Downloading: {url}")
    print(f"Saving to: {output_path}")
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[OK] Downloaded: {output_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error downloading: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python splice_downloader.py <splice_url> [output_dir]")
        print("Example: python splice_downloader.py https://splice.com/sounds/sample/750243... ./downloads")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './splice_downloads'
    
    sample_id = get_sample_id(url)
    if not sample_id:
        print(f"Could not extract sample ID from URL: {url}")
        sys.exit(1)
    
    print(f"Sample ID: {sample_id}")
    print("Searching for audio preview URL...")
    
    audio_url, filename = extract_audio_from_page(url)
    
    if audio_url:
        # Clean filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        print(f"Found audio: {filename}")
        download_audio(audio_url, filename, output_dir)
    else:
        print("Could not find audio preview URL")
        print("\nTip: Try opening the URL in a browser and checking the Network tab")
        print("     Look for .mp3 requests when clicking play on the sample")

if __name__ == '__main__':
    main()