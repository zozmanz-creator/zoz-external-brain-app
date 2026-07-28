#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, re, urllib.request
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
VENUE_ASSETS = ASSETS / 'venues'
ASSETS.mkdir(exist_ok=True)
VENUE_ASSETS.mkdir(exist_ok=True)

HERO_SOURCES = [
    'https://images.pexels.com/photos/30592890/pexels-photo-30592890.jpeg?auto=compress&cs=tinysrgb&w=2400',
    'https://images.pexels.com/photos/3171837/pexels-photo-3171837.jpeg?auto=compress&cs=tinysrgb&w=2400',
]

def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'ZlachnyChisinauBuild/1.0'})
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

def cover(image: Image.Image, size: tuple[int,int]) -> Image.Image:
    tw,th=size; w,h=image.size
    scale=max(tw/w, th/h); nw,nh=round(w*scale),round(h*scale)
    image=image.resize((nw,nh),Image.Resampling.LANCZOS)
    left=(nw-tw)//2; top=(nh-th)//2
    return image.crop((left,top,left+tw,top+th))

def save_webp(image: Image.Image, path: Path, size: tuple[int,int], quality=84) -> dict:
    image=cover(image,size)
    image=ImageEnhance.Contrast(image).enhance(1.03)
    image=ImageEnhance.Color(image).enhance(1.04)
    path.parent.mkdir(parents=True,exist_ok=True)
    image.save(path,'WEBP',quality=quality,method=6)
    blob=path.read_bytes()
    return {'path':str(path.relative_to(ROOT)).replace('\\','/'),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()}

hero, hero_source = open_remote(HERO_SOURCES)
manifest={'generatedAt':'2026-07-28','heroSource':hero_source,'assets':{}}
manifest['assets']['heroDesktop']=save_webp(hero,ASSETS/'hero-desktop.webp',(2000,1000),88)
w,h=hero.size
mobile=hero.crop((int(w*.28),0,w,h))
manifest['assets']['heroMobile']=save_webp(mobile,ASSETS/'hero-mobile.webp',(900,1200),88)

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
        info=save_webp(image,target,(960,720),82)
        manifest['assets'][venue['id']]={**info,'source':url,'status':'illustrative'}
        venue['image']=info['path']
        venue['imageStatus']='local-illustrative'
    except Exception as exc:
        venue['imageStatus']='external-fallback'
        venue['imageError']=str(exc)

data['schemaVersion']=4
data['updatedAt']='2026-07-28'
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
js=js.replace("function localNow(){return new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Chisinau'}))}","function localNow(){if(new URLSearchParams(location.search).has('qa'))return new Date('2026-07-28T21:00:00');return new Date(new Date().toLocaleString('en-US',{timeZone:'Europe/Chisinau'}))}")
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

(ASSETS/'README.md').write_text('''# Local generated assets\n\nThese files are generated by `scripts/build_v10.py` and committed by GitHub Actions. The published site serves them from this repository, not from third-party image CDNs. Venue images remain illustrative and are labelled as such in the UI. See `manifest.json` for source URLs and SHA-256 hashes.\n''',encoding='utf-8')
print(json.dumps({'hero':hero_source,'venueCount':len(data.get('items',[])),'assetCount':len(manifest['assets'])},indent=2))
