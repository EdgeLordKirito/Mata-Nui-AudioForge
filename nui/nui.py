import os
import re
import sys
import subprocess
import shutil
from PIL import Image
from itertools import count


def print_error(message):
    # ANSI escape code for red color text
    RED_COLOR_CODE = '\033[91m'
    # ANSI escape code to reset color to default
    RESET_COLOR_CODE = '\033[0m'
    
    # Print the message in red color
    print(RED_COLOR_CODE + message + RESET_COLOR_CODE)

def print_success(message):
    # ANSI escape code for green color text
    GREEN_COLOR_CODE = '\033[92m'
    # ANSI escape code to reset color to default
    RESET_COLOR_CODE = '\033[0m'
    
    # Print the message in green color
    print(GREEN_COLOR_CODE + message + RESET_COLOR_CODE)

def print_highlighted(message, color):
    # Dictionary mapping color names to ANSI escape codes
    color_codes = {
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'orange': '\033[38;5;208m',  # Orange
    }
    # ANSI escape code for default text color (black or white)
    default_text_color_code = '\033[39m'
    # ANSI escape code to reset color to default
    reset_color_code = '\033[0m'
    
    # Check if the specified color is supported
    if color in color_codes:
        # Print the message in the specified color
        print(color_codes[color] + message + reset_color_code)
    else:
        # Print the message in default text color
        print(default_text_color_code + message + reset_color_code)


def is_standard_keyboard_ascii(s):
    return all(32 <= ord(char) <= 126 for char in s)

def ensure_unique_filename(filename):
    # Check if the file already exists
    if os.path.exists(filename):
        # Split the filename and extension
        name, extension = os.path.splitext(filename)
        # Initialize counter
        counter = 1
        # Increment the counter until a unique filename is found
        while os.path.exists(f"{name}({counter}){extension}"):
            counter += 1
        # Construct the unique filename
        return f"{name}({counter}){extension}"
    else:
        # If the file doesn't exist, return the original filename
        return filename

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
        #print_success("Download directory created successfully.")
    else:
        print_error("Download directory already exists. Stopping execution.")
        sys.exit(1)

def listen_to_yt_dlp_stdout(yt_dlp_command):
    # Start the subprocess and capture its stdout
    process = subprocess.Popen(yt_dlp_command, stdout=subprocess.PIPE, text=True)

    # Listen to the subprocess stdout line by line
    for line in process.stdout:
        # Check if the line contains the specific messages we're interested in
        if "Downloading item" in line:
            line = line.replace("[download]", "").strip()
            parts = line.split()
            num1 = parts[2]  # First number
            num2 = parts[4]  # Second number

            # Colorize the numbers
            colored_num1 = f"\033[32m{num1}\033[0m"  # Green for num1
            colored_num2 = f"\033[33m{num2}\033[0m"  # Yellow for num2

            # Construct the colored output
            colored_output = f"Downloading {colored_num1} / {colored_num2}"
            print(colored_output)

def download_playlist(video_id):
    # Command to download the playlist using yt-dlp
    command = [
        "yt-dlp",
        #"-q",
        #"--progress",
        "-f", "bestaudio",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "320k",
        "-o", "[%(id)s]§§§%(title)s+++%(uploader)s.%(ext)s",
        #"--restrict-filenames",
        "--windows-filenames",  
        video_id
    ]
    print_highlighted("Downloading Playlist this may take a while","magenta")
    print()
    listen_to_yt_dlp_stdout(command)
    
    index = video_id.find("/playlist?list=")

    # Extract the substring after "/playlist?list="
    playlist_id = video_id[index+len("/playlist?list="):]
    
    #print_success(f"Downloaded Playlist: {playlist_id}")

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
        #"--restrict-filenames",
        "--windows-filenames",
        video_id
    ]
    print_highlighted("Downloading File this may take a while","magenta")
    subprocess.run(command)
    #print_success(f"Downloaded File: {video_id}")

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
    title = process_title(title)
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
    
def process_title(title):
    delimiters = ['_', '-', '.', ' ', ',', '/', '\\', '|', ':', ';']
    words_to_remove = ["topic", "official", "Vevo", "[Audio]", "Audio"]

    # Add "YouTube[delimiter]Channel" variations to the words_to_remove list
    youtube_channel_variants = [f"YouTube{delimiter}Channel" for delimiter in delimiters]
    words_to_remove.extend(youtube_channel_variants)

    for word in words_to_remove:
        title = remove_from_string(word, title)

    return title    
 
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
        print_error("Download directory not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        #print_success("Output directory created successfully.")

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
    print_success("Files moved from 'download' to 'output' directory.")


def check_write_permissions():
    current_directory = os.getcwd()
    if not os.access(current_directory, os.W_OK):
        print_error("Error: No write permission in the current directory.")
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
            print_error("Error: Image dimensions should not exceed 2000x2000 pixels.")
            sys.exit(1)
    else:
        print_error("Error: Invalid override image path or file format. Please provide a valid JPEG image.")
        sys.exit(1)

def check_absolute_path(path):
    if os.path.isabs(path):
        return path
    else:
        print_error("Error: Absolute path to the override image is required.")
        sys.exit(1)

def copy_image_to_download_dir(override_image_path, download_dir):
    # Copy the file to the download directory
    shutil.copy(override_image_path, download_dir)


def resolve_path(file_path):
    # Check if the provided path is an absolute path
    if os.path.isabs(file_path):
        return file_path
    else:
        # Remove leading "./" or ".\" from the relative path if present
        if file_path.startswith("./") or file_path.startswith(".\\"):
            file_path = file_path[2:]
        
        # Prepend the directory of the current script to the relative path and normalize it
        base_dir = os.path.dirname(__file__)
        path = os.path.join(base_dir, file_path)
        return path

def main():

    check_write_permissions()
    
    if len(sys.argv) < 2:
        print("Usage: python nui.py <Video URL | Video ID | Playlist link> [-t] [-o] [-over | -override <override_image_path>]")
        sys.exit(1)

    url = sys.argv[1]
    
    debug_mode = False
    original_thumbnail_flag = False
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
            original_thumbnail_flag = True
        elif arg == "-debug" or arg == "-d":
            debug_mode = True  # Assuming debug_mode is a boolean variable
        elif arg == "-over" or arg == "-override":
            if i + 1 < len(sys.argv):
                override_image_path = resolve_path(sys.argv[i + 1])
                if check_override_path(override_image_path):
                    override_image = True
                    skip_thumbnail_flag = True
            else:
                print_error("Error: Missing argument for -over/-override flag.")
                sys.exit(1)
    
    # Check for conflicting flags after parsing all arguments
    if skip_thumbnail_flag and original_thumbnail_flag:
        print_error("Error: Skipping thumbnails and embedding the original thumbnails is not possible at the same time.")
        sys.exit(1)
    
    
    is_playlist = is_playlist_link(url)
    
    # Check if the input is a full URL or just a video ID
    if 'watch?v=' in url:
        video_id = extract_video_id(url)
    else:
        video_id = url  # Assume it's already a video ID
    
    # Print Video ID and Playlist status
    if debug_mode:
        print("Video ID:", video_id)
        print("Is Playlist:", is_playlist)
    
    create_download_directory()
    
    # Branch based on whether it's a playlist
    if is_playlist:
        os.chdir("download")
        download_playlist(video_id)
        print()
        pass
    else:
        os.chdir("download")
        download_video(video_id)
        print()
        pass


    # Copy the needed script
    path_to_self = os.path.dirname(__file__)
    thumbnail_script_path = os.path.join(path_to_self, "thumbnail1-1Crop.py")
    metadata_script_path = os.path.join(path_to_self, "embedMetaData.py")
    picard_script_path = os.path.join(path_to_self, "picardCanary.py")
    override_script_path = os.path.join(path_to_self, "overrideImage.py")
    
    # Part 4: Collect MP3 files
    mp3_files = collect_mp3_files()
    if debug_mode:
        print("Number of MP3 files in current directory:", len(mp3_files))
     
    #Idea add list that holds all seen ids then id data is not lost after renaming the files
    
    #build dictionary to contain key value pairs that link mp3 to its image so that it can be overwritten after picard
    
    mp3_to_image = {}
    seen_ids = []
    counter = count(start=1)
    
    # Loop over the mp3_files list
    for mp3_file in mp3_files:
        # Extract the data from the currently looked at file
        video_id, title, uploader = extract_id_title_uploader(mp3_file)
        if debug_mode:
            print("ID:", video_id)
            print("Title:", title)
            print("Uploader:", uploader)
        
        if video_id in seen_ids:
            continue
        
        if not skip_thumbnail_flag:
            # Run the thumbnail1-1Crop.py script
            print_highlighted(f"Downloading Thumbnails for [{video_id}]", "cyan")
            thumbnail_Command = ["python", thumbnail_script_path, video_id]
            subprocess.run(thumbnail_Command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Execute the script
        
        # Use the ID to run the set_mp3_tags function
        cover_image = f"{video_id}.jpg"  # Assuming thumbnail1-1Crop.py generates a JPEG image with ID as filename
        if not os.path.exists(cover_image):
            cover_image = "None"
        # metadata script execution
        metaDataCommand = ["python", metadata_script_path, mp3_file, title, uploader, cover_image, f"[{video_id}]"]
        completed_process = subprocess.run(metaDataCommand, capture_output=True, text=True)  # Execute the script
        #print_highlighted(completed_process.stdout, "cyan")
        
        # Rename the MP3 file based on extracted title and uploader
        
        #prepend ascii number to non ascii starting string
        if not is_standard_keyboard_ascii(uploader):
            next_value = next(counter)
            uploader = f"{next_value}_{uploader}"
        
        
        new_filename = f"{uploader} - {title}.mp3".replace("_", " ")  # Construct new filename
        new_filename = ensure_unique_filename(new_filename)
        mp3_to_image[new_filename] = cover_image
        #add increment if already exist
        os.rename(mp3_file, new_filename)  # Rename the file
        seen_ids.append(video_id)
        
            
    # Change directory one level up
    os.chdir("..")

    # Run the picardCanary subprocess with the download directory as the first argument
    picard_command = ["python", picard_script_path, os.path.abspath("download")]
    picard = subprocess.run(picard_command, capture_output=True, text=True)
    if debug_mode:
        print_success(picard.stdout)
    
    os.chdir("download")
    
    if original_thumbnail_flag:
        print_highlighted("Setting original thumbnails", "cyan")
        for mp3_file, image_file in mp3_to_image.items():
            # Check if the image file is None
            if image_file is None:
                continue  # Skip the call if value is None
    
            # Construct the override command
            override_command = ["python", override_script_path, mp3_file, image_file]
    
            # Call the override script subprocess
            subprocess.run(override_command)
      
    
    if override_image:
        print_highlighted("Overriding Cover images", "cyan")
        #os.chdir("download")
        mp3_files = collect_mp3_files()
        for mp3_file in mp3_files:      
            override_command = ["python", override_script_path, mp3_file, override_image_path]
            completed_process = subprocess.run(override_command, capture_output=True, text=True)

    # Cleanup step
    # Remove all JPEG files
    if debug_mode:
        print_highlighted("Cleaning Up Jpg files", "yellow")
    for file in os.listdir(os.getcwd()):
        if file.endswith(".jpg"):
            os.remove(os.path.join(os.getcwd(), file))
    
    os.chdir("..")
    
    move_download_to_output()

if __name__ == "__main__":
    main()
