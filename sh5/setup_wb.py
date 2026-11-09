# workbench: fetch assets, blur logos, align, split.  python3 setup_wb.py  (cwd sh5)
import os,json,re,subprocess,requests,numpy as np,shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw,ImageFilter
CACHE='/mnt/files/sh5'; os.makedirs(CACHE,exist_ok=True); os.makedirs('wav',exist_ok=True)
F=json.load(open('urls.json'))
def one(kv):
    k,u=kv; c=f'{CACHE}/{k}'
    if not os.path.exists(c):
        r=requests.get(u,timeout=90); r.raise_for_status(); open(c,'wb').write(r.content)
    shutil.copy(c,'assets/'+k); return k
with ThreadPoolExecutor(10) as e: list(e.map(one,F.items()))
def blot(fn,boxes):
    im=Image.open(fn).convert('RGB'); bl=im.filter(ImageFilter.GaussianBlur(28))
    m=Image.new('L',im.size,0); d=ImageDraw.Draw(m)
    for b in boxes: d.ellipse(b,fill=255)
    Image.composite(bl,im,m.filter(ImageFilter.GaussianBlur(10))).save(fn)
blot('assets/g183.png',[(170,1560,390,1720)]); blot('assets/g184.png',[(60,1130,340,1320)])
if os.path.exists(f'{CACHE}/cuts.json'): shutil.copy(f'{CACHE}/cuts.json','assets/cuts.json')
else:
    from faster_whisper import WhisperModel
    M=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=4)
    def load16k(fn):
        raw=subprocess.run(['ffmpeg','-v','error','-i',fn,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
        return np.frombuffer(raw,np.int16).astype('float32')/32768
    norm=lambda w:re.sub(r"[^a-z0-9]","",w.lower())
    L={l.split('\t')[0]:re.sub(r'\[[^\]]*\]','',l.split('\t')[2]).strip() for l in open('lines.tsv').read().strip().split('\n')}
    C={}
    for b in json.load(open('batches.json')):
        segs,_=M.transcribe(load16k('assets/'+b['file']),word_timestamps=True,beam_size=1,language='en')
        W=[(norm(w.word),w.start,w.end) for s in segs for w in s.words if norm(w.word)]
        p=0;out=[]
        for lid in b['lines']:
            lw=[norm(x) for x in L[lid].split() if norm(x)];hits=[];q=p
            for w in lw:
                for j in range(q,min(len(W),q+8)):
                    if W[j][0]==w: hits.append(j);q=j+1;break
            if hits: out.append([W[hits[0]][1],W[hits[-1]][2],len(hits),len(lw)]);p=hits[-1]+1
            else: out.append(None)
        C[b['file'][:-4]]=out
    json.dump(C,open('assets/cuts.json','w')); shutil.copy('assets/cuts.json',f'{CACHE}/cuts.json')
print(subprocess.run(['python3','../pipe/split3.py'],capture_output=True,text=True).stdout[-300:])
