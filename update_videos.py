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

        /* -- Custom Video Wrapper for Reels-like Experience -- */
        .vid-wrapper {
            position: relative;
            width: 100%;
            padding-top: 177.77%; /* Fallback for older browsers (16:9) */
            border-radius: 8px;
            overflow: hidden;
            background: #111;
            cursor: pointer;
        }
        @supports (aspect-ratio: 9 / 16) {
            .vid-wrapper {
                padding-top: 0;
                aspect-ratio: 9 / 16;
            }
        }
        .vid-wrapper video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .play-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50px;
            height: 50px;
            background: rgba(0, 0, 0, 0.6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            transition: opacity 0.3s ease, transform 0.3s ease;
            z-index: 10;
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        }
        .play-overlay::after {
            content: '';
            display: block;
            border-style: solid;
            border-width: 12px 0 12px 18px;
            border-color: transparent transparent transparent #fff;
            margin-left: 6px;
        }
        .vid-wrapper.is-playing .play-overlay {
            opacity: 0;
            transform: translate(-50%, -50%) scale(1.2);
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
            const wrappers = document.querySelectorAll('.vid-wrapper');
            
            wrappers.forEach(wrapper => {
                const video = wrapper.querySelector('video');
                if (!video) return;
                
                video.style.opacity = '1';
                
                // Toggle play/pause and unmute on click anywhere on the wrapper
                wrapper.addEventListener('click', () => {
                    if (video.paused) {
                        video.muted = false; // Unmute on first interaction
                        video.play().catch(e => console.log('Playback prevented', e));
                    } else {
                        video.pause();
                    }
                });
                
                video.addEventListener('play', () => {
                    wrapper.classList.add('is-playing');
                    // Pause other videos automatically
                    document.querySelectorAll('video').forEach(v => {
                        if (v !== video && !v.paused) {
                            v.pause();
                        }
                    });
                });
                
                video.addEventListener('pause', () => {
                    wrapper.classList.remove('is-playing');
                });
                
                video.addEventListener('ended', () => {
                    wrapper.classList.remove('is-playing');
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
                    <div class="vid-wrapper">
                        <video loop muted playsinline preload="metadata">
                            <source src="assets/5d4n/drone-1-web.mp4#t=0.001" type="video/mp4">
                        </video>
                        <div class="play-overlay"></div>
                    </div>
                </div>
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DJI MAVIC 4 PRO</div>
                    <div class="vid-wrapper">
                        <video loop muted playsinline preload="metadata">
                            <source src="assets/5d4n/drone-2-web.mp4#t=0.001" type="video/mp4">
                        </video>
                        <div class="play-overlay"></div>
                    </div>
                </div>
            </div>

            <div class="drone-grid-1">
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DJI MINI 3 & MAVIC 4 PRO</div>
                    <div class="vid-wrapper">
                        <video loop muted playsinline preload="metadata">
                            <source src="assets/5d4n/drone-3-web.mp4#t=0.001" type="video/mp4">
                        </video>
                        <div class="play-overlay"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="custom-frame drone-screen-2">
            <div class="drone-grid-2">
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>DRONE FPV DJI AVATA 360</div>
                    <div class="vid-wrapper">
                        <video loop muted playsinline preload="metadata">
                            <source src="assets/5d4n/drone-4-web.mp4#t=0.001" type="video/mp4">
                        </video>
                        <div class="play-overlay"></div>
                    </div>
                </div>
                <div class="vid-card">
                    <div class="vid-label">CONTOH HASIL VIDEO<br>IPHONE 17 PRO + DRONE DJI MINI 3</div>
                    <div class="vid-wrapper">
                        <video loop muted playsinline preload="metadata">
                            <source src="assets/5d4n/drone-5-web.mp4#t=0.001" type="video/mp4">
                        </video>
                        <div class="play-overlay"></div>
                    </div>
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
                    <div class="vid-wrapper">
                        <video loop muted playsinline preload="metadata">
                            <source src="assets/{folder}/hotel-day{i+j+1}-web.mp4#t=0.001" type="video/mp4">
                        </video>
                        <div class="play-overlay"></div>
                    </div>
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
    
    # Force rebuild the videos section
    start_marker = '<!-- ═══════════════════════════════════════════ -->\\n        <!-- VIDEO HOTEL'
    end_marker = '<!-- ===== MENGAPA MEMILIH KAMI ===== -->'
    
    # We replace everything between start_marker and end_marker with our new HTML
    hotel_html = generate_hotel_html(days, folder)
    drone_html = html_drone.format(folder=folder)
    replacement = hotel_html + drone_html + '\\n        ' + end_marker
    content = re.sub(r'<!-- ═══════════════════════════════════════════ -->\s*<!-- VIDEO HOTEL.*?<!-- ===== MENGAPA MEMILIH KAMI ===== -->', replacement, content, flags=re.DOTALL)
    
    # Clean up old CSS block to replace it with the new one
    content = re.sub(r'/\* ── Custom HTML Frames for Drone Videos ── \*/.*?</style>', css_to_add + '\\n    </style>', content, flags=re.DOTALL)
    
    # Clean up old JS and insert new one
    content = re.sub(r'<!-- ── Video Controller Script ── -->.*?</body>', js_to_add, content, flags=re.DOTALL)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {file}")
