import os
import re
import sys
import subprocess
import shutil

def extract_video_id(url):
    # Extract video ID using regex
    video_id_match = re.search(r'(?<=watch\?v=)[\w-]+', url)
    if video_id_match:
        return video_id_match.group(0)
    else:
        return None

def is_playlist_link(url):
    # Check if the URL is a playlist link
    return 'playlist' in url

def create_download_directory():
    if not os.path.exists("download"):
        os.makedirs("download")
        print("Download directory created successfully.")
    else:
        print("Download directory already exists. Stopping execution.")
        sys.exit(1)

def download_playlist(video_id):
    # Command to download the playlist using yt-dlp
    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "320k",
        "-o", "[%(id)s]§§§%(title)s+++%(uploader)s.%(ext)s",
        "--restrict-filenames",
        "--windows-filenames",  
        video_id
    ]
    subprocess.run(command)

def download_video(video_id):
    # Command to download the video using yt-dlp
    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "320k",
        "-o", "[%(id)s]§§§%(title)s+++%(uploader)s.%(ext)s",
        "--restrict-filenames",
        "--windows-filenames",
        video_id
    ]
    subprocess.run(command)

def collect_mp3_files():
    mp3_files = []
    current_directory = os.getcwd()
    for file in os.listdir(current_directory):
        if file.endswith(".mp3"):
            mp3_files.append(file)
    return mp3_files
    
import re

def extract_id_title_uploader(filename):
    # The id is in []
    id_match = re.search(r'\[(.*?)\]', filename)
    if id_match:
        video_id = id_match.group(1)
    else:
        video_id = None

    # The title is after 3 § signs
    title_match = re.search(r'§{3}(.*?)\+{3}', filename)
    if title_match:
        title = title_match.group(1)
    else:
        title = None

    # The uploader is after 3 + signs, excluding the .mp3 extension
    uploader_match = re.search(r'\+{3}(.*?)(?=\.\w+$)', filename)
    if uploader_match:
        uploader = uploader_match.group(1)
    else:
        uploader = None

    # Trim the title to remove leading and following '-', '_', and spaces
    title = remove_uploader_from_title(uploader,title)

    return video_id, title, uploader


def remove_uploader_from_title(uploader, title):
    uploader_copy = uploader
    title_copy = title

    uploader_lower = uploader_copy.lower()
    title_lower = title_copy.lower()

    if uploader_lower in title_lower:
        title_temp = title_lower.replace(uploader_lower, " ")
        title_temp = [c.upper() if o.isupper() else c for c, o in zip(title_temp, title_copy)]

        # Construct the final title string
        modified_title = ''.join(title_temp).strip("-_ ").strip()
        return modified_title

    return title
    
    
def move_download_to_output():
    download_dir = "download"
    output_dir = "output"

    if not os.path.exists(download_dir):
        print("Download directory not found.")
        return

    if not os.path.exists(output_dir):
        os.rename(download_dir, output_dir)
        print("Download directory renamed to 'output'.")
    else:
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(output_dir, file)

                if os.path.exists(dst_file):
                    filename, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(os.path.join(output_dir, f"{filename}_{counter}{ext}")):
                        counter += 1
                    dst_file = os.path.join(output_dir, f"{filename}_{counter}{ext}")

                shutil.copy2(src_file, dst_file)

        shutil.rmtree(download_dir)
        print("Files moved from 'download' to 'output' directory.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <YouTube video URL or video ID>")
        sys.exit(1)

    url = sys.argv[1]
    is_playlist = is_playlist_link(url)
    
    # Check if the input is a full URL or just a video ID
    if 'watch?v=' in url:
        video_id = extract_video_id(url)
    else:
        video_id = url  # Assume it's already a video ID
    
    # Print Video ID and Playlist status
    print("Video ID:", video_id)
    print("Is Playlist:", is_playlist)
    
    # Branch based on whether it's a playlist
    if is_playlist:
        create_download_directory()
        os.chdir("download")
        download_playlist(video_id)
        pass
    else:
        create_download_directory()
        os.chdir("download")
        download_video(video_id)
        pass
    
    # Part 4: Collect MP3 files
    mp3_files = collect_mp3_files()
    print("Number of MP3 files in current directory:", len(mp3_files))
    
    # Copy the needed script
    thumbnail_script_path = os.path.join(os.path.dirname(__file__), "thumbnail1-1Crop.py")
    metadata_script_path = os.path.join(os.path.dirname(__file__), "embedMetaData.py")
    picard_script_path = os.path.join(os.path.dirname(__file__), "picardCanary.py")
    
    # Loop over the mp3_files list
    for mp3_file in mp3_files:
        # Extract the data from the currently looked at file
        video_id, title, uploader = extract_id_title_uploader(mp3_file)
        print("ID:", video_id)
        print("Title:", title)
        print("Uploader:", uploader)
        
        # Run the thumbnail1-1Crop.py script
        subprocess.run(["python", thumbnail_script_path, video_id])  # Execute the script
        
        # Use the ID to run the set_mp3_tags function
        cover_image = f"{video_id}.jpg"  # Assuming thumbnail1-1Crop.py generates a JPEG image with ID as filename
        # metadata script execution
        subprocess.run(["python", metadata_script_path, mp3_file, title, uploader, cover_image])  # Execute the script
        
        # Rename the MP3 file based on extracted title and uploader
        new_filename = f"{uploader} - {title}.mp3"  # Construct new filename
        os.rename(mp3_file, new_filename)  # Rename the file
        
    # Cleanup step  
    # Remove all JPEG files
    for file in os.listdir(os.getcwd()):
        if file.endswith(".jpg"):
            os.remove(os.path.join(os.getcwd(), file))
            
    # Change directory one level up
    os.chdir("..")

    # Run the picardCanary subprocess with the download directory as the first argument
    picard_command = ["python", picard_script_path, os.path.abspath("download")]
    subprocess.run(picard_command)
    
    move_download_to_output()

if __name__ == "__main__":
    main()
