from pathlib import Path
import numpy as np
import os,wave
def build(out:Path,seconds:float,accents:list[float],soundfont:Path):
    import ctypes as ct
    from ctypes import c_void_p,c_char_p,c_int,c_double
    from math import pi
    # Render an original eight-bar phrase with a sampled acoustic grand.
    fs=48000; count=round(fs*seconds)
    fluid=ct.CDLL('libfluidsynth.so.3')
    def bind(n,r,*args):
        f=getattr(fluid,n);f.restype=r;f.argtypes=args;return f
    settings=bind('new_fluid_settings',c_void_p)()
    setnum=bind('fluid_settings_setnum',c_int,c_void_p,c_char_p,c_double)
    setint=bind('fluid_settings_setint',c_int,c_void_p,c_char_p,c_int)
    setnum(settings,b'synth.sample-rate',fs);setnum(settings,b'synth.gain',.55)
    setint(settings,b'synth.reverb.active',0);setint(settings,b'synth.chorus.active',0)
    synth=bind('new_fluid_synth',c_void_p,c_void_p)(settings)
    sf=bind('fluid_synth_sfload',c_int,c_void_p,c_char_p,c_int)(synth,os.fsencode(soundfont),1)
    assert sf>=0
    noteon=bind('fluid_synth_noteon',c_int,c_void_p,c_int,c_int,c_int)
    noteoff=bind('fluid_synth_noteoff',c_int,c_void_p,c_int,c_int)
    write=bind('fluid_synth_write_float',c_int,c_void_p,c_int,c_void_p,c_int,c_int,c_void_p,c_int,c_int)

    pg=bind('fluid_synth_program_select',c_int,c_void_p,c_int,c_int,c_int,c_int)
    for ch,preset in enumerate([48,45,61,38]):assert pg(synth,ch,sf,0,preset)==0
    events={}; beat=.5
    def note(t,ch,n,v,d):
        if t>=seconds:return
        for s,k in [(t,v),(min(t+d,seconds-1/fs),0)]:
            events.setdefault(round(s*fs),[]).append((ch,n,k))
    prog=[(38,50,[57,60,64]),(34,46,[57,60,62]),(41,53,[57,60,67]),(36,48,[55,62,65])]
    for bar in range(int(seconds/2)+1):
        t=bar*2;r,mid,chord=prog[bar%4]
        for i,n in enumerate(chord):note(t+.03*i,0,n,46+(bar%4)*3,1.78)
        for i in range(8):
            note(t+i*.25,1,[mid,chord[0],mid,chord[2],mid,chord[1],mid,chord[2]][i],65 if i in (0,3,6) else 48,.145)
        for k in [0,.75,1.5]:note(t+k,3,r,70,.22)
    for t in accents:
        for n in [50,57,62]:note(t,2,n,67 if t==0 else 50,.30)
    end=max(0,seconds-1)
    for n in (38,50,57,62):note(end,2,n,58,.62)
    a=np.empty((count,2),np.float32); pos=0
    for k,e in sorted(events.items()):
        if k>pos:assert write(synth,k-pos,a.ctypes.data,pos*2,2,a.ctypes.data,pos*2+1,2)==0
        pos=k
        for ch,n,v in e: (noteon(synth,ch,n,v) if v else noteoff(synth,ch,n))
    if pos<count:assert write(synth,count-pos,a.ctypes.data,pos*2,2,a.ctypes.data,pos*2+1,2)==0
    rng=np.random.default_rng(17)
    def add(t,d,f):
        p=round(t*fs);n=min(count-p,round(d*fs))
        if n<=0:return
        x=np.arange(n)/fs;a[p:p+n]+=f(x)[:,None]
    for i in range(int(seconds*2)):
        t=i*.5
        add(t,.18,lambda x:.13*np.exp(-x*34)*np.sin(2*pi*(90*x-95*x*x))*np.minimum(1,x/.005))
        add(t+.25,.048,lambda x:.024*rng.uniform(-1,1,len(x))*np.exp(-x*88))
        if i%2:add(t,.16,lambda x:.048*rng.uniform(-1,1,len(x))*np.exp(-x*29))
    for t in accents:
        add(max(0,t-.16),.21,lambda x:.034*rng.uniform(-1,1,len(x))*np.sin(x/.21*pi)**2)
        add(t,.4,lambda x:.095*np.exp(-x*14)*np.sin(2*pi*48*x)*np.minimum(1,x/.007))
    x=np.arange(count)/fs
    a*=np.minimum(1,(seconds-x)/.37)[:,None]
    a*=.67/max(.001,np.max(np.abs(a)))
    with wave.open(str(out),'wb') as w:
        w.setparams((2,2,fs,0,'NONE','not compressed')); w.writeframes((a*32767).astype('<i2').tobytes())
