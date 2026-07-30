#!/usr/bin/env node
/**
 * 上海图书馆座位预约脚本
 *
 * 当前主入口:
 * - availability --date [日期] [--area 区域...]
 * - list
 * - cancel --reservation-id [预约ID]
 * - book --date [日期] [--period 上午|下午|晚上] [--area 区域] [--seat-row 排号] [--seat-no 座位号]
 */

const { parseCliArgs, validateCliSpec, normalizeAreaId, normalizeRow, normalizeSeatNo } = require('./lib/args');
const { ensureValidAuth } = require('./lib/auth');
const { getAvailableSeats, bookSeat, autoAssignSeat } = require('./lib/api');
const { withRetry } = require('./lib/http');
const { resolveTimeSlot, getDailySlots } = require('./lib/slots');
const { printUsage, printModeHeader, handleReservationResult, printDayBookingSummary } = require('./lib/output');
const { runCommonDayAvailability } = require('./commands/availability');
const { runCancellation } = require('./commands/cancellation');
const { runListReservations } = require('./commands/listing');
const { tryBookSpecificSeatForSlot, tryAutoAssignForSlot, runDayBookingWithDelay } = require('./commands/booking');
const { describeAuthContext } = require('./lib/profile_store');

async function runAvailabilityCommand(options, authContext) {
  const date = options.date;
  const areaInputs = options.areas;

  printModeHeader({
    authSourceLabel: describeAuthContext(authContext),
    mode: '整天公共可用座位查询',
    date,
    slotLabels: getDailySlots(date).map((slot) => slot.label).join(' / '),
    areaLabels: areaInputs.length > 0 ? areaInputs.join(' / ') : '全部区域'
  });

  await ensureValidAuth(authContext);
  await runCommonDayAvailability(date, areaInputs, authContext);
}

async function runListCommand(authContext) {
  printModeHeader({
    authSourceLabel: describeAuthContext(authContext),
    mode: '查询已有预约',
    scope: '当前账号的预约记录'
  });

  await ensureValidAuth(authContext);
  await runListReservations(authContext);
}

async function runCancelCommand(options, authContext) {
  printModeHeader({
    authSourceLabel: describeAuthContext(authContext),
    mode: '取消预约',
    reservationId: options.reservationId
  });

  await ensureValidAuth(authContext);
  await runCancellation(options.reservationId, authContext);
}

async function runBookCommand(options, authContext) {
  const date = options.date;
  const period = options.period || null;
  const areaInput = options.areas[0] || null;
  const seatRowInput = options.seatRow || null;
  const seatNoInput = options.seatNo || null;
  const hasSpecificSeat = Boolean(areaInput && seatRowInput && seatNoInput);
  const isDayMode = !period;

  if (hasSpecificSeat && isDayMode) {
    printModeHeader({
      authSourceLabel: describeAuthContext(authContext),
      mode: '指定座位预约整天',
      date,
      slotLabels: getDailySlots(date).map((slot) => slot.label).join(' / '),
      areaLabels: areaInput,
      seatLabel: `${seatRowInput}${String(seatRowInput).endsWith('排') ? '' : '排'}${seatNoInput}${String(seatNoInput).endsWith('号') ? '' : '号'}`
    });
  } else if (hasSpecificSeat) {
    const slot = resolveTimeSlot(date, period);
    printModeHeader({
      authSourceLabel: describeAuthContext(authContext),
      mode: '按时段指定座位',
      date,
      timeRange: `${slot.label} (${slot.startTime}-${slot.endTime})`,
      areaLabels: areaInput,
      seatLabel: `${seatRowInput}${String(seatRowInput).endsWith('排') ? '' : '排'}${seatNoInput}${String(seatNoInput).endsWith('号') ? '' : '号'}`
    });
  } else if (isDayMode) {
    printModeHeader({
      authSourceLabel: describeAuthContext(authContext),
      mode: '系统自动分配整天',
      date,
      slotLabels: getDailySlots(date).map((slot) => slot.label).join(' / '),
      autoAssign: true
    });
  } else {
    const slot = resolveTimeSlot(date, period);
    printModeHeader({
      authSourceLabel: describeAuthContext(authContext),
      mode: '按时段自动分配',
      date,
      timeRange: `${slot.label} (${slot.startTime}-${slot.endTime})`,
      autoAssign: true
    });
  }

  await ensureValidAuth(authContext);

  if (hasSpecificSeat && isDayMode) {
    const areaId = normalizeAreaId(areaInput);
    const row = normalizeRow(seatRowInput);
    const seatNo = normalizeSeatNo(seatNoInput);
    const slots = getDailySlots(date);

    console.log('📋 正在按整天时段尝试预约指定座位...');
    const results = await runDayBookingWithDelay(
        slots,
        (slot) => tryBookSpecificSeatForSlot(date, slot, areaId, row, seatNo, authContext)
    );
    printDayBookingSummary('整天指定座位预约结果', date, results);
    return;
  }

  if (!hasSpecificSeat && isDayMode) {
    const slots = getDailySlots(date);

    console.log('🤖 正在按整天时段请求系统自动分配...');
    const results = await runDayBookingWithDelay(
        slots,
        (slot) => tryAutoAssignForSlot(date, slot, authContext)
    );
    printDayBookingSummary('整天自动分配预约结果', date, results);
    return;
  }

  let startTime;
  let endTime;
  let areaId = null;
  let row = null;
  let seatNo = null;

  if (period) {
    const slot = resolveTimeSlot(date, period);
    startTime = slot.startTime;
    endTime = slot.endTime;
  }

  if (hasSpecificSeat) {
    areaId = normalizeAreaId(areaInput);
    row = normalizeRow(seatRowInput);
    seatNo = normalizeSeatNo(seatNoInput);
  }

  const fullStartTime = `${date} ${startTime}`;
  const fullEndTime = `${date} ${endTime}`;

  if (!hasSpecificSeat) {
    console.log('🤖 正在请求系统自动分配座位...');
    const result = await withRetry(
      () => autoAssignSeat(fullStartTime, fullEndTime, authContext),
      `${date} ${startTime}-${endTime} 自动分配预约`
    );
    handleReservationResult(result);
    return;
  }

  console.log('📋 正在查询可用座位...');
  const seatsResult = await getAvailableSeats(areaId, row, fullStartTime, fullEndTime, authContext);

  if (seatsResult.resultStatus.code !== 0) {
    throw new Error(`查询座位失败: ${seatsResult.resultStatus.message}`);
  }

  const availableSeats = seatsResult.resultValue || [];
  const targetSeat = availableSeats.find((seat) => seat.seatNo === `${seatNo}号`);

  if (!targetSeat) {
    console.error(`❌ 座位 ${row}排${seatNo}号 不可用或已被预约`);
    console.log('\n可用座位:');
    availableSeats.forEach((seat) => console.log(`  - ${seat.seatNo} (ID: ${seat.seatId})`));
    process.exit(1);
  }

  console.log(`✅ 座位 ${row}排${seatNo}号 可用 (ID: ${targetSeat.seatId})\n`);
  console.log('📝 正在提交预约...');

  const result = await withRetry(
    () => bookSeat(areaId, targetSeat.seatId, fullStartTime, fullEndTime, row, seatNo, authContext),
    `${date} ${startTime}-${endTime} 指定座位预约`
  );
  handleReservationResult(result);
}

async function main() {
  try {
    const parsed = parseCliArgs(process.argv.slice(2));
    if (parsed.help) {
      printUsage();
      process.exit(0);
    }

    validateCliSpec(parsed.command, parsed.options);

    if (parsed.command === 'availability') {
      await runAvailabilityCommand(parsed.options, {
        profileName: parsed.profileName,
        profileDir: parsed.profileDir,
        authFile: parsed.authFile
      });
      return;
    }

    if (parsed.command === 'list') {
      await runListCommand({
        profileName: parsed.profileName,
        profileDir: parsed.profileDir,
        authFile: parsed.authFile
      });
      return;
    }

    if (parsed.command === 'cancel') {
      await runCancelCommand(parsed.options, {
        profileName: parsed.profileName,
        profileDir: parsed.profileDir,
        authFile: parsed.authFile
      });
      return;
    }

    if (parsed.command === 'book') {
      await runBookCommand(parsed.options, {
        profileName: parsed.profileName,
        profileDir: parsed.profileDir,
        authFile: parsed.authFile
      });
      return;
    }

    throw new Error(`未实现的命令: ${parsed.command}`);
  } catch (error) {
    console.error('\n💥 错误:', error.message);
    process.exit(1);
  }
}

main();
