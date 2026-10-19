import json, glob, os, subprocess, urllib.request, sys
bad = 0
for mf in sorted(glob.glob('media/manifests/*.json')):
    m = json.load(open(mf)); d = m['dir']; os.makedirs(d, exist_ok=True)
    for name, url in m['items'].items():
        out = os.path.join(d, name)
        if os.path.exists(out) and not m.get('force'): continue
        tmp = '/tmp/in.mp4'
        try:
            urllib.request.urlretrieve(url, tmp)
            subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-vf','scale=640:-2','-c:v','libx264','-preset','slow','-crf','27',
                            '-c:a','aac','-b:a','96k','-movflags','+faststart',out], check=True)
            print('ok', out, os.path.getsize(out))
        except Exception as e:
            bad += 1; print('FOUT', out, e, file=sys.stderr)
sys.exit(1 if bad else 0)
