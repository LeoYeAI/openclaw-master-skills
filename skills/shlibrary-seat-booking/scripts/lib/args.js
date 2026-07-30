const { AREA_NAME_TO_ID } = require('./config');
const { normalizeProfileName } = require('./profile_store');

const KNOWN_COMMANDS = new Set(['availability', 'list', 'cancel', 'book']);

function parseCliArgs(rawArgs) {
  const args = [...rawArgs];
  let profileName = null;
  let profileDir = null;
  let authFile = null;
  let command = null;
  const options = {
    areas: []
  };

  for (let index = 0; index < args.length; index += 1) {
    const token = args[index];

    if (token === '--help' || token === '-h') {
      return {
        help: true,
        profileName: null,
        profileDir: null,
        authFile: null,
        command: null,
        options
      };
    }

    if (token === '--profile') {
      const candidate = args[index + 1];
      if (!candidate) {
        throw new Error('`--profile` 后面需要跟一个名称，例如: --profile liurenyu');
      }
      profileName = normalizeProfileName(candidate);
      index += 1;
      continue;
    }

    if (token === '--profile-dir') {
      const candidate = args[index + 1];
      if (!candidate) {
        throw new Error('`--profile-dir` 后面需要跟一个目录路径');
      }
      profileDir = String(candidate).trim();
      if (!profileDir) {
        throw new Error('profile-dir 不能为空');
      }
      index += 1;
      continue;
    }

    if (token === '--auth-file') {
      const candidate = args[index + 1];
      if (!candidate) {
        throw new Error('`--auth-file` 后面需要跟一个文件路径');
      }
      authFile = String(candidate).trim();
      if (!authFile) {
        throw new Error('auth-file 不能为空');
      }
      index += 1;
      continue;
    }

    if (!command) {
      if (!KNOWN_COMMANDS.has(token)) {
        throw new Error(`无法识别命令: ${token}。支持 availability / list / cancel / book`);
      }
      command = token;
      continue;
    }

    if (token === '--date') {
      const value = args[index + 1];
      if (!value) {
        throw new Error('`--date` 后面需要跟日期，例如: --date 2026-03-20');
      }
      options.date = String(value).trim();
      index += 1;
      continue;
    }

    if (token === '--period') {
      const value = args[index + 1];
      if (!value) {
        throw new Error('`--period` 后面需要跟时段，例如: --period 下午');
      }
      options.period = String(value).trim();
      index += 1;
      continue;
    }

    if (token === '--reservation-id') {
      const value = args[index + 1];
      if (!value) {
        throw new Error('`--reservation-id` 后面需要跟预约ID');
      }
      options.reservationId = String(value).trim();
      index += 1;
      continue;
    }

    if (token === '--seat-row') {
      const value = args[index + 1];
      if (!value) {
        throw new Error('`--seat-row` 后面需要跟排号，例如: --seat-row 4');
      }
      options.seatRow = String(value).trim();
      index += 1;
      continue;
    }

    if (token === '--seat-no') {
      const value = args[index + 1];
      if (!value) {
        throw new Error('`--seat-no` 后面需要跟座位号，例如: --seat-no 5');
      }
      options.seatNo = String(value).trim();
      index += 1;
      continue;
    }

    if (token === '--area') {
      const values = [];
      while (index + 1 < args.length && !String(args[index + 1]).startsWith('--')) {
        values.push(String(args[index + 1]).trim());
        index += 1;
      }
      if (values.length === 0) {
        throw new Error('`--area` 后面至少需要一个区域，例如: --area 北区 东区');
      }
      options.areas.push(...values);
      continue;
    }

    throw new Error(`无法识别参数: ${token}`);
  }

  return {
    help: false,
    profileName,
    profileDir,
    authFile,
    command,
    options
  };
}

function validateCliSpec(command, options) {
  if (!command) {
    throw new Error('缺少命令。支持 availability / list / cancel / book');
  }

  const hasDate = Boolean(options.date);
  const hasPeriod = Boolean(options.period);
  const hasAreas = options.areas.length > 0;
  const hasSeatRow = Boolean(options.seatRow);
  const hasSeatNo = Boolean(options.seatNo);
  const hasReservationId = Boolean(options.reservationId);

  if (command === 'availability') {
    if (!hasDate) {
      throw new Error('`availability` 需要 `--date`，例如: availability --date 2026-03-20');
    }
    if (hasPeriod || hasSeatRow || hasSeatNo || hasReservationId) {
      throw new Error('`availability` 只支持 `--date` 和可选的 `--area`');
    }
    return;
  }

  if (command === 'list') {
    if (hasDate || hasPeriod || hasAreas || hasSeatRow || hasSeatNo || hasReservationId) {
      throw new Error('`list` 不接受额外参数，只支持可选的 `--profile`');
    }
    return;
  }

  if (command === 'cancel') {
    if (!hasReservationId) {
      throw new Error('`cancel` 需要 `--reservation-id`，例如: cancel --reservation-id 5187335');
    }
    if (hasDate || hasPeriod || hasAreas || hasSeatRow || hasSeatNo) {
      throw new Error('`cancel` 只支持 `--reservation-id` 和可选的 `--profile`');
    }
    return;
  }

  if (command === 'book') {
    if (!hasDate) {
      throw new Error('`book` 需要 `--date`，例如: book --date 2026-03-24');
    }

    const hasSpecificSeat = hasAreas || hasSeatRow || hasSeatNo;
    if (hasSpecificSeat && !(hasAreas && hasSeatRow && hasSeatNo)) {
      throw new Error('指定座位预约需要同时提供 `--area`、`--seat-row` 和 `--seat-no`');
    }
    if (options.areas.length > 1) {
      throw new Error('`book` 一次只能预约一个区域，请只传一个 `--area` 值');
    }
    if (hasReservationId) {
      throw new Error('`book` 不支持 `--reservation-id`');
    }
    return;
  }
}

function normalizeAreaId(areaInput) {
  const normalized = String(areaInput || '').trim();
  if (/^[2-5]$/.test(normalized)) {
    return normalized;
  }
  if (AREA_NAME_TO_ID[normalized]) {
    return String(AREA_NAME_TO_ID[normalized]);
  }
  throw new Error(`无法识别区域: ${normalized}。支持 2/3/4/5 或 东区/西区/北区/南区`);
}

function normalizeRow(rowInput) {
  const normalized = String(rowInput || '').trim().replace(/排$/, '');
  if (!/^\d+$/.test(normalized)) {
    throw new Error(`无法识别排号: ${rowInput}`);
  }
  return normalized;
}

function normalizeSeatNo(seatInput) {
  const normalized = String(seatInput || '').trim().replace(/号$/, '');
  if (!/^\d+$/.test(normalized)) {
    throw new Error(`无法识别座位号: ${seatInput}`);
  }
  return normalized;
}

function normalizeSeatRowLabel(item) {
  if (item && typeof item === 'object') {
    const candidate = String(item.seatRow || item.row || item.name || item.label || '').trim();
    return candidate.replace(/排$/, '');
  }

  return String(item || '').trim().replace(/排$/, '');
}

module.exports = {
  parseCliArgs,
  validateCliSpec,
  normalizeAreaId,
  normalizeRow,
  normalizeSeatNo,
  normalizeSeatRowLabel
};
