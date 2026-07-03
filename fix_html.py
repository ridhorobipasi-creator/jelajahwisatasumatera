import re

for file in ['trip-4d3n.html', 'trip-3d2n.html', 'trip-2d1n.html']:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        continue
    
    # Fix the drone paths so they all point to 5d4n
    content = content.replace('assets/4d3n/drone-', 'assets/5d4n/drone-')
    content = content.replace('assets/3d2n/drone-', 'assets/5d4n/drone-')
    content = content.replace('assets/2d1n/drone-', 'assets/5d4n/drone-')
    
    # Now ensure all .mp4 and .mov have #t=0.001
    # First, let's remove any existing #t=0.001 to avoid duplicates
    content = content.replace('.mp4#t=0.001"', '.mp4"')
    content = content.replace('.mov#t=0.001"', '.mov"')
    
    # Now add it
    content = re.sub(r'(\.mp4|\.mov)"', r'\1#t=0.001"', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed', file)
