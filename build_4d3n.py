import re

def build():
    with open('trip-5d4n.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Update metadata and tags
    html = html.replace('5D4N', '4D3N')
    html = html.replace('5 Hari 4 Malam', '4 Hari 3 Malam')
    
    # We will slice out the body to reconstruct it
    match = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    if not match:
        print("Body not found")
        return
    
    body_inner = match.group(1)
    
    # Find the floating WhatsApp script and everything after it
    wa_match = re.search(r'(<!-- ── Floating WhatsApp ── -->.*)', body_inner, re.DOTALL)
    footer_scripts = wa_match.group(1) if wa_match else ''
    
    # Extract the Back Button
    back_btn_match = re.search(r'(<!-- ── Back Button ── -->.*?</a>)', body_inner, re.DOTALL)
    back_btn = back_btn_match.group(1) if back_btn_match else ''
    
    # Extract Drone Video HTML block (Screen 1 and Screen 2)
    drone_match = re.search(r'(<!-- ══════════════════════════════════════════════════════════════ -->\s*<!-- FRAME 8a — Custom HTML Drone Videos \(Screen 1\).*?)(?=\s*<!-- ═══════════════════════════════════════════ -->\s*<!-- FRAME 9)', body_inner, re.DOTALL)
    drone_html = drone_match.group(1) if drone_match else ''
    
    # Construct Image Frames
    frames_top = '''
    <!-- ═══════════════════════════════════════════ -->
    <!-- FRAMES TOP -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="frame">
        <img src="assets/4d3n/frame-02.webp" alt="Pricelist 4D3N Cover" fetchpriority="high" decoding="async">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-03.webp" alt="Frame 2" decoding="async" loading="lazy">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-04.webp" alt="Frame 3" decoding="async" loading="lazy">
    </div>
'''

    frames_bottom = '''
    <!-- ═══════════════════════════════════════════ -->
    <!-- FRAMES BOTTOM -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="frame">
        <img src="assets/4d3n/frame-06.webp" alt="Frame 6" decoding="async" loading="lazy">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-07.webp" alt="Frame 7" decoding="async" loading="lazy">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-08.webp" alt="Frame 8" decoding="async" loading="lazy">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-09.webp" alt="Frame 9" decoding="async" loading="lazy">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-10.webp" alt="Frame 10" decoding="async" loading="lazy">
    </div>
    <div class="frame">
        <img src="assets/4d3n/frame-11.webp" alt="Frame 11" decoding="async" loading="lazy">
    </div>
'''

    hotel_html = '''
    <!-- ═══════════════════════════════════════════ -->
    <!-- FRAME HOTEL — Video Hotel                  -->
    <!-- ═══════════════════════════════════════════ -->
    <div class="custom-frame drone-screen-1">
        <h2 class="drone-title">(VIDEO HOTEL YANG AKAN DIGUNAKAN)</h2>
        
        <div class="drone-grid-2">
            <div class="vid-card">
                <div class="vid-label">HOTEL DAY 1</div>
                <video controls loop muted playsinline preload="metadata">
                    <source src="assets/4d3n/hotel-day1-web.mp4" type="video/mp4">
                </video>
            </div>
            <div class="vid-card">
                <div class="vid-label">HOTEL DAY 2</div>
                <video controls loop muted playsinline preload="metadata">
                    <source src="assets/4d3n/hotel-day2-web.mp4" type="video/mp4">
                </video>
            </div>
        </div>

        <div class="drone-grid-1">
            <div class="vid-card">
                <div class="vid-label">HOTEL DAY 3</div>
                <video controls loop muted playsinline preload="metadata">
                    <source src="assets/4d3n/hotel-day3-web.mp4" type="video/mp4">
                </video>
            </div>
        </div>
    </div>
'''
    
    new_body = f"""
<body>
    {back_btn}
    {frames_top}
    {hotel_html}
    {drone_html}
    {frames_bottom}
    
    {footer_scripts}
</body>
"""

    new_html = re.sub(r'<body>.*?</body>', new_body, html, flags=re.DOTALL)
    
    with open('trip-4d3n.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print("trip-4d3n.html built successfully.")

build()
