import os
import re

css_to_add = """
        /* ── Custom HTML Frames for Drone Videos ── */
        .custom-frame {
            width: 100%;
            max-width: 480px;
            margin: 0 auto;
            background: radial-gradient(circle at top right, #0d2611, #040a05);
            padding: 40px 15px;
            font-family: 'Arial', sans-serif;
            color: #fff;
            position: relative;
            line-height: 1.4;
        }
        
        .drone-screen-2 {
            background: radial-gradient(circle at bottom left, #0d2611, #040a05);
            padding-top: 20px;
            padding-bottom: 60px;
        }

        .drone-title {
            text-align: center;
            font-size: 18px;
            font-weight: 900;
            color: #fff;
            margin-bottom: 24px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 0.5px;
            line-height: 1.3;
        }

        .drone-grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }

        .drone-grid-1 {
            display: grid;
            grid-template-columns: 1fr;
            padding: 0 15%;
            margin-bottom: 24px;
        }

        .vid-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 8px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .vid-card .vid-label {
            font-size: 10.5px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #e0f2e3;
            text-transform: uppercase;
            min-height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.2;
        }

        .vid-card video {
            width: 100%;
            aspect-ratio: 9 / 16;
            object-fit: cover;
            border-radius: 8px;
            background: #111;
            display: block;
        }

        .drone-alert {
            text-align: center;
            margin-top: 32px;
            padding: 0 10px;
        }

        .drone-logo {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            margin-bottom: 12px;
            border: 2px solid #25D366;
            background: #fff;
            padding: 2px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .drone-alert p {
            font-size: 13.5px;
            font-weight: 800;
            color: #d8f5d6;
            line-height: 1.5;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 0.3px;
        }
"""

js_to_add = """
    <!-- ── Video Controller Script ── -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const videos = document.querySelectorAll('video');
            
            videos.forEach(video => {
                video.style.opacity = '1';
                
                video.addEventListener('play', () => {
                    videos.forEach(v => {
                        if (v !== video && !v.paused) {
                            v.pause();
                        }
                    });
                });
            });
        });
    </script>
</body>
"""

html_drone = """
        <!-- ══════════════════════════════════════════════════════════════ -->
        <!-- DRONE VIDEOS (Screen 1 & 2)                                    -->
        <!-- ══════════════════════════════════════════════════════════════ -->
        <div class="custom-frame drone-screen-1">
            <h2 class="drone-title">(HASIL VIDEO DRONE + EDITING)</h2>
            
            <div class="drone-grid-2">
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>DRONE DJI MAVIC 4 PRO</div>
                    <video controls loop muted playsinline preload="metadata">
                        <source src="assets/{folder}/drone-1-web.mp4" type="video/mp4">
                    </video>
                </div>
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DJI MAVIC 4 PRO</div>
                    <video controls loop muted playsinline preload="metadata">
                        <source src="assets/{folder}/drone-2-web.mp4" type="video/mp4">
                    </video>
                </div>
            </div>

            <div class="drone-grid-1">
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DJI MINI 3 & MAVIC 4 PRO</div>
                    <video controls loop muted playsinline preload="metadata">
                        <source src="assets/{folder}/drone-3-web.mp4" type="video/mp4">
                    </video>
                </div>
            </div>
        </div>

        <div class="custom-frame drone-screen-2">
            <div class="drone-grid-2">
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>DRONE FPV DJI AVATA 360</div>
                    <video controls loop muted playsinline preload="metadata">
                        <source src="assets/{folder}/drone-4-web.mp4" type="video/mp4">
                    </video>
                </div>
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DRONE DJI MINI 3</div>
                    <video controls loop muted playsinline preload="metadata">
                        <source src="assets/{folder}/drone-5-web.mp4" type="video/mp4">
                    </video>
                </div>
            </div>

            <div class="drone-alert">
                <img src="assets/avatar.jpg" alt="Logo Jelajahwisatasumatera" class="drone-logo">
                <p>SEMUA VIDEO DIATAS ASLI DARI GEAR CAMERA DAN DRONE KAMI,<br>BUKAN AMBIL VIDEO ORANG LAIN!!</p>
            </div>
        </div>

        <hr>
"""

def generate_hotel_html(days, folder):
    html = '''
        <!-- ═══════════════════════════════════════════ -->
        <!-- VIDEO HOTEL                                -->
        <!-- ═══════════════════════════════════════════ -->
        <div class="custom-frame drone-screen-1">
            <h2 class="drone-title">(VIDEO HOTEL YANG AKAN DIGUNAKAN)</h2>
'''
    nights = days - 1
    hotels = [
        "HOTEL DAY 1<br>TBD",
        "HOTEL DAY 2<br>TBD",
        "HOTEL DAY 3<br>TBD",
        "HOTEL DAY 4<br>TBD"
    ]
    
    for i in range(0, nights, 2):
        html += '            <div class="drone-grid-2">\n'
        for j in range(2):
            if i + j < nights:
                html += f'''                <div class="vid-card">
                    <div class="vid-label">{hotels[i+j]}</div>
                    <video controls loop muted playsinline preload="metadata">
                        <source src="assets/{folder}/hotel-day{i+j+1}-web.mp4" type="video/mp4">
                    </video>
                </div>
'''
        html += '            </div>\n'
    
    html += '        </div>\n'
    return html

files = [
    ('trip-4d3n.html', 4, '4d3n'),
    ('trip-3d2n.html', 3, '3d2n'),
    ('trip-2d1n.html', 2, '2d1n')
]

for file, days, folder in files:
    if not os.path.exists(file):
        print(f"{file} not found")
        continue
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '.custom-frame' not in content:
        content = content.replace('</style>', css_to_add + '\n    </style>')
    
    # insert videos before MENGAPA MEMILIH KAMI
    if '<!-- ═══════════════════════════════════════════ -->\n        <!-- VIDEO HOTEL' not in content:
        hotel_html = generate_hotel_html(days, folder)
        drone_html = html_drone.format(folder=folder)
        
        target = '<!-- ===== MENGAPA MEMILIH KAMI ===== -->'
        replacement = hotel_html + drone_html + '\n        ' + target
        
        content = content.replace(target, replacement)
    
    # replace scripts
    if '<!-- ── Auto-Play on Scroll Script ── -->' in content:
        content = re.sub(r'<!-- ── Auto-Play on Scroll Script ── -->.*?</body>', js_to_add, content, flags=re.DOTALL)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file}")
