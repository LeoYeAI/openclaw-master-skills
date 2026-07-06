/**
 * Click Login button on LINE OAuth page
 * Handles both email/password page and quick-login page (with user avatar)
 * Returns: {clicked: true} or {error: string}
 */
function() {
  // Try multiple selectors to handle different page layouts:
  // 1. Email/password page: .mdFormGroup01Btn button.MdBtn01[type="submit"]
  // 2. Quick-login page: button with text "登入"
  // 3. Fallback: any submit button with MdBtn01 class
  
  const selectors = [
    '.mdFormGroup01Btn button.MdBtn01[type="submit"]',
    'button.MdBtn01[type="submit"]',
    'button[type="submit"]'
  ];
  
  for (const selector of selectors) {
    const btn = document.querySelector(selector);
    if (btn && btn.textContent.includes('登入')) {
      btn.click();
      return { clicked: true, selector };
    }
  }
  
  return { error: 'Login button not found', tried: selectors };
}
