import os
import urllib.request
import zipfile
import tarfile

def download_ffmpeg_for_linux():
    # Define download URL for the Linux static build
    ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    
    # Local file paths for saving the tarball and extracting FFmpeg
    download_dir = "./ffmpeg_for_linux"
    tarball_path = os.path.join(download_dir, "ffmpeg-release-amd64-static.tar.xz")
    output_dir = os.path.join(download_dir, "ffmpeg_binary")
    
    # Ensure directories exist
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Download the FFmpeg tarball
    print("🔄 Downloading FFmpeg for Linux...")
    urllib.request.urlretrieve(ffmpeg_url, tarball_path)
    print(f"✅ FFmpeg tarball downloaded: {tarball_path}")
    
    # Extract the tarball
    print("🔄 Extracting FFmpeg tarball...")
    with tarfile.open(tarball_path, "r:xz") as tar:
        tar.extractall(path=output_dir)
    print(f"✅ FFmpeg extracted to: {output_dir}")
    
    # Locate the FFmpeg binary
    extracted_folder = [f for f in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, f))]
    if not extracted_folder:
        raise RuntimeError("FFmpeg binary folder not found after extraction.")
    ffmpeg_binary_path = os.path.join(output_dir, extracted_folder[0], "ffmpeg")
    
    # Confirm binary location
    print(f"✅ FFmpeg binary ready at: {ffmpeg_binary_path}")
    print("👉 You can now upload the binary folder to your server.")
    
    # Optionally clean up tarball
    os.remove(tarball_path)

# Run the script
download_ffmpeg_for_linux()
