"""Build a dependency-free static site from reviewed content and CV bibliography."""
from pathlib import Path
import re, json, html, shutil, hashlib
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site'
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True)
STYLE_VERSION = hashlib.sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:10]
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
keys = ['DattaVadapalli2027RewardFunctions','SivalankaVadapalli2027ImageCaptions','KolarVadapalli2027BrainMRI','10.1007/978-3-032-28463-1_18','DBLP:journals/corr/abs-2509-23990','DBLP:journals/sncs/Vadapalli25','DBLP:conf/blizzard/AchantaVG17','DBLP:conf/interspeech/VadapalliG16','DBLP:conf/ssw/AchantaBPVG16','DBLP:conf/blizzard/PrahalladVRKM0S15','DBLP:conf/blizzard/RallabandiVAG15','DBLP:journals/corr/AchantaVRG15','DBLP:conf/blizzard/PrahalladVKML0P14','DBLP:conf/interspeech/VadapalliP14','DBLP:conf/acl/ElluruVEMP13','DBLP:conf/blizzard/PrahalladVEMPBM13','DBLP:conf/ssw/VadapalliBP13']
projects = json.loads((ROOT/'projects.json').read_text())
assert sorted(i for p in projects for i in p['papers']) == list(range(17)), 'Every CV paper must belong to one project'
for p in projects:
    for i in p['papers']: entries[keys[i]]['project'] = p['slug']
email='anandaswarup.vadapalli@gmail.com'
social = [('Google Scholar','https://scholar.google.com/citations?user=jeGx-8EAAAAJ&hl=en'),('GitHub','https://github.com/anandaswarup'),('LinkedIn','https://www.linkedin.com/in/anandaswarupvadapalli/')]
def links(): return ''.join(f'<a href="{E(u)}">{t} ↗</a>' for t,u in social)
def page(name,title,body,depth=0,description=None):
    pre='/' if title == 'Page not found' else '../'*depth
    nav=''.join(f'<a href="{pre}{f}"'+(' aria-current="page"' if name==label else '')+f'>{label}</a>' for label,f in [('Home','index.html'),('Projects','projects.html'),('Publications','publications.html'),('About','about.html'),('CV','cv.html')])
    text=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{E(description or 'Anandaswarup Vadapalli — machine learning researcher, educator, and technical lead. Research in language, multimodal evaluation, and speech synthesis.')}"><meta name="theme-color" content="#f6f5ef"><title>{E(title)} · Anandaswarup Vadapalli</title><link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{pre}assets/style.css?v={STYLE_VERSION}"><script defer src="{pre}assets/site.js"></script><noscript><style>@media(max-width:720px){{.header{{height:auto;min-height:86px;flex-wrap:wrap;padding-top:15px;padding-bottom:15px}}.header nav{{display:flex;position:static;flex-wrap:wrap;padding:0;border:0;box-shadow:none}}.menu-toggle{{display:none}}}}</style></noscript></head><body><a class="skip" href="#main">Skip to content</a><header class="header"><a class="brand" href="{pre}index.html" aria-label="Anandaswarup Vadapalli home"><span class="brand-name">Anandaswarup<br>Vadapalli</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu <span aria-hidden="true">☰</span></button><nav id="navigation" aria-label="Main navigation">{nav}<a class="nav-contact" href="mailto:{email}">Get in touch ↗</a></nav></header><main id="main">{body}</main><footer><div><a class="footer-name" href="{pre}index.html">Anandaswarup Vadapalli<span>·</span></a><p>Machine learning. Language. Speech.</p></div><div class="footer-links">{links()}<a href="mailto:{email}">Email ↗</a></div><div class="footer-bottom"><span>© 2026 Anandaswarup Vadapalli</span><span>Research with curiosity. Evaluation with care.</span><a href="#main">Back to top ↑</a></div></footer></body></html>'''
    return text

def intro(kicker,title,desc): return f'<section class="page-intro"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lede">{desc}</p></section>'
def card(p,n=0):
    return f'''<article class="project-card" data-category="{p['category']}" data-search="{E(p['title']+' '+p['summary'])}"><a class="project-art art-{p['art']}" href="projects/{p['slug']}.html" tabindex="-1" aria-hidden="true"><span class="art-number">{n+1:02d} / RESEARCH</span><div class="art-lines"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><span class="art-label">{p['motif']}</span><span class="art-arrow">↗</span></a><div class="card-meta"><span>{p['category']}</span><span>{len(p['papers'])} paper{'s' if len(p['papers'])!=1 else ''}</span></div><h3><a href="projects/{p['slug']}.html">{p['title']}</a></h3><p>{p['summary']}</p><a class="text-link" href="projects/{p['slug']}.html">Explore project <span>↗</span></a></article>'''

def publication(i,pre='',compact=False):
    p=entries[keys[i]]; title=E(p['title']); authors=E(p['author'].replace(' and ', ', ')).replace('Anandaswarup Vadapalli','<strong>Anandaswarup Vadapalli</strong>')
    status='Accepted · ACDSA 2027' if i<3 else ('Preprint · '+p['year'] if p.get('journal')=='CoRR' else p.get('year',''))
    venue=p.get('booktitle',p.get('journal',''))
    if i<3: venue='International Conference on Artificial Intelligence, Computer, Data Sciences, and Applications'
    url=p.get('url', 'https://doi.org/'+p['key'] if i==3 else '')
    paperlink=f'<a href="{E(url)}">Paper ↗</a>' if url else '<span class="muted">Manuscript link forthcoming</span>'
    cite=f'{pre}assets/citations/paper-{i+1}.bib'
    return f'''<article class="publication" data-search="{E(p['title']+' '+p['author']+' '+venue+' '+status)}" data-category="{'Accepted' if i<3 else 'Preprint' if p.get('journal')=='CoRR' else 'Published'}"><div class="pub-year">{status}</div><div><h3>{title}</h3><p class="authors">{authors}</p><p class="venue">{E(venue)}</p><div class="pub-links">{paperlink}<a href="{pre}projects/{p['project']}.html">Project ↗</a><a href="{cite}" download>BibTeX ↓</a></div></div></article>'''

home='''<section class="hero"><div class="hero-copy"><p class="eyebrow"><span class="dot"></span> RESEARCHER · EDUCATOR · TECHNICAL LEAD</p><h1>Understanding models.<br>Building with<br><em>evidence.</em></h1><p class="hero-bio">I’m <strong>Anandaswarup Vadapalli</strong>, a machine learning researcher working across language, multimodal AI, and speech. I build models, examine how they behave, and connect evaluation to human experience.</p><div class="actions"><a class="button primary" href="projects.html">Explore my research <span>↗</span></a><a class="button secondary" href="assets/anandaswarup-vadapalli-cv.pdf">View full CV <span>↗</span></a></div><div class="hero-affiliation"><span>Assistant Professor · MSIT, CIHL, IIIT Hyderabad Campus</span><span>Technical Lead (Consultant) · ResearchSpark Hub</span></div></div><figure class="hero-portrait"><img src="assets/anandaswarup-vadapalli.png" alt="Anandaswarup Vadapalli" width="800" height="800" fetchpriority="high"><figcaption><span>Anandaswarup Vadapalli</span><span>Researcher & educator</span></figcaption></figure></section>'''
home+='''<section class="focus-strip"><p class="eyebrow">RESEARCH FOCUS</p><span>LLM & multimodal evaluation</span><span>Efficient machine learning</span><span>Speech & language</span></section><section class="section"><div class="section-heading"><div><p class="eyebrow">A CLOSER LOOK</p><h2>Selected research</h2></div><a class="text-link" href="projects.html">All 9 projects ↗</a></div><div class="project-grid">'''+''.join(card(projects[i],i) for i in [0,3,4])+'''</div></section><section class="approach"><p class="eyebrow">HOW I WORK</p><h2>A model’s score is<br>the start of the question.</h2><div><p>My work combines controlled experiments, hands-on model development, and human evaluation. I’m interested in what a benchmark captures, what it misses, and how those differences affect the people using a system.</p><a class="text-link" href="about.html">More about my work ↗</a></div></section><section class="section"><div class="section-heading"><div><p class="eyebrow">RECENT WORK</p><h2>From the publication desk</h2></div><a class="text-link" href="publications.html">All publications ↗</a></div>'''+''.join(publication(i) for i in [0,4,5])+'''</section><section class="contact-band"><div><p class="eyebrow">LET’S CONNECT</p><h2>Good research starts<br>with a conversation.</h2><p>Research collaborations, applied ML opportunities, and conversations about evaluation, language, or speech.</p></div><a class="button primary" href="mailto:'''+email+'''">Get in touch ↗</a></section>'''
(OUT/'index.html').write_text(page('Home','Research & practice',home))
filters=lambda options: '<div class="filters" role="group" aria-label="Filter by category">'+''.join(f'<button data-filter="{x}" aria-pressed="{str(j==0).lower()}">{x}</button>' for j,x in enumerate(options))+'</div>'
body=intro('RESEARCH / PROJECTS','Questions into <em>investigations.</em>','Nine research threads spanning all 17 papers in my CV. Explore the questions, methods, findings, and publications behind each project.')
body+='<section class="filter-section" data-filter-section>'+filters(['All','Evaluation','Efficiency','Speech & language','Applied ML'])+'<p class="results-count" aria-live="polite">9 projects</p><div class="project-grid">'+''.join(card(p,n) for n,p in enumerate(projects))+'</div><p class="empty" hidden>No projects match this filter.</p></section>'
(OUT/'projects.html').write_text(page('Projects','Projects',body))
body=intro('RESEARCH / PUBLICATIONS','A record of <em>inquiry.</em>','Work across machine learning, language, and speech, from 2013 onward. Accepted manuscripts, published papers, and preprints are labelled separately.')
body+='<section class="filter-section" data-filter-section><div class="publication-tools"><label class="search-label">Search publications<input type="search" placeholder="Title, author, venue, or year…" aria-label="Search publications"></label><a class="text-link" href="assets/publications.bib" download>Download bibliography ↓</a></div>'+filters(['All','Published','Accepted','Preprint'])+'<p class="results-count" aria-live="polite">17 publications</p>'+''.join(publication(i) for i in range(17))+'<p class="empty" hidden>No matching publications. Try another search or category.</p></section>'
(OUT/'publications.html').write_text(page('Publications','Publications',body))
about=intro('ABOUT / BACKGROUND','Researcher.<br>Educator. <em>Collaborator.</em>','I work at the intersection of machine learning research, hands-on development, and technical mentorship.')
about+='''<section class="about-grid"><div class="about-note"><img class="about-portrait" src="assets/anandaswarup-vadapalli.png" alt="Anandaswarup Vadapalli" width="800" height="800"><p>Ph.D. in Computer Science<br>and Engineering</p><span class="eyebrow">IIIT HYDERABAD · 2025</span></div><div class="prose"><h2>From speech to broader<br>questions about AI.</h2><p>My research background is in speech synthesis and language technologies, with work on phrase break prediction, learned word representations, neural text-to-speech, and multilingual synthesis.</p><p>My recent work extends these interests into LLM evaluation, reward-model distillation, multimodal prompting, and inference efficiency. Across these areas, I combine model development with controlled experiments and human evaluation.</p><p>Alongside research, I design and teach the Machine Learning track in the MSIT program at CIHL, IIIT Hyderabad Campus, and guide research teams as a part-time Technical Lead at ResearchSpark Hub.</p></div></section><section class="section"><div class="section-heading"><div><p class="eyebrow">RESEARCH & TEACHING</p><h2>Experience</h2></div></div><div class="timeline"><article><span>JAN 2026 — PRESENT</span><div><h3>Technical Lead (Consultant) · Part-time</h3><a href="https://www.researchsparkhub.com/board-of-advisors">ResearchSpark Hub ↗</a><p>Guide ML and GenAI research across reward modeling, image captioning, multimodal prompting, and audio. Advise teams on model selection, experimental controls, evaluation, and implementation quality.</p></div></article><article><span>AUG 2020 — PRESENT</span><div><h3>Assistant Professor · Machine Learning Track</h3><p class="institution">MSIT Program, CIHL · IIIT Hyderabad Campus</p><p>Design and deliver the ML curriculum; mentor students through model development and evaluation; supervise practicum and co-op projects with academic and industry partners.</p></div></article><article><span>AUG 2010 — MAR 2025</span><div><h3>Researcher · Language Technologies Research Center</h3><p class="institution">IIIT Hyderabad</p><p>Developed sequence models and word representations, built neural TTS pipelines, and evaluated systems through benchmarks and listening studies. Co-authored speech and language research and contributed to Blizzard Challenge systems.</p></div></article></div></section><section class="section education"><p class="eyebrow">FOUNDATIONS</p><h2>Education</h2><div class="education-grid"><article><span>2025</span><h3>Ph.D., Computer Science & Engineering</h3><p>IIIT Hyderabad</p><p class="small">Thesis: Prediction and Incorporation of Phrase Break Models in Text-to-Speech Systems<br><br>Advisor: Dr. Kishore Prahallad</p></article><article><span>2010</span><h3>M.S., Information Technology</h3><p>IIIT Hyderabad</p><p class="small">Specialization in Language Technologies</p></article><article><span>2005</span><h3>B.E., Electrical & Electronics Engineering</h3><p>Osmania University, Hyderabad</p></article></div></section><section class="contact-band"><div><p class="eyebrow">CONTACT</p><h2>Let’s exchange ideas.</h2><a class="email" href="mailto:'''+email+'">'+email+'''</a></div><div class="contact-social">'''+links()+'''</div></section>'''
(OUT/'about.html').write_text(page('About','About',about))
cv=intro('CURRICULUM VITAE','The full <em>picture.</em>','Research, publications, teaching, education, and technical experience in one document.')
cv+='''<section class="cv-panel"><div><p class="eyebrow">FULL ACADEMIC & PROFESSIONAL CV</p><h2>Anandaswarup<br>Vadapalli</h2><p>Machine learning researcher and technical lead.<br>Ph.D., Computer Science and Engineering, IIIT Hyderabad.</p><div class="actions"><a class="button primary" href="assets/anandaswarup-vadapalli-cv.pdf" download>Download CV ↓</a><a class="button secondary" href="assets/anandaswarup-vadapalli-cv.pdf">Open PDF ↗</a></div><p class="small">PDF · 4 pages · Updated October 2026</p></div><div class="cv-index"><span>01 <b>Research & professional experience</b></span><span>02 <b>Selected ML & GenAI projects</b></span><span>03 <b>Education & technical skills</b></span><span>04 <b>Complete publication list</b></span></div></section><section class="section"><p class="eyebrow">TECHNICAL PRACTICE</p><h2>From experiment to implementation.</h2><div class="education-grid"><article><h3>Models & methods</h3><p>Transformers, representation learning, sequence modeling, supervised fine-tuning, reward modeling, and prompt design.</p></article><article><h3>Evaluation & efficiency</h3><p>Controlled benchmarking, human evaluation, error analysis, distillation, quantization, latency, and carbon-impact measurement.</p></article><article><h3>Tools & collaboration</h3><p>Python, PyTorch, Hugging Face Transformers, Git, Bash, reproducible pipelines, technical mentorship, and scientific writing.</p></article></div></section>'''
(OUT/'cv.html').write_text(page('CV','Curriculum vitae',cv))
(OUT/'projects').mkdir(exist_ok=True)
for n,p in enumerate(projects):
    body='<a class="breadcrumb" href="../projects.html">← All projects</a>'+intro(p['category'].upper()+' / '+p['period'],p['title'],p['summary'])
    body+='<div class="project-detail"><aside class="project-sidebar"><p class="eyebrow">IN THIS PROJECT</p><a href="#question">The question</a><a href="#approach">The approach</a><a href="#findings">Findings & scope</a><a href="#papers">Related publications</a><div class="sidebar-note">'+str(len(p['papers']))+' related publication'+('s' if len(p['papers'])>1 else '')+'</div></aside><div class="prose"><section id="question"><p class="eyebrow">01 / MOTIVATION</p><h2>The question</h2><p>'+p['question']+'</p></section><section id="approach"><p class="eyebrow">02 / METHOD</p><h2>The approach</h2>'+''.join('<p>'+v+'</p>' for v in p['approach'])+'</section><section id="findings"><p class="eyebrow">03 / EVIDENCE</p><h2>Findings & scope</h2>'+''.join('<p>'+v+'</p>' for v in p['findings'])+'</section>'
    if p.get('resources'): body+='<div class="resource-links">'+''.join(f'<a class="text-link" href="{E(u)}">{t} ↗</a>' for t,u in p['resources'])+'</div>'
    body+='</div></div><section class="section" id="papers"><p class="eyebrow">READ THE WORK</p><h2>Related publications</h2>'+''.join(publication(i,'../') for i in p['papers'])+'</section>'
    nxt=projects[(n+1)%len(projects)]
    body+=f'<a class="next-project" href="{nxt["slug"]}.html"><span class="eyebrow">NEXT PROJECT</span><span>{nxt["title"]}</span><b>→</b></a>'
    (OUT/'projects'/f'{p["slug"]}.html').write_text(page('Projects',p['title'],body,1,p['summary']))
(OUT/'assets/citations').mkdir(exist_ok=True)
for i,key in enumerate(keys): (OUT/'assets/citations'/f'paper-{i+1}.bib').write_text(entries[key]['raw']+'\n')
# The bibliography download matches the CV publication list exactly (not uncited entries).
(OUT/'assets/publications.bib').write_text('\n\n'.join(entries[k]['raw'] for k in keys)+'\n')
(OUT/'404.html').write_text(page('', 'Page not found',intro('404 / PAGE NOT FOUND','A different <em>direction.</em>','This page could not be found. <a href="/index.html">Return to the homepage →</a>')))
(OUT/'.nojekyll').touch()
print(f'Built 5 main pages, {len(projects)} project pages, and {len(keys)} publications in {OUT}')
