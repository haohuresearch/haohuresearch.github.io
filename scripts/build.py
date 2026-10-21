"""Build a portable, static academic website. Python standard library only."""
import json
import re
import shutil
from pathlib import Path
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

def entry(title, sub, dates, detail):
    return f'<article class="entry"><div class="entry-heading"><h3>{e(title)}</h3><span class="date">{e(dates)}</span></div><p class="entry-sub">{e(sub)}</p><p class="entry-detail">{e(detail)}</p></article>'

p = data['profile']
sections = [('about','About me'),('news','News'),('education','Education background'),('experience','Work experience'),('publications','Publications'),('services','Services'),('awards','Awards')]
navigation = ''.join(f'<a href="#{anchor}">{title}</a>' for anchor,title in sections)
social = ' · '.join(link(p[key],label) for key,label in [('scholar','Google Scholar'),('linkedin','LinkedIn'),('github','GitHub')] if p.get(key))
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
about += '<h3 class="small-heading">Research interests</h3><ul class="interests">' + ''.join(f'<li>{e(t)}</li>' for t in data['interests'])+'</ul>'
news = heading('news','News')+'<ul class="dated-list news-list">'+''.join(f'<li><span class="date">{e(n["date"])}</span><span>{link(n["url"],n["text"])}</span></li>' for n in data['news'])+'</ul>'
education = heading('education','Education background')+''.join(entry(n['institution'],n['degree'],n['dates'],n['detail']) for n in data['education'])
experience = heading('experience','Work experience')+''.join(entry(n['role'],n['institution'],n['dates'],n['detail']) for n in data['experience'])
pubs = [n for n in data['publications'] if n.get('visible',True)]
publications = heading('publications','Publications','Published and accepted work, preprints, and ongoing manuscripts.')
publications += '''<div class="publication-tools" hidden><div class="filters" role="group" aria-label="Filter publications">'''
for group,label in [('all','All'),('published','Published / Accepted'),('review','Preprint / Under review'),('preparation','In preparation')]:
    count = len(pubs) if group=='all' else sum(n['group']==group for n in pubs)
    if count == 0:
        continue
    publications += f'<button type="button" data-filter="{group}" aria-pressed="{"true" if group=="all" else "false"}">{label} <span>{count}</span></button>'
publications += '</div><label class="search-label" for="publication-search">Search publications</label><input type="search" id="publication-search" placeholder="Search by title, author, or journal…" autocomplete="off"><p id="publication-count" class="result-count" aria-live="polite"></p></div>'
for group,label in [('published','Published or accepted'),('review','Preprints and manuscripts under review'),('preparation','Manuscripts in preparation')]:
    if not any(n['group'] == group for n in pubs):
        continue
    publications += f'<div class="publication-group" data-group="{group}"><h3>{label}</h3><ol class="publication-list">'
    for n in [n for n in pubs if n['group']==group]:
        authors = e(n['authors']).replace('Hao Hu#','<strong>Hao Hu</strong><sup>#</sup>').replace('Hao Hu','<strong>Hao Hu</strong>')
        authors = authors.replace('<strong><strong>Hao Hu</strong></strong>','<strong>Hao Hu</strong>')
        title = link(n['url'],n['title']) if n['url'] else e(n['title'])
        publications += f'<li class="publication"><div class="paper-title">{title}</div><p class="authors">{authors}.</p><p class="venue">{e(n["venue"])}</p><span class="status status-{group}">{e(n["status"])}</span>'
        if n['url']:
            publications += ' '+link(n['url'],'Preprint ↗' if group=='review' else 'Paper ↗','paper-link')
        publications += '</li>'
    publications += '</ol></div>'
publications += '<p class="empty-state" hidden>No matching publications. Try another search term or filter.</p><p class="cofirst-note"># Co-first authors.</p><h3 class="report-heading">Reports and assessments</h3>'
for n in data['reports']:
    publications += f'<article class="report"><h4>{link(n["url"],n["title"])}</h4><p class="venue">{e(n["venue"])}</p><p>{e(n["detail"])}</p></article>'
services=heading('services','Services')+'<h3>Journal reviewing</h3><p>I have reviewed manuscripts for:</p><ul class="reviewing">'+''.join(f'<li>{e(n)}</li>' for n in data['services']['reviewing'])+'</ul><h3>Mentorship and teaching</h3>'
services+=''.join(entry(n['title'],'',n['dates'],n['detail']) for n in data['services']['teaching'])
awards=heading('awards','Honors and awards')+'<ul class="dated-list awards-list">'+''.join(f'<li><span class="date">{e(n["year"])}</span><span>{e(n["title"])}</span></li>' for n in data['awards'])+'</ul>'
content=''.join(f'<section class="content-section" aria-labelledby="{anchor}">{body}</section>' for (anchor,_),body in zip(sections,[about,news,education,experience,publications,services,awards]))
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
</main></div></body></html>'''
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
(OUT/'index.html').write_text(html,encoding='utf-8')
(OUT/'.nojekyll').touch()
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://haohuresearch.github.io/sitemap.xml\n',encoding='utf-8')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://haohuresearch.github.io/</loc></url></urlset>\n',encoding='utf-8')
assert len(re.findall(r'<section class="content-section"',html)) == 7
assert html.count('class="publication"') == len(pubs)
assert all(f'id="{anchor}"' in html for anchor,_ in sections)
print(f'Built dist/index.html: 7 sections, {len(pubs)} publications, {len(data["reports"])} report, {len(data["awards"])} awards.')
