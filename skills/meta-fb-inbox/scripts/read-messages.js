(function() {
  // Find all message bubbles in the conversation
  // Messages are identified by specific background colors:
  // - Blue (rgb(10, 124, 255)) = our replies
  // - Gray (rgb(239, 239, 239) or similar) = customer messages
  
  const allDivs = document.querySelectorAll('div');
  const messages = [];
  const processedImages = new Set();
  
  // First pass: collect text messages
  for (let div of allDivs) {
    const text = div.textContent.trim();
    
    // Skip if text is too short or too long
    if (text.length < 2 || text.length > 1000) continue;
    
    // Check background color
    const bg = window.getComputedStyle(div).backgroundColor;
    const match = bg.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (!match) continue;
    
    const [_, r, g, b] = match.map(Number);
    
    let isCustomer = null;
    
    // Blue background = our message
    if (b > 200 && r < 50 && g > 100 && g < 150) {
      isCustomer = false;
    }
    // Gray/white background = customer message  
    else if (r > 200 && g > 200 && b > 200) {
      isCustomer = true;
    }
    
    // Skip if not a message bubble
    if (isCustomer === null) continue;
    
    // Check if this div has the common message class pattern
    const className = div.className || '';
    if (!className.includes('x1y1aw1k')) continue;
    
    // Avoid duplicate messages (parent containers may also match)
    // Only take messages with relatively few children
    if (div.children.length > 5) continue;
    
    // Check for duplicates
    const isDuplicate = messages.some(m => m.text === text);
    if (isDuplicate) continue;
    
    messages.push({
      text: text,
      isCustomer: isCustomer,
      hasImage: false,
      imageUrl: null,
      bg: bg
    });
  }
  
  // Second pass: find standalone images (photos without text bubbles)
  const images = document.querySelectorAll('img[src*="fbcdn.net"]');
  for (let img of images) {
    // Only process large images (actual message photos, not icons/avatars)
    if (img.width < 100 || img.height < 100) continue;
    if (processedImages.has(img.src)) continue;
    
    // Filter out link preview images (external.*.fna.fbcdn.net)
    // Only keep actual uploaded photos (scontent-*.xx.fbcdn.net)
    if (img.src.includes('external.') && img.src.includes('.fna.fbcdn.net')) {
      continue;
    }
    
    // Images in Facebook Messenger are typically customer messages (left side)
    // unless they're in a blue bubble container
    processedImages.add(img.src);
    
    messages.push({
      text: '[Image]',
      isCustomer: true,  // Assume customer sent it
      hasImage: true,
      imageUrl: img.src,
      bg: 'image'
    });
  }
  
  // Reverse to show chronological order (oldest first)
  return messages.reverse();
})()
