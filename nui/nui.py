import os
import re
import sys
import subprocess
import shutil
from PIL import Image


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
        "-q",
        "--progress",
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
        "-q",
        "--progress",
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
    title = remove_from_string(uploader,title)
    uploader = process_uploader(uploader)

    return video_id, title, uploader


#should be deprecated but is still here to ensure that if there is an call no exception is thrown
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
    
def process_uploader(uploader):
    delimiters = ['_', '-', '.', ' ', ',', '/', '\\', '|', ':', ';']
    words_to_remove = ["topic", "official", "Vevo"]

    # Add "YouTube[delimiter]Channel" variations to the words_to_remove list
    youtube_channel_variants = [f"YouTube{delimiter}Channel" for delimiter in delimiters]
    words_to_remove.extend(youtube_channel_variants)

    for word in words_to_remove:
        uploader = remove_from_string(word, uploader)

    return uploader
 
def remove_from_string(replacer, target):
    replacer_lower = replacer.lower()
    target_lower = target.lower()

    # Replace all occurrences of replacer (case insensitive) with an empty string
    pattern = re.compile(re.escape(replacer_lower), re.IGNORECASE)
    modified_target, count = pattern.subn('', target)

    # Replace multiple consecutive delimiters with a single one if any substitution was made
    if count > 0:
        modified_target = re.sub(r'([_\-. ,/\\|:;])\1+', r'\1', modified_target)

    # Strip leading and trailing undesired characters and return the result
    modified_target = modified_target.strip("_- .,/\\|:;").strip()
    
    return modified_target

 
def move_download_to_output():
    download_dir = "download"
    output_dir = "output"

    if not os.path.exists(download_dir):
        print("Download directory not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Output directory created successfully.")

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

            shutil.move(src_file, dst_file)

    shutil.rmtree(download_dir)
    print("Files moved from 'download' to 'output' directory.")


def check_write_permissions():
    current_directory = os.getcwd()
    if not os.access(current_directory, os.W_OK):
        print("Error: No write permission in the current directory.")
        sys.exit(1) 

def check_override_path(override_image_path):
    """
    Check if the provided override image path is valid and if the image dimensions are within 2000x2000 pixels.

    Args:
        override_image_path (str): Path to the override image file.

    Returns:
        bool: True if the image is valid, False otherwise.
    """
    
    if os.path.isfile(override_image_path) and override_image_path.lower().endswith('.jpg'):
        # Check image dimensions
        img = Image.open(override_image_path)
        width, height = img.size
        if width <= 2000 and height <= 2000:
            return True
        else:
            print("Error: Image dimensions should not exceed 2000x2000 pixels.")
            sys.exit(1)
    else:
        print("Error: Invalid override image path or file format. Please provide a valid JPEG image.")
        sys.exit(1)

def check_absolute_path(path):
    if os.path.isabs(path):
        return path
    else:
        print("Error: Absolute path to the override image is required.")
        sys.exit(1)


def main():

    check_write_permissions()
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <Video URL | Video ID | Playlist link> [-t] [-o <override_image_path>]")
        sys.exit(1)

    url = sys.argv[1]
    
    skip_thumbnail_flag = False
    override_image_path = None
    override_image = False

    # Check for the flags in the arguments
    for i, arg in enumerate(sys.argv):
        if i == 0:  # Skip the script name at index 0
            continue
        if arg == "-t":
            skip_thumbnail_flag = True
        elif arg == "-o":
            if i + 1 < len(sys.argv):
                override_image_path = check_absolute_path(sys.argv[i + 1])
                if check_override_path(override_image_path):
                    override_image = True
            else:
                print("Error: Missing argument for -o flag.")
                sys.exit(1)
    
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


    # Copy the needed script
    path_to_self = os.path.dirname(__file__)
    thumbnail_script_path = os.path.join(path_to_self, "thumbnail1-1Crop.py")
    metadata_script_path = os.path.join(path_to_self, "embedMetaData.py")
    picard_script_path = os.path.join(path_to_self, "picardCanary.py")
    override_script_path = os.path.join(path_to_self, "overrideImage.py")
    
    # Part 4: Collect MP3 files
    mp3_files = collect_mp3_files()
    print("Number of MP3 files in current directory:", len(mp3_files))
     
    #Idea add list that holds all seen ids then id data is not lost after renaming the files
    
    # Loop over the mp3_files list
    for mp3_file in mp3_files:
        # Extract the data from the currently looked at file
        video_id, title, uploader = extract_id_title_uploader(mp3_file)
        print("ID:", video_id)
        print("Title:", title)
        print("Uploader:", uploader)
        
        
        if not skip_thumbnail_flag:
            # Run the thumbnail1-1Crop.py script
            print(f"Downloading Thumbnails for [{video_id}]")
            thumbnail_Command = ["python", thumbnail_script_path, video_id]
            subprocess.run(thumbnail_Command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Execute the script
        
        # Use the ID to run the set_mp3_tags function
        cover_image = f"{video_id}.jpg"  # Assuming thumbnail1-1Crop.py generates a JPEG image with ID as filename
        if not os.path.exists(cover_image):
            cover_image = "None"
        # metadata script execution
        metaDataCommand = ["python", metadata_script_path, mp3_file, title, uploader, cover_image, f"[{video_id}]"]
        subprocess.run(metaDataCommand)  # Execute the script
        
        # Rename the MP3 file based on extracted title and uploader
        new_filename = f"{uploader} - {title}.mp3".replace("_", " ")  # Construct new filename
        print("new filename is")
        print(new_filename)
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
    
    if override_image:
        os.chdir("download")
        mp3_files = collect_mp3_files()
        for mp3_file in mp3_files:      
            override_command = ["python", override_script_path, mp3_file, override_image_path]
            subprocess.run(override_command)
        
        os.chdir("..")
    
    move_download_to_output()

if __name__ == "__main__":
    main()
