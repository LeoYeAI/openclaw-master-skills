#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
import json
from playwright.sync_api import sync_playwright

def extract_keyframes(url, output_file):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Get all @keyframes from stylesheets
        keyframes_data = page.evaluate("""() => {
            const sheets = document.styleSheets;
            const results = [];
            for (let sheet of sheets) {
                try {
                    const rules = sheet.cssRules || [];
                    for (let rule of rules) {
                        if (rule.type === CSSRule.KEYFRAMES_RULE) {
                            results.push({
                                name: rule.name,
                                cssText: rule.cssText
                            });
                        }
                    }
                } catch(e) {
                    // CORS restriction, skip
                }
            }
            return results;
        }""")
        
        # Also get computed animation/transition properties
        animations_info = page.evaluate("""() => {
            const style = document.documentElement.style;
            const animations = [];
            
            // Check for animation-related CSS custom properties
            for (let prop of style) {
                if (prop.includes('animation') || prop.includes('motion') || prop.includes('transition')) {
                    animations.push({
                        property: prop,
                        value: style.getPropertyValue(prop)
                    });
                }
            }
            
            return animations;
        }""")
        
        result = {
            "url": url,
            "keyframes": keyframes_data,
            "animationCssVars": animations_info
        }
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved @keyframes extraction to {output_file}")
        print(f"Found {len(keyframes_data)} @keyframes rules")
        
        for kf in keyframes_data[:5]:
            print(f"  - {kf['name']}: {kf['cssText'][:100]}...")
        
        browser.close()

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://factory.ai/"
    output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/keyframes.json"
    extract_keyframes(url, output)
