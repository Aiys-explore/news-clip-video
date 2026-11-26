#!/usr/bin/env python3
import argparse,json,subprocess,tempfile,shutil
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
W,H,FPS=1280,720,30
P,I,M,A='#f8f3e5','#202d30','#4b6263','#a54530'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def run(*a):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,a)],check=True)
def probe(p,what='v:0'):
    res=subprocess.check_output(['ffprobe','-v','error','-select_streams',what,'-show_entries','stream=duration:format=duration','-of','json',str(p)])
    val=json.loads(res);s=val.get('streams',[])
    need(s,f'No {what} stream: {p}')
    return float(s[0].get('duration') or val['format']['duration'])
def main():
    ap=argparse.ArgumentParser(description='Assemble a source-checked news edit')
    ap.add_argument('manifest',type=Path);ap.add_argument('--media',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--narration',type=Path);ap.add_argument('--voice-kind',choices=['recorded','synthetic-own','synthetic-stock'])
    ap.add_argument('--font',type=Path,default=Path('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'))
    a=ap.parse_args();m=json.loads(a.manifest.read_text(encoding='utf8'))
    need(bool(a.narration)==bool(a.voice_kind),'Declare whether narration is recorded, synthetic-own, or synthetic-stock')
    need(bool(m['story_source']),'Story source missing')
    need(a.font.is_file(),'Provide a CJK font with --font')
    a.out.mkdir(parents=True,exist_ok=True)
    media=a.media.resolve(); assets=m['assets'];beats=m['beats']
    def asset_file(x):
        p=(media/x['file']).resolve()
        need(p.is_relative_to(media) and p.is_file(),'Missing asset or outside media folder')
        need(x.get('rights_status')=='cleared_for_edit' and all(x.get(k) for k in ('source','rights','credit')),f'Rights or provenance missing: {p.name}')
        return p
    total=0;plan=[]
    for b in beats:
        dur=float(b['duration']);need(1<=dur<=30 and abs(round(dur*FPS)-dur*FPS)<1e-7,'Beat lengths must align to video frames')
        x=assets[b['asset']] if 'asset' in b else None
        if x:
            p=asset_file(x);start=float(b['in']);need(start>=0 and start+dur<=probe(p)+.01,'Cut exceeds source')
        else:p=None;start=0
        plan.append((total,dur,p,start,x,b));total+=dur
    need(plan and total<=180,'Use a 1–180 second edit')
    if a.narration:
        ln=probe(a.narration,'a:0');need(total-2<=ln<=total+.04,'Retiming required: narration must fit within 2 seconds of the edit')
    def page(idx,b,x):
        im=Image.new('RGB',(W,H),P);d=ImageDraw.Draw(im)
        def text(pos,s,size,c=I,maxw=None,center=False):
            f=ImageFont.truetype(str(a.font),size,index=2 if 'NotoSerifCJK' in a.font.name else 0)
            w=f.getlength(s);need(maxw is None or w<=maxw,'Text too long in scene '+str(idx+1)+': '+s)
            px,py=pos;d.text((px-w/2 if center else px,py),s,font=f,fill=c,anchor='lt')
        d.line((42,44,1238,44),fill=I,width=2)
        text((45,56),m.get('brand','新闻图解'),21,A,600)
        text((920,57),m.get('edition','NEWS BRIEF'),19,M,310)
        text((44,94),m['title'],47,I,1190)
        # Only the editor-specified window receives moving archival footage.
        d.rectangle((44,167,761,568),outline='#a5a79a',width=2)
        d.rectangle((787,167,1237,568),fill='#eee9da')
        d.line((808,209,1214,209),fill=A,width=2)
        text((808,181),f'{idx+1:02d} / {len(beats):02d}',19,A)
        text((808,230),b['headline'],31,I,400)
        text((808,292),b['fact'],39,A,400)
        text((808,358),b['detail'],23,I,400)
        text((808,407),b['note'],20,M,400)
        if x:text((808,496),x['credit'],20,M,400)
        else:
            graphic=b['graphic'];steps=graphic['steps']
            need(2<=len(steps)<=4,'Graphic needs 2–4 timeline labels')
            text((403,231),graphic['title'],44,I,690,True)
            d.line((148,360,656,360),fill='#a5a79a',width=2)
            for k,(label,sub) in enumerate(steps):
                px=148+508*k/(len(steps)-1)
                d.ellipse((px-8,352,px+8,368),fill=A);text((px,382),label,25,I,120,True);text((px,428),sub,22,M,126,True)
            text((403,522),graphic.get('note','示意图｜非比例时间轴'),18,M,410,True)
        d.line((44,604,1237,604),fill=I,width=1)
        text((640,621),b['caption'],25,I,1155,True)
        mode={'recorded':'本人录音','synthetic-own':'本人授权AI配音','synthetic-stock':'AI合成旁白',None:'剪辑预览｜无旁白'}[a.voice_kind]
        text((45,678),mode,17,M);text((1055,678),m.get('author_credit',''),17,M,172)
        return im
    music=m.get('music');mp=asset_file(music) if music else None
    with tempfile.TemporaryDirectory(dir=a.out) as td:
        td=Path(td); pieces=[]
        for idx,(_,dur,p,start,x,b) in enumerate(plan):
            bg=td/f'bg{idx}.png';page(idx,b,x).save(bg)
            out=td/f'piece{idx}.mp4'; pieces.append(out)
            if p:
                crop=x.get('crop')
                need(not crop or (len(crop)==4 and all(isinstance(i,int) and i>=0 for i in crop) and min(crop[:2])>=2),'Invalid crop')
                pre=('crop='+':'.join(map(str,crop))+',') if crop else ''
                vf=f'[1:v]{pre}fps=30,scale=714:398:force_original_aspect_ratio=decrease,pad=714:398:(ow-iw)/2:(oh-ih)/2:color=0x171e20,setsar=1[c];[0:v][c]overlay=46:169:shortest=1[v]'
                run('-filter_complex_threads','1','-loop','1','-framerate',FPS,'-i',bg,'-ss',start,'-t',dur,'-i',p,'-filter_complex',vf,'-map','[v]','-an','-t',dur,'-threads','3','-c:v','libx264','-preset','fast','-pix_fmt','yuv420p',out)
            else:run('-loop','1','-framerate',FPS,'-i',bg,'-t',dur,'-an','-threads','3','-c:v','libx264','-preset','fast','-pix_fmt','yuv420p',out)
        lst=td/'concat.txt';lst.write_text(''.join(f'file {p.name}\n' for p in pieces))
        silent=td/'silent.mp4';run('-f','concat','-safe','1','-i',lst,'-c','copy',silent)
        final=a.out/'news-preview.mp4'
        if a.narration and mp:
            filt='[1:a]loudnorm=I=-16:TP=-2:LRA=9,aresample=48000,apad[n];[n]asplit=2[drv][voice];[2:a]volume=0.19,aresample=48000[bg];[bg][drv]sidechaincompress=threshold=0.04:ratio=4:attack=16:release=220[bed];[voice][bed]amix=inputs=2:normalize=0,alimiter=limit=0.93[a]'
            run('-i',silent,'-i',a.narration,'-stream_loop','-1','-i',mp,'-filter_complex',filt,'-map','0:v:0','-map','[a]','-t',total,'-c:v','copy','-c:a','aac','-movflags','+faststart',final)
        elif a.narration:run('-i',silent,'-i',a.narration,'-map','0:v:0','-map','1:a:0','-af','loudnorm=I=-16:TP=-2:LRA=9,aresample=48000,apad','-t',total,'-c:v','copy','-c:a','aac','-movflags','+faststart',final)
        elif mp:run('-i',silent,'-stream_loop','-1','-i',mp,'-map','0:v:0','-map','1:a:0','-af',f'volume=0.55,afade=t=out:st={max(0,total-1)}:d=1','-t',total,'-c:v','copy','-c:a','aac','-movflags','+faststart',final)
        else:run('-i',silent,'-c','copy','-movflags','+faststart',final)
    need(abs(probe(final)-total)<.07,'Video duration mismatch')
    if mp or a.narration:need(abs(probe(final,'a:0')-total)<.12,'Audio duration mismatch')
    run('-i',final,'-f','null','-')
    refs={'story_source':m['story_source'],'shots':[{'at':t,'duration':d,'source_in':i if x else None,'source_out':i+d if x else None,'source':x['source'] if x else 'original graphic','rights':x['rights'] if x else None,'credit':x['credit'] if x else None,'caption':b['caption']} for t,d,p,i,x,b in plan],'music':music,'voice_kind':a.voice_kind}
    (a.out/'edit-and-credits.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf8')
    def stamp(t):
        ms=round(t*1000)
        return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    (a.out/'captions.srt').write_text('\n\n'.join(f'{j+1}\n{stamp(t)} --> {stamp(t+d)}\n{b["caption"]}' for j,(t,d,p,i,x,b) in enumerate(plan))+'\n',encoding='utf8')
if __name__=='__main__':main()
