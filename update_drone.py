import os

files = ['trip-4d3n.html', 'trip-3d2n.html', 'trip-2d1n.html']

for file in files:
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace specific drone paths to use the 5d4n folder so they share the same video files
        content = content.replace('assets/4d3n/drone-', 'assets/5d4n/drone-')
        content = content.replace('assets/3d2n/drone-', 'assets/5d4n/drone-')
        content = content.replace('assets/2d1n/drone-', 'assets/5d4n/drone-')
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file} drone paths")
