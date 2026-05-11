const puppeteer = require('puppeteer');

async function readUrl(url) {
  let browser;
  try {
    browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Extract text content from the body
    const content = await page.evaluate(() => {
      // You can add more sophisticated content extraction here if needed
      return document.body.innerText;
    });

    return content;
  } catch (error) {
    console.error(`Error reading URL: ${error.message}`);
    return `Error: Could not render the page. ${error.message}`;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Basic command-line handler
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const url = args[1];

  if (command === 'read' && url) {
    const content = await readUrl(url);
    console.log(content);
  } else {
    console.log('Usage: node index.js read <url>');
  }
}

main();
