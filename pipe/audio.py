import json, wave, subprocess, numpy as np
from scipy.signal import butter, sosfilt
SR = 44100; rng = np.random.default_rng(7)
TL = json.load(open('timeline.json')); N = int((TL['total'] + 1) * SR)

def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; return x
def bp(x, lo, hi, o=4): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=4): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def noise(s): return rng.standard_normal(int(s * SR)).astype(np.float32)
def tone(f, s, d=0.3, a=0.003):
    t = np.arange(int(s * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(len(t), a, d)

def sfx(name):
    if name == 'crunch':
        x = lp(noise(0.9), 2500) * env(int(.9 * SR), .002, .18) * 1.4
        x += tone(55, .9, .15) * 1.2 + bp(noise(.9), 2000, 6000) * env(int(.9 * SR), .01, .08) * .5
        x[int(.25 * SR):] += (bp(noise(.65), 3000, 9000) * env(int(.65 * SR), .001, .05) * .4)
        return x * .8
    if name == 'pop':
        t = np.arange(int(.12 * SR)) / SR; f = 900 * np.exp(-t * 18) + 150
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .001, .04) * .9
    if name == 'squelch':
        t = np.arange(int(.5 * SR)) / SR; f = 120 + 60 * np.sin(2 * np.pi * 9 * t)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .02, .2) * .5 + lp(noise(.5), 600) * env(len(t), .02, .15) * .3
    if name == 'clang':
        x = sum(tone(f, 1.6, 0.5 / (i + 1) ** .3) * (1 / (i + 1)) for i, f in enumerate([523, 1187, 1873, 2630, 3540]))
        return x * .7 + lp(noise(1.6), 3000) * env(int(1.6 * SR), .001, .05) * .6
    if name == 'roll':
        n = int(1.3 * SR); x = bp(noise(1.3), 300, 1500) * .25
        am = (np.sin(2 * np.pi * 7 * np.arange(n) / SR) > .3) * 1.0
        return x * am * np.linspace(1, 0, n)
    if name == 'whoosh':
        n = int(.5 * SR); x = bp(noise(.5), 600, 5000) * np.sin(np.linspace(0, np.pi, n)) ** 2 * .35
        return x
    if name == 'slap':
        return lp(noise(.2), 3500) * env(int(.2 * SR), .001, .03) * 1.2
    if name == 'rip':
        n = int(.75 * SR); x = bp(noise(.75), 1500, 7000)
        am = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 38 * np.arange(n) / SR))
        return x * am * np.minimum(1, np.arange(n) / (.03 * SR)) * np.linspace(1, .3, n) * .45
    if name == 'dryer':
        n = int(2.9 * SR); x = bp(noise(2.9), 400, 4000) * .14 + tone(180, 2.9, 99) * .05
        return x * np.minimum(1, np.arange(n) / (.15 * SR)) * np.minimum(1, (n - np.arange(n)) / (.3 * SR))
    if name == 'bubble':
        x = np.zeros(int(1.2 * SR), np.float32)
        for k in range(9):
            s = int(rng.uniform(0, 1.0) * SR); b = sfx('pop')[:int(.06 * SR)] * .35; x[s:s + len(b)] += b
        return x
    if name == 'scribble':
        n = int(1.4 * SR); x = bp(noise(1.4), 2500, 8000) * .12
        am = np.abs(np.sin(2 * np.pi * 5.5 * np.arange(n) / SR)) ** 2
        return x * am
    if name == 'marker':
        n = int(2.2 * SR); x = bp(noise(2.2), 1800, 5000) * .12
        am = (np.sin(2 * np.pi * 3 * np.arange(n) / SR) > -.2) * 1.0
        return x * am
    if name == 'keys':
        x = np.zeros(int(.6 * SR), np.float32)
        for k in range(7):
            s = int(rng.uniform(0, .4) * SR); f = rng.uniform(3000, 6500); c = tone(f, .2, .05) * .18; x[s:s + len(c)] += c
        return x
    if name == 'ring':
        n = int(1.0 * SR); t = np.arange(n) / SR
        x = (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)) * .12
        return x * ((t % .5) < .35)
    if name in ('sprint', 'steps'):
        k = 10 if name == 'sprint' else 5; x = np.zeros(int(3.0 * SR), np.float32); s = 0
        for i in range(k):
            st = lp(noise(.08), 900) * env(int(.08 * SR), .001, .02) * (.9 if name == 'sprint' else .5)
            x[s:s + len(st)] += st * (1 - i / (k * 1.3)); s += int((0.32 - 0.02 * i if name == 'sprint' else .45) * SR)
        return x
    if name == 'door':
        return lp(noise(.4), 800) * env(int(.4 * SR), .002, .08) * .7 + tone(90, .4, .1) * .3
    if name == 'truckdoor':
        return lp(noise(.5), 1200) * env(int(.5 * SR), .002, .1) * .8 + tone(70, .5, .12) * .5
    if name == 'whine':
        n = int(1.0 * SR); t = np.arange(n) / SR; f = 1450 + 120 * t + 30 * np.sin(2 * np.pi * 3 * t)
        ph = 2 * np.pi * np.cumsum(f) / SR; x = (np.sin(ph) + .3 * np.sin(2 * ph)) * np.minimum(1, t / .15) * np.minimum(1, (1 - t) / .2)
        x = x * .09 + lp(noise(1.0), 300) * .25 * np.minimum(1, t / .1) * np.minimum(1, (1 - t) / .2); return x.astype(np.float32)
    if name == 'squeal':
        n = int(0.9 * SR); t = np.arange(n) / SR; f = 3200 + 250 * np.sin(2 * np.pi * 7 * t)
        ph = 2 * np.pi * np.cumsum(f) / SR; x = np.sin(ph) * np.minimum(1, t / .05) * np.minimum(1, (.9 - t) / .25) * (0.7 + 0.3 * np.sin(2 * np.pi * 11 * t))
        return (x * .1).astype(np.float32)
    if name == 'rattle':
        x = np.zeros(int(1.0 * SR), np.float32)
        for i in range(16):
            c = bp(noise(.02), 2500, 9000) * env(int(.02 * SR), .0005, .004) * (.35 + .25 * rng.random()); s = int((i * .055 + .01 * rng.random()) * SR); x[s:s + len(c)] += c
        return x
    if name == 'tick':
        x = np.zeros(int(1.1 * SR), np.float32)
        for i in range(9):
            c = bp(noise(.015), 1800, 7000) * env(int(.015 * SR), .0003, .003) * .45; s = int(i * .12 * SR); x[s:s + len(c)] += c
        return x
    if name == 'bell':
        return tone(1318, 1.0, .35) * .25 + tone(1975, 1.0, .25) * .12
    if name == 'click2':
        c = bp(noise(.03), 2000, 8000) * env(int(.03 * SR), .0005, .005) * .6
        x = np.zeros(int(.35 * SR), np.float32); x[:len(c)] += c; x[int(.2 * SR):int(.2 * SR) + len(c)] += c; return x
    if name == 'ratchet':
        x = np.zeros(int(1.2 * SR), np.float32)
        for i in range(10):
            c = bp(noise(.025), 1500, 6000) * env(int(.025 * SR), .0005, .006) * .3; s = int(i * .09 * SR); x[s:s + len(c)] += c
        return x
    if name in ('sting', 'sting2'):
        # little comedic brass-ish stab + bass walk
        out = np.zeros(int(3.0 * SR), np.float32)
        notes = [(0.0, [196, 247, 294]), (0.25, [220, 277, 330]), (0.55, [262, 330, 392, 523])] if name == 'sting' else \
                [(0.0, [262, 330, 392]), (0.35, [247, 311, 370]), (0.7, [233, 294, 349, 466])]
        for st, ch in notes:
            last = st == notes[-1][0]; d = 1.6 if last else .22
            for f in ch:
                t = np.arange(int((d + .3) * SR)) / SR
                w = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4)) * env(len(t), .01, d * .7)
                s = int(st * SR); out[s:s + len(w)] += w.astype(np.float32) * .09
        return lp(out, 5000)
    raise KeyError(name)

GAIN = {'crunch': 1.0, 'clang': .9}
vo = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
for L in TL['lines']:
    x = rd(f"wav/a{L['n']}.wav")
    if L['phone']: x = np.tanh(bp(x, 350, 3200) * 2.2) * .55
    if L['muffled']: x = lp(x, 900) * 1.3
    s = int(L['t0'] * SR); vo[s:s + len(x)] += x
for name, t in TL['sfx']:
    x = sfx(name).astype(np.float32) * GAIN.get(name, 1.0); s = int(t * SR); e = min(N, s + len(x)); fx[s:e] += x[:e - s]

def wr(p, x):
    w = wave.open(p, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
wr('vo_raw.wav', vo); wr('fx.wav', fx * .8)
CH = ('highpass=f=90,afftdn=nf=-32:nr=14,agate=threshold=0.008:ratio=6:attack=3:release=120,'
      'equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1.5:g=2.5,treble=g=3:f=9000,'
      'acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'vo_raw.wav', '-af', CH, 'vo.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'vo.wav', '-i', 'fx.wav', '-filter_complex',
                '[1:a]volume=0.55[f];[0:a][f]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[o]',
                '-map', '[o]', '-ac', '2', 'mix.wav'], check=True)
# mouth envelopes (30 fps) with hysteresis
ENV = {}
for L in TL['lines']:
    x = rd(f"wav/a{L['n']}.wav"); hop = SR // 30; n = int(np.ceil(len(x) / hop))
    r = np.array([np.sqrt(np.mean(x[j * hop:(j + 1) * hop + hop // 2] ** 2)) if len(x[j * hop:]) else 0 for j in range(n)])
    ref = np.percentile(r[r > .003], 85) if (r > .003).any() else 1
    lv = r / ref; op = []; st = 0; run = 0
    for v in lv:
        if st == 0 and v > .45: st = 1
        elif st == 1 and v < .28: st = 0
        run = run + 1 if st else 0
        if run > 5 and v < .8: st = 0; run = 0   # close briefly in long vowels so it reads as talking
        op.append(st)
    ENV[L['n']] = op
json.dump(ENV, open('env.json', 'w'))
print('audio ok', N / SR)
