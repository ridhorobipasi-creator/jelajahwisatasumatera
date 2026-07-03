import os
import re

def fix_html_in_file(filename, folder):
    if not os.path.exists(filename): return
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where the hotel section starts
    start_match = re.search(r'<!-- ═══════════════════════════════════════════ -->\s*<!-- (FRAME HOTEL|VIDEO HOTEL).*?<div class="custom-frame drone-screen-1">', content, flags=re.DOTALL)
    
    # Find where it ends
    end_match = re.search(r'<!-- ═══════════════════════════════════════════ -->\s*<!-- FRAMES BOTTOM', content, flags=re.DOTALL)
    
    if start_match and end_match:
        start_idx = start_match.start()
        end_idx = end_match.start()
        
        from update_videos import generate_hotel_html, html_drone
        
        days = int(filename.split('-')[1][0])
        hotel_html = generate_hotel_html(days, folder)
        drone_html = html_drone.format(folder=folder)
        
        replacement = hotel_html + drone_html + '\n    '
        
        content = content[:start_idx] + replacement + content[end_idx:]
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed HTML in', filename)
    else:
        print('Could not find markers in', filename)

fix_html_in_file('trip-4d3n.html', '4d3n')
fix_html_in_file('trip-3d2n.html', '3d2n')
fix_html_in_file('trip-2d1n.html', '2d1n')
