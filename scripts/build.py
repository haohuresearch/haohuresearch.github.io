"""Build a portable, static academic website. Python standard library only."""
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
data = json.loads((ROOT / 'content.json').read_text(encoding='utf-8-sig'))
e = lambda value: escape(str(value), quote=True)

def link(url, label, cls=''):
    if not url:
        return e(label)
    if not (url.startswith(('https://', 'mailto:')) or url.startswith('assets/')):
        raise ValueError('Unsupported link URL: ' + url)
    return f'<a href="{e(url)}" class="{e(cls)}">{e(label)}</a>'

def heading(anchor, title, subtitle=''):
    return f'<h2 id="{anchor}">{title}</h2>' + (f'<p class="section-note">{e(subtitle)}</p>' if subtitle else '')

def entry(title, sub, dates, detail, item=None):
    media = entry_image(item, 'institution') if item else ''
    classes = 'entry institution-entry has-image' if media else 'entry'
    return (f'<article class="{classes}">{media}<div class="entry-body">'
            f'<div class="entry-heading"><h3>{e(title)}</h3><span class="date">{e(dates)}</span></div>'
            f'<p class="entry-sub">{e(sub)}</p><p class="entry-detail">{e(detail)}</p></div></article>')

def entry_image(item, kind):
    """Optional local thumbnail; keep the full image available without cropping."""
    src = item.get('image', '').strip()
    if not src:
        return ''
    path = PurePosixPath(src)
    if (path.parts[:2] != ('assets', 'img') or '..' in path.parts
            or '\\' in src or path.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.avif')):
        raise ValueError('Image must be a relative path under assets/img/: ' + src)
    image_path = (ROOT / src).resolve()
    if not image_path.is_relative_to((ROOT / 'assets' / 'img').resolve()) or not image_path.is_file():
        raise ValueError('Image file not found under assets/img/: ' + src)
    alt = item.get('image_alt', '').strip() or item.get('institution') or item.get('title') or item.get('text', 'Research image')
    caption = item.get('image_caption', '').strip()
    return (f'<figure class="entry-media {kind}-media">'
            f'<a class="image-full-link" href="{e(src)}" target="_blank" rel="noopener" aria-label="View full image: {e(alt)}">'
            f'<img src="{e(src)}" alt="{e(alt)}" width="640" height="400" loading="lazy" decoding="async"></a>'
            + (f'<figcaption>{e(caption)}</figcaption>' if caption else '') + '</figure>')

def research_section(config):
    """Render only enabled research content; hidden drafts are omitted from HTML."""
    result = heading('research', e(config.get('title', 'Research')))
    result += ''.join(f'<p>{e(text)}</p>' for text in config.get('intro', []))
    result += entry_image(config, 'research-hero')
    chapters = [chapter for chapter in config.get('chapters', []) if chapter.get('visible', True)]
    if chapters:
        result += '<nav class="research-contents" aria-label="Research chapters">'
        for index, chapter in enumerate(chapters, 1):
            result += (f'<a href="#research-chapter-{index}"><span class="research-number">{index:02d}</span>'
                       f'<span class="research-topic">{e(chapter["title"])}</span>'
                       + (f'<span class="research-summary">{e(chapter["summary"])}</span>' if chapter.get('summary') else '') + '</a>')
        result += '</nav>'
    for index, chapter in enumerate(chapters, 1):
        result += (f'<article class="research-chapter" aria-labelledby="research-chapter-{index}">'
                   f'<h3 id="research-chapter-{index}">{index}. {e(chapter["title"])}</h3>')
        result += ''.join(f'<p>{e(text)}</p>' for text in chapter.get('paragraphs', []))
        if chapter.get('bullets'):
            result += '<ul class="research-bullets">'+''.join(f'<li>{e(text)}</li>' for text in chapter['bullets'])+'</ul>'
        gallery = ''.join(entry_image(image, 'research') for image in chapter.get('images', []))
        if gallery:
            result += '<div class="research-gallery">'+gallery+'</div>'
        result += '</article>'
    return result

p = data['profile']
research_config = data.get('research', {})
sections = [('about','About me')]
if research_config.get('visible', False):
    sections.append(('research','Research'))
sections += [('news','News'),('publications','Publication'),('education','Education background'),('experience','Work experience'),('services','Services'),('awards','Awards')]
navigation = ''.join(f'<a href="#{anchor}">{title}</a>' for anchor,title in sections)
social = ' · '.join(link(p[key],label) for key,label in [('scholar','Google Scholar'),('linkedin','LinkedIn'),('github','GitHub'),('xiaohongshu','Xiaohongshu')] if p.get(key))
profile = f'''<header class="profile" id="profile">
    <a class="portrait-link" href="#about" aria-label="About {e(p['name'])}"><img class="portrait" src="{e(p['portrait'])}" width="154" height="154" alt="{e(p['name'])}" fetchpriority="high"></a>
    <h1>{e(p['name'])}</h1><p class="position">{e(p['position'])}</p>
    <p class="institution">{e(p['affiliation'])}</p><p class="department">{e(p['department'])}</p>
    <p class="location">{e(p['location'])}</p>
    <p class="email">{link('mailto:'+p['email'],p['email'])}</p>
    <div class="social-links">{social}</div>
    <nav aria-label="On this page">{navigation}</nav>
    <p class="profile-note">Climate · Cities · Energy</p>
    </header>'''

about = heading('about','About me') + ''.join(f'<p>{e(t)}</p>' for t in data['about'])
news = heading('news','News')+'<ul class="dated-list news-list">'
for n in data['news']:
    image = entry_image(n, 'news')
    news += (f'<li><span class="date">{e(n["date"])}</span>'
             f'<div class="news-body{" has-image" if image else ""}"><p class="news-text">{link(n["url"],n["text"])}</p>{image}</div></li>')
news += '</ul>'
education = heading('education','Education background')+''.join(entry(n['institution'],n['degree'],n['dates'],n['detail'],n) for n in data['education'])
experience = heading('experience','Work experience')+''.join(entry(n['role'],n['institution'],n['dates'],n['detail'],n) for n in data['experience'])
pubs = [n for n in data['publications'] if n.get('visible',True)]
publications = heading('publications','Publication') + '<ol class="publication-list">'
for n in pubs:
    group = n['group']
    authors = e(n['authors']).replace('Hao Hu#','<strong>Hao Hu</strong><sup>#</sup>').replace('Hao Hu','<strong>Hao Hu</strong>')
    authors = authors.replace('<strong><strong>Hao Hu</strong></strong>','<strong>Hao Hu</strong>')
    title = link(n['url'],n['title']) if n['url'] else e(n['title'])
    image = entry_image(n, 'paper')
    publications += (f'<li class="publication"><div class="paper-entry{" has-image" if image else ""}">{image}'
                     f'<div class="paper-details"><div class="paper-title">{title}</div><p class="authors">{authors}.</p><p class="venue">{e(n["venue"])}</p><span class="status status-{group}">{e(n["status"])}</span>')
    if n['url']:
        publications += ' '+link(n['url'],'Preprint ↗' if group=='review' else 'Paper ↗','paper-link')
    publications += '</div></div></li>'
publications += '</ol><p class="cofirst-note"># Co-first authors.</p>'
for n in data['reports']:
    publications += f'<article class="report"><h4>{link(n["url"],n["title"])}</h4><p class="venue">{e(n["venue"])}</p><p>{e(n["detail"])}</p></article>'
services=heading('services','Services')+'<h3>Journal reviewing</h3><p>I have reviewed manuscripts for:</p><ul class="reviewing">'+''.join(f'<li>{e(n)}</li>' for n in data['services']['reviewing'])+'</ul><h3>Mentorship and teaching</h3>'
services+=''.join(entry(n['title'],'',n['dates'],n['detail']) for n in data['services']['teaching'])
awards=heading('awards','Honors and awards')+'<ul class="dated-list awards-list">'+''.join(f'<li><span class="date">{e(n["year"])}</span><span>{e(n["title"])}</span></li>' for n in data['awards'])+'</ul>'
section_content = dict(about=about, news=news, education=education, experience=experience, publications=publications, services=services, awards=awards)
if research_config.get('visible', False):
    section_content['research'] = research_section(research_config)
content=''.join(f'<section class="content-section" aria-labelledby="{anchor}">{section_content[anchor]}</section>' for anchor,_ in sections)
cloudflare_site_token = data.get('analytics', {}).get('cloudflare_site_token', '').strip()
analytics_script = ''
if cloudflare_site_token:
    beacon_config = e(json.dumps({'token': cloudflare_site_token}, separators=(',', ':')))
    analytics_script = f'<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon="{beacon_config}"></script>'
html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['name'])} | {e(p['affiliation'])}</title>
<meta name="description" content="Hao Hu, Ph.D. student at USC. Research on urban climate, data centers, air quality, and climate-resilient energy systems.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#173f54">
<link rel="canonical" href="https://haohuresearch.github.io/">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/minimal-light.css"><link rel="stylesheet" href="assets/css/custom.css">
<script src="assets/js/main.js" defer></script></head>
<body><a class="skip-link" href="#main">Skip to content</a><div class="wrapper">{profile}<main id="main">{content}
<footer class="site-footer"><p>© {e(p['name'])} · Updated {e(p['updated'])}</p><p>Based on {link('https://github.com/qizhang94/qizhang94.github.io','Qi Zhang’s template')} and {link('https://github.com/yaoyao-liu/minimal-light','Minimal Light')}.</p></footer>
</main></div>{analytics_script}</body></html>'''
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
(OUT/'index.html').write_text(html,encoding='utf-8')
(OUT/'.nojekyll').touch()
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://haohuresearch.github.io/sitemap.xml\n',encoding='utf-8')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://haohuresearch.github.io/</loc></url></urlset>\n',encoding='utf-8')
assert len(re.findall(r'<section class="content-section"',html)) == len(sections)
assert html.count('class="publication"') == len(pubs)
assert all(f'id="{anchor}"' in html for anchor,_ in sections)
print(f'Built dist/index.html: {len(sections)} sections, {len(pubs)} publications, {len(data["reports"])} report, {len(data["awards"])} awards.')
