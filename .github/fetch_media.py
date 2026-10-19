# Haalt avatarvideo's op volgens media/manifests/*.json en zet ze om (480x480, H.264).
# Manifest: {"dir": "media/<map>", "items": {"slide-NN.mp4": "<HeyGen-url>"}, "audio_base": "<url van de map met slide-NN.mp3>" (optioneel)}
# Afspraak Peter (19/10): voor NIEUWE video's de audio van HeyGen vervangen door de originele ElevenLabs-mp3
# (zelfde opname, maar zonder de -3 dB van HeyGen en zonder extra compressieverlies). Gebeurt als "audio_base" in het manifest staat.
# Bestaande bestanden worden niet opnieuw opgehaald.
import json, glob, os, subprocess, urllib.request, sys
bad = 0
for mf in sorted(glob.glob('media/manifests/*.json')):
    m = json.load(open(mf)); d = m['dir']; os.makedirs(d, exist_ok=True)
    ab = m.get('audio_base')
    for name, url in m['items'].items():
        out = os.path.join(d, name)
        if os.path.exists(out) and not m.get('force'): continue
        tmp = '/tmp/in.mp4'
        try:
            urllib.request.urlretrieve(url, tmp)
            vf = ['-vf', 'scale=1280:720,crop=480:480:374:0', '-c:v', 'libx264', '-preset', 'slow', '-crf', '27']
            if ab:
                mp3 = '/tmp/in.mp3'
                urllib.request.urlretrieve(ab.rstrip('/') + '/' + name.replace('.mp4', '.mp3'), mp3)
                cmd = ['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', mp3, '-map', '0:v:0', '-map', '1:a:0', *vf,
                       '-c:a', 'aac', '-b:a', '160k', '-ac', '1', '-shortest', '-movflags', '+faststart', out]
            else:
                cmd = ['ffmpeg', '-v', 'error', '-y', '-i', tmp, *vf, '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', out]
            subprocess.run(cmd, check=True)
            print('ok', out, os.path.getsize(out), 'originele audio' if ab else 'audio HeyGen')
        except Exception as e:
            bad += 1; print('FOUT', out, e, file=sys.stderr)
sys.exit(1 if bad else 0)
