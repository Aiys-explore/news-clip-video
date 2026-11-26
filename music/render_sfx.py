"""Render short original editorial cues. Requires NumPy, SciPy and FFmpeg."""
from pathlib import Path
import subprocess
import numpy as np
from scipy import signal
SR=48000
DIR=Path(__file__).resolve().parent/'sfx'
DIR.mkdir(exist_ok=True)

def effect(name,duration,level,fn):
    x=np.arange(round(duration*SR))/SR
    rng=np.random.default_rng(386)
    def noise(lo,hi):
        return signal.sosfilt(signal.butter(2,[lo,hi],btype='bandpass',fs=SR,output='sos'),rng.standard_normal(len(x)))
    arr=fn(x,noise)
    if arr.ndim==1:arr=np.column_stack((arr,arr))
    a=np.minimum(x/.008,1)*np.minimum((duration-x)/.042,1)
    arr*=a[:,None]
    arr*=10**(level/20)/np.max(np.abs(arr))
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','libmp3lame','-b:a','128k',str(DIR/(name+'.mp3'))],input=arr.astype('<f4').tobytes(),check=True)

def sweep(t,n):
    w=np.sin(np.pi*t/.64)**1.7
    snd=(.70*n(240,1200)+.21*n(900,3300)+.09*np.sin(2*np.pi*(118*t+114*t*t)))*w
    pan=0.46*np.sin(np.pi*(t/.64-.5))
    return np.column_stack((snd*(1-pan),snd*(1+pan)))

def hit(t,n):
    return (.75*np.sin(2*np.pi*(49*t+39*(1-np.exp(-14*t))/14))+.16*np.sin(2*np.pi*107*t)*np.exp(-16*t)+.18*n(85,470))*np.exp(-8*t)

def tick(t,n):
    u=2*np.pi*553*t
    return (.69*np.sin(u)+.22*np.sin(1.51*u)+.14*n(380,2300))*np.exp(-18*t)

def atmosphere(t,n):
    f=(.24*np.sin(2*np.pi*49*t)+.17*np.sin(2*np.pi*73.6*t+.3)+.26*n(57,205))*(.86+.10*np.sin(2*np.pi*.38*t))
    return np.column_stack((f+.12*n(160,430),f+.12*n(160,430)))*np.sin(np.pi*t/5.5)[:,None]**.52

if __name__=='__main__':
    effect('air-sweep',.64,-10,sweep)
    effect('soft-impact',.92,-11,hit)
    effect('data-tick',.33,-13,tick)
    effect('low-room-tone',5.5,-16,atmosphere)
