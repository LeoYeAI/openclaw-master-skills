/**
 * Read unread customer messages from LINE OA chat.
 * Run via browser evaluate after opening a chat.
 *
 * Returns: { unreadMessages: [{ from, content, time, hasImage, imageSrc }], count }
 * Only includes customer messages (left-side white bubbles) after the unread divider.
 */
function() {
  // Find the unread divider by data-id attribute (most reliable method)
  const divider = document.querySelector('[data-id^="unread_"]');
  
  if (!divider) {
    return { unreadMessages: [], note: 'No unread divider found - all messages are read' };
  }
  
  // Get all chat bubbles after the divider
  const allChats = Array.from(document.querySelectorAll('.chat'));
  
  // Find the divider's position in DOM
  let chatsAfterDivider = [];
  let foundDivider = false;
  
  // Traverse DOM to find chats after the divider element
  allChats.forEach(chat => {
    // Check if we've passed the divider
    if (!foundDivider) {
      let el = chat.previousElementSibling;
      while (el) {
        if (el === divider || el.contains(divider)) {
          foundDivider = true;
          break;
        }
        el = el.previousElementSibling;
      }
    }
    
    // If we've found the divider, collect subsequent chats
    if (foundDivider) {
      chatsAfterDivider.push(chat);
    }
  });
  
  // Extract customer messages (white bubbles, no chat-reverse class)
  const unreadMessages = [];
  chatsAfterDivider.forEach(chat => {
    // Skip if it's from us (has chat-reverse class)
    if (chat.classList.contains('chat-reverse')) return;
    
    const content = chat.querySelector('.chat-content')?.innerText?.trim();
    const timeMatch = chat.innerText.match(/\d{2}:\d{2}/);
    const time = timeMatch ? timeMatch[0] : '';
    
    // Get sender name if available (usually in chat header)
    const nameEl = chat.querySelector('.chat-name, [class*="name"]');
    const from = nameEl?.textContent?.trim() || 'Customer';
    
    // Check for images
    const photoImg = chat.querySelector('img[alt="Photo"]');
    const hasImage = !!photoImg;
    let imageSrc = null;
    
    if (hasImage && photoImg) {
      imageSrc = photoImg.src;
    }
    
    if (content || hasImage) {
      unreadMessages.push({
        from,
        content: content ? content.split('\n')[0] : '', // Take first line only
        time,
        hasImage,
        imageSrc
      });
    }
  });
  
  return { unreadMessages, count: unreadMessages.length };
}
