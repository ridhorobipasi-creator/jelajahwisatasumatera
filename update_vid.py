import os, re
for file in os.listdir('.'):
    if file.endswith('.html'):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'<video\s+controls\s+playsinline\s+preload=\"metadata\">', '<video controls autoplay loop muted playsinline preload="metadata">', content)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated videos in ' + file)
