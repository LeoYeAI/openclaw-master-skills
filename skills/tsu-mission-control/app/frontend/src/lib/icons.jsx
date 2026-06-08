/**
 * Icon library for Mission Control
 *
 * Consistent 20x20 stroke-based icons. Each icon is a function
 * that returns JSX. Uses currentColor so they inherit text color.
 *
 * Usage:
 *   import { Icon } from "../lib/icons";
 *   <Icon name="dashboard" />
 *   <Icon name="inbox" size={16} className="text-amber-400" />
 */
import React from "react";

const paths = {
  // ── Navigation ────────────────────────────────────
  dashboard: (
    <>
      <rect x="3" y="3" width="6" height="6" rx="1" />
      <rect x="11" y="3" width="6" height="4" rx="1" />
      <rect x="11" y="9" width="6" height="8" rx="1" />
      <rect x="3" y="11" width="6" height="6" rx="1" />
    </>
  ),
  inbox: (
    <>
      <path d="M3 7l4 4h6l4-4" />
      <path d="M3 7v8a2 2 0 002 2h10a2 2 0 002-2V7" />
      <path d="M7 3h6l4 4H3l4-4z" />
    </>
  ),
  pipeline: (
    <>
      <rect x="3" y="3" width="4" height="14" rx="1" />
      <rect x="8" y="6" width="4" height="11" rx="1" />
      <rect x="13" y="9" width="4" height="8" rx="1" />
    </>
  ),
  folder: (
    <path d="M3 6a2 2 0 012-2h3.93a2 2 0 011.664.89l.812 1.22A2 2 0 0013.07 7H15a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2V6z" />
  ),
  library: (
    <>
      <path d="M4 19V5a2 2 0 012-2h8a2 2 0 012 2v14" />
      <path d="M4 19h12" />
      <path d="M8 3v4" />
      <path d="M12 7H8" />
    </>
  ),
  agents: (
    <>
      <circle cx="10" cy="7" r="3" />
      <path d="M3 19c0-3.314 3.134-6 7-6s7 2.686 7 6" />
    </>
  ),
  costs: (
    <>
      <circle cx="10" cy="10" r="7" />
      <path d="M10 6v8" />
      <path d="M8 8.5c0-.828.895-1.5 2-1.5s2 .672 2 1.5S11.105 10 10 10s-2 .672-2 1.5.895 1.5 2 1.5 2-.672 2-1.5" />
    </>
  ),
  activity: (
    <>
      <polyline points="4 14 8 10 12 13 16 6" />
      <path d="M3 3v14h14" />
    </>
  ),

  // ── Actions ───────────────────────────────────────
  plus: <path d="M10 4v12M4 10h12" />,
  refresh: (
    <>
      <path d="M4 10a6 6 0 0111.472-2.5" />
      <path d="M16 10a6 6 0 01-11.472 2.5" />
      <polyline points="15 3 16 7.5 11.5 8" />
      <polyline points="5 17 4 12.5 8.5 12" />
    </>
  ),
  check: <polyline points="5 10 8.5 13.5 15 6.5" />,
  x: <><path d="M6 6l8 8" /><path d="M14 6l-8 8" /></>,
  search: (
    <>
      <circle cx="9" cy="9" r="5" />
      <path d="M13 13l4 4" />
    </>
  ),
  filter: <path d="M3 4h14l-5 6v5l-4 2V10L3 4z" />,
  chevronRight: <polyline points="7 5 13 10 7 15" />,
  chevronDown: <polyline points="5 7 10 13 15 7" />,
  arrowUp: <><path d="M10 16V4" /><polyline points="5 9 10 4 15 9" /></>,
  arrowDown: <><path d="M10 4v12" /><polyline points="5 11 10 16 15 11" /></>,
  externalLink: (
    <>
      <path d="M11 3h6v6" />
      <path d="M17 3L8 12" />
      <path d="M15 8v7a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h7" />
    </>
  ),

  // ── Status / State ────────────────────────────────
  alertTriangle: (
    <>
      <path d="M10 2L1 18h18L10 2z" />
      <path d="M10 8v4" />
      <circle cx="10" cy="14.5" r="0.5" fill="currentColor" />
    </>
  ),
  alertCircle: (
    <>
      <circle cx="10" cy="10" r="7" />
      <path d="M10 7v4" />
      <circle cx="10" cy="13.5" r="0.5" fill="currentColor" />
    </>
  ),
  checkCircle: (
    <>
      <circle cx="10" cy="10" r="7" />
      <polyline points="7 10 9.5 12.5 13.5 7.5" />
    </>
  ),
  clock: (
    <>
      <circle cx="10" cy="10" r="7" />
      <path d="M10 6v4l3 2" />
    </>
  ),
  zap: <polygon points="10 1 4 11 10 11 10 19 16 9 10 9" />,
  shield: <path d="M10 2l7 3v5c0 4.5-3 8.5-7 9.5-4-1-7-5-7-9.5V5l7-3z" />,
  eye: (
    <>
      <path d="M2 10s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" />
      <circle cx="10" cy="10" r="2.5" />
    </>
  ),

  // ── Objects ───────────────────────────────────────
  file: (
    <>
      <path d="M5 3h7l5 5v9a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z" />
      <path d="M12 3v5h5" />
    </>
  ),
  fileText: (
    <>
      <path d="M5 3h7l5 5v9a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z" />
      <path d="M12 3v5h5" />
      <path d="M7 11h6" />
      <path d="M7 14h4" />
    </>
  ),
  tag: <path d="M3 5a2 2 0 012-2h4.586a1 1 0 01.707.293l6.414 6.414a2 2 0 010 2.828l-4.172 4.172a2 2 0 01-2.828 0L3.293 10.293A1 1 0 013 9.586V5zm4 1a1 1 0 100 2 1 1 0 000-2z" />,
  star: <polygon points="10 2 12.5 7.5 18 8 14 12 15 18 10 15 5 18 6 12 2 8 7.5 7.5" />,
  bookmark: <path d="M5 3h10a1 1 0 011 1v14l-6-3-6 3V4a1 1 0 011-1z" />,
  cpu: (
    <>
      <rect x="5" y="5" width="10" height="10" rx="1" />
      <rect x="7.5" y="7.5" width="5" height="5" rx="0.5" />
      <path d="M8 2v3M12 2v3M8 15v3M12 15v3M2 8h3M2 12h3M15 8h3M15 12h3" />
    </>
  ),
  send: <path d="M3 10l14-7-7 14-2-5-5-2z" />,
  bell: (
    <>
      <path d="M14 13.5V8a4 4 0 00-8 0v5.5L4 16h12l-2-2.5z" />
      <path d="M8.5 17a1.5 1.5 0 003 0" />
    </>
  ),
};

export function Icon({ name, size = 20, className = "", style = {} }) {
  const content = paths[name];
  if (!content) return null;
  return (
    <svg
      viewBox="0 0 20 20"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      style={{ flexShrink: 0, ...style }}
    >
      {content}
    </svg>
  );
}

export default Icon;
