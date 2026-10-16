import asyncio, re, os, json, glob
from html.parser import HTMLParser
from playwright.async_api import async_playwright
ROOT='/home/claude/src'; B='http://localhost:8765'
results=[]
def ok(name, cond, info=''):
    results.append((name, bool(cond), info)); print(('PASS' if cond else 'FAIL'), name, info)

# 1. static link check across all generated pages
class P(HTMLParser):
    def __init__(s): super().__init__(); s.links=[]; s.ids=set()
    def handle_starttag(s,t,a):
        a=dict(a)
        if 'id' in a: s.ids.add(a['id'])
        for k in ('href','src'):
            v=a.get(k)
            if t!='base' and v and not v.startswith(('http','//','mailto','#','data:')): s.links.append(v)
pages={}
for f in glob.glob(ROOT+'/**/index.html', recursive=True)+[ROOT+'/404.html']:
    p=P(); p.feed(open(f,encoding='utf-8').read()); pages[f]=p
bad=[]
for f,p in pages.items():
    for l in p.links:
        path,_,frag=l.partition('#'); path=path.split('?')[0]
        if f.endswith('404.html'): path='/'+path   # 404 resolves against <base>
        elif not path.startswith('/'): path=os.path.normpath(os.path.join(os.path.dirname(f)[len(ROOT):] or '/', path)) + ('/' if path.endswith('/') else '')
        fp=ROOT+path+('index.html' if path.endswith('/') else '')
        if not os.path.exists(fp): bad.append((f,l)); continue
        if frag:
            tgt=pages.get(fp)
            if tgt and frag not in tgt.ids: bad.append((f,l))
ok('internal links & anchors resolve', not bad, f'{len(pages)} pages; bad={bad[:5]}')

# hreflang / canonical sanity
html=open(ROOT+'/ja/technology/index.html',encoding='utf-8').read()
ok('ja page has 6 hreflang alternates + canonical', html.count('hreflang=')>=6 and 'rel="canonical" href="https://kabukplatform.com/ja/technology/"' in html)
ok('noindex while domain unverified', 'noindex' in html)
ok('ar page dir=rtl', 'dir="rtl"' in open(ROOT+'/ar/index.html',encoding='utf-8').read())

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1440,'height':900})
        pg=await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' and 'fonts' not in m.text and 'TUNNEL' not in m.text else None)
        # JS errors on every page/locale
        for loc in ['','ja/','ko/','zh-tw/','ar/']:
            for pth in ['','solutions/','technology/','why-platform/','about/','contact/','privacy/']:
                await pg.goto(f'{B}/{loc}{pth}?lang=en'); await pg.wait_for_timeout(50)
        ok('no JS errors across 35 pages', not errs, str(errs[:3]))

        # dropdown keyboard
        await pg.goto(B+'/?lang=en')
        await pg.focus('[aria-controls=menu-solutions]'); await pg.keyboard.press('Enter')
        ok('Solutions menu opens via keyboard', await pg.get_attribute('[aria-controls=menu-solutions]','aria-expanded')=='true')
        focused=await pg.evaluate('document.activeElement.closest("#menu-solutions")!==null')
        ok('focus moves into menu', focused)
        await pg.keyboard.press('Escape')
        ok('Escape closes menu & restores focus', await pg.get_attribute('[aria-controls=menu-solutions]','aria-expanded')=='false' and await pg.evaluate('document.activeElement.getAttribute("aria-controls")')=='menu-solutions')
        # skip link
        await pg.keyboard.press('Tab') if False else None
        await pg.goto(B+'/?lang=en'); await pg.keyboard.press('Tab')
        ok('skip link is first tab stop', await pg.evaluate('document.activeElement.className')=='skip-link')
        # config link applied
        ok('Exchange link from site-config', await pg.get_attribute('footer [data-config-link=exchange]','href')=='https://kabukexchange.com/')

        # language persistence
        await pg.click('[aria-controls=menu-lang]'); await pg.click('#menu-lang a[data-set-locale=ja]')
        await pg.wait_for_load_state(); ok('lang switch navigates to /ja/', pg.url.endswith('/ja/'))
        await pg.goto(B+'/technology/'); await pg.wait_for_timeout(200)
        ok('stored ja preference redirects English page', '/ja/technology/' in pg.url, pg.url)
        await pg.goto(B+'/technology/?lang=en'); ok('?lang=en bypasses redirect', '/ja/' not in pg.url)
        await pg.evaluate("localStorage.setItem('kbk-locale','en')")

        # contact form
        await pg.goto(B+'/contact/?type=hotel&interest=pricing&lang=en')
        ok('query preselects orgType/interest', await pg.input_value('#orgType')=='hotel' and await pg.input_value('#interest')=='pricing')
        await pg.click('#lead-form button[type=submit]')
        n=await pg.locator('.field.has-error').count()
        ok('empty submit shows inline errors + summary', n>=5 and await pg.is_visible('#form-summary'), f'{n} errors')
        ok('first invalid field focused', await pg.evaluate('document.activeElement.id')=='name')
        await pg.fill('#name','Test'); await pg.fill('#company','Acme'); await pg.fill('#email','bad')
        await pg.select_option('#region','japan'); await pg.fill('#message','Hello')
        await pg.check('#privacy'); await pg.click('#lead-form button[type=submit]')
        ok('invalid email flagged', 'valid business email' in (await pg.text_content('#email-error')))
        await pg.fill('#email','a@acme.co')
        # intercept mailto navigation

        await pg.locator('#lead-form button[type=submit]').scroll_into_view_if_needed()
        print('HIT', await pg.evaluate("(()=>{const b=document.querySelector('#lead-form button[type=submit]').getBoundingClientRect();const e=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return e&&(e.outerHTML.slice(0,90))})()"))
        pg.on('console', lambda m: print('LOG', m.text) if m.text.startswith('SUB') else None)
        await pg.evaluate("document.getElementById('lead-form').addEventListener('submit',()=>console.log('SUB fired'));window.addEventListener('beforeunload',()=>console.log('SUB unload'))")
        print('BTN', await pg.evaluate("(()=>{const b=document.querySelector('#lead-form button[type=submit]');return [b.disabled, b.form&&b.form.id, document.querySelectorAll('#lead-form').length, getComputedStyle(b).pointerEvents]})()"))
        await pg.click('#lead-form button[type=submit]'); await pg.wait_for_timeout(800); print('ERRS', errs, await pg.evaluate("[document.getElementById('form-status').innerHTML.slice(0,80), document.getElementById('form-summary').hidden, document.activeElement.id, [...new FormData(document.getElementById('lead-form')).entries()].map(e=>e.join('=')).join('&')]"))
        st=await pg.text_content('#form-status') or ''
        print('DEBUG url', pg.url, 'errs', await pg.locator('.has-error').count(), [await e.get_attribute('class') for e in await pg.locator('.has-error').all()])
        ok('mailto confirmation (not "submitted") shown', 'Your email application will open' in st and 'network@kabuk.com' in st, st[:80])
        ok('hotel type routed to hotels mailbox', 'network@kabuk.com' in st)

        # mobile menu
        m=await b.new_page(viewport={'width':375,'height':800})
        await m.goto(B+'/?lang=en'); await m.click('.nav-toggle')
        ok('mobile menu opens', await m.is_visible('#site-nav'))
        await m.click('[aria-controls=menu-technology]')
        ok('mobile accordion opens', await m.is_visible('#menu-technology a[href$="technology/#pricing"]'))
        await m.keyboard.press('Escape'); await m.keyboard.press('Escape')
        ok('Escape closes mobile panel', not await m.is_visible('#site-nav'))

        # reduced motion
        r=await b.new_page(reduced_motion='reduce'); await r.goto(B+'/?lang=en'); await r.wait_for_timeout(300)
        anim=await r.evaluate("getComputedStyle(document.querySelector('.arch-links span'),'::after').display")
        vis=await r.evaluate("[...document.querySelectorAll('[data-reveal]')].every(e=>getComputedStyle(e).opacity==='1')")
        lit=await r.evaluate("document.querySelectorAll('.is-lit').length")
        ok('reduced motion: pulses hidden, content visible, no node cycling', anim=='none' and vis and lit==0)
        # no-JS rendering
        nj=await b.new_context(java_script_enabled=False); q=await nj.new_page(); await q.goto(B+'/')
        ok('no-JS: content visible (no hidden reveals)', await q.evaluate("getComputedStyle(document.querySelector('[data-reveal]')).opacity")=='1')
        await b.close()
asyncio.run(main())
json.dump(results, open('/home/claude/qa/results.json','w'))
print(sum(r[1] for r in results),'/',len(results),'passed')
