#!/usr/bin/env python3
"""
Splice.com Audio Preview Downloader using Playwright
Downloads preview audio files by simulating a real browser
"""

import asyncio
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Response

async def download_splice_sample(url: str, output_dir: str = './splice_downloads'):
    """Download a sample from Splice using Playwright"""
    
    # Extract sample ID from URL
    match = re.search(r'/sounds/sample/([a-f0-9]+)', url)
    if not match:
        print(f"Could not extract sample ID from URL: {url}")
        return None
    
    sample_id = match.group(1)
    print(f"Sample ID: {sample_id}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    audio_data = None
    best_filename = f"sample_{sample_id}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Intercept network responses
        async def handle_response(response: Response):
            nonlocal audio_data, best_filename
            
            url_str = response.url
            content_type = response.headers.get('content-type', '')
            status = response.status
            
            # Look for audio content
            if status == 200 and 'audio/' in content_type:
                print(f"\n[AUDIO] {url_str[:100]}...")
                print(f"    Content-Type: {content_type}")
                print(f"    Content-Length: {response.headers.get('content-length', 'unknown')}")
                
                try:
                    content = await response.body()
                    print(f"    First 20 bytes: {content[:20].hex()}")
                    print(f"    First 20 bytes (ascii): {content[:20]}")
                    
                    # Check if it starts like audio
                    is_mp3_id3 = content[:3] == b'ID3'
                    is_mp3_frame = content[:2] in [b'\xff\xfb', b'\xff\xfa', b'\xff\xfc', b'\xff\xf3', b'\xff\xf2']
                    is_wav = content[:4] == b'RIFF'
                    is_ogg = content[:4] == b'OggS'
                    
                    print(f"    Is MP3 (ID3): {is_mp3_id3}")
                    print(f"    Is MP3 (frame): {is_mp3_frame}")
                    print(f"    Is WAV: {is_wav}")
                    print(f"    Is OGG: {is_ogg}")
                    
                    if is_mp3_id3 or is_mp3_frame or is_wav or is_ogg:
                        if len(content) > len(audio_data or b''):
                            audio_data = content
                            print(f"    => VALID AUDIO! Size: {len(content)} bytes")
                        else:
                            print(f"    => Smaller than current best")
                    else:
                        # Could still be valid - let's check content more
                        # Splice might scramble the audio
                        print(f"    => Unknown format, but saving anyway...")
                        if len(content) > len(audio_data or b''):
                            audio_data = content
                            print(f"    => Keeping ({len(content)} bytes)")
                            
                except Exception as e:
                    print(f"    Error: {e}")
                    import traceback
                    traceback.print_exc()
        
        page.on('response', handle_response)
        
        print(f"\nNavigating to: {url}")
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Get sample name from page
            try:
                name_elem = await page.query_selector('h1')
                if name_elem:
                    name = await name_elem.inner_text()
                    name = re.sub(r'[<>:"/\\|?*]', '_', name.strip())
                    if name:
                        best_filename = name
                        print(f"Sample name: {name}")
            except:
                pass
            
            # Try to click play
            play_selectors = [
                'button[aria-label*="play" i]',
                'button:has(svg)',
                '[data-testid*="play"]',
                '.play-button',
            ]
            
            for selector in play_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        try:
                            await elem.click(timeout=1000)
                            print("Clicked play button")
                            await page.wait_for_timeout(3000)
                            break
                        except:
                            continue
                except:
                    pass
            
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        await browser.close()
    
    # Save the downloaded audio
    if audio_data:
        # Determine extension based on content
        if audio_data[:3] == b'ID3' or audio_data[:2] in [b'\xff\xfb', b'\xff\xfa', b'\xff\xfc', b'\xff\xf3', b'\xff\xf2']:
            ext = 'mp3'
        elif audio_data[:4] == b'RIFF':
            ext = 'wav'
        elif audio_data[:4] == b'OggS':
            ext = 'ogg'
        else:
            ext = 'mp3'  # Default to mp3
        
        filename = f"{best_filename}.{ext}"
        file_path = output_path / filename
        
        counter = 1
        while file_path.exists():
            file_path = output_path / f"{best_filename}_{counter}.{ext}"
            counter += 1
        
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        print(f"\n[OK] Saved: {file_path} ({len(audio_data)} bytes)")
        return file_path
    
    print("\n[ERROR] Could not download audio.")
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python splice_browser.py <splice_url> [output_dir]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './splice_downloads'
    
    result = asyncio.run(download_splice_sample(url, output_dir))

if __name__ == '__main__':
    main()