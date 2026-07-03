import re

with open('update_videos.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace .mp4" with .mp4#t=0.001" and .mov" with .mov#t=0.001"
content = re.sub(r'(\.mp4|\.mov)\"', r'\1#t=0.001"', content)

with open('update_videos.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated update_videos.py with #t=0.001')
