# robust splitter: DP over silence gaps, guided by whisper hints (assets/cuts.json) and char-length interpolation.
import json, subprocess, numpy as np, wave, os, re
SR = 44100; HOP = SR // 100
B = json.load(open('batches.json')); C = json.load(open('assets/cuts.json')); os.makedirs('wav', exist_ok=True)
L = {l.split('\t')[0]: re.sub(r'\[[^\]]*\]', '', l.split('\t')[2]).strip() for l in open('lines.tsv').read().strip().split('\n')}
report = []
for b in B:
    name = b['file'][:-4]; lines = b['lines']; n = len(lines); hint = C[name]
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'assets/' + b['file'], '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                                     capture_output=True).stdout, np.int16).astype(np.float32) / 32768
    r = np.array([np.sqrt(np.mean(x[i:i + HOP] ** 2)) for i in range(0, len(x) - HOP, HOP)]); T = len(r)
    thr = max(0.006, np.percentile(r, 20) * 1.8)
    sil = r < thr; G = []; s = None
    for i, v in enumerate(list(sil) + [False]):
        if v and s is None: s = i
        if not v and s is not None:
            if s > 0 and i < T and i - s >= 5: G.append((s, i))
            s = None
    good = [h if h and h[2] >= 0.6 * h[3] else None for h in hint]
    # expected boundary positions (in frames) and sigma
    w = np.array([max(4, len(L[ln])) for ln in lines], float)
    E = [None] * (n - 1); S = [None] * (n - 1)
    for k in range(n - 1):
        a, c = good[k], good[k + 1]
        if a and c: E[k] = (a[1] + c[0]) * 50; S[k] = max(25, (c[0] - a[1]) * 50 + 20)
        elif a: E[k] = a[1] * 100 + 25; S[k] = 60
        elif c: E[k] = c[0] * 100 - 25; S[k] = 60
    # interpolate missing using char weights between anchors
    anchors = [(-1, 0.0)] + [(k, E[k]) for k in range(n - 1) if E[k] is not None] + [(n - 1, float(T))]
    for (ka, pa), (kb, pb) in zip(anchors, anchors[1:]):
        if kb - ka <= 1: continue
        tot = w[ka + 1:kb + 1].sum(); acc = pa
        for k in range(ka + 1, kb):
            acc += (pb - pa) * w[k] / tot; E[k] = acc; S[k] = max(80, (pb - pa) / (kb - ka))
    # DP over gaps
    mids = np.array([(g[0] + g[1]) / 2 for g in G]); lens = np.array([g[1] - g[0] for g in G], float)
    m = len(G); NEG = -1e18
    if n == 1: m = 0
    if m < n - 1:
        report.append((name, 'TOO FEW GAPS', m, n)); continue
    if n == 1: cuts = []
    else:
     score = np.full((n - 1, m), NEG); back = np.zeros((n - 1, m), int)
    def cost(k, j): return np.log1p(lens[j]) * 2.0 - ((mids[j] - E[k]) / S[k]) ** 2
    for j in range(m): score[0, j] = cost(0, j)
    for k in range(1, n - 1):
        best = NEG; bi = -1; jj = 0
        for j in range(m):
            while jj < j and mids[jj] < mids[j] - 15:  # prev cut at least 0.15s earlier
                if score[k - 1, jj] > best: best = score[k - 1, jj]; bi = jj
                jj += 1
            if bi >= 0: score[k, j] = best + cost(k, j); back[k, j] = bi
    j = int(np.argmax(score[n - 2])) if n > 1 else 0; cuts = []
    for k in range(n - 2, -1, -1): cuts.append(int(mids[j])); j = back[k, j]
    cuts = cuts[::-1]
    edges = [0] + cuts + [T]
    for k, ln in enumerate(lines):
        a, e = edges[k], edges[k + 1]; seg = r[a:e]; on = np.where(seg > thr * 1.3)[0]
        if len(on) == 0: on = np.array([0, max(0, e - a - 1)]); report.append((name, ln, 'EMPTY'))
        s0 = max(0, a + on[0] - 4) * HOP; s1 = min(len(x), (a + on[-1] + 9) * HOP)
        y = x[s0:s1].copy(); f = min(len(y) // 2, 300); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
        wv = wave.open(f'wav/a{ln}.wav', 'wb'); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
        wv.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
        h = hint[k]
        if h and h[2] >= 0.6 * h[3] and abs((s1 - s0) / SR - (h[1] - h[0])) > 1.0: report.append((name, ln, 'dur', round((s1 - s0) / SR, 2), round(h[1] - h[0], 2)))
    print(name, n, 'ok')
print('REPORT', report)
