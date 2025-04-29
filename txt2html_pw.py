import os
import sys
from datetime import datetime

def extract_video_id(url):
    """Extract video ID from PW URL containing /master.mpd"""
    print(f"Extracting ID from URL: {url}")  # Debug log
    
    # If URL is already in player format, return None to skip processing
    if 'player.muftukmall.site/?id=' in url:
        print(f"URL is already a player URL, skipping ID extraction")  # Debug log
        return None
        
    # Extract from MPD URL
    if '/master.mpd' in url:
        parts = url.split('/')
        try:
            index = parts.index('master.mpd')
            if index > 0:
                video_id = parts[index - 1]
                print(f"Extracted ID from MPD URL: {video_id}")  # Debug log
                return video_id
        except ValueError:
            pass
    print("No video ID found in URL")  # Debug log
    return None

def clean_url(url):
    """Clean and extract proper URL from potentially malformed string"""
    # If the URL contains a title prefix, remove it
    if ':https://' in url:
        url = 'https://' + url.split(':https://')[-1]
    return url.strip()

def create_html_file(file_name, batch_name, contents):
    """Convert text file to HTML with PW player format"""
    try:
        content_cards = []

        # Process each line
        for line in contents:
            if ':' in line:
                try:
                    text, url = [item.strip('\n').strip() for item in line.split(':', 1)]
                    print(f"\nProcessing line - Text: {text}")  # Debug log
                    print(f"Original URL: {url}")  # Debug log
                    
                    # Clean the URL
                    url = clean_url(url)
                    print(f"Cleaned URL: {url}")  # Debug log
                    
                    # Handle player URLs directly
                    if url.startswith('https://player.muftukmall.site/?id='):
                        print("URL is already in player format, using as-is")  # Debug log
                        content_cards.append(f'<div class="content-card"><a href="javascript:void(0)" onclick="playVideo(\'{url}\')">{text}</a></div>')
                        continue

                    # Handle MPD URLs
                    video_id = extract_video_id(url)
                    if video_id:
                        # Create player URL for PW videos
                        player_url = f'https://player.muftukmall.site/?id={video_id}'
                        print(f"Created player URL: {player_url}")  # Debug log
                        content_cards.append(f'<div class="content-card"><a href="javascript:void(0)" onclick="playVideo(\'{player_url}\')">{text}</a></div>')
                        continue

                    # Handle PDF URLs
                    if url.endswith('.pdf'):
                        print("Processing PDF URL")  # Debug log
                        content_cards.append(f'<div class="content-card"><a href="{url}" target="_blank">{text}</a></div>')
                        continue

                    # Skip invalid URLs
                    print(f"Skipping invalid URL: {url}")

                except Exception as e:
                    print(f"Error processing line: {line}. Error: {str(e)}")
                    continue

        # Read template file
        with open('template_pw.html', 'r', encoding='utf-8') as f:
            template = f.read()

        # Replace content in template
        html_content = template.replace('tbody_content', '\n'.join(content_cards))
        html_content = html_content.replace('batch_name', batch_name)

        # Write output file
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\nSuccessfully created HTML file: {file_name}")
        print(f"Total entries processed: {len(contents)}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python txt2html_pw.py input.txt")
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return

    if not input_file.endswith('.txt'):
        print("Error: Input file must be a .txt file")
        return

    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{os.path.splitext(input_file)[0]}_{timestamp}.html"
    batch_name = os.path.splitext(os.path.basename(input_file))[0]

    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            contents = f.readlines()
        
        if create_html_file(output_file, batch_name, contents):
            print("\nInstructions:")
            print("1. Open the generated HTML file in Chrome for best experience")
            print("2. The player supports fullscreen and orientation changes")
            print("3. Use the search bar to filter content")
            print("4. Click on any title to play the video")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 