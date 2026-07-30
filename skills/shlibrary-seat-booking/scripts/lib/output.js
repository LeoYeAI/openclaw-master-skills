const { getDailySlots } = require('./slots');

function printUsage() {
  console.log('使用方法:');
  console.log('  查询整天公共可用座位: node book_seat.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件] availability --date [日期] [--area 区域...]');
  console.log('  查询已有预约:         node book_seat.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件] list');
  console.log('  取消预约:             node book_seat.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件] cancel --reservation-id [预约ID]');
  console.log('  预约座位:             node book_seat.js [--profile 名称] [--profile-dir 目录] [--auth-file 文件] book --date [日期] [--period 上午|下午|晚上] [--area 区域] [--seat-row 排号] [--seat-no 座位号]');
  console.log('');
  console.log('示例:');
  console.log('  node book_seat.js availability --date 2026-03-20 --area 北区 东区');
  console.log('  node book_seat.js list --profile liurenyu');
  console.log('  node book_seat.js list --auth-file ~/.config/shlibrary-seat-booking/profiles/user1.json');
  console.log('  node book_seat.js cancel --profile liurenyu --reservation-id 5187335');
  console.log('  node book_seat.js availability --profile user1 --profile-dir ~/.config/shlibrary-seat-booking --date 2026-03-20');
  console.log('  node book_seat.js book --profile liurenyu --date 2026-03-24');
  console.log('  node book_seat.js book --date 2026-03-24 --period 上午');
  console.log('  node book_seat.js book --date 2026-03-24 --area 南区 --seat-row 4 --seat-no 5');
  console.log('  node book_seat.js book --date 2026-03-24 --period 下午 --area 南区 --seat-row 4 --seat-no 5');
  console.log('');
  console.log('区域参数支持: 东区 / 西区 / 北区 / 南区，或 2 / 3 / 4 / 5');
}

function printModeHeader({ authSourceLabel, profileName, mode, scope, reservationId, date, slotLabels, areaLabels, seatLabel, timeRange, autoAssign }) {
  console.log('========================================');
  console.log('上海图书馆座位预约');
  console.log('========================================');
  console.log(`认证来源: ${authSourceLabel || (profileName ? `profile ${profileName}` : '默认账号')}`);
  console.log(`模式: ${mode}`);

  if (scope) {
    console.log(`范围: ${scope}`);
  } else if (reservationId) {
    console.log(`预约ID: ${reservationId}`);
  } else if (date) {
    console.log(`日期: ${date}`);
    if (slotLabels) {
      console.log(`时段: 全天 (${slotLabels})`);
    } else if (timeRange) {
      console.log(`时间: ${timeRange}`);
    }

    if (areaLabels) {
      console.log(`区域: ${areaLabels}`);
    }

    if (seatLabel) {
      console.log(`座位: ${seatLabel}`);
    } else if (autoAssign) {
      console.log('座位: 系统自动分配');
    }
  }

  console.log('========================================\n');
}

function printReservationSuccess(result) {
  console.log('\n🎉 预约成功！\n');
  console.log('========================================');
  console.log('预约详情');
  console.log('========================================');
  console.log(`预约人: ${result.resultValue.reservationUser}`);
  console.log(`手机号: ${result.resultValue.reservationMobile}`);
  console.log(`日期: ${result.resultValue.reservationDate}`);
  console.log(`座位: ${result.resultValue.reservationSeat}`);
  console.log(`状态: ${result.resultValue.currReservationStatus}`);
  console.log(`预约ID: ${result.resultValue.reservationId}`);
  console.log('========================================');
}

function handleReservationResult(result) {
  if (result.resultStatus.code === 0) {
    printReservationSuccess(result);
    return;
  }

  console.error('\n❌ 预约失败:', result.resultStatus.msg || result.resultStatus.message || JSON.stringify(result.resultStatus));
  console.error('完整响应:', JSON.stringify(result, null, 2));
  process.exit(1);
}

function printReservationList(result) {
  if (!result?.resultStatus) {
    console.error('❌ 查询结果格式异常');
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  if (result.resultStatus.code !== 0) {
    console.error('\n❌ 查询失败:', result.resultStatus.msg || result.resultStatus.message || JSON.stringify(result.resultStatus));
    console.error('完整响应:', JSON.stringify(result, null, 2));
    process.exit(1);
  }

  const groups = result.resultValue?.content || [];
  const total = result.resultValue?.totalElements ?? 0;

  console.log('\n📚 我的预约\n');
  console.log(`共 ${total} 条记录\n`);

  if (groups.length === 0) {
    console.log('当前没有预约记录。');
    return;
  }

  for (const group of groups) {
    console.log(`=== ${group.reservationDate} ===`);
    for (const item of group.reservationList || []) {
      console.log(`- [${item.reservationStatusName}] ${item.startTime}-${item.endTime} ${item.libraryName || ''}${item.seatNo ? ` ${item.seatNo}` : ''}`);
      console.log(`  预约ID: ${item.reservationId}`);
      if (item.seatRowColumn) {
        console.log(`  座位: ${item.seatRowColumn}`);
      }
      if (item.areaId != null) {
        console.log(`  区域ID: ${item.areaId}`);
      }
      console.log(`  可取消: ${item.flgCancel === 1 ? '是' : '否'}`);
    }
    console.log('');
  }
}

function handleSimpleResult(result, successMessage) {
  if (!result?.resultStatus) {
    console.error('❌ 返回结果格式异常');
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  if (result.resultStatus.code !== 0) {
    console.error('\n❌ 操作失败:', result.resultStatus.msg || result.resultStatus.message || JSON.stringify(result.resultStatus));
    console.error('完整响应:', JSON.stringify(result, null, 2));
    process.exit(1);
  }

  console.log(`\n🎉 ${successMessage}\n`);
  console.log('========================================');
  console.log(result.resultStatus.message || successMessage);
  console.log('========================================');
}

function printCommonAvailabilitySummary(date, areaResults) {
  const slots = getDailySlots(date);

  console.log('\n🔎 整天公共可用座位\n');
  console.log(`日期: ${date}`);
  console.log(`时段: ${slots.map((slot) => `${slot.label}(${slot.startTime}-${slot.endTime})`).join(' / ')}`);
  console.log('');

  for (const areaResult of areaResults) {
    console.log(`=== ${areaResult.areaName} ===`);
    console.log(`覆盖排号: ${areaResult.rows.length > 0 ? areaResult.rows.map((row) => `${row}排`).join('、') : '无'}`);
    console.log(`公共可用座位数: ${areaResult.commonSeats.length}`);

    if (areaResult.commonSeats.length === 0) {
      console.log('没有同时覆盖当天全部时段的座位。\n');
      continue;
    }

    console.log(`公共可用座位: ${areaResult.commonSeats.join('、')}\n`);
  }
}

function printDayBookingSummary(title, date, results) {
  const successCount = results.filter((item) => item.success).length;
  const failCount = results.length - successCount;

  console.log(`\n📅 ${title}\n`);
  console.log(`日期: ${date}`);
  console.log(`成功 ${successCount} 段，失败 ${failCount} 段\n`);

  for (const item of results) {
    const timeRange = `${item.slot.label} (${item.slot.startTime}-${item.slot.endTime})`;
    if (item.success) {
      const detail = item.result.resultValue;
      console.log(`- ✅ ${timeRange}`);
      console.log(`  座位: ${detail.reservationSeat}`);
      console.log(`  预约ID: ${detail.reservationId}`);
      console.log(`  状态: ${detail.currReservationStatus}`);
    } else {
      console.log(`- ❌ ${timeRange}`);
      console.log(`  原因: ${item.message}`);
    }
  }
}

module.exports = {
  printUsage,
  printModeHeader,
  handleReservationResult,
  printReservationList,
  handleSimpleResult,
  printCommonAvailabilitySummary,
  printDayBookingSummary
};
