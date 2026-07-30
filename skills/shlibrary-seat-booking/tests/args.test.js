const test = require('node:test');
const assert = require('node:assert/strict');

const {
  parseCliArgs,
  validateCliSpec,
  normalizeAreaId,
  normalizeRow,
  normalizeSeatNo,
  normalizeSeatRowLabel
} = require('../scripts/lib/args');

test('parseCliArgs parses profile, command, and Chinese area values', () => {
  const parsed = parseCliArgs([
    '--profile', 'user1',
    'availability',
    '--date', '2026-03-20',
    '--area', '北区', '东区'
  ]);

  assert.deepEqual(parsed, {
    help: false,
    profileName: 'user1',
    profileDir: null,
    authFile: null,
    command: 'availability',
    options: {
      areas: ['北区', '东区'],
      date: '2026-03-20'
    }
  });
});

test('validateCliSpec accepts full specific-seat booking args', () => {
  assert.doesNotThrow(() => validateCliSpec('book', {
    areas: ['南区'],
    date: '2026-03-24',
    period: '下午',
    seatRow: '4排',
    seatNo: '2号'
  }));
});

test('validateCliSpec rejects partial seat arguments', () => {
  assert.throws(
    () => validateCliSpec('book', {
      areas: ['南区'],
      date: '2026-03-24',
      seatRow: '4',
      areas: ['南区']
    }),
    /指定座位预约需要同时提供/
  );
});

test('validateCliSpec rejects multiple book areas', () => {
  assert.throws(
    () => validateCliSpec('book', {
      areas: ['南区', '北区'],
      date: '2026-03-24',
      seatRow: '4',
      seatNo: '2'
    }),
    /一次只能预约一个区域/
  );
});

test('normalize helpers support Chinese and numeric values', () => {
  assert.equal(normalizeAreaId('南区'), '5');
  assert.equal(normalizeAreaId('2'), '2');
  assert.equal(normalizeRow('4排'), '4');
  assert.equal(normalizeRow('4'), '4');
  assert.equal(normalizeSeatNo('2号'), '2');
  assert.equal(normalizeSeatNo('2'), '2');
  assert.equal(normalizeSeatRowLabel({ seatRow: '12排' }), '12');
});

test('normalizeAreaId rejects unknown area names', () => {
  assert.throws(() => normalizeAreaId('中区'), /无法识别区域/);
});
