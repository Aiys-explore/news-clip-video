"""Render two original instrumental beds. Requires NumPy, SciPy and FFmpeg."""
from pathlib import Path
import subprocess, wave
import numpy as np
from scipy import signal
SR=48000
D=22
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets'
OUT.mkdir(exist_ok=True)
def make(kind):
    r=np.random.default_rng(1802+kind)
    bus=np.zeros((SR*D,2))
    def add(t,length,gain,pan,fx):
        ix=round(t*SR); a=max(ix,0); b=min(ix+round(length*SR),len(bus))
        if b<=a:return
        x=np.arange(a-ix,b-ix)/SR
        f=fx(x)*gain
        bus[a:b]+=f[:,None]*np.sqrt([(1-pan)*.5,(1+pan)*.5])
    def note(t,length,m,g,p,inst):
        f=440*2**((m-69)/12)
        def sound(x):
            u=2*np.pi*f*x
            if inst=='piano':
                env=np.minimum(x/.005,1)*np.exp(-2*x)*np.clip((length-x)/.18,0,1)
                y=sum(a*np.sin(u*i*np.sqrt(1+.00022*i*i))*np.exp(-i*.65*x) for i,a in enumerate([0,1,.43,.30,.14,.073,.05,.029]) if i)
                return env*y
            if inst=='bow':
                v=.026*np.sin(2*np.pi*4.3*x)
                y=sum(np.sin(u*h+v*h+.21*h)/(h**1.22) for h in range(1,11))*.67
                y+=.42*np.sin(u*1.003+v)+.32*np.sin(u*.997+v)
                env=np.sin(np.pi/2*np.clip(x/.45,0,1))**1.5*np.clip((length-x)/.55,0,1)
                return y*env*(.89+.10*np.sin(2*np.pi*.72*x+.3))
            if inst=='organ':
                y=(np.sin(u)+.47*np.sin(2*u+.21)+.26*np.sin(3*u-.15)+.24*np.sin(u/2)+.12*np.sin(4*u+.31)+.055*np.sin(6*u))
                y+=.28*np.sin(u*1.0016+.15)+.19*np.sin(2*u*.9985)
                return y*np.clip(x/.52,0,1)*np.clip((length-x)/.55,0,1)*(.93+.07*np.sin(2*np.pi*.66*x))
            if inst=='air':
                y=np.sin(u+.38*np.sin(1.004*u))+.11*np.sin(2.006*u)
                return y*np.sin(np.pi*np.clip(x/length,0,1))**1.5
            y=np.sin(u)+.34*np.sin(2*u+.21)
            return y*np.minimum(x/.013,1)*np.exp(-2.9*x)*np.clip((length-x)/.15,0,1)
        add(t,length,g,p,sound)
    def filtered(x,lo,hi):
        return signal.sosfilt(signal.butter(2,[lo,hi],fs=SR,btype='bandpass',output='sos'),r.normal(0,1,len(x)))
    def drum(t,g,p=0):
        add(t,.68,g,p,lambda x:(np.sin(2*np.pi*(38*x+30*(1-np.exp(-14*x))/14))+.10*filtered(x,80,550))*np.minimum(x/.008,1)*np.exp(-9*x))
    def tick(t,g,p):
        add(t,.14,g,p,lambda x:(.55*filtered(x,1000,4400)+.48*np.sin(2*np.pi*935*x))*np.minimum(x/.002,1)*np.exp(-40*x))
    def swell(t,l,g,p):
        add(t,l,g,p,lambda x:filtered(x,125,1250)*np.sin(np.pi*x/l)**2)
    if kind==0:
        # A minor and a b2 inflection; silence between phrases is part of the cue.
        blocks=[(0,45,[45,52,57,60]),(5.35,41,[41,48,52,57]),(10.7,46,[46,53,57,62]),(16.1,40,[40,47,53,56]),(20,45,[45,52,57,60])]
        for j,(t,root,ch) in enumerate(blocks):
            stop=blocks[j+1][0]+.25 if j<4 else 22
            for k,n in enumerate(ch):note(t+.1*k,stop-t+.32, n,.043-(k*.008),(-.55,.45,-.34,.25)[k],'bow')
            for off in [0,2.25,3.80] if j<4 else [0]:
                if t+off<21.1:note(t+off,.92,root-12,.078,0,'sub')
            for off,n,vel,p in [(0.27,ch[0],.22,-.12),(.86,ch[2]+12,.095,.24),(2.38,ch[1]+12,.12,-.19),(3.10,ch[2]+12,.086,.32),(4.08,ch[1]+12,.070,-.27)]:
                if t+off<21.2:note(t+off,1.27,n,vel,p,'piano')
        for j in range(35):
            t=.61+j*.59
            if j not in {5,6,14,15,22,27,28,32}:tick(t,.042 if j%4 else .069,(-.31,.23)[j%2])
        for t,g in [(0.07,.20),(3.52,.145),(5.39,.21),(8.05,.17),(10.74,.23),(14.21,.15),(16.14,.25),(19.17,.14),(20.1,.22)]:drum(t,g)
        for t,d,g in [(3.8,1.46,.075),(8.85,1.75,.093),(13.93,2.15,.085),(18.09,1.85,.11)]:swell(t,d,g,.15)
    else:
        # An original spacious D pedal cue. The upper parts only arrive later.
        blocks=[(0.0,38,[50,57,62,64]),(4.9,34,[46,53,57,60]),(9.8,41,[53,60,64,67]),(14.7,36,[48,55,62,65]),(19.6,38,[50,57,62,69])]
        for j,(t,root,ch) in enumerate(blocks):
            l=5.35 if j<4 else 2.45
            for k,n in enumerate(ch):
                base=[.038,.053,.064,.079,.062][j]
                note(t+.18*k,l-.12*k,n,base*(1-.16*k),(-.48,.43,-.30,.37)[k],'organ')
            note(t,l+.1,root,.056+.012*j,.03,'bow')
            if j in (1,2,3,4):note(t+.1,l,ch[2]+12,.027+.008*j,.55,'air')
            for k in [0,1,2,3,5,6]:
                q=t+.32+.59*k
                if q<21.1:note(q,1.35,ch[(0,1,2,1,3,2,1)[k]]+12,.069 if k%3==0 else .048,(-.32,.31)[k%2],'piano')
        for t,g in [(0.09,.11),(4.90,.13),(9.83,.15),(14.70,.19),(19.62,.19)]:drum(t,g)
        for t,d,g in [(2.3,2.5,.048),(7.1,2.6,.064),(11.3,3.3,.082),(16.7,2.8,.083)]:swell(t,d,g,-.13)
    dry=bus.copy()
    for sec,wet in [(0.035,.085),(.081,.075),(.128,.063),(.203,.044),(.294,.029),(.390,.021)] if kind==0 else [(.041,.11),(.112,.09),(.201,.074),(.322,.064),(.55,.042),(.71,.023)]:
        n=round(sec*SR); bus[n:]+=wet*dry[:-n,::-1]
    sos=signal.butter(2,[32,14300],fs=SR,btype='bandpass',output='sos')
    bus=signal.sosfilt(sos,bus,axis=0)
    x=np.arange(len(bus))/SR
    bus*=np.minimum(1,x/.045)[:,None]*np.clip((D-x)/(1.35 if kind==0 else 1.7),0,1)[:,None]
    bus=np.tanh(bus*.77)
    return np.int16(bus/np.max(np.abs(bus))*.70*32767)
def one(name,nums,gain):
    tmp=OUT/(name+'.wav'); final=OUT/(name+'.mp3')
    with wave.open(str(tmp),'wb') as f:
        f.setparams((2,2,SR,0,'NONE','not compressed'));f.writeframes(nums.tobytes())
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(tmp),'-af',f'loudnorm=I=-18:TP=-2:LRA=7,volume={gain}dB,aresample=48000','-c:a','libmp3lame','-b:a','160k',str(final)],check=True)
    tmp.unlink()
if __name__=='__main__':
    one('A-suspense',make(0),.75); one('B-orbit',make(1),-.75)
