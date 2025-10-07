import asyncio
from typing import List, Tuple
from playwright.async_api import async_playwright
from scrapper import scrape_place, append_to_combined, try_open_reviews_tab

LINKS: List[Tuple[str, str]] = [
    #("club_majadas", "https://www.google.com/maps/place/Club+Majadas/@14.6349945,-90.6766972,12z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a1ac4a4e8949:0xc08daa26fa8794a6!8m2!3d14.6199411!4d-90.560102!15sCgRjbHViWgYiBGNsdWKSAQtzcG9ydHNfY2x1YpoBJENoZERTVWhOTUc5blMwVkpRMEZuU1VSSWVWOWxYM2hSUlJBQqoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAECk!16s%2Fg%2F11rs0x5cr?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    #("club_espaniol", "https://www.google.com/maps/place/Club+Espa%C3%B1ol+-+Guatemala/@14.6349945,-90.6511765,13z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a0387ea8f411:0x7295032c17ead494!8m2!3d14.6349945!4d-90.5749588!15sCgRjbHViWgYiBGNsdWKSAQtzb2NpYWxfY2x1YpoBI0NoWkRTVWhOTUc5blMwVkpRMEZuU1VSMmRXVXlVbUZuRUFFqgE2EAEqCCIEY2x1YigOMh4QASIaGZv4OPPObOnajxBf3lYlnCMNPox3SI-tcIoyCBACIgRjbHVi4AEA-gEECAAQNQ!16s%2Fg%2F1hf9wpwqp?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    #("club_montania", "https://www.google.com/maps/place/Club+Campestre+La+monta%C3%B1a/@14.6349945,-90.6511765,13z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x85899fe4af26f5ef:0xaa5237c68a36bc1a!8m2!3d14.671049!4d-90.59737!15sCgRjbHViWgYiBGNsdWKSAQxjb3VudHJ5X2NsdWKaASNDaFpEU1VoTk1HOW5TMFZKUTBGblNVTXlOblpEUzA5bkVBRaoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAECk!16s%2Fg%2F1tp08fqj?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    #("club_americano", "https://www.google.com/maps/place/Club+Americano/@14.6063905,-90.5754284,13z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a3b26f62b751:0x79b676724cd180fb!8m2!3d14.6063905!4d-90.4992107!15sCgRjbHViWgYiBGNsdWKSAQtzcG9ydHNfY2x1YpoBJENoZERTVWhOTUc5blMwVkpRMEZuU1VSMWJtVkVWR2gzUlJBQqoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAECI!16s%2Fg%2F1tjmd_0q?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    #("club_oficiales", "https://www.google.com/maps/place/Club+de+Oficiales/@14.5837042,-90.5500062,15z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a15c17a677f9:0xbab56faa86fbcd4f!8m2!3d14.5837042!4d-90.5309518!15sCgRjbHViWgYiBGNsdWKSAQpuaWdodF9jbHVimgEjQ2haRFNVaE5NRzluUzBWSlEwRm5TVVIyZURaaU0wRlJFQUWqATYQASoIIgRjbHViKA4yHhABIhoZm_g4885s6dqPEF_eViWcIw0-jHdIj61wijIIEAIiBGNsdWLgAQD6AQQIABAk!16s%2Fg%2F1hf49m0vg?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    ("club_guatebanco", "https://www.google.com/maps/place/Club+Guatebanco/@14.5709783,-90.5523072,16.46z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a135e1ddd223:0x861f7288db23359f!8m2!3d14.5703574!4d-90.5455778!15sCgRjbHViWgYiBGNsdWKSAQxjb3VudHJ5X2NsdWKaASRDaGREU1VoTk1HOW5TMFZKUTBGblNVTmFhVjlMZG5CblJSQUKqATYQASoIIgRjbHViKA4yHhABIhoZm_g4885s6dqPEF_eViWcIw0-jHdIj61wijIIEAIiBGNsdWLgAQD6AQQITRAs!16s%2Fg%2F1td76xf6?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D"),
    ("club_guatemala", "https://www.google.com/maps/place/Club+Guatemala/@14.6303683,-90.5766538,12.87z/data=!4m10!1m2!2m1!1sclub!3m6!1s0x8589a2163966e641:0x38ca3e9e7e81fac2!8m2!3d14.6359837!4d-90.5131767!15sCgRjbHViWgYiBGNsdWKSARFicnVuY2hfcmVzdGF1cmFudJoBJENoZERTVWhOTUc5blMwVk5XSEJ2VUhwMFp6Z3RTWGhuUlJBQqoBNhABKggiBGNsdWIoDjIeEAEiGhmb-Djzzmzp2o8QX95WJZwjDT6Md0iPrXCKMggQAiIEY2x1YuABAPoBBAgAEB4!16s%2Fg%2F11c57j9vqk?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D")    
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

            # Ensure the reviews tab/panel is opened before scraping
            opened = await try_open_reviews_tab(page, timeout=25000)
            if not opened:
                print(f"Warning: couldn't open the 'Opiniones/Reseñas' tab for {url}; continuing but results may be incomplete")

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
