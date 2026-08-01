#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
DESKTOP = ASSETS / 'hero-approved.svg'
MOBILE = ASSETS / 'hero-approved-mobile.svg'

for path in (DESKTOP, MOBILE):
    if not path.exists():
        raise RuntimeError(f'Missing approved hero asset: {path}')

manifest_path = ASSETS / 'manifest.json'
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
else:
    manifest = {'assets': {}}

manifest['generatedAt'] = '2026-08-01'
manifest['heroSource'] = {'type': 'project-approved-svg-recreation'}
manifest.setdefault('assets', {})['heroDesktop'] = {
    'path': 'assets/hero-approved.svg',
    'bytes': DESKTOP.stat().st_size,
    'sha256': hashlib.sha256(DESKTOP.read_bytes()).hexdigest(),
}
manifest['assets']['heroMobile'] = {
    'path': 'assets/hero-approved-mobile.svg',
    'bytes': MOBILE.stat().st_size,
    'sha256': hashlib.sha256(MOBILE.read_bytes()).hexdigest(),
}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

print(json.dumps({
    'heroDesktop': manifest['assets']['heroDesktop'],
    'heroMobile': manifest['assets']['heroMobile'],
}, indent=2))
