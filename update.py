import os, re

new_wa = '''<a href="https://wa.me/6285272388532" class="floating-wa" target="_blank" aria-label="Chat WhatsApp">
        <svg viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12c0 2.1.6 4.2 1.6 6L0 24l6.2-1.6c1.8 1 3.8 1.5 5.8 1.5 6.6 0 12-5.4 12-12S18.6 0 12 0zm0 21.8c-1.8 0-3.6-.5-5.1-1.4l-.4-.2-3.7 1 1-3.6-.2-.4c-1-1.6-1.5-3.4-1.5-5.2 0-5.5 4.5-9.9 9.9-9.9 5.5 0 9.9 4.5 9.9 9.9s-4.4 9.8-9.9 9.8zm5.5-7.4c-.3-.2-1.8-.9-2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-.9 1.1-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.5c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5 0-.2-.7-1.7-1-2.3-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.2-.3-.3-.6-.4z"></path></svg>
    </a>'''

for file in os.listdir('.'):
    if file.endswith('.html'):
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the WA link
        content = re.sub(r'<a href="https://wa\.me/[^"]*" class="floating-wa"[^>]*>.*?</a>', new_wa, content, flags=re.DOTALL)
        
        # Ensure fill is #fff
        content = re.sub(r'\.floating-wa svg \{.*?\}', '.floating-wa svg { width: 28px; height: 28px; fill: #fff; }', content)
        
        # Make z-index very high so it floats dimanapun
        content = re.sub(r'z-index:\s*99;?', 'z-index: 9999;', content)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {file}')
