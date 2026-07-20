export function coerceBool(val, fallback) {
  if (val === true || val === 'true') return true;
  if (val === false || val === 'false') return false;
  return fallback;
}
