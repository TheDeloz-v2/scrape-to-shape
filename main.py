import asyncio
import csv
import re
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URL = "https://www.google.com/maps/place/Sky+Zone+Majadas/@14.6243552,-90.5562381,16.21z/data=!4m6!3m5!1s0x8589a1b264da9645:0x6f7483afde72fae5!8m2!3d14.6239401!4d-90.5608469!16s%2Fg%2F11hczwcg4s?entry=ttu&g_ep=EgoyMDI1MDkyOS4wIKXMDSoASAFQAw%3D%3D"

async def scroll_reviews_until_done(page, max_no_new=6, max_iters=300):
    # Find a review element to determine the scrollable container
    await page.wait_for_selector('div[data-review-id][jsaction]', timeout=20000)
    scrollable = await page.evaluate_handle("""
    () => {
        const sample = document.querySelector('div[data-review-id][jsaction]');
        if (!sample) return document.scrollingElement || document.documentElement;
        let p = sample.parentElement;
        while (p && p !== document.body) {
            const s = window.getComputedStyle(p).overflowY;
            if (s === 'auto' || s === 'scroll') return p;
            p = p.parentElement;
        }
        return document.scrollingElement || document.documentElement;
    }
    """)
    seen = set()
    no_new = 0
    iters = 0

    while no_new < max_no_new and iters < max_iters:
        iters += 1
        
        # Scroll the container down
        await scrollable.evaluate("el => el.scrollBy(0, 2000)")
        
        # Allow content to load
        await page.wait_for_timeout(800)
        
        # Force click any "Ver más" visible to expand long reviews
        await page.evaluate("""
            () => document.querySelectorAll('button[aria-label=\"Ver más\"]').forEach(b => { try { b.click(); } catch(e){} })
        """)
        # Recolecta ids actuales
        ids = await page.evaluate('''() => Array.from(document.querySelectorAll('div[data-review-id][jsaction]'))
                                        .map(e => e.getAttribute('data-review-id'))''')
        new_ids = [i for i in ids if i and i not in seen]
        if new_ids:
            for i in new_ids:
                seen.add(i)
            no_new = 0
        else:
            no_new += 1
            
        # if len(seen) >= 2400: break
    return list(seen)

def parse_review_html(html):
    soup = BeautifulSoup(html, "lxml")
    # id
    rid = None
    root = soup.find(attrs={"data-review-id": True})
    if root:
        rid = root.get("data-review-id")

    # user url & username
    user_url = None
    username = None
    btn = soup.select_one('button[data-href*="/maps/contrib/"]')
    if btn:
        user_url = btn.get("data-href")
        d = btn.find('div')
        if d:
            username = d.get_text(strip=True)

    # stars
    stars = None
    star_el = soup.select_one('[aria-label*="estrella"], [aria-label*="estrellas"]')
    if star_el:
        aria = star_el.get("aria-label", "")
        m = re.search(r'([1-5])', aria)
        if m:
            stars = int(m.group(1))

    # time
    time_text = None
    # span with "hace" or similar words
    txt_candidates = soup.find_all(string=re.compile(r'\bhace\b|\bdía\b|\bdías\b|\bmes\b|\baño\b|\baños\b|\bha\b', re.I))
    if txt_candidates:
        time_text = txt_candidates[0].strip()
    else:
        # fallback
        spans = soup.find_all('span')
        for s in spans:
            t = s.get_text(strip=True)
            if len(t) < 40 and re.search(r'\d', t):
                time_text = t
                break

    # review text
    text = ""
    # google use <div lang="..."> for the main text
    t_el = soup.select_one('div[lang]')
    if t_el:
        text = t_el.get_text(separator=' ', strip=True)
    else:
        # fallback
        text = soup.get_text(separator=' ', strip=True)

    return {
        "review_id": rid,
        "user_url": user_url,
        "username": username,
        "stars": stars,
        "time": time_text,
        "text": text
    }

async def run():
    reviews = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(URL)
        
        # click on "Opiniones" tab
        try:
            reviews_tab = page.locator('div.Gpq6kf.NlVald >> text="Opiniones"')
            await reviews_tab.wait_for(state="visible", timeout=10000)
            await reviews_tab.click()
        except Exception:
            # fallback
            await page.wait_for_selector('div[data-review-id][jsaction]', timeout=20000)

        await page.wait_for_selector('div[data-review-id][jsaction]', timeout=20000)
        
        # scroll until done
        ids = await scroll_reviews_until_done(page, max_no_new=6, max_iters=500)

        # expand all "Ver más"
        await page.evaluate("""
            () => document.querySelectorAll('button[aria-label=\"Ver más\"]').forEach(b => { try { b.click(); } catch(e){} })
        """)
        await page.wait_for_timeout(500)

        # catch all review elements
        elems = await page.query_selector_all('div[data-review-id][jsaction]')
        outer_htmls = []
        for el in elems:
            try:
                html = await el.evaluate("el => el.outerHTML")
                outer_htmls.append(html)
            except Exception:
                continue

        for html in outer_htmls:
            r = parse_review_html(html)
            if not r["review_id"]:
                continue
            reviews[r["review_id"]] = r

        await browser.close()

    # export CSV
    rows = list(reviews.values())
    with open("../data/raw/google_maps_reviews_bs4.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["review_id","user_url","username","stars","time","text"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} reviews to google_maps_reviews_bs4.csv")

if __name__ == "__main__":
    asyncio.run(run())
