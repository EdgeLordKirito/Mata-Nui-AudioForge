import sys
import eyed3

def embed_metadata(mp3_path, title, artist, cover_path, comment):
    try:
        # Load MP3 file
        audio = eyed3.load(mp3_path)

        # Set title and artist with underscores replaced by spaces
        audio.tag.title = title.replace("_", " ")
        audio.tag.artist = artist.replace("_", " ")

        # Embed cover image if cover_path is not 'None'
        if cover_path.lower() != 'none':
            with open(cover_path, 'rb') as f:
                cover_data = f.read()
            audio.tag.images.set(3, cover_data, "image/jpeg", u"Cover")

        # Set comment
        audio.tag.comments.set(comment)

        # Save changes
        audio.tag.save()
        print("Metadata embedded successfully.")
    except Exception as e:
        print("Error embedding metadata:", e)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py <mp3_path> <title> <artist> <cover_path> <comment>")
        sys.exit(1)

    mp3_path = sys.argv[1]
    title = sys.argv[2]
    artist = sys.argv[3]
    cover_path = sys.argv[4]
    comment = sys.argv[5]

    embed_metadata(mp3_path, title, artist, cover_path, comment)
