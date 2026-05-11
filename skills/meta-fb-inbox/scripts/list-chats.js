(function() {
  // Find chat list container by structural pattern:
  // - Parent contains multiple children with position: absolute
  // - Each child is a conversation item with timestamp and name div
  let chatContainer = null;
  const containers = document.querySelectorAll('div[style*="position: absolute"]');
  
  for (let container of containers) {
    const parent = container.parentElement;
    if (!parent) continue;
    
    const siblings = Array.from(parent.children);
    // Chat list usually has 5-30 items
    if (siblings.length >= 5 && siblings.length <= 30) {
      // Verify it's the chat list by checking for timestamp and name elements
      const hasTimestamp = !!parent.querySelector('abbr.timestamp');
      const hasNameDiv = !!parent.querySelector('div.x1vvvo52.x1fvot60.xxio538');
      
      if (hasTimestamp && hasNameDiv) {
        chatContainer = parent;
        break;
      }
    }
  }
  
  if (!chatContainer) {
    return { error: 'Chat container not found' };
  }
  
  // Extract chat items
  const items = Array.from(chatContainer.children);
  const chats = [];
  
  items.forEach(item => {
    try {
      const text = item.textContent || '';
      
      // Skip if too short or empty
      if (text.length < 10) return;
      
      // Find name element by class pattern
      const nameEl = item.querySelector('div.x1vvvo52.x1fvot60.xxio538');
      const name = nameEl ? nameEl.textContent.trim() : '';
      
      // Find time using timestamp element
      const timeEl = item.querySelector('abbr.timestamp');
      const time = timeEl ? timeEl.textContent.trim() : '';
      
      // Find last message preview
      // Look for divs that contain message content (usually short text with <=3 children)
      const allDivs = item.querySelectorAll('div');
      let lastMsg = '';
      for (let div of allDivs) {
        const divText = div.textContent.trim();
        // Message preview typically 10-300 chars, has few children
        if (divText.length > 10 && divText.length < 300 && div.children.length <= 3) {
          // Skip if it's just the name or time
          if (divText === name || divText === time) continue;
          
          // Clean up: remove name prefix if present
          let cleaned = divText;
          if (cleaned.startsWith(name)) {
            cleaned = cleaned.substring(name.length).trim();
          }
          
          // Take the first suitable message preview
          if (cleaned.length > 5) {
            lastMsg = cleaned.substring(0, 100);
            break;
          }
        }
      }
      
      // Check unread status by font weight
      const nameStyle = nameEl ? window.getComputedStyle(nameEl) : null;
      const unread = nameStyle && (nameStyle.fontWeight === 'bold' || parseInt(nameStyle.fontWeight) >= 600);
      
      if (name) {
        chats.push({
          name: name,
          time: time || '',
          lastMsg: lastMsg || '',
          unread: !!unread
        });
      }
    } catch (e) {
      // Skip items that fail to parse
    }
  });
  
  return chats;
})()
