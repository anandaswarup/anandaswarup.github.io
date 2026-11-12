"""Build a dependency-free static site from reviewed content and CV bibliography."""
from pathlib import Path
import re, json, html, shutil, hashlib
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site'
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
VERSION = hashlib.sha256((ROOT/'assets/style.css').read_bytes()+(ROOT/'assets/site.js').read_bytes()).hexdigest()[:10]
E = html.escape
bib = (ROOT/'assets/publications.bib').read_text()
# Brace-aware extraction preserves author lists and titles from the CV's BibTeX.
entries = {}
for m in re.finditer(r'@(\w+)\s*\{([^,]+),', bib):
    start = m.end(); i = start; depth = 1
    while depth:
        if bib[i] == '{': depth += 1
        elif bib[i] == '}': depth -= 1
        i += 1
    body = bib[start:i-1]; fields = {}; pos = 0
    while match := re.search(r'(\w+)\s*=\s*([{"])', body[pos:]):
        key = match[1].lower(); delim = match[2]; a = pos + match.end(); b = a
        if delim == '{':
            d = 1
            while d:
                if body[b] == '{': d += 1
                elif body[b] == '}': d -= 1
                b += 1
        else:
            b = body.index('"',a)+1
        value = body[a:b-1]
        value = re.sub(r'\\(?:textbf|emph)\{([^{}]*)\}',r'\1',value)
        value = value.replace('\\_','_').replace('{','').replace('}','')
        fields[key] = ' '.join(value.split()); pos = b
    fields['key'] = m[2]; fields['raw'] = bib[m.start():i]
    entries[m[2]] = fields
# Order matches the PUBLICATIONS section of cv_anandaswarup.tex (uncited entries are excluded).
keys = ['Vadapalli2027LALMCaptions','DattaVadapalli2027RewardFunctions','SivalankaVadapalli2027ImageCaptions','KolarVadapalli2027BrainMRI','10.1007/978-3-032-28463-1_18','DBLP:journals/corr/abs-2509-23990','DBLP:journals/sncs/Vadapalli25','DBLP:conf/blizzard/AchantaVG17','DBLP:conf/interspeech/VadapalliG16','DBLP:conf/ssw/AchantaBPVG16','DBLP:conf/blizzard/PrahalladVRKM0S15','DBLP:conf/blizzard/RallabandiVAG15','DBLP:journals/corr/AchantaVRG15','DBLP:conf/blizzard/PrahalladVKML0P14','DBLP:conf/interspeech/VadapalliP14','DBLP:conf/acl/ElluruVEMP13','DBLP:conf/blizzard/PrahalladVEMPBM13','DBLP:conf/ssw/VadapalliBP13']
N = len(keys)
# Unpublished manuscripts carry no invented dates, proceedings metadata, or links.
FORTHCOMING = {
    'Vadapalli2027LALMCaptions': ('Submitted', 'ERC-LM Workshop at ICASSP 2027'),
    'DattaVadapalli2027RewardFunctions': ('Accepted', 'ACDSA 2027 · International Conference on Artificial Intelligence, Computer, Data Sciences, and Applications'),
    'SivalankaVadapalli2027ImageCaptions': ('Accepted', 'ACDSA 2027 · International Conference on Artificial Intelligence, Computer, Data Sciences, and Applications'),
    'KolarVadapalli2027BrainMRI': ('Accepted', 'ACDSA 2027 · International Conference on Artificial Intelligence, Computer, Data Sciences, and Applications'),
}
projects = json.loads((ROOT/'projects.json').read_text())
assert sorted(i for p in projects for i in p['papers']) == list(range(N)), 'Every CV paper must belong to one project'
for p in projects:
    for i in p['papers']: entries[keys[i]]['project'] = p['slug']
email = 'anandaswarup.vadapalli@gmail.com'
social = [('Google Scholar','https://scholar.google.com/citations?user=jeGx-8EAAAAJ&hl=en'),('GitHub','https://github.com/anandaswarup'),('LinkedIn','https://www.linkedin.com/in/anandaswarupvadapalli/')]
def links(): return ''.join(f'<a href="{E(u)}">{t}</a>' for t,u in social)

def page(name,title,body,depth=0,description=None):
    pre = '/' if title == 'Page not found' else '../'*depth
    nav = ''.join(f'<a href="{pre}{f}"'+(' aria-current="page"' if name==label else '')+f'>{label}</a>' for label,f in [('Research','projects.html'),('Publications','publications.html'),('About','about.html'),('CV','cv.html')])
    desc = description or 'Anandaswarup Vadapalli — machine learning researcher. Evaluation of generative models across speech, language, and multimodal AI.'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#fbfaf7" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#14161a" media="(prefers-color-scheme: dark)"><title>{E(title)} · Anandaswarup Vadapalli</title><link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap"><link rel="stylesheet" href="{pre}assets/style.css?v={VERSION}"><script defer src="{pre}assets/site.js?v={VERSION}"></script><noscript><style>.menu-toggle{{display:none!important}}.site-nav{{display:flex!important}}</style></noscript></head><body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="{pre}index.html">Anandaswarup Vadapalli</a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation"><span class="sr-only">Menu</span><span aria-hidden="true" class="bars"></span></button><nav id="navigation" class="site-nav" aria-label="Main navigation">{nav}</nav></div></header><main id="main" class="wrap">{body}</main><footer class="site-footer"><div class="wrap footer-inner"><div><p class="footer-name">Anandaswarup Vadapalli</p><p>Machine learning researcher · Hyderabad, India</p></div><div class="footer-links"><a href="mailto:{email}">Email</a>{links()}</div></div><div class="wrap footer-bottom"><span>© 2026 Anandaswarup Vadapalli</span><a href="#main">Back to top ↑</a></div></footer></body></html>'''

def intro(kicker,title,desc): return f'<header class="page-intro"><p class="kicker">{kicker}</p><h1>{title}</h1><p class="lede">{desc}</p></header>'
def heading(title,link=None):
    return '<div class="section-head"><h2>'+title+'</h2>'+(f'<a class="more" href="{link[1]}">{link[0]} →</a>' if link else '')+'</div>'
def card(p,pre=''):
    n = len(p['papers'])
    return f'''<article class="card" data-category="{E(p['category'])}" data-search="{E(p['title']+' '+p['summary'])}"><p class="card-meta"><span class="tag">{E(p['category'])}</span><span>{E(p['period'])}</span></p><h3><a href="{pre}projects/{p['slug']}.html">{p['title']}</a></h3><p>{p['summary']}</p><p class="card-foot">{n} paper{'s' if n!=1 else ''} <span aria-hidden="true">→</span></p></article>'''

def authors(p):
    names = [', '.join(reversed(a.split(', '))).replace(', ',' ') if ', ' in a else a for a in p['author'].split(' and ')]
    return E(', '.join(names)).replace('Anandaswarup Vadapalli','<strong>Anandaswarup Vadapalli</strong>')
def status(p):
    if p['key'] in FORTHCOMING: return FORTHCOMING[p['key']][0]
    return 'Preprint' if p.get('journal')=='CoRR' else 'Published'
def venue(p):
    if p['key'] in FORTHCOMING: return FORTHCOMING[p['key']][1]
    if p.get('journal')=='CoRR': return 'arXiv preprint'
    v = p.get('booktitle', p.get('journal',''))
    if p.get('publisher','').startswith('Springer'): v += ' (Springer)'
    return v.replace('SN Comput. Sci.','SN Computer Science')
def publication(i,pre=''):
    p = entries[keys[i]]; s = status(p)
    url = p.get('url', 'https://doi.org/'+p['key'] if p['key'].startswith('10.') else '')
    title = f'<a href="{E(url)}">{E(p["title"])}</a>' if url else E(p['title'])
    badge = f'<span class="badge badge-{s.lower()}">{s}</span>' if s!='Published' else ''
    year = '' if p['key'] in FORTHCOMING or p.get('year','') in venue(p) else f' · {p.get("year","")}'
    actions = (f'<a href="{E(url)}">Paper ↗</a>' if url else '<span class="muted">Manuscript forthcoming</span>')+f'<a href="{pre}projects/{p["project"]}.html">Project</a><a href="{pre}assets/citations/paper-{i+1}.bib" download>BibTeX</a>'
    return f'''<article class="pub" data-category="{s}" data-search="{E(p['title']+' '+p['author']+' '+venue(p)+' '+s+' '+p.get('year',''))}"><h3>{badge}{title}</h3><p class="authors">{authors(p)}</p><p class="venue"><em>{E(venue(p))}</em>{year}</p><p class="pub-links">{actions}</p></article>'''

# Home
lalm = projects[0]
stats = ''.join(f'<div><b>{v}</b><span>{t}</span></div>' for v,t in lalm['highlights'])
news = [('Submitted','Sole-author paper on evaluating large audio language model captions: <a href="projects/lalm-captions.html">reference agreement is not acoustic correctness</a>. ERC-LM Workshop, ICASSP 2027.'),
        ('Accepted','Three papers with mentees at ACDSA 2027, on <a href="projects/reward-evaluation.html">reward functions for robots</a>, <a href="projects/caption-evaluation.html">LLM image captions</a>, and <a href="projects/mri-explanations.html">brain MRI explanations</a>.'),
        ('Preprint','<a href="projects/efficient-translation.html">The hidden costs of translation accuracy</a>: distillation, quantization, and carbon impact for NLLB-200.'),
        ('Published','<a href="projects/phrase-breaks.html">Phrase break prediction in an end-to-end TTS system</a>, SN Computer Science, 2025.'),
        ('Ph.D.','Awarded a Ph.D. in Computer Science and Engineering by IIIT Hyderabad, March 2025. <a href="assets/anandaswarup-vadapalli-phd-thesis.pdf">Read the thesis (PDF)</a>.')]
home = f'''<section class="hero"><div class="hero-text"><p class="kicker">Machine learning researcher · Hyderabad, India</p><h1>Anandaswarup Vadapalli</h1><p class="lede">I test whether generative model outputs are actually correct, using controlled benchmarks, statistical analysis, and human review.</p><p>My research focuses on speech, language, and multimodal AI, from building neural text-to-speech systems to evaluating large language and audio models. I teach the Machine Learning track of the MSIT program at CIHL, IIIT Hyderabad Campus, and mentor applied research at ResearchSpark Hub.</p><div class="actions"><a class="button primary" href="projects.html">Explore my research</a><a class="button" href="assets/anandaswarup-vadapalli-cv.pdf">CV (PDF)</a><a class="button" href="mailto:{email}">Email me</a></div><p class="profiles">{links()}</p></div><figure class="portrait"><img src="assets/anandaswarup-vadapalli.png" alt="Portrait of Anandaswarup Vadapalli" width="800" height="800" fetchpriority="high"></figure></section>'''
home += f'''<section class="feature" aria-labelledby="feature-title"><div class="feature-text"><p class="kicker">Latest work · {E(lalm['period'])}</p><h2 id="feature-title"><a href="projects/{lalm['slug']}.html">{E(entries[keys[0]]['title'])}</a></h2><p>{lalm['summary']} In a blind listening review, the model ranked third or fourth by reference-based metrics was rated accurate on 47 of 50 recordings.</p><p class="feature-links"><a class="button primary" href="projects/{lalm['slug']}.html">Read the project</a><a class="button" href="{lalm['resources'][0][1]}">Code and data ↗</a></p></div><div class="stats">{stats}</div></section>'''
home += '<section class="section">'+heading('News')+'<ul class="news">'+''.join(f'<li><span class="badge badge-{t.lower().strip(".")}">{t}</span><p>{x}</p></li>' for t,x in news)+'</ul></section>'
home += '<section class="section">'+heading('Research',('All research threads','projects.html'))+'<div class="grid">'+''.join(card(projects[i]) for i in [1,4,5])+'</div></section>'
home += '<section class="section">'+heading('Selected publications',('All publications','publications.html'))+'<div class="pub-list">'+''.join(publication(i) for i in [0,5,6,8])+'</div></section>'
(OUT/'index.html').write_text(page('Home','Research',home))

def filters(options): return '<div class="filters" role="group" aria-label="Filter by category">'+''.join(f'<button type="button" data-filter="{x}" aria-pressed="{str(j==0).lower()}">{x}</button>' for j,x in enumerate(options))+'</div>'
body = intro('Research','Research threads',f'{len(projects)} projects spanning all {N} papers in my CV. Each page sets out the question, the method, what was found, and the limits of the evidence.')
body += '<section class="filter-section" data-filter-section><div class="toolbar">'+filters(['All','Evaluation','Efficiency','Speech & language','Applied ML'])+f'<p class="results-count" aria-live="polite">{len(projects)} projects</p></div><div class="grid">'+''.join(card(p) for p in projects)+'</div><p class="empty" hidden>No projects match this filter.</p></section>'
(OUT/'projects.html').write_text(page('Research','Research',body))

groups = {}
for i,k in enumerate(keys): groups.setdefault('Forthcoming' if k in FORTHCOMING else entries[k].get('year',''), []).append(i)
body = intro('Publications','Publications',f'{N} papers on machine learning, language, and speech since 2013. Submitted and accepted manuscripts are labelled; links are added once they are public.')
body += '<section class="filter-section" data-filter-section><div class="toolbar"><label class="search"><span class="sr-only">Search publications</span><input type="search" placeholder="Search title, author, venue, or year" aria-label="Search publications"></label>'+filters(['All','Published','Accepted','Submitted','Preprint'])+f'</div><div class="toolbar-meta"><p class="results-count" aria-live="polite">{N} publications</p><a class="more" href="assets/publications.bib" download>Download BibTeX</a></div>'
body += ''.join(f'<section class="pub-group" data-group><h2 class="group-label">{g}</h2><div class="pub-list">'+''.join(publication(i) for i in items)+'</div></section>' for g,items in groups.items())
body += '<p class="empty" hidden>No matching publications. Try another search or category.</p></section>'
(OUT/'publications.html').write_text(page('Publications','Publications',body))

timeline = [('Apr 2025 – present','Innovation Mentor (part-time)','ResearchSpark Hub','https://www.researchsparkhub.com/board-of-advisors','Guide ML and GenAI research across reward modeling, image captioning, multimodal prompting, and audio applications. Advise research teams on model selection, experimental controls, evaluation methods, and implementation quality.'),
            ('Aug 2020 – present','Assistant Professor, Machine Learning Track','MSIT Program, CIHL · IIIT Hyderabad Campus','','Design and deliver the Machine Learning track curriculum. Mentor student cohorts through model development, evaluation, and prototyping in NLP and generative modeling, and supervise practicum and co-op projects with academic and industry partners.'),
            ('Aug 2010 – Mar 2025','Researcher and Ph.D. candidate','Language Technologies Research Center, IIIT Hyderabad','','Developed sequence models and learned word representations, progressing from recurrent networks to fine-tuned BERT. Built neural text-to-speech pipelines, evaluated them with objective benchmarks and listening studies, and contributed to Blizzard Challenge systems.')]
education = [('Mar 2025','Ph.D., Computer Science and Engineering','IIIT Hyderabad','Thesis: <em>Prediction and Incorporation of Phrase Break Models in Text-to-Speech Systems</em>. Advisor: Dr. Kishore Prahallad.<br><a href="assets/anandaswarup-vadapalli-phd-thesis.pdf">Read the thesis (PDF, 85 pages)</a>'),
             ('Jul 2010','M.S., Information Technology','IIIT Hyderabad','Specialization in Language Technologies.'),
             ('May 2005','B.E., Electrical and Electronics Engineering','Osmania University, Hyderabad','')]
def entry(when,title,where,url,text): return f'<li><span class="when">{when}</span><div><h3>{title}</h3><p class="where">'+(f'<a href="{url}">{where} ↗</a>' if url else where)+f'</p>'+(f'<p>{text}</p>' if text else '')+'</div></li>'
about = intro('About','About me','Researcher, educator, and mentor working on how we evaluate machine learning systems.')
about += '''<section class="about"><img class="about-portrait" src="assets/anandaswarup-vadapalli.png" alt="Portrait of Anandaswarup Vadapalli" width="800" height="800"><div class="prose"><p>My research began in speech synthesis and language technologies: phrase break prediction, learned word representations, neural text-to-speech, and multilingual synthesis for Indian languages. That work, and my Ph.D. thesis at IIIT Hyderabad, taught me that a system's benchmark score and the experience of the person using it can disagree.</p><p>My recent work follows that question into generative AI. My sole-author study of large audio language models found that reference-based metrics can rank models differently from listening-based assessment. With the research teams I mentor, I study LLM judges and reward modeling, image-caption benchmarking, audience-targeted medical explanations, and the cost of efficient inference.</p><p>Across these areas I combine model development with controlled experiments, statistical testing, and human evaluation. I teach the Machine Learning track of the MSIT program at CIHL, IIIT Hyderabad Campus, and serve as a part-time Innovation Mentor at ResearchSpark Hub.</p><p class="profiles"><a href="mailto:'''+email+'">'+email+'</a>'+links()+'''</p></div></section>'''
about += '<section class="section">'+heading('Experience')+'<ol class="timeline">'+''.join(entry(*t) for t in timeline)+'</ol></section>'
about += '<section class="section">'+heading('Education')+'<ol class="timeline">'+''.join(entry(w,t,p,'',x) for w,t,p,x in education)+'</ol></section>'
(OUT/'about.html').write_text(page('About','About',about))

skills = [('ML and generative AI','Transformers, representation learning, sequence modeling, supervised fine-tuning, reward modeling, large audio language models, multimodal LLM evaluation, prompt design.'),
          ('Evaluation and efficiency','Controlled benchmarking, human evaluation, error analysis, statistical testing (permutation tests, bootstrap intervals, Holm correction), audio captioning metrics, distillation, quantization (FP16, INT8, INT4), latency and carbon-impact measurement.'),
          ('Tools and implementation','Python, PyTorch, Hugging Face Transformers, Hugging Face Jobs, Git, GitHub Actions, Bash, reproducible training and evaluation pipelines.'),
          ('Research leadership','Experimental design, technical mentorship, implementation review, academic and industry collaboration, scientific writing.')]
cv = intro('Curriculum vitae','CV','Experience, projects, education, skills, and the complete publication list in one document.')
cv += '''<section class="cv-panel"><div><h2>Full CV</h2><p>PDF · 4 pages · Updated November 2026</p></div><div class="actions"><a class="button primary" href="assets/anandaswarup-vadapalli-cv.pdf" download>Download PDF</a><a class="button" href="assets/anandaswarup-vadapalli-cv.pdf">Open in browser ↗</a></div></section>'''
cv += '<section class="section">'+heading('Skills')+'<dl class="skills">'+''.join(f'<div><dt>{t}</dt><dd>{d}</dd></div>' for t,d in skills)+'</dl></section>'
(OUT/'cv.html').write_text(page('CV','Curriculum vitae',cv))

(OUT/'projects').mkdir(exist_ok=True)
for n,p in enumerate(projects):
    body = '<a class="breadcrumb" href="../projects.html">← All research</a>'+intro(E(p['category'])+' · '+E(p['period']),p['title'],p['summary'])
    if p.get('highlights'): body += '<div class="stats stats-inline">'+''.join(f'<div><b>{v}</b><span>{t}</span></div>' for v,t in p['highlights'])+'</div>'
    body += '<div class="project-detail"><nav class="toc" aria-label="On this page"><p class="kicker">On this page</p><a href="#question">The question</a><a href="#approach">Approach</a><a href="#findings">Findings and scope</a><a href="#papers">Publications</a></nav><div class="prose"><section id="question"><h2>The question</h2><p>'+p['question']+'</p></section><section id="approach"><h2>Approach</h2>'+''.join('<p>'+v+'</p>' for v in p['approach'])+'</section><section id="findings"><h2>Findings and scope</h2>'+''.join('<p>'+v+'</p>' for v in p['findings'])+'</section>'
    if p.get('resources'): body += '<p class="resources">'+''.join(f'<a class="button" href="{E(u)}">{t} ↗</a>' if u.startswith('http') else f'<a class="button" href="../{E(u)}">{t}</a>' for t,u in p['resources'])+'</p>'
    body += '<section id="papers"><h2>Publications</h2><div class="pub-list">'+''.join(publication(i,'../') for i in p['papers'])+'</div></section></div></div>'
    nxt = projects[(n+1)%len(projects)]
    body += f'<a class="next" href="{nxt["slug"]}.html"><span class="kicker">Next project</span><span>{nxt["title"]} →</span></a>'
    (OUT/'projects'/f'{p["slug"]}.html').write_text(page('Research',p['title'],body,1,p['summary']))
(OUT/'assets/citations').mkdir(exist_ok=True)
for f in (OUT/'assets/citations').glob('paper-*.bib'): f.unlink()
for i,key in enumerate(keys): (OUT/'assets/citations'/f'paper-{i+1}.bib').write_text(entries[key]['raw']+'\n')
# The bibliography download matches the CV publication list exactly (not uncited entries).
(OUT/'assets/publications.bib').write_text('\n\n'.join(entries[k]['raw'] for k in keys)+'\n')
(OUT/'404.html').write_text(page('', 'Page not found',intro('404','Page not found','This page could not be found. <a href="/index.html">Return to the homepage →</a>')))
(OUT/'.nojekyll').touch()
print(f'Built 5 main pages, {len(projects)} project pages, and {N} publications in {OUT}')
