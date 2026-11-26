#!/usr/bin/env python3
"""Private news cut; searches and exports remain separate operations."""
import argparse,json,subprocess,tempfile
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
from assemble import probe,need,run
from news_music import build
from story_preflight import validate as validate_story

W,H,FPS=1920,1080,30
BG='#101A27'; WHITE='#F3F4F2'; SUB='#B7C6D2'; LINE='#415467'; RED='#ED6259'
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest',type=Path);ap.add_argument('--media',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--font',type=Path,default=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'))
    ap.add_argument('--bold',type=Path,default=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'))
    ap.add_argument('--soundfont',type=Path,default=Path('/usr/share/sounds/sf2/TimGM6mb.sf2'))
    ap.add_argument('--narration',type=Path);ap.add_argument('--voice-kind',choices=['recorded','synthetic-own','synthetic-stock'])
    a=ap.parse_args()
    m=json.loads(a.manifest.read_text());root=a.media.resolve()
    editorial=validate_story(m) if 'editorial' in m else None
    a.out.mkdir(parents=True,exist_ok=True)
    need(bool(a.narration)==bool(a.voice_kind),'Narration needs a voice kind')
    @lru_cache
    def ft(size,b=False):
        f=a.bold if b else a.font
        return ImageFont.truetype(str(f),size,index=2 if 'NotoSansCJK' in f.name else 0)
    def tx(d,x,y,s,n,c=WHITE,b=False,w=None):
        f=ft(n,b); maxw=w if w is not None else W-x-66
        need(f.getlength(s)<=maxw,'Text outside safe: '+s)
        d.text((x,y),s,anchor='lt',font=f,fill=c)
    plan=[];t=0
    need(m.get('story_source'),'Provide the fact source')
    for b in m['beats']:
        du=float(b['duration']); n=round(du*FPS)
        need(1<=du<=60 and abs(n-du*FPS)<1e-7,'Beat duration must align to frames')
        x=m['assets'][b['asset']] if 'asset' in b else None
        f=None; start=0
        if x:
            f=(root/x['file']).resolve();start=float(b['in'])
            need(f.is_relative_to(root) and f.is_file(),'Missing local asset')
            need(x.get('rights_status')=='cleared_for_edit' or (m.get('mode')=='private_preview' and x.get('rights_status')=='private_reference_reviewed'),'Asset must be reviewed for this viewing mode')
            need(all(x.get(k) for k in ['source','rights','credit']),'Missing source or review notes')
            need(start>=0 and start+du<=probe(f)+.01,'Source in/out outside clip')
        mode=b.get('layout','split' if x else 'timeline')
        need(mode in ('split','full','timeline','close','statement') and bool(x)==(mode in ('split','full')),'Layout/asset mismatch')
        if mode in ('timeline','close'):
            need(2<=len(b['graphic']['steps'])<=4,'Provide 2–4 timeline milestones')
        if mode=='statement':
            need(1<=len(b['graphic']['lines'])<=3,'Provide 1–3 short statement lines')
        plan.append((t,du,n,b,x,f,start,mode));t+=du
    total=t;need(0<total<=180,'Invalid duration')
    if a.narration:need(total-2<=probe(a.narration,'a:0')<=total+.05,'Retiming required for narration')
    score=a.out/'news-bed.wav';build(score,total,[p[0] for p in plan],a.soundfont)
    temporary=a.out/'video-only.mp4'
    enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','fast','-threads','4','-crf','19','-pix_fmt','yuv420p','-an',str(temporary)],stdin=subprocess.PIPE)
    def fixed(idx,b,x,mode):
        im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
        d.rectangle((70,63,78,100),fill=RED);tx(d,96,63,m.get('brand','新闻档案'),31,b=True)
        tx(d,1420,72,m.get('edition','ARCHIVE'),24,SUB,w=410)
        d.line((70,119,1850,119),fill=LINE,width=2)
        d.line((70,907,1850,907),fill=LINE,width=2)
        tx(d,72,928,f'{idx+1:02d} / {len(plan):02d}',32,RED,True,180)
        tx(d,279,924,b['caption'],36,WHITE,False,1520)
        tx(d,72,1003,{'recorded':'本人录音','synthetic-own':'本人授权AI配音','synthetic-stock':'AI合成旁白',None:'剪辑预览 / 无旁白'}[a.voice_kind],22,SUB)
        tx(d,1430,1003,m.get('author_credit',''),22,SUB,w=390)
        if mode=='split':
            d.rectangle((70,170,1119,857),fill='#162436')
            tx(d,113,231,b['headline'],65,b=True,w=960)
            tx(d,114,353,b['fact'],73,WHITE,True,950)
            d.rectangle((116,456,204,462),fill=RED)
            tx(d,114,509,b['detail'],37,SUB,w=950)
            tx(d,114,733,x['credit'],26,SUB,w=970)
        elif mode=='full':
            d.rectangle((82,653,900,846),fill='#162436')
            d.rectangle((82,653,93,846),fill=RED)
            tx(d,111,675,b['headline'],55,WHITE,True,760)
            tx(d,114,766,b['detail'],32,SUB,w=760)
            tx(d,560,1003,x['credit'],22,SUB,w=700)
        elif mode=='statement':
            d.rectangle((70,160,1850,856),fill='#162436')
            tx(d,114,197,b['headline'],26,RED,True)
            tx(d,114,270,b['fact'],64,WHITE,True)
            tx(d,114,362,b['detail'],31,SUB)
            d.line((115,441,1805,441),fill=LINE,width=2)
            for j,line in enumerate(b['graphic']['lines']):
                tx(d,114,485+j*92,line,51,WHITE,True,w=1680)
        else:
            tx(d,76,193,b['headline'],72,WHITE,True)
            tx(d,79,310,b['fact'],98,RED,True)
            tx(d,83,463,b['detail'],33,SUB)
            d.line((108,671,1756,671),fill=LINE,width=4)
            for j,(k,v) in enumerate(b['graphic']['steps']):
                xp=108+1648*j/(len(b['graphic']['steps'])-1)
                if j==len(b['graphic']['steps'])-1:xp-=200
                tx(d,xp,723,k,37,WHITE,True,360);tx(d,xp,784,v,24,SUB,w=360)
        return im
    def smooth(z):
        z=min(1,max(0,z));return z*z*(3-2*z)
    try:
        for idx,(at,du,n,b,x,f,start,mode) in enumerate(plan):
            layer=fixed(idx,b,x,mode); dec=None
            if f:
                if mode=='full': xx,yy,vw,vh=0,122,W,776
                else:xx,yy,vw,vh=1150,170,700,687
                crop=x.get('crop'); pre=('crop='+':'.join(map(str,crop))+',') if crop else ''
                vf=pre+f'fps=30,scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:color=0x101a27,setsar=1'
                dec=subprocess.Popen(['ffmpeg','-v','error','-ss',str(start),'-i',str(f),'-an','-vf',vf,'-frames:v',str(n),'-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'],stdout=subprocess.PIPE)
            for k in range(n):
                im=layer.copy();local=k/FPS
                if dec:
                    raw=dec.stdout.read(vw*vh*3);need(len(raw)==vw*vh*3,'Clip ended unexpectedly')
                    im.paste(Image.frombytes('RGB',(vw,vh),raw),(xx,yy))
                    if mode=='full':im.paste(layer.crop((82,653,901,847)),(82,653))
                d=ImageDraw.Draw(im)
                if mode in ('timeline','close'):
                    p=smooth(local/1.5)
                    d.line((108,671,108+1648*p,671),fill=RED,width=4)
                    for j in range(len(b['graphic']['steps'])):
                        uu=j/(len(b['graphic']['steps'])-1); xp=108+1648*uu
                        if p+.01>=uu:d.ellipse((xp-8,663,xp+8,679),fill=RED)
                d.line((70,118,70+1780*(at+local)/total,118),fill=RED,width=3)
                if local<.34:
                    q=smooth(local/.34)
                    d.rectangle((70,141,70+int(96*q),145),fill=RED)
                enc.stdin.write(im.tobytes())
            if dec:need(dec.wait()==0,'Source decode failed')
    finally:
        enc.stdin.close()
    need(enc.wait()==0,'Encode failed')
    out=a.out/'broadcast-preview.mp4'
    if a.narration:
        g='[1:a]loudnorm=I=-16:TP=-2:LRA=9,aresample=48000,apad[n];[n]asplit=2[d][v];[2:a]volume=0.24[b];[b][d]sidechaincompress=threshold=0.035:ratio=5:attack=15:release=240[m];[v][m]amix=inputs=2:normalize=0,alimiter=limit=0.92[a]'
        run('-i',temporary,'-i',a.narration,'-i',score,'-filter_complex',g,'-map','0:v','-map','[a]','-t',total,'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',out)
    else:
        run('-i',temporary,'-i',score,'-map','0:v','-map','1:a','-af','loudnorm=I=-17:TP=-2:LRA=9,aresample=48000','-t',total,'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',out)
    need(abs(probe(out)-total)<.05 and abs(probe(out,'a:0')-total)<.08,'Timing mismatch')
    run('-i',out,'-f','null','-')
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    (a.out/'captions.srt').write_text('\n\n'.join(f'{k+1}\n{stamp(p[0])} --> {stamp(p[0]+p[1])}\n{p[3]["caption"]}' for k,p in enumerate(plan))+'\n')
    data=[{'at':at,'duration':du,'source_in':start if x else None,'source_out':start+du if x else None,'source':x['source'] if x else m['story_source'],'credit':x['credit'] if x else 'original graphic','rights':x['rights'] if x else None} for at,du,n,b,x,f,start,mode in plan]
    payload={'story':m['story_source'],'shots':data,'voice':a.voice_kind,'score':'original broadcast bed'}
    if editorial:
        payload['editorial']=editorial
        for row, (_,_,_,b,*_) in zip(data, plan):
            row.update({k:b[k] for k in ('role','fact_ids','visual_role','visual_date','event_date','quote_mode') if k in b})
    (a.out/'edit-and-credits.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
