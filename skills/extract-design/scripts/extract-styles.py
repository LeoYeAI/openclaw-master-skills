#!/usr/bin/env python3
"""
extract-styles.py — Extract computed CSS design tokens from a live webpage.

Usage:
    python3 extract-styles.py <url> [--dark] [--out <path>]

Options:
    --dark      Switch to dark mode before extracting (clicks dark theme toggle if present)
    --out       Output JSON file path (default: stdout)

Requirements:
    pip install playwright
    playwright install chromium

Output: JSON with keys:
    meta, theme, colors, fonts, css_vars, background_images, transitions, cards, typography
"""

import sys
import json
import argparse
from playwright.sync_api import sync_playwright


JS_EXTRACT = """
() => {
  // 1. CSS custom properties from all stylesheets
  const cssVars = {};
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.style) {
          for (const prop of rule.style) {
            if (prop.startsWith('--')) {
              cssVars[prop] = rule.style.getPropertyValue(prop).trim();
            }
          }
        }
      }
    } catch (e) {}
  }

  // 2. Body computed styles
  const bodyStyle = getComputedStyle(document.body);
  const htmlStyle = getComputedStyle(document.documentElement);

  // 3. All elements with background-image (patterns, gradients)
  const bgImages = [...document.querySelectorAll('*')]
    .filter(el => getComputedStyle(el).backgroundImage !== 'none')
    .slice(0, 30)
    .map(el => {
      const s = getComputedStyle(el);
      return {
        tag: el.tagName,
        cls: el.className?.toString().substring(0, 80) || '',
        backgroundImage: s.backgroundImage.substring(0, 300),
        backgroundSize: s.backgroundSize,
        backgroundRepeat: s.backgroundRepeat,
        backgroundColor: s.backgroundColor,
      };
    });

  // 4. Button computed styles
  const btn = document.querySelector('button');
  const btnStyle = btn ? getComputedStyle(btn) : null;

  // 5. Card/surface elements
  const card = document.querySelector('[class*="card"], [class*="Card"]');
  const cardStyle = card ? getComputedStyle(card) : null;

  // 6. Accent/brand colors from links and accent-classed elements
  const accentEls = [...document.querySelectorAll('a, [class*="accent"], [class*="brand"]')]
    .slice(0, 10)
    .map(el => ({
      tag: el.tagName,
      cls: el.className?.toString().substring(0, 60) || '',
      color: getComputedStyle(el).color,
      bg: getComputedStyle(el).backgroundColor,
    }));

  // 7. Typography samples
  const h1 = document.querySelector('h1');
  const h2 = document.querySelector('h2');
  const h1Style = h1 ? getComputedStyle(h1) : null;
  const h2Style = h2 ? getComputedStyle(h2) : null;

  return {
    meta: {
      url: location.href,
      title: document.title,
      dataTheme: document.documentElement.getAttribute('data-theme'),
      htmlClass: document.documentElement.className.substring(0, 200),
      hasDarkClass: document.documentElement.classList.contains('dark'),
      colorScheme: htmlStyle.colorScheme,
    },
    colors: {
      htmlBg: htmlStyle.backgroundColor,
      bodyBg: bodyStyle.backgroundColor,
      bodyColor: bodyStyle.color,
      cardBg: cardStyle ? cardStyle.backgroundColor : null,
      cardBorder: cardStyle ? cardStyle.borderColor : null,
      cardRadius: cardStyle ? cardStyle.borderRadius : null,
      cardShadow: cardStyle ? cardStyle.boxShadow : null,
    },
    fonts: {
      bodyFamily: bodyStyle.fontFamily,
      bodySize: bodyStyle.fontSize,
      bodyWeight: bodyStyle.fontWeight,
      h1Family: h1Style ? h1Style.fontFamily : null,
      h1Size: h1Style ? h1Style.fontSize : null,
      h1Weight: h1Style ? h1Style.fontWeight : null,
      h1LetterSpacing: h1Style ? h1Style.letterSpacing : null,
      h1LineHeight: h1Style ? h1Style.lineHeight : null,
      h2Size: h2Style ? h2Style.fontSize : null,
    },
    button: btnStyle ? {
      bg: btnStyle.backgroundColor,
      color: btnStyle.color,
      border: btnStyle.border,
      radius: btnStyle.borderRadius,
      padding: btnStyle.padding,
      height: btnStyle.height,
      fontSize: btnStyle.fontSize,
      fontFamily: btnStyle.fontFamily,
      transition: btnStyle.transition,
    } : null,
    cssVars,
    backgroundImages: bgImages,
    accentColors: accentEls,
    typography: {
      h1: h1Style ? {
        size: h1Style.fontSize,
        weight: h1Style.fontWeight,
        letterSpacing: h1Style.letterSpacing,
        lineHeight: h1Style.lineHeight,
        color: h1Style.color,
      } : null,
    },
  };
}
"""

JS_FIND_DARK_TOGGLE = """
() => {
  const candidates = [...document.querySelectorAll('button, [role="button"]')].filter(el => {
    const label = (el.getAttribute('aria-label') || el.textContent || '').toLowerCase();
    return label.includes('dark') || label.includes('theme') || label.includes('mode');
  });
  return candidates.map(el => ({
    tag: el.tagName,
    ariaLabel: el.getAttribute('aria-label'),
    text: el.textContent.trim().substring(0, 40),
  }));
}
"""


def extract(url: str, switch_dark: bool = False, out_path: str = None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        print(f"[extract-styles] Navigating to {url}", file=sys.stderr)
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Extract light mode first
        light_data = page.evaluate(JS_EXTRACT)
        light_data["_mode"] = "light"

        dark_data = None
        if switch_dark:
            # Try to find and click dark mode toggle
            toggles = page.evaluate(JS_FIND_DARK_TOGGLE)
            clicked = False
            for t in toggles:
                label = (t.get("ariaLabel") or "").lower()
                if "dark" in label:
                    try:
                        page.get_by_role("button", name=t["ariaLabel"]).click()
                        page.wait_for_timeout(500)
                        clicked = True
                        print(f"[extract-styles] Switched to dark via: {t['ariaLabel']}", file=sys.stderr)
                        break
                    except Exception:
                        pass

            if not clicked:
                # Fallback: force dark via prefers-color-scheme emulation
                page.emulate_media(color_scheme="dark")
                page.wait_for_timeout(300)
                print("[extract-styles] Forced dark via prefers-color-scheme emulation", file=sys.stderr)

            dark_data = page.evaluate(JS_EXTRACT)
            dark_data["_mode"] = "dark"

        browser.close()

        result = {
            "light": light_data,
            "dark": dark_data,
        }

        output = json.dumps(result, indent=2, ensure_ascii=False)

        if out_path:
            with open(out_path, "w") as f:
                f.write(output)
            print(f"[extract-styles] Saved to {out_path}", file=sys.stderr)
        else:
            print(output)


def main():
    parser = argparse.ArgumentParser(description="Extract computed CSS design tokens from a webpage")
    parser.add_argument("url", help="URL to extract from")
    parser.add_argument("--dark", action="store_true", help="Also extract dark mode")
    parser.add_argument("--out", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    extract(args.url, switch_dark=args.dark, out_path=args.out)


if __name__ == "__main__":
    main()
