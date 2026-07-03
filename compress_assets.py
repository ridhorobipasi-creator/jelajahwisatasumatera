import os
import subprocess
from PIL import Image

def compress_images():
    folder = 'assets/4d3n'
    print("--- CONVERTING PNG TO WEBP ---")
    for file in os.listdir(folder):
        if file.endswith('.png'):
            # Delete frame-05 because it's no longer used in the website code
            if file == 'frame-05.png':
                png_path = os.path.join(folder, file)
                os.remove(png_path)
                print(f"Deleted unused {file}")
                continue
                
            png_path = os.path.join(folder, file)
            webp_path = os.path.splitext(png_path)[0] + '.webp'
            
            try:
                with Image.open(png_path) as img:
                    img.save(webp_path, 'WEBP', quality=80)
                orig_size = os.path.getsize(png_path) / (1024 * 1024)
                new_size = os.path.getsize(webp_path) / (1024 * 1024)
                print(f"Converted {file} -> {os.path.basename(webp_path)} ({orig_size:.2f}MB -> {new_size:.2f}MB, saved {((orig_size-new_size)/orig_size)*100:.1f}%)")
                os.remove(png_path)
            except Exception as e:
                print(f"Error converting {file}: {e}")

def compress_videos():
    folder = 'assets/4d3n'
    print("\n--- COMPRESSING MP4 VIDEOS USING FFMPEG ---")
    for file in os.listdir(folder):
        if file.endswith('.mp4') and not file.endswith('_temp.mp4'):
            mp4_path = os.path.join(folder, file)
            temp_path = os.path.join(folder, file.replace('.mp4', '_temp.mp4'))
            
            orig_size = os.path.getsize(mp4_path) / (1024 * 1024)
            print(f"Compressing {file} (Original Size: {orig_size:.2f} MB)...")
            
            # Compress using FFmpeg with CRF 28 (very high compression, good mobile quality)
            # Preset fast, target AAC 128k audio
            cmd = [
                'ffmpeg', '-y', '-i', mp4_path,
                '-vcodec', 'libx264', '-crf', '28', '-preset', 'fast',
                '-acodec', 'aac', '-b:a', '128k', temp_path
            ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                new_size = os.path.getsize(temp_path) / (1024 * 1024)
                if new_size < orig_size:
                    os.remove(mp4_path)
                    os.rename(temp_path, mp4_path)
                    print(f"Compressed {file} -> {orig_size:.2f}MB -> {new_size:.2f}MB (saved {((orig_size-new_size)/orig_size)*100:.1f}%)")
                else:
                    os.remove(temp_path)
                    print(f"Compression did not reduce size for {file}, keeping original.")
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"Error compressing {file}: {e}")

if __name__ == '__main__':
    compress_images()
    compress_videos()
    print("\nCompression finished!")
