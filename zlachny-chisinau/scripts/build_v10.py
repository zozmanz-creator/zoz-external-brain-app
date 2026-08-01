#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
VENUE_ASSETS = ASSETS / 'venues'
SOURCE_PART = ASSETS / 'source' / 'approved-hero.webp.b64'
ASSETS.mkdir(exist_ok=True)
VENUE_ASSETS.mkdir(exist_ok=True)


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'ZlachnyChisinauBuild/1.2'})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def open_remote(urls: list[str]) -> tuple[Image.Image, str]:
    errors=[]
    for url in urls:
        try:
            return Image.open(io.BytesIO(download(url))).convert('RGB'), url
        except Exception as exc:
            errors.append(f'{url}: {exc}')
    raise RuntimeError('All image sources failed:\n'+'\n'.join(errors))


def cover_position(image: Image.Image, size: tuple[int,int], position=(0.5,0.5)) -> Image.Image:
    tw,th=size; w,h=image.size
    scale=max(tw/w, th/h); nw,nh=round(w*scale),round(h*scale)
    image=image.resize((nw,nh),Image.Resampling.LANCZOS)
    px=max(0,min(1,position[0])); py=max(0,min(1,position[1]))
    left=round((nw-tw)*px); top=round((nh-th)*py)
    return image.crop((left,top,left+tw,top+th))


def contain_on_blur(image: Image.Image, size: tuple[int,int]) -> Image.Image:
    background=cover_position(image,size,(0.5,0.5)).filter(ImageFilter.GaussianBlur(max(12,size[1]//35)))
    background=ImageEnhance.Brightness(background).enhance(0.72)
    tw,th=size; w,h=image.size
    scale=min(tw/w,th/h); nw,nh=round(w*scale),round(h*scale)
    foreground=image.resize((nw,nh),Image.Resampling.LANCZOS)
    left=(tw-nw)//2; top=(th-nh)//2
    background.paste(foreground,(left,top))
    return background


def save_webp(image: Image.Image, path: Path, quality=90) -> dict:
    path.parent.mkdir(parents=True,exist_ok=True)
    image=ImageEnhance.Sharpness(image).enhance(1.08)
    image.save(path,'WEBP',quality=quality,method=6)
    blob=path.read_bytes()
    return {'path':str(path.relative_to(ROOT)).replace('\\','/'),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}


if not SOURCE_PART.exists():
    raise RuntimeError(f'Missing approved hero source: {SOURCE_PART}')
approved_raw=base64.b64decode(''.join(SOURCE_PART.read_text(encoding='utf-8').split()))
approved=Image.open(io.BytesIO(approved_raw)).convert('RGB')
source_hash=hashlib.sha256(approved_raw).hexdigest()

manifest={'generatedAt':'2026-08-01','heroSource':{'type':'project-approved-reference','sha256':source_hash},'assets':{}}
manifest['assets']['heroDesktop']=save_webp(contain_on_blur(approved,(2360,1000)),ASSETS/'hero-desktop.webp',92)
manifest['assets']['heroMobile']=save_webp(cover_position(approved,(900,1200),(0.72,0.48)),ASSETS/'hero-mobile.webp',91)

source_json = ROOT/'venues-v9.json'
if not source_json.exists():
    source_json = ROOT/'venues.json'
data=json.loads(source_json.read_text(encoding='utf-8'))
for venue in data.get('items',[]):
    url=venue.get('image') or venue.get('imageSource')
    if not url or not re.match(r'https?://',url):
        continue
    try:
        image,_=open_remote([url])
        target=VENUE_ASSETS/f"{venue['id']}.webp"
        local=cover_position(image,(960,720))
        local=ImageEnhance.Contrast(local).enhance(1.03)
        local=ImageEnhance.Color(local).enhance(1.04)
        info=save_webp(local,target,82)
        manifest['assets'][venue['id']]={**info,'source':url,'status':'illustrative'}
        venue['image']=info['path']
        venue['imageStatus']='local-illustrative'
    except Exception as exc:
        venue['imageStatus']='external-fallback'
        venue['imageError']=str(exc)

data['schemaVersion']=4
data['updatedAt']='2026-08-01'
(ROOT/'venues-v10.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(ASSETS/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

css=(ROOT/'styles.css').read_text(encoding='utf-8')
extra=ROOT/'v9.css'
if extra.exists(): css += '\n' + extra.read_text(encoding='utf-8')
css=re.sub(r"\.hero-bg\{position:absolute;inset:0;background:[^}]+\}",
           ".hero-bg{position:absolute;inset:0;background:url('assets/hero-desktop.webp') center/cover no-repeat;filter:saturate(1.04) contrast(1.02)}",css,count=1)
css=css.replace(".hero-bg{background-position:67% center}",".hero-bg{background-image:url('assets/hero-mobile.webp');background-position:center 42%}")
css=css.replace('font-family:Inter,system-ui,sans-serif','font-family:Arial,"DejaVu Sans",system-ui,sans-serif')
css=css.replace('font-family:Oswald,Impact,sans-serif','font-family:"DejaVu Sans Condensed",Arial,sans-serif')
(ROOT/'v10.css').write_text(css,encoding='utf-8')

js_source=ROOT/'v9.js'
if not js_source.exists(): js_source=ROOT/'app.js'
js=js_source.read_text(encoding='utf-8')
js=js.replace("fetch('venues-v9.json?v=9'","fetch('venues-v10.json?v=10'")
js=js.replace("fetch('venues.json?v=9'","fetch('venues-v10.json?v=10'")
js=js.replace("function localNow(){return new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Chisinau'}))}","function localNow(){if(new URLSearchParams(location.search).has('qa'))return new Date('2026-08-01T21:00:00');return new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Chisinau'}))}")
(ROOT/'v10.js').write_text(js,encoding='utf-8')

html=(ROOT/'index.html').read_text(encoding='utf-8')
html=re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">','',html)
html=re.sub(r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>','',html)
html=re.sub(r'<link href="https://fonts\.googleapis\.com[^>]+>','',html)
html=re.sub(r'<link rel="stylesheet" href="styles\.css\?v=\d+">(?:<link rel="stylesheet" href="v9\.css\?v=\d+">)?','<link rel="stylesheet" href="v10.css?v=10">',html)
html=re.sub(r'<script src="(?:app|v9)\.js\?v=\d+"></script>','<script src="v10.js?v=10"></script>',html)
html=html.replace('<body>','<body data-build="v10">',1)
html=html.replace('<body data-build="v9">','<body data-build="v10">')
(ROOT/'index.html').write_text(html,encoding='utf-8')

(ASSETS/'README.md').write_text('''# Local generated assets\n\nThese files are generated by `scripts/build_v10.py` and committed by GitHub Actions. The published hero is generated from the exact project-approved reference stored in `assets/source/approved-hero.webp.b64`. Venue images remain illustrative and are labelled in the UI. See `manifest.json` for hashes.\n''',encoding='utf-8')
print(json.dumps({'hero':'project-approved-reference','heroSha256':source_hash,'venueCount':len(data.get('items',[])),'assetCount':len(manifest['assets'])},indent=2))
