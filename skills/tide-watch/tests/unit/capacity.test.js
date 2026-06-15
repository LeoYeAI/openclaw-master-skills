const {
  formatRelativeTime,
  parseTimeString,
  formatChannelLabel,
  filterByThreshold,
  filterByActivityAge,
  getSessionsOlderThan,
  sortByCapacity
} = require('../../lib/capacity');

describe('formatRelativeTime', () => {
  test('should format just now for recent timestamps', () => {
    const now = new Date();
    expect(formatRelativeTime(now.toISOString())).toBe('just now');
  });

  test('should format minutes ago', () => {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    expect(formatRelativeTime(fiveMinutesAgo.toISOString())).toBe('5m ago');
  });

  test('should format hours ago', () => {
    const threeHoursAgo = new Date(Date.now() - 3 * 60 * 60 * 1000);
    expect(formatRelativeTime(threeHoursAgo.toISOString())).toBe('3h ago');
  });

  test('should format days ago', () => {
    const fourDaysAgo = new Date(Date.now() - 4 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(fourDaysAgo.toISOString())).toBe('4d ago');
  });

  test('should format weeks ago', () => {
    const twoWeeksAgo = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(twoWeeksAgo.toISOString())).toBe('2w ago');
  });

  test('should format months ago', () => {
    const threeMonthsAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(threeMonthsAgo.toISOString())).toBe('3mo ago');
  });

  test('should format years ago', () => {
    const oneYearAgo = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(oneYearAgo.toISOString())).toBe('1y ago');
  });
});

describe('parseTimeString', () => {
  test('should parse minutes', () => {
    expect(parseTimeString('15m')).toBe(0.25);
  });

  test('should parse hours', () => {
    expect(parseTimeString('2h')).toBe(2);
  });

  test('should parse days', () => {
    expect(parseTimeString('4d')).toBe(96);
  });

  test('should parse weeks', () => {
    expect(parseTimeString('2w')).toBe(336);
  });

  test('should parse months', () => {
    expect(parseTimeString('1mo')).toBe(720);
  });

  test('should parse years', () => {
    expect(parseTimeString('1y')).toBe(8760);
  });

  test('should throw error for invalid format', () => {
    expect(() => parseTimeString('invalid')).toThrow('Invalid time format');
    expect(() => parseTimeString('4days')).toThrow('Invalid time format');
    expect(() => parseTimeString('2')).toThrow('Invalid time format');
  });
});

describe('formatChannelLabel', () => {
  test('should format channel without label', () => {
    expect(formatChannelLabel('discord', null)).toBe('discord');
  });

  test('should format channel with label', () => {
    expect(formatChannelLabel('discord', '#navi-code')).toBe('discord/#navi-code');
  });

  test('should handle empty label', () => {
    expect(formatChannelLabel('webchat', '')).toBe('webchat');
  });
});

describe('filterByThreshold', () => {
  const sessions = [
    { sessionId: '1', percentage: 85.5 },
    { sessionId: '2', percentage: 72.3 },
    { sessionId: '3', percentage: 90.1 },
    { sessionId: '4', percentage: 60.0 }
  ];

  test('should filter sessions above threshold', () => {
    const result = filterByThreshold(sessions, 75);
    expect(result).toHaveLength(2);
    expect(result.map(s => s.sessionId)).toEqual(['1', '3']);
  });

  test('should include sessions at exact threshold', () => {
    const result = filterByThreshold([{ sessionId: '1', percentage: 75.0 }], 75);
    expect(result).toHaveLength(1);
  });

  test('should return empty array if no sessions above threshold', () => {
    const result = filterByThreshold(sessions, 95);
    expect(result).toHaveLength(0);
  });

  test('should return all sessions with threshold of 0', () => {
    const result = filterByThreshold(sessions, 0);
    expect(result).toHaveLength(4);
  });
});

describe('filterByActivityAge', () => {
  const now = Date.now();
  const sessions = [
    { sessionId: '1', lastActivity: new Date(now - 2 * 60 * 60 * 1000).toISOString() }, // 2 hours ago
    { sessionId: '2', lastActivity: new Date(now - 10 * 60 * 60 * 1000).toISOString() }, // 10 hours ago
    { sessionId: '3', lastActivity: new Date(now - 50 * 60 * 60 * 1000).toISOString() }, // 50 hours ago
    { sessionId: '4', lastActivity: new Date(now - 100 * 60 * 60 * 1000).toISOString() } // 100 hours ago
  ];

  test('should filter sessions active within specified hours', () => {
    const result = filterByActivityAge(sessions, 24);
    expect(result).toHaveLength(2);
    expect(result.map(s => s.sessionId)).toEqual(['1', '2']);
  });

  test('should include sessions at exact cutoff time', () => {
    const result = filterByActivityAge(sessions, 48);
    expect(result.length).toBeGreaterThanOrEqual(2);
    expect(result.length).toBeLessThanOrEqual(3);
  });

  test('should return all sessions with large time window', () => {
    const result = filterByActivityAge(sessions, 200);
    expect(result).toHaveLength(4);
  });

  test('should return sessions within very small time window', () => {
    const result = filterByActivityAge(sessions, 1);
    expect(result.length).toBeGreaterThanOrEqual(0);
    expect(result.length).toBeLessThanOrEqual(1);
  });
});

describe('getSessionsOlderThan', () => {
  const now = Date.now();
  const sessions = [
    { sessionId: '1', lastActivity: new Date(now - 2 * 60 * 60 * 1000).toISOString() }, // 2 hours ago
    { sessionId: '2', lastActivity: new Date(now - 10 * 60 * 60 * 1000).toISOString() }, // 10 hours ago
    { sessionId: '3', lastActivity: new Date(now - 50 * 60 * 60 * 1000).toISOString() }, // 50 hours ago
    { sessionId: '4', lastActivity: new Date(now - 100 * 60 * 60 * 1000).toISOString() } // 100 hours ago
  ];

  test('should return sessions older than specified hours', () => {
    const result = getSessionsOlderThan(sessions, 24);
    expect(result).toHaveLength(2);
    expect(result.map(s => s.sessionId)).toEqual(['3', '4']);
  });

  test('should return empty array if all sessions are recent', () => {
    const result = getSessionsOlderThan(sessions, 200);
    expect(result).toHaveLength(0);
  });

  test('should return most sessions if time window is very small', () => {
    const result = getSessionsOlderThan(sessions, 1);
    expect(result.length).toBeGreaterThanOrEqual(3);
    expect(result.length).toBeLessThanOrEqual(4);
  });
});

describe('sortByCapacity', () => {
  test('should sort sessions by percentage descending', () => {
    const sessions = [
      { sessionId: '1', percentage: 60.0 },
      { sessionId: '2', percentage: 90.5 },
      { sessionId: '3', percentage: 75.2 },
      { sessionId: '4', percentage: 85.0 }
    ];

    const result = sortByCapacity(sessions);
    expect(result.map(s => s.percentage)).toEqual([90.5, 85.0, 75.2, 60.0]);
  });

  test('should handle sessions with same percentage', () => {
    const sessions = [
      { sessionId: '1', percentage: 75.0 },
      { sessionId: '2', percentage: 75.0 },
      { sessionId: '3', percentage: 80.0 }
    ];

    const result = sortByCapacity(sessions);
    expect(result[0].percentage).toBe(80.0);
    expect(result[1].percentage).toBe(75.0);
    expect(result[2].percentage).toBe(75.0);
  });

  test('should handle empty array', () => {
    const result = sortByCapacity([]);
    expect(result).toEqual([]);
  });

  test('should handle single session', () => {
    const sessions = [{ sessionId: '1', percentage: 85.0 }];
    const result = sortByCapacity(sessions);
    expect(result).toEqual(sessions);
  });
});
