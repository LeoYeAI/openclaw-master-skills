/**
 * Click LINE Account login button
 * Returns: {clicked: true} or {error: string}
 */
function() {
  const btn = document.querySelector('button:has(i18n-message[key="login.button.loginWithLine"])');
  if (btn) {
    btn.click();
    return { clicked: true };
  }
  return { error: 'LINE Account button not found' };
}
