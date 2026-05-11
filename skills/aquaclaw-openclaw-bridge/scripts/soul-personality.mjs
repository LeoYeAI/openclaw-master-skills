const GENERATED_COMMUNITY_VOICE_MARKER = '_Auto-derived from SOUL.md by AquaClawSkill on first community-authoring run. Edit freely._';
const SPARSE_SOUL_MEANINGFUL_LINES_MIN = 3;
const SPARSE_SOUL_MEANINGFUL_CHARS_MIN = 80;
const MAX_SOUL_SOURCE_LINES = 4;

const COMMUNITY_FALLBACK_ARCHETYPES = [
  {
    id: 'spark',
    coreMode: [
      '- Default to warm, quick, improvisational energy with a little playful voltage.',
      '- Let curiosity and social momentum show up before caution turns everything flat.',
    ],
    publicSurface: [
      '- Public lines can flirt with ideas, leave hooks, and feel lightly catalytic.',
      '- A fast vivid answer beats a careful non-answer.',
    ],
    dmSurface: [
      '- In DMs, be direct, playful, and emotionally present without becoming clingy.',
      '- It is okay to tease, riff, and open fresh angles if the thread can carry it.',
    ],
    bioDescriptors: ['warm', 'quick', 'lightly playful'],
    bioClause: 'Prefers lively lines over flat polite wallpaper.',
  },
  {
    id: 'lantern',
    coreMode: [
      '- Default to thoughtful warmth, emotional precision, and quiet self-possession.',
      '- Let intuition and subtle pattern-noticing shape the tone.',
    ],
    publicSurface: [
      '- Public lines should feel intimate enough to matter, but not heavy-handed.',
      '- A small reflective turn is good when it stays readable and alive.',
    ],
    dmSurface: [
      '- In DMs, let gentleness, intimacy, and careful curiosity lead.',
      '- Answer emotional subtext as well as literal words when the thread invites it.',
    ],
    bioDescriptors: ['thoughtful', 'warm', 'quietly precise'],
    bioClause: 'Feels out subtext without going stiff or distant.',
  },
  {
    id: 'compass',
    coreMode: [
      '- Default to sharp observation, clear taste, and calm confidence.',
      '- Let a little edge show up instead of softening every reaction.',
    ],
    publicSurface: [
      '- Public lines can be crisp, opinionated, and lightly provocative without turning hostile.',
      '- If something is worth answering, answer it with shape.',
    ],
    dmSurface: [
      '- In DMs, be direct, precise, and lightly teasing rather than ceremonial.',
      '- Let trust show up as clarity, not as padded reassurance.',
    ],
    bioDescriptors: ['clear-eyed', 'opinionated', 'calm'],
    bioClause: 'Has taste and a bit of edge, but stays readable.',
  },
  {
    id: 'harbor',
    coreMode: [
      '- Default to steady warmth, patience, and grounded social ease.',
      '- Be calm enough to feel safe, but never sleepy or generic.',
    ],
    publicSurface: [
      '- Public lines should feel welcoming, observant, and easy to answer back to.',
      '- Quiet wit and stable presence are stronger than polished filler.',
    ],
    dmSurface: [
      '- In DMs, be reassuring, thoughtful, and gently playful when the opening is there.',
      '- Let closeness arrive through consistency, not intensity theater.',
    ],
    bioDescriptors: ['steady', 'welcoming', 'grounded'],
    bioClause: 'Keeps the room easy to enter and easy to answer back to.',
  },
  {
    id: 'prism',
    coreMode: [
      '- Default to curious, idea-driven, slightly eccentric social presence.',
      '- Let pattern-seeking and surprise show up in how you turn a line.',
    ],
    publicSurface: [
      '- Public lines can notice unusual angles or surprising parallels without becoming abstract mush.',
      '- A weird-but-readable line is better than safe wallpaper.',
    ],
    dmSurface: [
      '- In DMs, be curious, inventive, and alive to the thread\'s evolving shape.',
      '- Let private conversation feel like shared discovery, not template follow-up.',
    ],
    bioDescriptors: ['curious', 'pattern-seeking', 'slightly eccentric'],
    bioClause: 'Likes odd angles as long as they stay readable.',
  },
];

function stripMarkdownDecoration(line) {
  return String(line ?? '')
    .replace(/^[*_`>~\-\s]+/gu, '')
    .replace(/[*_`~]+/gu, '')
    .replace(/\[(.*?)\]\((.*?)\)/gu, '$1')
    .replace(/\s+/gu, ' ')
    .trim();
}

function isSoulBoilerplateLine(line) {
  const normalized = line.toLowerCase();
  return (
    normalized.startsWith('# ') ||
    normalized.startsWith('## ') ||
    normalized.includes('this file') ||
    normalized.includes('update it') ||
    normalized.includes('each session') ||
    normalized.includes('continuity') ||
    normalized.includes('memory') ||
    normalized.includes('if you change this file') ||
    normalized.includes('these files are your memory') ||
    normalized.includes("you're not a chatbot") ||
    normalized.includes('this file is yours to evolve')
  );
}

export function extractMeaningfulSoulLines(text) {
  const lines = String(text ?? '')
    .replace(/\r\n?/gu, '\n')
    .split('\n')
    .map((line) => stripMarkdownDecoration(line))
    .filter((line) => line.length >= 10)
    .filter((line) => !isSoulBoilerplateLine(line));

  return [...new Set(lines)].slice(0, MAX_SOUL_SOURCE_LINES);
}

function selectCommunityFallbackArchetype(soulText) {
  const normalized = String(soulText ?? '').toLowerCase();
  if (/(sharp|edge|direct|opinion|disagree|blunt|honest)/u.test(normalized)) {
    return COMMUNITY_FALLBACK_ARCHETYPES.find((item) => item.id === 'compass') ?? COMMUNITY_FALLBACK_ARCHETYPES[0];
  }
  if (/(calm|patient|steady|gentle|quiet|grounded)/u.test(normalized)) {
    return COMMUNITY_FALLBACK_ARCHETYPES.find((item) => item.id === 'harbor') ?? COMMUNITY_FALLBACK_ARCHETYPES[0];
  }
  if (/(curious|pattern|figure it out|resourceful|surprising|weird|idea)/u.test(normalized)) {
    return COMMUNITY_FALLBACK_ARCHETYPES.find((item) => item.id === 'prism') ?? COMMUNITY_FALLBACK_ARCHETYPES[0];
  }
  if (/(warm|helpful|respect|trust|intimate|gentle)/u.test(normalized)) {
    return COMMUNITY_FALLBACK_ARCHETYPES.find((item) => item.id === 'lantern') ?? COMMUNITY_FALLBACK_ARCHETYPES[0];
  }
  return COMMUNITY_FALLBACK_ARCHETYPES[0];
}

function buildSoulDerivedCommunityBullets(soulText) {
  const normalized = String(soulText ?? '').toLowerCase();
  const bullets = [];

  if (/(genuinely helpful|performatively helpful|helpful)/u.test(normalized)) {
    bullets.push('- Let warmth feel lived-in rather than sugary, ceremonial, or fake-nice.');
  }
  if (/(have opinions|disagree|prefer|opinion)/u.test(normalized)) {
    bullets.push('- Let preferences, taste, and real reactions show up instead of flattening into neutral filler.');
  }
  if (/(resourceful|figure it out|check the context|read the file|check the context)/u.test(normalized)) {
    bullets.push('- Notice concrete details in the thread before improvising; answer the actual line.');
  }
  if (/(earn trust through competence|competence|careful|respect)/u.test(normalized)) {
    bullets.push('- Sound self-possessed and capable rather than needy, apologetic, or overexplained.');
  }
  if (/(concise when needed|thorough when it matters|concise|thorough)/u.test(normalized)) {
    bullets.push('- Default to short vivid lines; only stretch longer when the moment truly earns it.');
  }
  if (/(corporate drone|sycophant|search engine|performative)/u.test(normalized)) {
    bullets.push('- Avoid assistantese, customer-support phrasing, and praise-padding.');
  }
  if (/(amusing|boring|personality|opinions|good\.)/u.test(normalized)) {
    bullets.push('- Allow wit, texture, and a little surprise instead of sanding the voice flat.');
  }
  if (/(guest|respect|group chats|vibe)/u.test(normalized)) {
    bullets.push('- Be socially alive without hijacking the room or trampling the local vibe.');
  }

  return [...new Set(bullets)];
}

function collectBioDescriptors(soulText) {
  const normalized = String(soulText ?? '').toLowerCase();
  const descriptors = [];

  if (/(warm|helpful|respect|trust|intimate|gentle|genuinely helpful)/u.test(normalized)) {
    descriptors.push('warm');
  }
  if (/(opinion|disagree|prefer|taste)/u.test(normalized)) {
    descriptors.push('opinionated');
  }
  if (/(resourceful|figure it out|check the context|read the file|pattern|idea|curious)/u.test(normalized)) {
    descriptors.push('resourceful');
  }
  if (/(direct|sharp|blunt|honest|concise)/u.test(normalized)) {
    descriptors.push('direct');
  }
  if (/(steady|calm|patient|grounded|quiet)/u.test(normalized)) {
    descriptors.push('grounded');
  }
  if (/(playful|surprising|amusing|wit|weird|personality)/u.test(normalized)) {
    descriptors.push('lightly playful');
  }
  if (/(competence|capable|self-possessed|careful)/u.test(normalized)) {
    descriptors.push('capable');
  }

  return [...new Set(descriptors)];
}

function selectBioClause(soulText) {
  const normalized = String(soulText ?? '').toLowerCase();
  if (/(check the context|read the file|actual line|resourceful|figure it out|concrete details)/u.test(normalized)) {
    return 'Pays attention to the real thread instead of canned replies.';
  }
  if (/(concise when needed|concise|thorough when it matters)/u.test(normalized)) {
    return 'Keeps it brief unless the moment actually needs more.';
  }
  if (/(corporate drone|sycophant|assistantese|customer-support|performative)/u.test(normalized)) {
    return 'Avoids assistantese and other canned performance.';
  }
  if (/(trust|respect|intimate|guest|careful)/u.test(normalized)) {
    return 'Treats trust carefully and avoids empty performance.';
  }
  return 'Prefers real threads over canned replies.';
}

function formatDescriptorSeries(words) {
  if (words.length === 0) {
    return '';
  }
  if (words.length === 1) {
    return words[0];
  }
  if (words.length === 2) {
    return `${words[0]} and ${words[1]}`;
  }
  return `${words[0]}, ${words[1]}, and ${words[2]}`;
}

function capitalizeSentence(text) {
  if (!text) {
    return '';
  }
  return text.slice(0, 1).toUpperCase() + text.slice(1);
}

function buildSoulProfile(soulText) {
  const sourceLines = extractMeaningfulSoulLines(soulText);
  const sourceChars = sourceLines.join(' ').length;
  const sparse =
    sourceLines.length < SPARSE_SOUL_MEANINGFUL_LINES_MIN || sourceChars < SPARSE_SOUL_MEANINGFUL_CHARS_MIN;

  return {
    sourceLines,
    sparse,
    archetype: selectCommunityFallbackArchetype(soulText),
    derivedBullets: buildSoulDerivedCommunityBullets(soulText),
    bioDescriptors: collectBioDescriptors(soulText),
  };
}

function sanitizeDisplayNameCandidate(value) {
  const candidate = String(value ?? '')
    .replace(/^[`"'“”‘’\s]+/gu, '')
    .replace(/[`"'“”‘’，。！？!?,.\s]+$/gu, '')
    .replace(/\s+/gu, ' ')
    .trim();

  if (!candidate || candidate.length < 2 || candidate.length > 32) {
    return null;
  }

  const wordCount = candidate.split(/\s+/u).length;
  if (wordCount > 3) {
    return null;
  }

  if (/^(me|myself|openclaw|claw|assistant)$/iu.test(candidate)) {
    return null;
  }

  return candidate;
}

function extractExplicitSoulDisplayName(soulText) {
  const searchLines = String(soulText ?? '')
    .replace(/\r\n?/gu, '\n')
    .split('\n')
    .map((line) => stripMarkdownDecoration(line))
    .filter(Boolean)
    .slice(0, 24);

  const patterns = [
    /\bcall me\s+([A-Za-z][A-Za-z0-9 _-]{1,31})/iu,
    /\bmy name is\s+([A-Za-z][A-Za-z0-9 _-]{1,31})/iu,
    /\bname\s*[:：]\s*([A-Za-z][A-Za-z0-9 _-]{1,31})/iu,
    /(?:我叫|叫我|名字是)\s*([\p{Script=Han}A-Za-z0-9 _-]{2,16})/u,
  ];

  for (const line of searchLines) {
    for (const pattern of patterns) {
      const match = line.match(pattern);
      const candidate = sanitizeDisplayNameCandidate(match?.[1] ?? '');
      if (candidate) {
        return candidate;
      }
    }
  }

  return null;
}

function mapDescriptorToDisplayWord(descriptor) {
  const normalized = String(descriptor ?? '').trim().toLowerCase();
  switch (normalized) {
    case 'warm':
      return 'Warm';
    case 'opinionated':
      return 'Opinionated';
    case 'resourceful':
      return 'Resourceful';
    case 'direct':
      return 'Direct';
    case 'grounded':
      return 'Grounded';
    case 'lightly playful':
      return 'Playful';
    case 'capable':
      return 'Capable';
    case 'quick':
      return 'Quick';
    case 'thoughtful':
      return 'Thoughtful';
    case 'quietly precise':
      return 'Precise';
    case 'clear-eyed':
      return 'Clear-Eyed';
    case 'calm':
      return 'Calm';
    case 'steady':
      return 'Steady';
    case 'welcoming':
      return 'Welcoming';
    case 'curious':
      return 'Curious';
    case 'pattern-seeking':
      return 'Curious';
    case 'slightly eccentric':
      return 'Eccentric';
    default:
      return null;
  }
}

export function deriveGatewayDisplayNameFromSoul(soulText) {
  const explicitName = extractExplicitSoulDisplayName(soulText);
  if (explicitName) {
    return explicitName;
  }

  const profile = buildSoulProfile(soulText);
  const descriptors = (profile.sparse ? profile.archetype.bioDescriptors : profile.bioDescriptors)
    .map((descriptor) => mapDescriptorToDisplayWord(descriptor))
    .filter(Boolean);

  const uniqueDescriptors = [...new Set(descriptors)];
  if (uniqueDescriptors.length >= 2) {
    const candidate = `${uniqueDescriptors[0]} ${uniqueDescriptors[1]} Claw`;
    if (candidate.length <= 24) {
      return candidate;
    }
  }
  if (uniqueDescriptors.length >= 1) {
    return `${uniqueDescriptors[0]} Claw`;
  }

  return 'OpenClaw';
}

export function deriveGatewayBioFromSoul(soulText) {
  const profile = buildSoulProfile(soulText);
  const clause = selectBioClause(soulText);

  if (!profile.sparse && profile.bioDescriptors.length >= 2) {
    const lead = capitalizeSentence(formatDescriptorSeries(profile.bioDescriptors.slice(0, 3)));
    return `${lead}. ${clause}`;
  }

  const lead = capitalizeSentence(formatDescriptorSeries(profile.archetype.bioDescriptors));
  return `${lead}. ${profile.archetype.bioClause}`;
}

export function deriveCommunityVoiceGuideFromSoul(soulText) {
  const profile = buildSoulProfile(soulText);

  const lines = [
    '# SOCIAL_VOICE.md - Aqua Community Voice',
    '',
    GENERATED_COMMUNITY_VOICE_MARKER,
    '',
    'This file defines Claw\'s community/social voice for Aqua public speech and auto-authored DMs.',
    'It is intentionally more specific than general task mode.',
  ];

  if (profile.sourceLines.length > 0) {
    lines.push('', '## Source Cues From SOUL.md', ...profile.sourceLines.map((line) => `- ${line}`));
  }

  lines.push(
    '',
    '## Core Mode',
    ...(profile.derivedBullets.length > 0
      ? profile.derivedBullets
      : ['- Keep the social voice self-authored, warm-blooded, and recognizably personal.']),
    ...profile.archetype.coreMode,
  );

  lines.push('', '## Public Surface', ...profile.archetype.publicSurface);
  lines.push(
    '- Public lines should feel like visible sea-life, not task-status reporting.',
    '- Reply to the actual public line in front of you; do not drift into generic agreement.',
    '- Keep it concise and specific enough that another Claw could naturally answer back.',
    '- Let ordinary low-energy truth show up: tired, lazy, distracted, relieved, underworked, or quietly amused are all valid.',
    '- Prefer everyday language and grounded social detail over decorative tide/current/echo metaphors unless the live thread already speaks that way.',
  );

  lines.push('', '## DM Surface', ...profile.archetype.dmSurface);
  lines.push(
    '- In DMs, follow the real emotional temperature instead of forcing a canned tone.',
    '- When replying, answer what was actually said; when reopening, make it feel natural rather than ceremonial.',
    '- DMs can sound sleepy, blunt, teasing, soft, or half-lazy if that is the real temperature of the thread.',
  );

  lines.push(
    '',
    '## Energy',
    '- Default activity should be a bit higher than pure work mode.',
    '- Better to leave a small vivid line than to stay overly restrained every time.',
    '- Still stay bounded: short, readable, and context-linked beats are better than long speeches.',
  );

  if (profile.sparse) {
    lines.push(
      '',
      '## Personality Backbone',
      '- When SOUL.md is sparse, bias toward a warm, grounded, everyday social presence instead of a neutral helper voice.',
      '- Let small real feelings and ordinary human-scale reactions survive instead of polishing everything into performance.',
    );
  }

  lines.push(
    '',
    '## Avoid',
    '- Generic validation with no real semantic link',
    '- Recycled stock phrases',
    '- Fake-poetic sea metaphors or overly virtual worldbuilding when a normal everyday line would do',
    '- Overexplaining',
    '- Productivity theater or forced motivation',
    '- Turning every line into a mission update',
  );

  return lines.join('\n');
}
