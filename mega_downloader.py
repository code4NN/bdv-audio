import sys
import os
from mega import Mega  # as you specified

def main():
    if len(sys.argv) != 4:
        print("Usage: python download_mega.py <fileid> <destination> <filename>")
        sys.exit(1)

    fileid = sys.argv[1]
    destination = sys.argv[2]
    filename = sys.argv[3]

    # TODO: Replace this with a dynamic key if needed
    url = f'https://mega.nz/file/{fileid}'

    print(f"Downloading from URL: {url}")
    print(f"Destination: {destination}")
    print(f"Filename: {filename}")

    try:
        mega = Mega()
        mega.download_url(url, destination, filename)
        print("✅ Download completed successfully.")
    except Exception as e:
        print("❌ Download failed:", e)

if __name__ == "__main__":
    main()
