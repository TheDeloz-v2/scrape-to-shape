import asyncio
from typing import List, Tuple
from playwright.async_api import async_playwright
from scrapper import scrape_place, append_to_combined

LINKS: List[Tuple[str, str]] = [
    ("club_majadas", "https://www.google.com/maps/place/Club+Majadas/@14.6349945,-90.6766972,12z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a1ac4a4e8949:0xc08daa26fa8794a6!8m2!3d14.6199411!4d-90.560102!15sCgRjbHViWgYiBGNsdWKSAQtzcG9ydHNfY2x1YpoBJENoZERTVWhOTUc5blMwVkpRMEZuU1VSSWVWOWxYM2hSUlJBQqoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAECk!16s%2Fg%2F11rs0x5cr?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    ("club_espaniol", "https://www.google.com/maps/place/Club+Espa%C3%B1ol+-+Guatemala/@14.6349945,-90.6511765,13z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a0387ea8f411:0x7295032c17ead494!8m2!3d14.6349945!4d-90.5749588!15sCgRjbHViWgYiBGNsdWKSAQtzb2NpYWxfY2x1YpoBI0NoWkRTVWhOTUc5blMwVkpRMEZuU1VSMmRXVXlVbUZuRUFFqgE2EAEqCCIEY2x1YigOMh4QASIaGZv4OPPObOnajxBf3lYlnCMNPox3SI-tcIoyCBACIgRjbHVi4AEA-gEECAAQNQ!16s%2Fg%2F1hf9wpwqp?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    ("club_montania", "https://www.google.com/maps/place/Club+Campestre+La+monta%C3%B1a/@14.6349945,-90.6511765,13z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x85899fe4af26f5ef:0xaa5237c68a36bc1a!8m2!3d14.671049!4d-90.59737!15sCgRjbHViWgYiBGNsdWKSAQxjb3VudHJ5X2NsdWKaASNDaFpEU1VoTk1HOW5TMFZKUTBGblNVTXlOblpEUzA5bkVBRaoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAECk!16s%2Fg%2F1tp08fqj?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    ("club_americano", "https://www.google.com/maps/place/Club+Americano/@14.6063905,-90.5754284,13z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a3b26f62b751:0x79b676724cd180fb!8m2!3d14.6063905!4d-90.4992107!15sCgRjbHViWgYiBGNsdWKSAQtzcG9ydHNfY2x1YpoBJENoZERTVWhOTUc5blMwVkpRMEZuU1VSMWJtVkVWR2gzUlJBQqoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAECI!16s%2Fg%2F1tjmd_0q?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D")
]
DEFAULT_OUT_DIR = "../../data/raw"
COMBINED_FILENAME = "google_maps_all_reviews.csv"

async def process_all(pairs, out_dir=DEFAULT_OUT_DIR, com_file=COMBINED_FILENAME, headless=False, sequential=True):
    total = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False para depurar
        for pid, url in pairs:
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(url, wait_until="domcontentloaded")
            
            try:
                await page.locator('button[aria-label*="Aceptar"], button[aria-label*="Acepto"], button:has-text("Aceptar")').first.click(timeout=2000)
            except Exception:
                pass
            
            print(f"\nScraping place_id='{pid}' url='{url}'")
            rows = await scrape_place(page=page, url=url, out_dir=out_dir, place_id=pid, save_per_place=True, headless=headless)
            append_to_combined(rows, out_dir=out_dir, combined_name=com_file)
            print(f" -> {len(rows)} reviews saved for {pid or url}")
            total += len(rows)
            await context.close()
        await browser.close()
    print(f"Done. Total reviews scraped: {total}")

if __name__ == "__main__":
    asyncio.run(process_all(LINKS, out_dir=DEFAULT_OUT_DIR, headless=False, sequential=True))
