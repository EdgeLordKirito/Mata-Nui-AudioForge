# Mata-Nui-AudioForge

Mata-Nui-AudioForge is a Python script that allows you to download YouTube videos as audio files and enrich them with metadata using Picard.
## Installation

To install the required dependencies, run the following command in your terminal:
```
pip install -r requirements.txt
```
This will install all necessary Python packages, including yt-dlp and Picard.

## Usage

To use Mata-Nui-AudioForge, follow these steps:
1. Open your terminal or command prompt.
2. Navigate to the directory where the nui.py script is located.
3. Run the script using Python, providing a YouTube video URL, video ID, or playlist link as an argument:
```
python script.py <Video URL | Video ID | Playlist link> [-t] [-o] [-over | -override <override_image_path>]
```
Replace <Video URL | Video Id | Playlist link> with the URL, video ID, or playlist link of the YouTube content you want to download and process.
Optional:  
The -t flag removes the automatic thumbnail embedding that is done.  
The -o flag replaces all covers with ones sourced from youtube.
the -over or -override flag overrides all embeded covers of the final files with the specified image an absolut path to the image is required.  

### Simplifying Execution

For easier access to the Mata-Nui-AudioForge script, consider creating a shell or batch script to invoke it directly. You can add the directory containing the script to your system's PATH environment variable to execute it from any location.

## Notes

  -  Ensure that you have Python installed on your system before running the script.
  -  Make sure you have sufficient disk space available, especially if you are downloading large playlists.
  -  It's recommended to run the script in a directory where you have write permissions, as it will create and modify files during the download and metadata enrichment process.

For additional assistance or troubleshooting, refer to the project documentation or contact the developer.

Enjoy using Mata-Nui-AudioForge to manage your audio collection!
