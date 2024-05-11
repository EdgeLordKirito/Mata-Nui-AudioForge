import os
import sys
import subprocess
from PIL import Image
import shutil
import re

def download_thumbnails(video_url):
    # Create folder named "temp"
    os.makedirs("temp", exist_ok=True)
    # Execute yt-dlp command to download all thumbnails
    subprocess.run(['yt-dlp', '--write-all-thumbnails', '--skip-download', video_url, '-o', 'temp/%(id)s.%(ext)s'])

def find_highest_resolution_thumbnail(folder):
    thumbnails = os.listdir(folder)
    max_resolution = 0
    max_res_thumbnail = None
    
    for thumbnail in thumbnails:
        if thumbnail.endswith('.jpg'):
            # Get the resolution of the image
            resolution = Image.open(os.path.join(folder, thumbnail)).size[1]
            if resolution > max_resolution:
                max_resolution = resolution
                max_res_thumbnail = thumbnail
    
    return max_res_thumbnail

def crop_to_square(image):
    width, height = image.size
    # Calculate the size for the square crop
    crop_size = min(width, height)
    # Calculate the starting coordinates for the crop to center it
    x_offset = (width - crop_size) // 2
    y_offset = (height - crop_size) // 2
    # Crop the square area from the center
    cropped_image = image.crop((x_offset, y_offset, x_offset + crop_size, y_offset + crop_size))
    return cropped_image

def is_playlist_link(url):
    # Check if the URL is a playlist link
    return 'playlist' in url

def extract_video_id(url):
    # Extract video ID using regex
    video_id_match = re.search(r'(?<=watch\?v=)[\w-]+', url)
    if video_id_match:
        return video_id_match.group(0)
    else:
        return None

def main(video_input):
    # Check if the input is a playlist link
    if is_playlist_link(video_input):
        print("Error: Playlist links are not supported.")
        sys.exit(1)

    # Check if the input is a full YouTube URL
    if '/watch?v=' in video_input:
        video_id = extract_video_id(video_input)
        if not video_id:
            print("Error: Invalid YouTube video URL.")
            sys.exit(1)
    else:
        video_id = video_input  # Otherwise, assume it's already a video ID
    
    # Download thumbnails
    download_thumbnails(f'https://www.youtube.com/watch?v={video_id}')
    
    # Find highest resolution thumbnail
    thumbnails_folder = "temp"
    max_res_thumbnail = find_highest_resolution_thumbnail(thumbnails_folder)
    
    if max_res_thumbnail:
        # Open the highest resolution thumbnail
        image_path = os.path.join(thumbnails_folder, max_res_thumbnail)
        image = Image.open(image_path)
        
        # Crop the image to square
        cropped_image = crop_to_square(image)
        
        # Save cropped image with video ID in filename
        cropped_image.save(f'{video_id}.jpg')
        print(f'Thumbnail downloaded, cropped, and saved as {video_id}.jpg')
        
        # Delete the "temp" folder
        shutil.rmtree(thumbnails_folder)
        print("Temp folder deleted.")
    else:
        print('No thumbnails found or error occurred.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py [YouTube Video URL or ID]")
        sys.exit(1)
        
    video_input = sys.argv[1]
    main(video_input)
