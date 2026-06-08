#!/bin/bash
# Brand Data Extraction Script using Scrapling
# Replaces Firecrawl - uses Python scrapling library

URL="${1:-https://example.com}"

if [ -z "$1" ]; then
    echo "Usage: $0 <URL>"
    echo "Example: $0 https://example.com"
    exit 1
fi

echo "Extracting brand data from: $URL"
echo "---"

# Run Python script to extract brand data
python3 -c "
import json
import sys
from scrapling.fetchers import StealthyFetcher
from urllib.parse import urljoin
import re

url = '$URL'

def extract_brand_data(url):
    try:
        page = StealthyFetcher.fetch(url, headless=True)
    except Exception as e:
        print(f'Error fetching: {e}', file=sys.stderr)
        return {'error': str(e)}
    
    html = page.text if hasattr(page, 'text') else ''
    
    def resolve(u):
        return urljoin(url, u) if u and not u.startswith('http') else u
    
    # Extract colors from CSS
    colors = list(set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', html)))[:5]
    
    # Extract social links
    social_links = {}
    for platform in ['twitter', 'facebook', 'instagram', 'linkedin', 'youtube', 'github']:
        link = page.css(f'a[href*=\"{platform}\"]::attr(href)').get()
        if link:
            social_links[platform] = link
    
    # Extract features
    features = []
    feature_cards = page.css('[class*=\"feature\"], .feature-card, .benefit-item')
    for card in feature_cards[:6]:
        feature_text = card.css('h3::text, h4::text, p::text').get()
        if feature_text:
            features.append(feature_text.strip())
    
    return {
        'brandName': (
            page.css('[property=\"og:site_name\"]::text').get() or
            page.css('h1::text').get() or
            page.css('title::text').get() or
            'Unknown'
        ),
        'tagline': (
            page.css('[property=\"og:description\"]::text').get() or
            page.css('.tagline::text').get() or
            page.css('[name=\"description\"]::attr(content)').get() or
            ''
        ),
        'headline': page.css('h1::text').get(),
        'description': (
            page.css('[property=\"og:description\"]::text').get() or
            page.css('[name=\"description\"]::attr(content)').get() or
            ''
        ),
        'features': features,
        'logoUrl': resolve(page.css('[rel=\"icon\"]::attr(href)').get()),
        'faviconUrl': resolve(page.css('[rel=\"icon\"]::attr(href)').get()),
        'primaryColors': colors,
        'ctaText': (
            page.css('a[href*=\"signup\"]::text').get() or
            page.css('a[href*=\"register\"]::text').get() or
            page.css('.cta::text').get() or
            page.css('[class*=\"button\"]::text').get() or
            ''
        ),
        'socialLinks': social_links,
        'ogImageUrl': resolve(page.css('[property=\"og:image\"]::attr(content)').get()),
        'screenshotUrl': f'https://image.thum.io/get/width/1200/crop/800/{url}'
    }

data = extract_brand_data(url)

# Export as shell variables
print(f'export brandName=\"{data.get(\"brandName\", \"\")}\"')
print(f'export tagline=\"{data.get(\"tagline\", \"\")}\"')
print(f'export headline=\"{data.get(\"headline\", \"\")}\"')
print(f'export description=\"{data.get(\"description\", \"\")}\"')
print(f'export logoUrl=\"{data.get(\"logoUrl\", \"\")}\"')
print(f'export faviconUrl=\"{data.get(\"faviconUrl\", \"\")}\"')
print(f'export primaryColors=\"{','.join(data.get('primaryColors', []))}\"')
print(f'export ctaText=\"{data.get(\"ctaText\", \"\")}\"')
print(f'export ogImageUrl=\"{data.get(\"ogImageUrl\", \"\")}\"')
print(f'export screenshotUrl=\"{data.get(\"screenshotUrl\", \"\")}\"')

# Also print full JSON for debugging
print('---JSON_START---')
print(json.dumps(data, indent=2))
"
