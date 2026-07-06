/**
 * List all chat items from LINE OA chat list with unread status.
 * Run via browser evaluate on chat.line.biz (chat list page).
 *
 * Returns: [{ name, time, lastMsg, unread }]
 * - name: customer display name
 * - time: last message time (e.g., "11:56", "Monday", "2/10")
 * - lastMsg: preview of last message (up to 100 chars)
 * - unread: true if green dot (span.badge.badge-pin) is visible
 *
 * ONE-LINER version (copy this for browser evaluate fn parameter):
 * (function(){var r=document.querySelectorAll('.list-group-item-chat');return Array.from(r).map(function(e){var h=e.querySelector('h6');var p=e.querySelector('.text-muted.small');var pt=p?p.textContent.trim():'';var ms=e.querySelectorAll('.text-muted');var t='';for(var i=0;i<ms.length;i++){var v=ms[i].textContent.trim();if(v&&v.length<20&&v!==pt)t=v;}var d=e.querySelector('span.badge.badge-pin');var u=!!d&&getComputedStyle(d).display!=='none';return{name:h?h.textContent.trim():'',time:t,lastMsg:pt.substring(0,100),unread:u};}).filter(function(i){return i.name;});})()
 */
function() {
  const items = document.querySelectorAll('.list-group-item-chat');
  return Array.from(items).map(el => {
    const h6 = el.querySelector('h6');
    const preview = el.querySelector('.text-muted.small');
    const prevText = preview?.textContent?.trim() || '';

    // Time: short .text-muted that isn't the preview
    const allMuted = el.querySelectorAll('.text-muted');
    let time = '';
    for (const m of allMuted) {
      const t = m.textContent.trim();
      if (t && t.length < 20 && t !== prevText) time = t;
    }

    // Unread: green dot badge
    const dot = el.querySelector('span.badge.badge-pin');
    const unread = !!dot && getComputedStyle(dot).display !== 'none';

    return {
      name: h6?.textContent?.trim() || '',
      time,
      lastMsg: prevText.substring(0, 100),
      unread
    };
  }).filter(i => i.name);
}
