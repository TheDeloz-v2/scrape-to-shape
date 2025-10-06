import asyncio
import csv
import os
import re
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from playwright.async_api import Page

async def scroll_reviews_until_done(page: Page, max_no_new: int = 12, max_iters: int = 800, pause_ms: int = 1800):
    """
    Scroll robusto: localiza contenedor scrollable, scrollTo end + wheel,
    reintentos con pequeños scrolls si no hay progreso.
    """
    await page.wait_for_selector('div[data-review-id][jsaction]', timeout=30000)

    # localizar contenedor scrollable que contiene reviews
    scrollable = await page.evaluate_handle("""
    () => {
        const item = document.querySelector('div[data-review-id][jsaction]');
        if (!item) return document.scrollingElement || document.documentElement;
        let el = item.parentElement;
        while (el && el !== document.body) {
            const style = window.getComputedStyle(el);
            const overflowY = style.overflowY;
            const canScroll = el.scrollHeight > el.clientHeight + 10;
            if ((overflowY === 'auto' || overflowY === 'scroll') && canScroll) return el;
            el = el.parentElement;
        }
        el = item;
        while (el && el !== document.body) {
            if (el.scrollHeight > el.clientHeight + 10) return el;
            el = el.parentElement;
        }
        return document.scrollingElement || document.documentElement;
    }
    """)

    seen = set()
    no_new = 0
    iters = 0
    prev_count = await page.evaluate("document.querySelectorAll('div[data-review-id][jsaction]').length")

    while no_new < max_no_new and iters < max_iters:
        iters += 1
        print(f"[scroll] iter={iters} prev_count={prev_count} no_new={no_new}")

        try:
            await scrollable.evaluate("el => { el.scrollTo({ top: el.scrollHeight, behavior: 'auto' }); el.dispatchEvent(new Event('scroll')); }")
            await scrollable.evaluate("el => el.dispatchEvent(new WheelEvent('wheel', {deltaY: 1200, bubbles: true, cancelable: true}));")
        except Exception:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        await page.wait_for_timeout(pause_ms)

        await page.evaluate("""
            () => document.querySelectorAll('button[aria-label^="Ver más"], button[aria-label*="more"], button[aria-label*="Más"]').forEach(b => { try { b.click(); } catch(e){} })
        """)

        try:
            await page.wait_for_function(
                "document.querySelectorAll('div[data-review-id][jsaction]').length > " + str(prev_count),
                timeout=max(2000, pause_ms + 800)
            )
            prev_count = await page.evaluate("document.querySelectorAll('div[data-review-id][jsaction]').length")
            no_new = 0
            ids = await page.evaluate('''() => Array.from(document.querySelectorAll('div[data-review-id][jsaction]')).map(e => e.getAttribute('data-review-id'))''')
            for i in ids:
                if i:
                    seen.add(i)
            print(f"[scroll] nuevos_total={len(seen)}")
            continue
        except Exception:
            recovered = False
            for _ in range(3):
                try:
                    await scrollable.evaluate("el => el.scrollBy(0, 400)")
                except Exception:
                    await page.evaluate("window.scrollBy(0, 400)")
                await page.wait_for_timeout(500)
                cur = await page.evaluate("document.querySelectorAll('div[data-review-id][jsaction]').length")
                if cur > prev_count:
                    prev_count = cur
                    no_new = 0
                    recovered = True
                    ids = await page.evaluate('''() => Array.from(document.querySelectorAll('div[data-review-id][jsaction]')).map(e => e.getAttribute('data-review-id'))''')
                    for i in ids:
                        if i:
                            seen.add(i)
                    print(f"[scroll] recovered new_total={len(seen)}")
                    break
            if recovered:
                continue
            no_new += 1

    if not seen:
        ids = await page.evaluate('''() => Array.from(document.querySelectorAll('div[data-review-id][jsaction]')).map(e => e.getAttribute('data-review-id'))''')
        for i in ids:
            if i:
                seen.add(i)

    return list(seen)

def normalize_text_one_line(s: str) -> str:
    if not s:
        return ""
    
    s = re.sub(r'[\r\n\u2028\u2029]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

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
        raw_text = t_el.get_text(separator=' ', strip=True)
    else:
        # fallback
        raw_text = soup.get_text(separator=' ', strip=True)

    text = normalize_text_one_line(raw_text)

    return {
        "review_id": rid,
        "user_url": user_url,
        "username": username,
        "stars": stars,
        "time": time_text,
        "text": text
    }

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    
    
async def try_open_reviews_tab(page: Page, timeout: int = 20000):
    """
    Intentos robustos para abrir el panel de opiniones.
    """
    selectors = [
        'div.Gpq6kf.NlVald >> text="Opiniones"',
        'button[aria-label*="Opiniones"]',
        'button[aria-label*="Reviews"]',
        'button[aria-label*="Reseñas"]',
        'a[href*="reviews"]',
        'div[role="tab"] >> text="Opiniones"',
    ]
    for sel in selectors:
        try:
            locator = page.locator(sel)
            await locator.first.wait_for(state="visible", timeout=2000)
            await locator.first.click()
            await page.wait_for_timeout(900)
            return True
        except Exception:
            continue
    # fallback: intentar abrir el panel simulando ENTER sobre el primer review
    try:
        await page.wait_for_selector('div[data-review-id][jsaction]', timeout=timeout)
        return True
    except Exception:
        return False
    
async def scrape_place(page: Page, url: str,  out_dir: str, place_id: Optional[str], save_per_place: bool = True, headless: bool = True) -> List[Dict]:
    """
    page: Playwright Page ya inicializada y con `await page.goto(url)` ejecutado.
    """
    ensure_dir(out_dir)
    # abrir panel de opiniones con varios intentos
    ok = await try_open_reviews_tab(page, timeout=25000)
    if not ok:
        print("No se pudo abrir el panel de opiniones para:", url)

    await page.wait_for_selector('div[data-review-id][jsaction]', timeout=30000)

    # scroll robusto
    ids = await scroll_reviews_until_done(page, max_no_new=10, max_iters=600, pause_ms=2000)

    # expandir "Ver más"
    await page.evaluate("""
        () => document.querySelectorAll('button[aria-label=\"Ver más\"]').forEach(b => { try { b.click(); } catch(e){} })
    """)
    await page.wait_for_timeout(1000)

    elems = await page.query_selector_all('div[data-review-id][jsaction]')
    rows = []
    for el in elems:
        try:
            html = await el.evaluate("el => el.outerHTML")
        except Exception:
            continue
        r = parse_review_html(html)
        if not r["review_id"]:
            continue
        r["place_id"] = place_id or ""
        r["place_url"] = url
        rows.append(r)

    # dedupe
    unique = {r["review_id"]: r for r in rows}.values()
    rows = list(unique)

    if save_per_place:
        pid = place_id or re.sub(r'[^0-9A-Za-z_-]', '_', url)[:60]
        per_path = os.path.join(out_dir, f"{pid}_reviews.csv")
        with open(per_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["place_id","place_url","review_id","user_url","username","stars","time","text"], quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(rows)

    return rows

def append_to_combined(rows: List[Dict], out_dir: str, combined_name: str):
    ensure_dir(out_dir)
    combined_path = os.path.join(out_dir, combined_name)
    write_header = not os.path.exists(combined_path)
    with open(combined_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["place_id","place_url","review_id","user_url","username","stars","time","text"], quoting=csv.QUOTE_MINIMAL)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
