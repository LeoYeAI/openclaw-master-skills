#!/usr/bin/env python3
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translate_images import translate_image

urls = [
    'https://cbu01.alicdn.com/img/ibank/O1CN0109gRVx1zPrBVAmA6p_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01K6soO11zPrSIDwxDA_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01FPl3Ww1zPrBZrq6Qt_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01Fo2kfn1zPrSDKGyfp_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01mn8R421zPrBZrpMgp_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN0128EvSg1zPrBTQA6h4_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01rSlKS41zPrBOldjcv_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01NtcwD91zPrBXrFHQA_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01YDv2CS1zPrBR0gXFI_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01FXDAa91zPrBTIuEYo_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN013hqQWq1zPrGIuflsk_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01UNFELq1zPrBbtYLSc_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01utZt1W1zPrRZQcrQH_!!1741586707-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01XT6mBF1EPbJJqGnya_!!2208893230344-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01yLeygD1EPbJOlW87Z_!!2208893230344-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN0127eQmd1EPbJQWO5e4_!!2208893230344-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01pUTHHG1EPbJREDKSL_!!2208893230344-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01tCd6TV1EPbJJqLu8a_!!2208893230344-0-cib.jpg',
    'https://cbu01.alicdn.com/img/ibank/O1CN01wEiMEP1EPbJPqhUSP_!!2208893230344-0-cib.jpg',
]

results = {}
for i, url in enumerate(urls):
    start = time.time()
    try:
        r = translate_image(url)
        elapsed = time.time() - start
        translated = url  # fallback
        if 'result' in r and 'result' in r['result']:
            t = r['result']['result'].get('translatedImageUrl', '')
            if t:
                translated = t
        results[url] = translated
        print(f'[{i+1}/{len(urls)}] {elapsed:.1f}s OK', flush=True)
    except Exception as e:
        results[url] = url
        print(f'[{i+1}/{len(urls)}] ERROR: {e}', flush=True)

# Save to file
with open('translated_urls.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('DONE - saved to translated_urls.json', flush=True)
