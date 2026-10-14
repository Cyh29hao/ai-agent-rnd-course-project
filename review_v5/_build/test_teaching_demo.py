from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1280,'height':920},device_scale_factor=1)
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto((ROOT/'outputs/蒸馏教学原型.html').as_uri())
    initial=page.evaluate('window.teachingState()')
    previous=initial['loss'];values=[]
    for _ in range(12):
        page.locator('#stepButton').click()
        s=page.evaluate('window.teachingState()');assert s['loss']<previous
        values.append(s);previous=s['loss']
    page.wait_for_timeout(500)
    page.screenshot(path=str(ROOT/'qa/interactive.png'),full_page=True)
    page.locator('#resetButton').click();assert page.evaluate('window.teachingState().steps')==0
    page.locator('#playButton').click()
    page.wait_for_function('window.teachingState().steps===12',timeout=10000)
    assert not errors,errors
    result={'initial':initial,'after_12_steps':values[-1],'loss_monotonically_decreased':True,'reset_pass':True,'play_pass':True,'browser_errors':errors,'boundary':'Single-parameter teaching model only; not LLM training or AAR reproduction.'}
    (ROOT/'qa/interactive_test.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True));browser.close()
