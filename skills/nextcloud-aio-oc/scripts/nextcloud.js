#!/usr/bin/env node
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
  return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// node_modules/@babel/runtime/helpers/interopRequireDefault.js
var require_interopRequireDefault = __commonJS({
  "node_modules/@babel/runtime/helpers/interopRequireDefault.js"(exports2, module) {
    function _interopRequireDefault(e) {
      return e && e.__esModule ? e : {
        "default": e
      };
    }
    module.exports = _interopRequireDefault, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/typeof.js
var require_typeof = __commonJS({
  "node_modules/@babel/runtime/helpers/typeof.js"(exports2, module) {
    function _typeof(o) {
      "@babel/helpers - typeof";
      return module.exports = _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(o2) {
        return typeof o2;
      } : function(o2) {
        return o2 && "function" == typeof Symbol && o2.constructor === Symbol && o2 !== Symbol.prototype ? "symbol" : typeof o2;
      }, module.exports.__esModule = true, module.exports["default"] = module.exports, _typeof(o);
    }
    module.exports = _typeof, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/date-fns/_lib/toInteger/index.js
var require_toInteger = __commonJS({
  "node_modules/date-fns/_lib/toInteger/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = toInteger;
    function toInteger(dirtyNumber) {
      if (dirtyNumber === null || dirtyNumber === true || dirtyNumber === false) {
        return NaN;
      }
      var number = Number(dirtyNumber);
      if (isNaN(number)) {
        return number;
      }
      return number < 0 ? Math.ceil(number) : Math.floor(number);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/requiredArgs/index.js
var require_requiredArgs = __commonJS({
  "node_modules/date-fns/_lib/requiredArgs/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = requiredArgs;
    function requiredArgs(required, args) {
      if (args.length < required) {
        throw new TypeError(required + " argument" + (required > 1 ? "s" : "") + " required, but only " + args.length + " present");
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/toDate/index.js
var require_toDate = __commonJS({
  "node_modules/date-fns/toDate/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = toDate;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_requiredArgs());
    function toDate(argument) {
      (0, _index.default)(1, arguments);
      var argStr = Object.prototype.toString.call(argument);
      if (argument instanceof Date || (0, _typeof2.default)(argument) === "object" && argStr === "[object Date]") {
        return new Date(argument.getTime());
      } else if (typeof argument === "number" || argStr === "[object Number]") {
        return new Date(argument);
      } else {
        if ((typeof argument === "string" || argStr === "[object String]") && typeof console !== "undefined") {
          console.warn("Starting with v2.0.0-beta.1 date-fns doesn't accept strings as date arguments. Please use `parseISO` to parse strings. See: https://github.com/date-fns/date-fns/blob/master/docs/upgradeGuide.md#string-arguments");
          console.warn(new Error().stack);
        }
        return /* @__PURE__ */ new Date(NaN);
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addDays/index.js
var require_addDays = __commonJS({
  "node_modules/date-fns/addDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addDays2;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addDays2(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var amount = (0, _index.default)(dirtyAmount);
      if (isNaN(amount)) {
        return /* @__PURE__ */ new Date(NaN);
      }
      if (!amount) {
        return date;
      }
      date.setDate(date.getDate() + amount);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addMonths/index.js
var require_addMonths = __commonJS({
  "node_modules/date-fns/addMonths/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addMonths;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addMonths(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var amount = (0, _index.default)(dirtyAmount);
      if (isNaN(amount)) {
        return /* @__PURE__ */ new Date(NaN);
      }
      if (!amount) {
        return date;
      }
      var dayOfMonth = date.getDate();
      var endOfDesiredMonth = new Date(date.getTime());
      endOfDesiredMonth.setMonth(date.getMonth() + amount + 1, 0);
      var daysInMonth = endOfDesiredMonth.getDate();
      if (dayOfMonth >= daysInMonth) {
        return endOfDesiredMonth;
      } else {
        date.setFullYear(endOfDesiredMonth.getFullYear(), endOfDesiredMonth.getMonth(), dayOfMonth);
        return date;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/add/index.js
var require_add = __commonJS({
  "node_modules/date-fns/add/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = add;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_addDays());
    var _index2 = _interopRequireDefault(require_addMonths());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var _index5 = _interopRequireDefault(require_toInteger());
    function add(dirtyDate, duration) {
      (0, _index4.default)(2, arguments);
      if (!duration || (0, _typeof2.default)(duration) !== "object") return /* @__PURE__ */ new Date(NaN);
      var years = duration.years ? (0, _index5.default)(duration.years) : 0;
      var months = duration.months ? (0, _index5.default)(duration.months) : 0;
      var weeks = duration.weeks ? (0, _index5.default)(duration.weeks) : 0;
      var days = duration.days ? (0, _index5.default)(duration.days) : 0;
      var hours = duration.hours ? (0, _index5.default)(duration.hours) : 0;
      var minutes = duration.minutes ? (0, _index5.default)(duration.minutes) : 0;
      var seconds = duration.seconds ? (0, _index5.default)(duration.seconds) : 0;
      var date = (0, _index3.default)(dirtyDate);
      var dateWithMonths = months || years ? (0, _index2.default)(date, months + years * 12) : date;
      var dateWithDays = days || weeks ? (0, _index.default)(dateWithMonths, days + weeks * 7) : dateWithMonths;
      var minutesToAdd = minutes + hours * 60;
      var secondsToAdd = seconds + minutesToAdd * 60;
      var msToAdd = secondsToAdd * 1e3;
      var finalDate = new Date(dateWithDays.getTime() + msToAdd);
      return finalDate;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isWeekend/index.js
var require_isWeekend = __commonJS({
  "node_modules/date-fns/isWeekend/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isWeekend;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isWeekend(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var day = date.getDay();
      return day === 0 || day === 6;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSunday/index.js
var require_isSunday = __commonJS({
  "node_modules/date-fns/isSunday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSunday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSunday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDay() === 0;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSaturday/index.js
var require_isSaturday = __commonJS({
  "node_modules/date-fns/isSaturday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSaturday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSaturday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDay() === 6;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addBusinessDays/index.js
var require_addBusinessDays = __commonJS({
  "node_modules/date-fns/addBusinessDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addBusinessDays;
    var _index = _interopRequireDefault(require_isWeekend());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var _index5 = _interopRequireDefault(require_isSunday());
    var _index6 = _interopRequireDefault(require_isSaturday());
    function addBusinessDays(dirtyDate, dirtyAmount) {
      (0, _index4.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var startedOnWeekend = (0, _index.default)(date);
      var amount = (0, _index3.default)(dirtyAmount);
      if (isNaN(amount)) return /* @__PURE__ */ new Date(NaN);
      var hours = date.getHours();
      var sign = amount < 0 ? -1 : 1;
      var fullWeeks = (0, _index3.default)(amount / 5);
      date.setDate(date.getDate() + fullWeeks * 7);
      var restDays = Math.abs(amount % 5);
      while (restDays > 0) {
        date.setDate(date.getDate() + sign);
        if (!(0, _index.default)(date)) restDays -= 1;
      }
      if (startedOnWeekend && (0, _index.default)(date) && amount !== 0) {
        if ((0, _index6.default)(date)) date.setDate(date.getDate() + (sign < 0 ? 2 : -1));
        if ((0, _index5.default)(date)) date.setDate(date.getDate() + (sign < 0 ? 1 : -2));
      }
      date.setHours(hours);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addMilliseconds/index.js
var require_addMilliseconds = __commonJS({
  "node_modules/date-fns/addMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addMilliseconds;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addMilliseconds(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var timestamp = (0, _index2.default)(dirtyDate).getTime();
      var amount = (0, _index.default)(dirtyAmount);
      return new Date(timestamp + amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addHours/index.js
var require_addHours = __commonJS({
  "node_modules/date-fns/addHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addHours;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addMilliseconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_HOUR = 36e5;
    function addHours(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, amount * MILLISECONDS_IN_HOUR);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/defaultOptions/index.js
var require_defaultOptions = __commonJS({
  "node_modules/date-fns/_lib/defaultOptions/index.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.getDefaultOptions = getDefaultOptions;
    exports2.setDefaultOptions = setDefaultOptions;
    var defaultOptions3 = {};
    function getDefaultOptions() {
      return defaultOptions3;
    }
    function setDefaultOptions(newOptions) {
      defaultOptions3 = newOptions;
    }
  }
});

// node_modules/date-fns/startOfWeek/index.js
var require_startOfWeek = __commonJS({
  "node_modules/date-fns/startOfWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_toInteger());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var _index4 = require_defaultOptions();
    function startOfWeek(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index3.default)(1, arguments);
      var defaultOptions3 = (0, _index4.getDefaultOptions)();
      var weekStartsOn = (0, _index2.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      var date = (0, _index.default)(dirtyDate);
      var day = date.getDay();
      var diff = (day < weekStartsOn ? 7 : 0) + day - weekStartsOn;
      date.setDate(date.getDate() - diff);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfISOWeek/index.js
var require_startOfISOWeek = __commonJS({
  "node_modules/date-fns/startOfISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfISOWeek;
    var _index = _interopRequireDefault(require_startOfWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfISOWeek(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, {
        weekStartsOn: 1
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getISOWeekYear/index.js
var require_getISOWeekYear = __commonJS({
  "node_modules/date-fns/getISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getISOWeekYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_startOfISOWeek());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function getISOWeekYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      var fourthOfJanuaryOfNextYear = /* @__PURE__ */ new Date(0);
      fourthOfJanuaryOfNextYear.setFullYear(year + 1, 0, 4);
      fourthOfJanuaryOfNextYear.setHours(0, 0, 0, 0);
      var startOfNextYear = (0, _index2.default)(fourthOfJanuaryOfNextYear);
      var fourthOfJanuaryOfThisYear = /* @__PURE__ */ new Date(0);
      fourthOfJanuaryOfThisYear.setFullYear(year, 0, 4);
      fourthOfJanuaryOfThisYear.setHours(0, 0, 0, 0);
      var startOfThisYear = (0, _index2.default)(fourthOfJanuaryOfThisYear);
      if (date.getTime() >= startOfNextYear.getTime()) {
        return year + 1;
      } else if (date.getTime() >= startOfThisYear.getTime()) {
        return year;
      } else {
        return year - 1;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfISOWeekYear/index.js
var require_startOfISOWeekYear = __commonJS({
  "node_modules/date-fns/startOfISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfISOWeekYear;
    var _index = _interopRequireDefault(require_getISOWeekYear());
    var _index2 = _interopRequireDefault(require_startOfISOWeek());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function startOfISOWeekYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var year = (0, _index.default)(dirtyDate);
      var fourthOfJanuary = /* @__PURE__ */ new Date(0);
      fourthOfJanuary.setFullYear(year, 0, 4);
      fourthOfJanuary.setHours(0, 0, 0, 0);
      var date = (0, _index2.default)(fourthOfJanuary);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/getTimezoneOffsetInMilliseconds/index.js
var require_getTimezoneOffsetInMilliseconds = __commonJS({
  "node_modules/date-fns/_lib/getTimezoneOffsetInMilliseconds/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getTimezoneOffsetInMilliseconds;
    function getTimezoneOffsetInMilliseconds(date) {
      var utcDate = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), date.getMinutes(), date.getSeconds(), date.getMilliseconds()));
      utcDate.setUTCFullYear(date.getFullYear());
      return date.getTime() - utcDate.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfDay/index.js
var require_startOfDay = __commonJS({
  "node_modules/date-fns/startOfDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfDay;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfDay(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarDays/index.js
var require_differenceInCalendarDays = __commonJS({
  "node_modules/date-fns/differenceInCalendarDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarDays;
    var _index = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index2 = _interopRequireDefault(require_startOfDay());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_DAY = 864e5;
    function differenceInCalendarDays(dirtyDateLeft, dirtyDateRight) {
      (0, _index3.default)(2, arguments);
      var startOfDayLeft = (0, _index2.default)(dirtyDateLeft);
      var startOfDayRight = (0, _index2.default)(dirtyDateRight);
      var timestampLeft = startOfDayLeft.getTime() - (0, _index.default)(startOfDayLeft);
      var timestampRight = startOfDayRight.getTime() - (0, _index.default)(startOfDayRight);
      return Math.round((timestampLeft - timestampRight) / MILLISECONDS_IN_DAY);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setISOWeekYear/index.js
var require_setISOWeekYear = __commonJS({
  "node_modules/date-fns/setISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setISOWeekYear;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_startOfISOWeekYear());
    var _index4 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index5 = _interopRequireDefault(require_requiredArgs());
    function setISOWeekYear(dirtyDate, dirtyISOWeekYear) {
      (0, _index5.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var isoWeekYear = (0, _index.default)(dirtyISOWeekYear);
      var diff = (0, _index4.default)(date, (0, _index3.default)(date));
      var fourthOfJanuary = /* @__PURE__ */ new Date(0);
      fourthOfJanuary.setFullYear(isoWeekYear, 0, 4);
      fourthOfJanuary.setHours(0, 0, 0, 0);
      date = (0, _index3.default)(fourthOfJanuary);
      date.setDate(date.getDate() + diff);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addISOWeekYears/index.js
var require_addISOWeekYears = __commonJS({
  "node_modules/date-fns/addISOWeekYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addISOWeekYears;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_getISOWeekYear());
    var _index3 = _interopRequireDefault(require_setISOWeekYear());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function addISOWeekYears(dirtyDate, dirtyAmount) {
      (0, _index4.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index3.default)(dirtyDate, (0, _index2.default)(dirtyDate) + amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addMinutes/index.js
var require_addMinutes = __commonJS({
  "node_modules/date-fns/addMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addMinutes;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addMilliseconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_MINUTE = 6e4;
    function addMinutes(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, amount * MILLISECONDS_IN_MINUTE);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addQuarters/index.js
var require_addQuarters = __commonJS({
  "node_modules/date-fns/addQuarters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addQuarters;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addMonths());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addQuarters(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      var months = amount * 3;
      return (0, _index2.default)(dirtyDate, months);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addSeconds/index.js
var require_addSeconds = __commonJS({
  "node_modules/date-fns/addSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addSeconds;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addMilliseconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addSeconds(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, amount * 1e3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addWeeks/index.js
var require_addWeeks = __commonJS({
  "node_modules/date-fns/addWeeks/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addWeeks;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addDays());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addWeeks(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      var days = amount * 7;
      return (0, _index2.default)(dirtyDate, days);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/addYears/index.js
var require_addYears = __commonJS({
  "node_modules/date-fns/addYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addYears;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addMonths());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function addYears(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, amount * 12);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/areIntervalsOverlapping/index.js
var require_areIntervalsOverlapping = __commonJS({
  "node_modules/date-fns/areIntervalsOverlapping/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = areIntervalsOverlapping;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function areIntervalsOverlapping(intervalLeft, intervalRight, options) {
      (0, _index2.default)(2, arguments);
      var leftStartTime = (0, _index.default)(intervalLeft === null || intervalLeft === void 0 ? void 0 : intervalLeft.start).getTime();
      var leftEndTime = (0, _index.default)(intervalLeft === null || intervalLeft === void 0 ? void 0 : intervalLeft.end).getTime();
      var rightStartTime = (0, _index.default)(intervalRight === null || intervalRight === void 0 ? void 0 : intervalRight.start).getTime();
      var rightEndTime = (0, _index.default)(intervalRight === null || intervalRight === void 0 ? void 0 : intervalRight.end).getTime();
      if (!(leftStartTime <= leftEndTime && rightStartTime <= rightEndTime)) {
        throw new RangeError("Invalid interval");
      }
      if (options !== null && options !== void 0 && options.inclusive) {
        return leftStartTime <= rightEndTime && rightStartTime <= leftEndTime;
      }
      return leftStartTime < rightEndTime && rightStartTime < leftEndTime;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/max/index.js
var require_max = __commonJS({
  "node_modules/date-fns/max/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = max;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function max(dirtyDatesArray) {
      (0, _index2.default)(1, arguments);
      var datesArray;
      if (dirtyDatesArray && typeof dirtyDatesArray.forEach === "function") {
        datesArray = dirtyDatesArray;
      } else if ((0, _typeof2.default)(dirtyDatesArray) === "object" && dirtyDatesArray !== null) {
        datesArray = Array.prototype.slice.call(dirtyDatesArray);
      } else {
        return /* @__PURE__ */ new Date(NaN);
      }
      var result;
      datesArray.forEach(function(dirtyDate) {
        var currentDate = (0, _index.default)(dirtyDate);
        if (result === void 0 || result < currentDate || isNaN(Number(currentDate))) {
          result = currentDate;
        }
      });
      return result || /* @__PURE__ */ new Date(NaN);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/min/index.js
var require_min = __commonJS({
  "node_modules/date-fns/min/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = min;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function min(dirtyDatesArray) {
      (0, _index2.default)(1, arguments);
      var datesArray;
      if (dirtyDatesArray && typeof dirtyDatesArray.forEach === "function") {
        datesArray = dirtyDatesArray;
      } else if ((0, _typeof2.default)(dirtyDatesArray) === "object" && dirtyDatesArray !== null) {
        datesArray = Array.prototype.slice.call(dirtyDatesArray);
      } else {
        return /* @__PURE__ */ new Date(NaN);
      }
      var result;
      datesArray.forEach(function(dirtyDate) {
        var currentDate = (0, _index.default)(dirtyDate);
        if (result === void 0 || result > currentDate || isNaN(currentDate.getDate())) {
          result = currentDate;
        }
      });
      return result || /* @__PURE__ */ new Date(NaN);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/clamp/index.js
var require_clamp = __commonJS({
  "node_modules/date-fns/clamp/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = clamp;
    var _index = _interopRequireDefault(require_max());
    var _index2 = _interopRequireDefault(require_min());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function clamp(date, _ref) {
      var start = _ref.start, end = _ref.end;
      (0, _index3.default)(2, arguments);
      return (0, _index2.default)([(0, _index.default)([date, start]), end]);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/closestIndexTo/index.js
var require_closestIndexTo = __commonJS({
  "node_modules/date-fns/closestIndexTo/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = closestIndexTo;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function closestIndexTo(dirtyDateToCompare, dirtyDatesArray) {
      (0, _index2.default)(2, arguments);
      var dateToCompare = (0, _index.default)(dirtyDateToCompare);
      if (isNaN(Number(dateToCompare))) return NaN;
      var timeToCompare = dateToCompare.getTime();
      var datesArray;
      if (dirtyDatesArray == null) {
        datesArray = [];
      } else if (typeof dirtyDatesArray.forEach === "function") {
        datesArray = dirtyDatesArray;
      } else {
        datesArray = Array.prototype.slice.call(dirtyDatesArray);
      }
      var result;
      var minDistance;
      datesArray.forEach(function(dirtyDate, index) {
        var currentDate = (0, _index.default)(dirtyDate);
        if (isNaN(Number(currentDate))) {
          result = NaN;
          minDistance = NaN;
          return;
        }
        var distance = Math.abs(timeToCompare - currentDate.getTime());
        if (result == null || distance < Number(minDistance)) {
          result = index;
          minDistance = distance;
        }
      });
      return result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/closestTo/index.js
var require_closestTo = __commonJS({
  "node_modules/date-fns/closestTo/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = closestTo;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function closestTo(dirtyDateToCompare, dirtyDatesArray) {
      (0, _index2.default)(2, arguments);
      var dateToCompare = (0, _index.default)(dirtyDateToCompare);
      if (isNaN(Number(dateToCompare))) return /* @__PURE__ */ new Date(NaN);
      var timeToCompare = dateToCompare.getTime();
      var datesArray;
      if (dirtyDatesArray == null) {
        datesArray = [];
      } else if (typeof dirtyDatesArray.forEach === "function") {
        datesArray = dirtyDatesArray;
      } else {
        datesArray = Array.prototype.slice.call(dirtyDatesArray);
      }
      var result;
      var minDistance;
      datesArray.forEach(function(dirtyDate) {
        var currentDate = (0, _index.default)(dirtyDate);
        if (isNaN(Number(currentDate))) {
          result = /* @__PURE__ */ new Date(NaN);
          minDistance = NaN;
          return;
        }
        var distance = Math.abs(timeToCompare - currentDate.getTime());
        if (result == null || distance < Number(minDistance)) {
          result = currentDate;
          minDistance = distance;
        }
      });
      return result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/compareAsc/index.js
var require_compareAsc = __commonJS({
  "node_modules/date-fns/compareAsc/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = compareAsc;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function compareAsc(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var diff = dateLeft.getTime() - dateRight.getTime();
      if (diff < 0) {
        return -1;
      } else if (diff > 0) {
        return 1;
      } else {
        return diff;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/compareDesc/index.js
var require_compareDesc = __commonJS({
  "node_modules/date-fns/compareDesc/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = compareDesc;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function compareDesc(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var diff = dateLeft.getTime() - dateRight.getTime();
      if (diff > 0) {
        return -1;
      } else if (diff < 0) {
        return 1;
      } else {
        return diff;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/constants/index.js
var require_constants = __commonJS({
  "node_modules/date-fns/constants/index.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.secondsInYear = exports2.secondsInWeek = exports2.secondsInQuarter = exports2.secondsInMonth = exports2.secondsInMinute = exports2.secondsInHour = exports2.secondsInDay = exports2.quartersInYear = exports2.monthsInYear = exports2.monthsInQuarter = exports2.minutesInHour = exports2.minTime = exports2.millisecondsInSecond = exports2.millisecondsInMinute = exports2.millisecondsInHour = exports2.maxTime = exports2.daysInYear = exports2.daysInWeek = void 0;
    var daysInWeek = 7;
    exports2.daysInWeek = daysInWeek;
    var daysInYear = 365.2425;
    exports2.daysInYear = daysInYear;
    var maxTime = Math.pow(10, 8) * 24 * 60 * 60 * 1e3;
    exports2.maxTime = maxTime;
    var millisecondsInMinute = 6e4;
    exports2.millisecondsInMinute = millisecondsInMinute;
    var millisecondsInHour = 36e5;
    exports2.millisecondsInHour = millisecondsInHour;
    var millisecondsInSecond = 1e3;
    exports2.millisecondsInSecond = millisecondsInSecond;
    var minTime = -maxTime;
    exports2.minTime = minTime;
    var minutesInHour = 60;
    exports2.minutesInHour = minutesInHour;
    var monthsInQuarter = 3;
    exports2.monthsInQuarter = monthsInQuarter;
    var monthsInYear = 12;
    exports2.monthsInYear = monthsInYear;
    var quartersInYear = 4;
    exports2.quartersInYear = quartersInYear;
    var secondsInHour = 3600;
    exports2.secondsInHour = secondsInHour;
    var secondsInMinute = 60;
    exports2.secondsInMinute = secondsInMinute;
    var secondsInDay = secondsInHour * 24;
    exports2.secondsInDay = secondsInDay;
    var secondsInWeek = secondsInDay * 7;
    exports2.secondsInWeek = secondsInWeek;
    var secondsInYear = secondsInDay * daysInYear;
    exports2.secondsInYear = secondsInYear;
    var secondsInMonth = secondsInYear / 12;
    exports2.secondsInMonth = secondsInMonth;
    var secondsInQuarter = secondsInMonth * 3;
    exports2.secondsInQuarter = secondsInQuarter;
  }
});

// node_modules/date-fns/daysToWeeks/index.js
var require_daysToWeeks = __commonJS({
  "node_modules/date-fns/daysToWeeks/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = daysToWeeks;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function daysToWeeks(days) {
      (0, _index.default)(1, arguments);
      var weeks = days / _index2.daysInWeek;
      return Math.floor(weeks);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameDay/index.js
var require_isSameDay = __commonJS({
  "node_modules/date-fns/isSameDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameDay;
    var _index = _interopRequireDefault(require_startOfDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameDay(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfDay = (0, _index.default)(dirtyDateLeft);
      var dateRightStartOfDay = (0, _index.default)(dirtyDateRight);
      return dateLeftStartOfDay.getTime() === dateRightStartOfDay.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isDate/index.js
var require_isDate = __commonJS({
  "node_modules/date-fns/isDate/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isDate;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_requiredArgs());
    function isDate(value) {
      (0, _index.default)(1, arguments);
      return value instanceof Date || (0, _typeof2.default)(value) === "object" && Object.prototype.toString.call(value) === "[object Date]";
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isValid/index.js
var require_isValid = __commonJS({
  "node_modules/date-fns/isValid/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isValid;
    var _index = _interopRequireDefault(require_isDate());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function isValid(dirtyDate) {
      (0, _index3.default)(1, arguments);
      if (!(0, _index.default)(dirtyDate) && typeof dirtyDate !== "number") {
        return false;
      }
      var date = (0, _index2.default)(dirtyDate);
      return !isNaN(Number(date));
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInBusinessDays/index.js
var require_differenceInBusinessDays = __commonJS({
  "node_modules/date-fns/differenceInBusinessDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInBusinessDays;
    var _index = _interopRequireDefault(require_addDays());
    var _index2 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index3 = _interopRequireDefault(require_isSameDay());
    var _index4 = _interopRequireDefault(require_isValid());
    var _index5 = _interopRequireDefault(require_isWeekend());
    var _index6 = _interopRequireDefault(require_toDate());
    var _index7 = _interopRequireDefault(require_requiredArgs());
    var _index8 = _interopRequireDefault(require_toInteger());
    function differenceInBusinessDays(dirtyDateLeft, dirtyDateRight) {
      (0, _index7.default)(2, arguments);
      var dateLeft = (0, _index6.default)(dirtyDateLeft);
      var dateRight = (0, _index6.default)(dirtyDateRight);
      if (!(0, _index4.default)(dateLeft) || !(0, _index4.default)(dateRight)) return NaN;
      var calendarDifference = (0, _index2.default)(dateLeft, dateRight);
      var sign = calendarDifference < 0 ? -1 : 1;
      var weeks = (0, _index8.default)(calendarDifference / 7);
      var result = weeks * 5;
      dateRight = (0, _index.default)(dateRight, weeks * 7);
      while (!(0, _index3.default)(dateLeft, dateRight)) {
        result += (0, _index5.default)(dateRight) ? 0 : sign;
        dateRight = (0, _index.default)(dateRight, sign);
      }
      return result === 0 ? 0 : result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarISOWeekYears/index.js
var require_differenceInCalendarISOWeekYears = __commonJS({
  "node_modules/date-fns/differenceInCalendarISOWeekYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarISOWeekYears;
    var _index = _interopRequireDefault(require_getISOWeekYear());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function differenceInCalendarISOWeekYears(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      return (0, _index.default)(dirtyDateLeft) - (0, _index.default)(dirtyDateRight);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarISOWeeks/index.js
var require_differenceInCalendarISOWeeks = __commonJS({
  "node_modules/date-fns/differenceInCalendarISOWeeks/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarISOWeeks;
    var _index = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index2 = _interopRequireDefault(require_startOfISOWeek());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function differenceInCalendarISOWeeks(dirtyDateLeft, dirtyDateRight) {
      (0, _index3.default)(2, arguments);
      var startOfISOWeekLeft = (0, _index2.default)(dirtyDateLeft);
      var startOfISOWeekRight = (0, _index2.default)(dirtyDateRight);
      var timestampLeft = startOfISOWeekLeft.getTime() - (0, _index.default)(startOfISOWeekLeft);
      var timestampRight = startOfISOWeekRight.getTime() - (0, _index.default)(startOfISOWeekRight);
      return Math.round((timestampLeft - timestampRight) / MILLISECONDS_IN_WEEK);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarMonths/index.js
var require_differenceInCalendarMonths = __commonJS({
  "node_modules/date-fns/differenceInCalendarMonths/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarMonths;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function differenceInCalendarMonths(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var yearDiff = dateLeft.getFullYear() - dateRight.getFullYear();
      var monthDiff = dateLeft.getMonth() - dateRight.getMonth();
      return yearDiff * 12 + monthDiff;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getQuarter/index.js
var require_getQuarter = __commonJS({
  "node_modules/date-fns/getQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getQuarter;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getQuarter(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var quarter = Math.floor(date.getMonth() / 3) + 1;
      return quarter;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarQuarters/index.js
var require_differenceInCalendarQuarters = __commonJS({
  "node_modules/date-fns/differenceInCalendarQuarters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarQuarters;
    var _index = _interopRequireDefault(require_getQuarter());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function differenceInCalendarQuarters(dirtyDateLeft, dirtyDateRight) {
      (0, _index3.default)(2, arguments);
      var dateLeft = (0, _index2.default)(dirtyDateLeft);
      var dateRight = (0, _index2.default)(dirtyDateRight);
      var yearDiff = dateLeft.getFullYear() - dateRight.getFullYear();
      var quarterDiff = (0, _index.default)(dateLeft) - (0, _index.default)(dateRight);
      return yearDiff * 4 + quarterDiff;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarWeeks/index.js
var require_differenceInCalendarWeeks = __commonJS({
  "node_modules/date-fns/differenceInCalendarWeeks/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarWeeks;
    var _index = _interopRequireDefault(require_startOfWeek());
    var _index2 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function differenceInCalendarWeeks(dirtyDateLeft, dirtyDateRight, options) {
      (0, _index3.default)(2, arguments);
      var startOfWeekLeft = (0, _index.default)(dirtyDateLeft, options);
      var startOfWeekRight = (0, _index.default)(dirtyDateRight, options);
      var timestampLeft = startOfWeekLeft.getTime() - (0, _index2.default)(startOfWeekLeft);
      var timestampRight = startOfWeekRight.getTime() - (0, _index2.default)(startOfWeekRight);
      return Math.round((timestampLeft - timestampRight) / MILLISECONDS_IN_WEEK);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInCalendarYears/index.js
var require_differenceInCalendarYears = __commonJS({
  "node_modules/date-fns/differenceInCalendarYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInCalendarYears;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function differenceInCalendarYears(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      return dateLeft.getFullYear() - dateRight.getFullYear();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInDays/index.js
var require_differenceInDays = __commonJS({
  "node_modules/date-fns/differenceInDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInDays;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function compareLocalAsc(dateLeft, dateRight) {
      var diff = dateLeft.getFullYear() - dateRight.getFullYear() || dateLeft.getMonth() - dateRight.getMonth() || dateLeft.getDate() - dateRight.getDate() || dateLeft.getHours() - dateRight.getHours() || dateLeft.getMinutes() - dateRight.getMinutes() || dateLeft.getSeconds() - dateRight.getSeconds() || dateLeft.getMilliseconds() - dateRight.getMilliseconds();
      if (diff < 0) {
        return -1;
      } else if (diff > 0) {
        return 1;
      } else {
        return diff;
      }
    }
    function differenceInDays(dirtyDateLeft, dirtyDateRight) {
      (0, _index3.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var sign = compareLocalAsc(dateLeft, dateRight);
      var difference = Math.abs((0, _index2.default)(dateLeft, dateRight));
      dateLeft.setDate(dateLeft.getDate() - sign * difference);
      var isLastDayNotFull = Number(compareLocalAsc(dateLeft, dateRight) === -sign);
      var result = sign * (difference - isLastDayNotFull);
      return result === 0 ? 0 : result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInMilliseconds/index.js
var require_differenceInMilliseconds = __commonJS({
  "node_modules/date-fns/differenceInMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInMilliseconds;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function differenceInMilliseconds(dateLeft, dateRight) {
      (0, _index2.default)(2, arguments);
      return (0, _index.default)(dateLeft).getTime() - (0, _index.default)(dateRight).getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/roundingMethods/index.js
var require_roundingMethods = __commonJS({
  "node_modules/date-fns/_lib/roundingMethods/index.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.getRoundingMethod = getRoundingMethod;
    var roundingMap = {
      ceil: Math.ceil,
      round: Math.round,
      floor: Math.floor,
      trunc: function trunc(value) {
        return value < 0 ? Math.ceil(value) : Math.floor(value);
      }
      // Math.trunc is not supported by IE
    };
    var defaultRoundingMethod = "trunc";
    function getRoundingMethod(method) {
      return method ? roundingMap[method] : roundingMap[defaultRoundingMethod];
    }
  }
});

// node_modules/date-fns/differenceInHours/index.js
var require_differenceInHours = __commonJS({
  "node_modules/date-fns/differenceInHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInHours;
    var _index = require_constants();
    var _index2 = _interopRequireDefault(require_differenceInMilliseconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var _index4 = require_roundingMethods();
    function differenceInHours(dateLeft, dateRight, options) {
      (0, _index3.default)(2, arguments);
      var diff = (0, _index2.default)(dateLeft, dateRight) / _index.millisecondsInHour;
      return (0, _index4.getRoundingMethod)(options === null || options === void 0 ? void 0 : options.roundingMethod)(diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subISOWeekYears/index.js
var require_subISOWeekYears = __commonJS({
  "node_modules/date-fns/subISOWeekYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subISOWeekYears;
    var _index = _interopRequireDefault(require_addISOWeekYears());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function subISOWeekYears(dirtyDate, dirtyAmount) {
      (0, _index2.default)(2, arguments);
      var amount = (0, _index3.default)(dirtyAmount);
      return (0, _index.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInISOWeekYears/index.js
var require_differenceInISOWeekYears = __commonJS({
  "node_modules/date-fns/differenceInISOWeekYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInISOWeekYears;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_differenceInCalendarISOWeekYears());
    var _index3 = _interopRequireDefault(require_compareAsc());
    var _index4 = _interopRequireDefault(require_subISOWeekYears());
    var _index5 = _interopRequireDefault(require_requiredArgs());
    function differenceInISOWeekYears(dirtyDateLeft, dirtyDateRight) {
      (0, _index5.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var sign = (0, _index3.default)(dateLeft, dateRight);
      var difference = Math.abs((0, _index2.default)(dateLeft, dateRight));
      dateLeft = (0, _index4.default)(dateLeft, sign * difference);
      var isLastISOWeekYearNotFull = Number((0, _index3.default)(dateLeft, dateRight) === -sign);
      var result = sign * (difference - isLastISOWeekYearNotFull);
      return result === 0 ? 0 : result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInMinutes/index.js
var require_differenceInMinutes = __commonJS({
  "node_modules/date-fns/differenceInMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInMinutes;
    var _index = require_constants();
    var _index2 = _interopRequireDefault(require_differenceInMilliseconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var _index4 = require_roundingMethods();
    function differenceInMinutes(dateLeft, dateRight, options) {
      (0, _index3.default)(2, arguments);
      var diff = (0, _index2.default)(dateLeft, dateRight) / _index.millisecondsInMinute;
      return (0, _index4.getRoundingMethod)(options === null || options === void 0 ? void 0 : options.roundingMethod)(diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfDay/index.js
var require_endOfDay = __commonJS({
  "node_modules/date-fns/endOfDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfDay;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfDay(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfMonth/index.js
var require_endOfMonth = __commonJS({
  "node_modules/date-fns/endOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var month = date.getMonth();
      date.setFullYear(date.getFullYear(), month + 1, 0);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isLastDayOfMonth/index.js
var require_isLastDayOfMonth = __commonJS({
  "node_modules/date-fns/isLastDayOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isLastDayOfMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_endOfDay());
    var _index3 = _interopRequireDefault(require_endOfMonth());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function isLastDayOfMonth(dirtyDate) {
      (0, _index4.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      return (0, _index2.default)(date).getTime() === (0, _index3.default)(date).getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInMonths/index.js
var require_differenceInMonths = __commonJS({
  "node_modules/date-fns/differenceInMonths/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInMonths;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_differenceInCalendarMonths());
    var _index3 = _interopRequireDefault(require_compareAsc());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var _index5 = _interopRequireDefault(require_isLastDayOfMonth());
    function differenceInMonths(dirtyDateLeft, dirtyDateRight) {
      (0, _index4.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var sign = (0, _index3.default)(dateLeft, dateRight);
      var difference = Math.abs((0, _index2.default)(dateLeft, dateRight));
      var result;
      if (difference < 1) {
        result = 0;
      } else {
        if (dateLeft.getMonth() === 1 && dateLeft.getDate() > 27) {
          dateLeft.setDate(30);
        }
        dateLeft.setMonth(dateLeft.getMonth() - sign * difference);
        var isLastMonthNotFull = (0, _index3.default)(dateLeft, dateRight) === -sign;
        if ((0, _index5.default)((0, _index.default)(dirtyDateLeft)) && difference === 1 && (0, _index3.default)(dirtyDateLeft, dateRight) === 1) {
          isLastMonthNotFull = false;
        }
        result = sign * (difference - Number(isLastMonthNotFull));
      }
      return result === 0 ? 0 : result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInQuarters/index.js
var require_differenceInQuarters = __commonJS({
  "node_modules/date-fns/differenceInQuarters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInQuarters;
    var _index = _interopRequireDefault(require_differenceInMonths());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = require_roundingMethods();
    function differenceInQuarters(dateLeft, dateRight, options) {
      (0, _index2.default)(2, arguments);
      var diff = (0, _index.default)(dateLeft, dateRight) / 3;
      return (0, _index3.getRoundingMethod)(options === null || options === void 0 ? void 0 : options.roundingMethod)(diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInSeconds/index.js
var require_differenceInSeconds = __commonJS({
  "node_modules/date-fns/differenceInSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInSeconds;
    var _index = _interopRequireDefault(require_differenceInMilliseconds());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = require_roundingMethods();
    function differenceInSeconds(dateLeft, dateRight, options) {
      (0, _index2.default)(2, arguments);
      var diff = (0, _index.default)(dateLeft, dateRight) / 1e3;
      return (0, _index3.getRoundingMethod)(options === null || options === void 0 ? void 0 : options.roundingMethod)(diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInWeeks/index.js
var require_differenceInWeeks = __commonJS({
  "node_modules/date-fns/differenceInWeeks/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInWeeks;
    var _index = _interopRequireDefault(require_differenceInDays());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = require_roundingMethods();
    function differenceInWeeks(dateLeft, dateRight, options) {
      (0, _index2.default)(2, arguments);
      var diff = (0, _index.default)(dateLeft, dateRight) / 7;
      return (0, _index3.getRoundingMethod)(options === null || options === void 0 ? void 0 : options.roundingMethod)(diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/differenceInYears/index.js
var require_differenceInYears = __commonJS({
  "node_modules/date-fns/differenceInYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = differenceInYears;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_differenceInCalendarYears());
    var _index3 = _interopRequireDefault(require_compareAsc());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function differenceInYears(dirtyDateLeft, dirtyDateRight) {
      (0, _index4.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      var sign = (0, _index3.default)(dateLeft, dateRight);
      var difference = Math.abs((0, _index2.default)(dateLeft, dateRight));
      dateLeft.setFullYear(1584);
      dateRight.setFullYear(1584);
      var isLastYearNotFull = (0, _index3.default)(dateLeft, dateRight) === -sign;
      var result = sign * (difference - Number(isLastYearNotFull));
      return result === 0 ? 0 : result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachDayOfInterval/index.js
var require_eachDayOfInterval = __commonJS({
  "node_modules/date-fns/eachDayOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachDayOfInterval;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function eachDayOfInterval(dirtyInterval, options) {
      var _options$step;
      (0, _index2.default)(1, arguments);
      var interval = dirtyInterval || {};
      var startDate = (0, _index.default)(interval.start);
      var endDate = (0, _index.default)(interval.end);
      var endTime = endDate.getTime();
      if (!(startDate.getTime() <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      var dates = [];
      var currentDate = startDate;
      currentDate.setHours(0, 0, 0, 0);
      var step = Number((_options$step = options === null || options === void 0 ? void 0 : options.step) !== null && _options$step !== void 0 ? _options$step : 1);
      if (step < 1 || isNaN(step)) throw new RangeError("`options.step` must be a number greater than 1");
      while (currentDate.getTime() <= endTime) {
        dates.push((0, _index.default)(currentDate));
        currentDate.setDate(currentDate.getDate() + step);
        currentDate.setHours(0, 0, 0, 0);
      }
      return dates;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachHourOfInterval/index.js
var require_eachHourOfInterval = __commonJS({
  "node_modules/date-fns/eachHourOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachHourOfInterval;
    var _index = _interopRequireDefault(require_addHours());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function eachHourOfInterval(dirtyInterval, options) {
      var _options$step;
      (0, _index3.default)(1, arguments);
      var interval = dirtyInterval || {};
      var startDate = (0, _index2.default)(interval.start);
      var endDate = (0, _index2.default)(interval.end);
      var startTime = startDate.getTime();
      var endTime = endDate.getTime();
      if (!(startTime <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      var dates = [];
      var currentDate = startDate;
      currentDate.setMinutes(0, 0, 0);
      var step = Number((_options$step = options === null || options === void 0 ? void 0 : options.step) !== null && _options$step !== void 0 ? _options$step : 1);
      if (step < 1 || isNaN(step)) throw new RangeError("`options.step` must be a number greater than 1");
      while (currentDate.getTime() <= endTime) {
        dates.push((0, _index2.default)(currentDate));
        currentDate = (0, _index.default)(currentDate, step);
      }
      return dates;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfMinute/index.js
var require_startOfMinute = __commonJS({
  "node_modules/date-fns/startOfMinute/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfMinute;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfMinute(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setSeconds(0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachMinuteOfInterval/index.js
var require_eachMinuteOfInterval = __commonJS({
  "node_modules/date-fns/eachMinuteOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachMinuteOfInterval;
    var _index = _interopRequireDefault(require_addMinutes());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_startOfMinute());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function eachMinuteOfInterval(interval, options) {
      var _options$step;
      (0, _index4.default)(1, arguments);
      var startDate = (0, _index3.default)((0, _index2.default)(interval.start));
      var endDate = (0, _index2.default)(interval.end);
      var startTime = startDate.getTime();
      var endTime = endDate.getTime();
      if (startTime >= endTime) {
        throw new RangeError("Invalid interval");
      }
      var dates = [];
      var currentDate = startDate;
      var step = Number((_options$step = options === null || options === void 0 ? void 0 : options.step) !== null && _options$step !== void 0 ? _options$step : 1);
      if (step < 1 || isNaN(step)) throw new RangeError("`options.step` must be a number equal to or greater than 1");
      while (currentDate.getTime() <= endTime) {
        dates.push((0, _index2.default)(currentDate));
        currentDate = (0, _index.default)(currentDate, step);
      }
      return dates;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachMonthOfInterval/index.js
var require_eachMonthOfInterval = __commonJS({
  "node_modules/date-fns/eachMonthOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachMonthOfInterval;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function eachMonthOfInterval(dirtyInterval) {
      (0, _index2.default)(1, arguments);
      var interval = dirtyInterval || {};
      var startDate = (0, _index.default)(interval.start);
      var endDate = (0, _index.default)(interval.end);
      var endTime = endDate.getTime();
      var dates = [];
      if (!(startDate.getTime() <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      var currentDate = startDate;
      currentDate.setHours(0, 0, 0, 0);
      currentDate.setDate(1);
      while (currentDate.getTime() <= endTime) {
        dates.push((0, _index.default)(currentDate));
        currentDate.setMonth(currentDate.getMonth() + 1);
      }
      return dates;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfQuarter/index.js
var require_startOfQuarter = __commonJS({
  "node_modules/date-fns/startOfQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfQuarter;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfQuarter(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var currentMonth = date.getMonth();
      var month = currentMonth - currentMonth % 3;
      date.setMonth(month, 1);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachQuarterOfInterval/index.js
var require_eachQuarterOfInterval = __commonJS({
  "node_modules/date-fns/eachQuarterOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachQuarterOfInterval;
    var _index = _interopRequireDefault(require_addQuarters());
    var _index2 = _interopRequireDefault(require_startOfQuarter());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function eachQuarterOfInterval(dirtyInterval) {
      (0, _index4.default)(1, arguments);
      var interval = dirtyInterval || {};
      var startDate = (0, _index3.default)(interval.start);
      var endDate = (0, _index3.default)(interval.end);
      var endTime = endDate.getTime();
      if (!(startDate.getTime() <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      var startDateQuarter = (0, _index2.default)(startDate);
      var endDateQuarter = (0, _index2.default)(endDate);
      endTime = endDateQuarter.getTime();
      var quarters = [];
      var currentQuarter = startDateQuarter;
      while (currentQuarter.getTime() <= endTime) {
        quarters.push((0, _index3.default)(currentQuarter));
        currentQuarter = (0, _index.default)(currentQuarter, 1);
      }
      return quarters;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachWeekOfInterval/index.js
var require_eachWeekOfInterval = __commonJS({
  "node_modules/date-fns/eachWeekOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachWeekOfInterval;
    var _index = _interopRequireDefault(require_addWeeks());
    var _index2 = _interopRequireDefault(require_startOfWeek());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function eachWeekOfInterval(dirtyInterval, options) {
      (0, _index4.default)(1, arguments);
      var interval = dirtyInterval || {};
      var startDate = (0, _index3.default)(interval.start);
      var endDate = (0, _index3.default)(interval.end);
      var endTime = endDate.getTime();
      if (!(startDate.getTime() <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      var startDateWeek = (0, _index2.default)(startDate, options);
      var endDateWeek = (0, _index2.default)(endDate, options);
      startDateWeek.setHours(15);
      endDateWeek.setHours(15);
      endTime = endDateWeek.getTime();
      var weeks = [];
      var currentWeek = startDateWeek;
      while (currentWeek.getTime() <= endTime) {
        currentWeek.setHours(0);
        weeks.push((0, _index3.default)(currentWeek));
        currentWeek = (0, _index.default)(currentWeek, 1);
        currentWeek.setHours(15);
      }
      return weeks;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachWeekendOfInterval/index.js
var require_eachWeekendOfInterval = __commonJS({
  "node_modules/date-fns/eachWeekendOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachWeekendOfInterval;
    var _index = _interopRequireDefault(require_eachDayOfInterval());
    var _index2 = _interopRequireDefault(require_isSunday());
    var _index3 = _interopRequireDefault(require_isWeekend());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function eachWeekendOfInterval(interval) {
      (0, _index4.default)(1, arguments);
      var dateInterval = (0, _index.default)(interval);
      var weekends = [];
      var index = 0;
      while (index < dateInterval.length) {
        var date = dateInterval[index++];
        if ((0, _index3.default)(date)) {
          weekends.push(date);
          if ((0, _index2.default)(date)) index = index + 5;
        }
      }
      return weekends;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfMonth/index.js
var require_startOfMonth = __commonJS({
  "node_modules/date-fns/startOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setDate(1);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachWeekendOfMonth/index.js
var require_eachWeekendOfMonth = __commonJS({
  "node_modules/date-fns/eachWeekendOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachWeekendOfMonth;
    var _index = _interopRequireDefault(require_eachWeekendOfInterval());
    var _index2 = _interopRequireDefault(require_startOfMonth());
    var _index3 = _interopRequireDefault(require_endOfMonth());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function eachWeekendOfMonth(dirtyDate) {
      (0, _index4.default)(1, arguments);
      var startDate = (0, _index2.default)(dirtyDate);
      if (isNaN(startDate.getTime())) throw new RangeError("The passed date is invalid");
      var endDate = (0, _index3.default)(dirtyDate);
      return (0, _index.default)({
        start: startDate,
        end: endDate
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfYear/index.js
var require_endOfYear = __commonJS({
  "node_modules/date-fns/endOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      date.setFullYear(year + 1, 0, 0);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfYear/index.js
var require_startOfYear = __commonJS({
  "node_modules/date-fns/startOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var cleanDate = (0, _index.default)(dirtyDate);
      var date = /* @__PURE__ */ new Date(0);
      date.setFullYear(cleanDate.getFullYear(), 0, 1);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachWeekendOfYear/index.js
var require_eachWeekendOfYear = __commonJS({
  "node_modules/date-fns/eachWeekendOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachWeekendOfYear;
    var _index = _interopRequireDefault(require_eachWeekendOfInterval());
    var _index2 = _interopRequireDefault(require_endOfYear());
    var _index3 = _interopRequireDefault(require_startOfYear());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function eachWeekendOfYear(dirtyDate) {
      (0, _index4.default)(1, arguments);
      var startDate = (0, _index3.default)(dirtyDate);
      var endDate = (0, _index2.default)(dirtyDate);
      return (0, _index.default)({
        start: startDate,
        end: endDate
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/eachYearOfInterval/index.js
var require_eachYearOfInterval = __commonJS({
  "node_modules/date-fns/eachYearOfInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = eachYearOfInterval;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function eachYearOfInterval(dirtyInterval) {
      (0, _index2.default)(1, arguments);
      var interval = dirtyInterval || {};
      var startDate = (0, _index.default)(interval.start);
      var endDate = (0, _index.default)(interval.end);
      var endTime = endDate.getTime();
      if (!(startDate.getTime() <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      var dates = [];
      var currentDate = startDate;
      currentDate.setHours(0, 0, 0, 0);
      currentDate.setMonth(0, 1);
      while (currentDate.getTime() <= endTime) {
        dates.push((0, _index.default)(currentDate));
        currentDate.setFullYear(currentDate.getFullYear() + 1);
      }
      return dates;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfDecade/index.js
var require_endOfDecade = __commonJS({
  "node_modules/date-fns/endOfDecade/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfDecade;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfDecade(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      var decade = 9 + Math.floor(year / 10) * 10;
      date.setFullYear(decade, 11, 31);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfHour/index.js
var require_endOfHour = __commonJS({
  "node_modules/date-fns/endOfHour/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfHour;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfHour(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setMinutes(59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfWeek/index.js
var require_endOfWeek = __commonJS({
  "node_modules/date-fns/endOfWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfWeek;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function endOfWeek(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index4.default)(1, arguments);
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      var weekStartsOn = (0, _index3.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      var date = (0, _index2.default)(dirtyDate);
      var day = date.getDay();
      var diff = (day < weekStartsOn ? -7 : 0) + 6 - (day - weekStartsOn);
      date.setDate(date.getDate() + diff);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfISOWeek/index.js
var require_endOfISOWeek = __commonJS({
  "node_modules/date-fns/endOfISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfISOWeek;
    var _index = _interopRequireDefault(require_endOfWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfISOWeek(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, {
        weekStartsOn: 1
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfISOWeekYear/index.js
var require_endOfISOWeekYear = __commonJS({
  "node_modules/date-fns/endOfISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfISOWeekYear;
    var _index = _interopRequireDefault(require_getISOWeekYear());
    var _index2 = _interopRequireDefault(require_startOfISOWeek());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function endOfISOWeekYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var year = (0, _index.default)(dirtyDate);
      var fourthOfJanuaryOfNextYear = /* @__PURE__ */ new Date(0);
      fourthOfJanuaryOfNextYear.setFullYear(year + 1, 0, 4);
      fourthOfJanuaryOfNextYear.setHours(0, 0, 0, 0);
      var date = (0, _index2.default)(fourthOfJanuaryOfNextYear);
      date.setMilliseconds(date.getMilliseconds() - 1);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfMinute/index.js
var require_endOfMinute = __commonJS({
  "node_modules/date-fns/endOfMinute/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfMinute;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfMinute(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setSeconds(59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfQuarter/index.js
var require_endOfQuarter = __commonJS({
  "node_modules/date-fns/endOfQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfQuarter;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfQuarter(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var currentMonth = date.getMonth();
      var month = currentMonth - currentMonth % 3 + 3;
      date.setMonth(month, 0);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfSecond/index.js
var require_endOfSecond = __commonJS({
  "node_modules/date-fns/endOfSecond/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfSecond;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function endOfSecond(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setMilliseconds(999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfToday/index.js
var require_endOfToday = __commonJS({
  "node_modules/date-fns/endOfToday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfToday;
    var _index = _interopRequireDefault(require_endOfDay());
    function endOfToday() {
      return (0, _index.default)(Date.now());
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfTomorrow/index.js
var require_endOfTomorrow = __commonJS({
  "node_modules/date-fns/endOfTomorrow/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfTomorrow;
    function endOfTomorrow() {
      var now = /* @__PURE__ */ new Date();
      var year = now.getFullYear();
      var month = now.getMonth();
      var day = now.getDate();
      var date = /* @__PURE__ */ new Date(0);
      date.setFullYear(year, month, day + 1);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/endOfYesterday/index.js
var require_endOfYesterday = __commonJS({
  "node_modules/date-fns/endOfYesterday/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = endOfYesterday;
    function endOfYesterday() {
      var now = /* @__PURE__ */ new Date();
      var year = now.getFullYear();
      var month = now.getMonth();
      var day = now.getDate();
      var date = /* @__PURE__ */ new Date(0);
      date.setFullYear(year, month, day - 1);
      date.setHours(23, 59, 59, 999);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subMilliseconds/index.js
var require_subMilliseconds = __commonJS({
  "node_modules/date-fns/subMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subMilliseconds;
    var _index = _interopRequireDefault(require_addMilliseconds());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function subMilliseconds(dirtyDate, dirtyAmount) {
      (0, _index2.default)(2, arguments);
      var amount = (0, _index3.default)(dirtyAmount);
      return (0, _index.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/getUTCDayOfYear/index.js
var require_getUTCDayOfYear = __commonJS({
  "node_modules/date-fns/_lib/getUTCDayOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getUTCDayOfYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_DAY = 864e5;
    function getUTCDayOfYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var timestamp = date.getTime();
      date.setUTCMonth(0, 1);
      date.setUTCHours(0, 0, 0, 0);
      var startOfYearTimestamp = date.getTime();
      var difference = timestamp - startOfYearTimestamp;
      return Math.floor(difference / MILLISECONDS_IN_DAY) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/startOfUTCISOWeek/index.js
var require_startOfUTCISOWeek = __commonJS({
  "node_modules/date-fns/_lib/startOfUTCISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfUTCISOWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfUTCISOWeek(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var weekStartsOn = 1;
      var date = (0, _index.default)(dirtyDate);
      var day = date.getUTCDay();
      var diff = (day < weekStartsOn ? 7 : 0) + day - weekStartsOn;
      date.setUTCDate(date.getUTCDate() - diff);
      date.setUTCHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/getUTCISOWeekYear/index.js
var require_getUTCISOWeekYear = __commonJS({
  "node_modules/date-fns/_lib/getUTCISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getUTCISOWeekYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_startOfUTCISOWeek());
    function getUTCISOWeekYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getUTCFullYear();
      var fourthOfJanuaryOfNextYear = /* @__PURE__ */ new Date(0);
      fourthOfJanuaryOfNextYear.setUTCFullYear(year + 1, 0, 4);
      fourthOfJanuaryOfNextYear.setUTCHours(0, 0, 0, 0);
      var startOfNextYear = (0, _index3.default)(fourthOfJanuaryOfNextYear);
      var fourthOfJanuaryOfThisYear = /* @__PURE__ */ new Date(0);
      fourthOfJanuaryOfThisYear.setUTCFullYear(year, 0, 4);
      fourthOfJanuaryOfThisYear.setUTCHours(0, 0, 0, 0);
      var startOfThisYear = (0, _index3.default)(fourthOfJanuaryOfThisYear);
      if (date.getTime() >= startOfNextYear.getTime()) {
        return year + 1;
      } else if (date.getTime() >= startOfThisYear.getTime()) {
        return year;
      } else {
        return year - 1;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/startOfUTCISOWeekYear/index.js
var require_startOfUTCISOWeekYear = __commonJS({
  "node_modules/date-fns/_lib/startOfUTCISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfUTCISOWeekYear;
    var _index = _interopRequireDefault(require_getUTCISOWeekYear());
    var _index2 = _interopRequireDefault(require_startOfUTCISOWeek());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function startOfUTCISOWeekYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var year = (0, _index.default)(dirtyDate);
      var fourthOfJanuary = /* @__PURE__ */ new Date(0);
      fourthOfJanuary.setUTCFullYear(year, 0, 4);
      fourthOfJanuary.setUTCHours(0, 0, 0, 0);
      var date = (0, _index2.default)(fourthOfJanuary);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/getUTCISOWeek/index.js
var require_getUTCISOWeek = __commonJS({
  "node_modules/date-fns/_lib/getUTCISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getUTCISOWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_startOfUTCISOWeek());
    var _index3 = _interopRequireDefault(require_startOfUTCISOWeekYear());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function getUTCISOWeek(dirtyDate) {
      (0, _index4.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var diff = (0, _index2.default)(date).getTime() - (0, _index3.default)(date).getTime();
      return Math.round(diff / MILLISECONDS_IN_WEEK) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/startOfUTCWeek/index.js
var require_startOfUTCWeek = __commonJS({
  "node_modules/date-fns/_lib/startOfUTCWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfUTCWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = require_defaultOptions();
    function startOfUTCWeek(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index2.default)(1, arguments);
      var defaultOptions3 = (0, _index4.getDefaultOptions)();
      var weekStartsOn = (0, _index3.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      var date = (0, _index.default)(dirtyDate);
      var day = date.getUTCDay();
      var diff = (day < weekStartsOn ? 7 : 0) + day - weekStartsOn;
      date.setUTCDate(date.getUTCDate() - diff);
      date.setUTCHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/getUTCWeekYear/index.js
var require_getUTCWeekYear = __commonJS({
  "node_modules/date-fns/_lib/getUTCWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getUTCWeekYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_startOfUTCWeek());
    var _index4 = _interopRequireDefault(require_toInteger());
    var _index5 = require_defaultOptions();
    function getUTCWeekYear(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$firstWeekCon, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getUTCFullYear();
      var defaultOptions3 = (0, _index5.getDefaultOptions)();
      var firstWeekContainsDate = (0, _index4.default)((_ref = (_ref2 = (_ref3 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref !== void 0 ? _ref : 1);
      if (!(firstWeekContainsDate >= 1 && firstWeekContainsDate <= 7)) {
        throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
      }
      var firstWeekOfNextYear = /* @__PURE__ */ new Date(0);
      firstWeekOfNextYear.setUTCFullYear(year + 1, 0, firstWeekContainsDate);
      firstWeekOfNextYear.setUTCHours(0, 0, 0, 0);
      var startOfNextYear = (0, _index3.default)(firstWeekOfNextYear, options);
      var firstWeekOfThisYear = /* @__PURE__ */ new Date(0);
      firstWeekOfThisYear.setUTCFullYear(year, 0, firstWeekContainsDate);
      firstWeekOfThisYear.setUTCHours(0, 0, 0, 0);
      var startOfThisYear = (0, _index3.default)(firstWeekOfThisYear, options);
      if (date.getTime() >= startOfNextYear.getTime()) {
        return year + 1;
      } else if (date.getTime() >= startOfThisYear.getTime()) {
        return year;
      } else {
        return year - 1;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/startOfUTCWeekYear/index.js
var require_startOfUTCWeekYear = __commonJS({
  "node_modules/date-fns/_lib/startOfUTCWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfUTCWeekYear;
    var _index = _interopRequireDefault(require_getUTCWeekYear());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_startOfUTCWeek());
    var _index4 = _interopRequireDefault(require_toInteger());
    var _index5 = require_defaultOptions();
    function startOfUTCWeekYear(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$firstWeekCon, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index2.default)(1, arguments);
      var defaultOptions3 = (0, _index5.getDefaultOptions)();
      var firstWeekContainsDate = (0, _index4.default)((_ref = (_ref2 = (_ref3 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref !== void 0 ? _ref : 1);
      var year = (0, _index.default)(dirtyDate, options);
      var firstWeek = /* @__PURE__ */ new Date(0);
      firstWeek.setUTCFullYear(year, 0, firstWeekContainsDate);
      firstWeek.setUTCHours(0, 0, 0, 0);
      var date = (0, _index3.default)(firstWeek, options);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/getUTCWeek/index.js
var require_getUTCWeek = __commonJS({
  "node_modules/date-fns/_lib/getUTCWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getUTCWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_startOfUTCWeek());
    var _index3 = _interopRequireDefault(require_startOfUTCWeekYear());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function getUTCWeek(dirtyDate, options) {
      (0, _index4.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var diff = (0, _index2.default)(date, options).getTime() - (0, _index3.default)(date, options).getTime();
      return Math.round(diff / MILLISECONDS_IN_WEEK) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/addLeadingZeros/index.js
var require_addLeadingZeros = __commonJS({
  "node_modules/date-fns/_lib/addLeadingZeros/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = addLeadingZeros;
    function addLeadingZeros(number, targetLength) {
      var sign = number < 0 ? "-" : "";
      var output2 = Math.abs(number).toString();
      while (output2.length < targetLength) {
        output2 = "0" + output2;
      }
      return sign + output2;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/format/lightFormatters/index.js
var require_lightFormatters = __commonJS({
  "node_modules/date-fns/_lib/format/lightFormatters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_addLeadingZeros());
    var formatters = {
      // Year
      y: function y(date, token) {
        var signedYear = date.getUTCFullYear();
        var year = signedYear > 0 ? signedYear : 1 - signedYear;
        return (0, _index.default)(token === "yy" ? year % 100 : year, token.length);
      },
      // Month
      M: function M(date, token) {
        var month = date.getUTCMonth();
        return token === "M" ? String(month + 1) : (0, _index.default)(month + 1, 2);
      },
      // Day of the month
      d: function d(date, token) {
        return (0, _index.default)(date.getUTCDate(), token.length);
      },
      // AM or PM
      a: function a(date, token) {
        var dayPeriodEnumValue = date.getUTCHours() / 12 >= 1 ? "pm" : "am";
        switch (token) {
          case "a":
          case "aa":
            return dayPeriodEnumValue.toUpperCase();
          case "aaa":
            return dayPeriodEnumValue;
          case "aaaaa":
            return dayPeriodEnumValue[0];
          case "aaaa":
          default:
            return dayPeriodEnumValue === "am" ? "a.m." : "p.m.";
        }
      },
      // Hour [1-12]
      h: function h(date, token) {
        return (0, _index.default)(date.getUTCHours() % 12 || 12, token.length);
      },
      // Hour [0-23]
      H: function H(date, token) {
        return (0, _index.default)(date.getUTCHours(), token.length);
      },
      // Minute
      m: function m(date, token) {
        return (0, _index.default)(date.getUTCMinutes(), token.length);
      },
      // Second
      s: function s(date, token) {
        return (0, _index.default)(date.getUTCSeconds(), token.length);
      },
      // Fraction of second
      S: function S(date, token) {
        var numberOfDigits = token.length;
        var milliseconds = date.getUTCMilliseconds();
        var fractionalSeconds = Math.floor(milliseconds * Math.pow(10, numberOfDigits - 3));
        return (0, _index.default)(fractionalSeconds, token.length);
      }
    };
    var _default = formatters;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/format/formatters/index.js
var require_formatters = __commonJS({
  "node_modules/date-fns/_lib/format/formatters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_getUTCDayOfYear());
    var _index2 = _interopRequireDefault(require_getUTCISOWeek());
    var _index3 = _interopRequireDefault(require_getUTCISOWeekYear());
    var _index4 = _interopRequireDefault(require_getUTCWeek());
    var _index5 = _interopRequireDefault(require_getUTCWeekYear());
    var _index6 = _interopRequireDefault(require_addLeadingZeros());
    var _index7 = _interopRequireDefault(require_lightFormatters());
    var dayPeriodEnum = {
      am: "am",
      pm: "pm",
      midnight: "midnight",
      noon: "noon",
      morning: "morning",
      afternoon: "afternoon",
      evening: "evening",
      night: "night"
    };
    var formatters = {
      // Era
      G: function G(date, token, localize) {
        var era = date.getUTCFullYear() > 0 ? 1 : 0;
        switch (token) {
          // AD, BC
          case "G":
          case "GG":
          case "GGG":
            return localize.era(era, {
              width: "abbreviated"
            });
          // A, B
          case "GGGGG":
            return localize.era(era, {
              width: "narrow"
            });
          // Anno Domini, Before Christ
          case "GGGG":
          default:
            return localize.era(era, {
              width: "wide"
            });
        }
      },
      // Year
      y: function y(date, token, localize) {
        if (token === "yo") {
          var signedYear = date.getUTCFullYear();
          var year = signedYear > 0 ? signedYear : 1 - signedYear;
          return localize.ordinalNumber(year, {
            unit: "year"
          });
        }
        return _index7.default.y(date, token);
      },
      // Local week-numbering year
      Y: function Y(date, token, localize, options) {
        var signedWeekYear = (0, _index5.default)(date, options);
        var weekYear = signedWeekYear > 0 ? signedWeekYear : 1 - signedWeekYear;
        if (token === "YY") {
          var twoDigitYear = weekYear % 100;
          return (0, _index6.default)(twoDigitYear, 2);
        }
        if (token === "Yo") {
          return localize.ordinalNumber(weekYear, {
            unit: "year"
          });
        }
        return (0, _index6.default)(weekYear, token.length);
      },
      // ISO week-numbering year
      R: function R(date, token) {
        var isoWeekYear = (0, _index3.default)(date);
        return (0, _index6.default)(isoWeekYear, token.length);
      },
      // Extended year. This is a single number designating the year of this calendar system.
      // The main difference between `y` and `u` localizers are B.C. years:
      // | Year | `y` | `u` |
      // |------|-----|-----|
      // | AC 1 |   1 |   1 |
      // | BC 1 |   1 |   0 |
      // | BC 2 |   2 |  -1 |
      // Also `yy` always returns the last two digits of a year,
      // while `uu` pads single digit years to 2 characters and returns other years unchanged.
      u: function u(date, token) {
        var year = date.getUTCFullYear();
        return (0, _index6.default)(year, token.length);
      },
      // Quarter
      Q: function Q(date, token, localize) {
        var quarter = Math.ceil((date.getUTCMonth() + 1) / 3);
        switch (token) {
          // 1, 2, 3, 4
          case "Q":
            return String(quarter);
          // 01, 02, 03, 04
          case "QQ":
            return (0, _index6.default)(quarter, 2);
          // 1st, 2nd, 3rd, 4th
          case "Qo":
            return localize.ordinalNumber(quarter, {
              unit: "quarter"
            });
          // Q1, Q2, Q3, Q4
          case "QQQ":
            return localize.quarter(quarter, {
              width: "abbreviated",
              context: "formatting"
            });
          // 1, 2, 3, 4 (narrow quarter; could be not numerical)
          case "QQQQQ":
            return localize.quarter(quarter, {
              width: "narrow",
              context: "formatting"
            });
          // 1st quarter, 2nd quarter, ...
          case "QQQQ":
          default:
            return localize.quarter(quarter, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // Stand-alone quarter
      q: function q(date, token, localize) {
        var quarter = Math.ceil((date.getUTCMonth() + 1) / 3);
        switch (token) {
          // 1, 2, 3, 4
          case "q":
            return String(quarter);
          // 01, 02, 03, 04
          case "qq":
            return (0, _index6.default)(quarter, 2);
          // 1st, 2nd, 3rd, 4th
          case "qo":
            return localize.ordinalNumber(quarter, {
              unit: "quarter"
            });
          // Q1, Q2, Q3, Q4
          case "qqq":
            return localize.quarter(quarter, {
              width: "abbreviated",
              context: "standalone"
            });
          // 1, 2, 3, 4 (narrow quarter; could be not numerical)
          case "qqqqq":
            return localize.quarter(quarter, {
              width: "narrow",
              context: "standalone"
            });
          // 1st quarter, 2nd quarter, ...
          case "qqqq":
          default:
            return localize.quarter(quarter, {
              width: "wide",
              context: "standalone"
            });
        }
      },
      // Month
      M: function M(date, token, localize) {
        var month = date.getUTCMonth();
        switch (token) {
          case "M":
          case "MM":
            return _index7.default.M(date, token);
          // 1st, 2nd, ..., 12th
          case "Mo":
            return localize.ordinalNumber(month + 1, {
              unit: "month"
            });
          // Jan, Feb, ..., Dec
          case "MMM":
            return localize.month(month, {
              width: "abbreviated",
              context: "formatting"
            });
          // J, F, ..., D
          case "MMMMM":
            return localize.month(month, {
              width: "narrow",
              context: "formatting"
            });
          // January, February, ..., December
          case "MMMM":
          default:
            return localize.month(month, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // Stand-alone month
      L: function L(date, token, localize) {
        var month = date.getUTCMonth();
        switch (token) {
          // 1, 2, ..., 12
          case "L":
            return String(month + 1);
          // 01, 02, ..., 12
          case "LL":
            return (0, _index6.default)(month + 1, 2);
          // 1st, 2nd, ..., 12th
          case "Lo":
            return localize.ordinalNumber(month + 1, {
              unit: "month"
            });
          // Jan, Feb, ..., Dec
          case "LLL":
            return localize.month(month, {
              width: "abbreviated",
              context: "standalone"
            });
          // J, F, ..., D
          case "LLLLL":
            return localize.month(month, {
              width: "narrow",
              context: "standalone"
            });
          // January, February, ..., December
          case "LLLL":
          default:
            return localize.month(month, {
              width: "wide",
              context: "standalone"
            });
        }
      },
      // Local week of year
      w: function w(date, token, localize, options) {
        var week = (0, _index4.default)(date, options);
        if (token === "wo") {
          return localize.ordinalNumber(week, {
            unit: "week"
          });
        }
        return (0, _index6.default)(week, token.length);
      },
      // ISO week of year
      I: function I(date, token, localize) {
        var isoWeek = (0, _index2.default)(date);
        if (token === "Io") {
          return localize.ordinalNumber(isoWeek, {
            unit: "week"
          });
        }
        return (0, _index6.default)(isoWeek, token.length);
      },
      // Day of the month
      d: function d(date, token, localize) {
        if (token === "do") {
          return localize.ordinalNumber(date.getUTCDate(), {
            unit: "date"
          });
        }
        return _index7.default.d(date, token);
      },
      // Day of year
      D: function D(date, token, localize) {
        var dayOfYear = (0, _index.default)(date);
        if (token === "Do") {
          return localize.ordinalNumber(dayOfYear, {
            unit: "dayOfYear"
          });
        }
        return (0, _index6.default)(dayOfYear, token.length);
      },
      // Day of week
      E: function E(date, token, localize) {
        var dayOfWeek = date.getUTCDay();
        switch (token) {
          // Tue
          case "E":
          case "EE":
          case "EEE":
            return localize.day(dayOfWeek, {
              width: "abbreviated",
              context: "formatting"
            });
          // T
          case "EEEEE":
            return localize.day(dayOfWeek, {
              width: "narrow",
              context: "formatting"
            });
          // Tu
          case "EEEEEE":
            return localize.day(dayOfWeek, {
              width: "short",
              context: "formatting"
            });
          // Tuesday
          case "EEEE":
          default:
            return localize.day(dayOfWeek, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // Local day of week
      e: function e(date, token, localize, options) {
        var dayOfWeek = date.getUTCDay();
        var localDayOfWeek = (dayOfWeek - options.weekStartsOn + 8) % 7 || 7;
        switch (token) {
          // Numerical value (Nth day of week with current locale or weekStartsOn)
          case "e":
            return String(localDayOfWeek);
          // Padded numerical value
          case "ee":
            return (0, _index6.default)(localDayOfWeek, 2);
          // 1st, 2nd, ..., 7th
          case "eo":
            return localize.ordinalNumber(localDayOfWeek, {
              unit: "day"
            });
          case "eee":
            return localize.day(dayOfWeek, {
              width: "abbreviated",
              context: "formatting"
            });
          // T
          case "eeeee":
            return localize.day(dayOfWeek, {
              width: "narrow",
              context: "formatting"
            });
          // Tu
          case "eeeeee":
            return localize.day(dayOfWeek, {
              width: "short",
              context: "formatting"
            });
          // Tuesday
          case "eeee":
          default:
            return localize.day(dayOfWeek, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // Stand-alone local day of week
      c: function c(date, token, localize, options) {
        var dayOfWeek = date.getUTCDay();
        var localDayOfWeek = (dayOfWeek - options.weekStartsOn + 8) % 7 || 7;
        switch (token) {
          // Numerical value (same as in `e`)
          case "c":
            return String(localDayOfWeek);
          // Padded numerical value
          case "cc":
            return (0, _index6.default)(localDayOfWeek, token.length);
          // 1st, 2nd, ..., 7th
          case "co":
            return localize.ordinalNumber(localDayOfWeek, {
              unit: "day"
            });
          case "ccc":
            return localize.day(dayOfWeek, {
              width: "abbreviated",
              context: "standalone"
            });
          // T
          case "ccccc":
            return localize.day(dayOfWeek, {
              width: "narrow",
              context: "standalone"
            });
          // Tu
          case "cccccc":
            return localize.day(dayOfWeek, {
              width: "short",
              context: "standalone"
            });
          // Tuesday
          case "cccc":
          default:
            return localize.day(dayOfWeek, {
              width: "wide",
              context: "standalone"
            });
        }
      },
      // ISO day of week
      i: function i(date, token, localize) {
        var dayOfWeek = date.getUTCDay();
        var isoDayOfWeek = dayOfWeek === 0 ? 7 : dayOfWeek;
        switch (token) {
          // 2
          case "i":
            return String(isoDayOfWeek);
          // 02
          case "ii":
            return (0, _index6.default)(isoDayOfWeek, token.length);
          // 2nd
          case "io":
            return localize.ordinalNumber(isoDayOfWeek, {
              unit: "day"
            });
          // Tue
          case "iii":
            return localize.day(dayOfWeek, {
              width: "abbreviated",
              context: "formatting"
            });
          // T
          case "iiiii":
            return localize.day(dayOfWeek, {
              width: "narrow",
              context: "formatting"
            });
          // Tu
          case "iiiiii":
            return localize.day(dayOfWeek, {
              width: "short",
              context: "formatting"
            });
          // Tuesday
          case "iiii":
          default:
            return localize.day(dayOfWeek, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // AM or PM
      a: function a(date, token, localize) {
        var hours = date.getUTCHours();
        var dayPeriodEnumValue = hours / 12 >= 1 ? "pm" : "am";
        switch (token) {
          case "a":
          case "aa":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "abbreviated",
              context: "formatting"
            });
          case "aaa":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "abbreviated",
              context: "formatting"
            }).toLowerCase();
          case "aaaaa":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "narrow",
              context: "formatting"
            });
          case "aaaa":
          default:
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // AM, PM, midnight, noon
      b: function b(date, token, localize) {
        var hours = date.getUTCHours();
        var dayPeriodEnumValue;
        if (hours === 12) {
          dayPeriodEnumValue = dayPeriodEnum.noon;
        } else if (hours === 0) {
          dayPeriodEnumValue = dayPeriodEnum.midnight;
        } else {
          dayPeriodEnumValue = hours / 12 >= 1 ? "pm" : "am";
        }
        switch (token) {
          case "b":
          case "bb":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "abbreviated",
              context: "formatting"
            });
          case "bbb":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "abbreviated",
              context: "formatting"
            }).toLowerCase();
          case "bbbbb":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "narrow",
              context: "formatting"
            });
          case "bbbb":
          default:
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // in the morning, in the afternoon, in the evening, at night
      B: function B(date, token, localize) {
        var hours = date.getUTCHours();
        var dayPeriodEnumValue;
        if (hours >= 17) {
          dayPeriodEnumValue = dayPeriodEnum.evening;
        } else if (hours >= 12) {
          dayPeriodEnumValue = dayPeriodEnum.afternoon;
        } else if (hours >= 4) {
          dayPeriodEnumValue = dayPeriodEnum.morning;
        } else {
          dayPeriodEnumValue = dayPeriodEnum.night;
        }
        switch (token) {
          case "B":
          case "BB":
          case "BBB":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "abbreviated",
              context: "formatting"
            });
          case "BBBBB":
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "narrow",
              context: "formatting"
            });
          case "BBBB":
          default:
            return localize.dayPeriod(dayPeriodEnumValue, {
              width: "wide",
              context: "formatting"
            });
        }
      },
      // Hour [1-12]
      h: function h(date, token, localize) {
        if (token === "ho") {
          var hours = date.getUTCHours() % 12;
          if (hours === 0) hours = 12;
          return localize.ordinalNumber(hours, {
            unit: "hour"
          });
        }
        return _index7.default.h(date, token);
      },
      // Hour [0-23]
      H: function H(date, token, localize) {
        if (token === "Ho") {
          return localize.ordinalNumber(date.getUTCHours(), {
            unit: "hour"
          });
        }
        return _index7.default.H(date, token);
      },
      // Hour [0-11]
      K: function K(date, token, localize) {
        var hours = date.getUTCHours() % 12;
        if (token === "Ko") {
          return localize.ordinalNumber(hours, {
            unit: "hour"
          });
        }
        return (0, _index6.default)(hours, token.length);
      },
      // Hour [1-24]
      k: function k(date, token, localize) {
        var hours = date.getUTCHours();
        if (hours === 0) hours = 24;
        if (token === "ko") {
          return localize.ordinalNumber(hours, {
            unit: "hour"
          });
        }
        return (0, _index6.default)(hours, token.length);
      },
      // Minute
      m: function m(date, token, localize) {
        if (token === "mo") {
          return localize.ordinalNumber(date.getUTCMinutes(), {
            unit: "minute"
          });
        }
        return _index7.default.m(date, token);
      },
      // Second
      s: function s(date, token, localize) {
        if (token === "so") {
          return localize.ordinalNumber(date.getUTCSeconds(), {
            unit: "second"
          });
        }
        return _index7.default.s(date, token);
      },
      // Fraction of second
      S: function S(date, token) {
        return _index7.default.S(date, token);
      },
      // Timezone (ISO-8601. If offset is 0, output is always `'Z'`)
      X: function X(date, token, _localize, options) {
        var originalDate = options._originalDate || date;
        var timezoneOffset = originalDate.getTimezoneOffset();
        if (timezoneOffset === 0) {
          return "Z";
        }
        switch (token) {
          // Hours and optional minutes
          case "X":
            return formatTimezoneWithOptionalMinutes(timezoneOffset);
          // Hours, minutes and optional seconds without `:` delimiter
          // Note: neither ISO-8601 nor JavaScript supports seconds in timezone offsets
          // so this token always has the same output as `XX`
          case "XXXX":
          case "XX":
            return formatTimezone(timezoneOffset);
          // Hours, minutes and optional seconds with `:` delimiter
          // Note: neither ISO-8601 nor JavaScript supports seconds in timezone offsets
          // so this token always has the same output as `XXX`
          case "XXXXX":
          case "XXX":
          // Hours and minutes with `:` delimiter
          default:
            return formatTimezone(timezoneOffset, ":");
        }
      },
      // Timezone (ISO-8601. If offset is 0, output is `'+00:00'` or equivalent)
      x: function x(date, token, _localize, options) {
        var originalDate = options._originalDate || date;
        var timezoneOffset = originalDate.getTimezoneOffset();
        switch (token) {
          // Hours and optional minutes
          case "x":
            return formatTimezoneWithOptionalMinutes(timezoneOffset);
          // Hours, minutes and optional seconds without `:` delimiter
          // Note: neither ISO-8601 nor JavaScript supports seconds in timezone offsets
          // so this token always has the same output as `xx`
          case "xxxx":
          case "xx":
            return formatTimezone(timezoneOffset);
          // Hours, minutes and optional seconds with `:` delimiter
          // Note: neither ISO-8601 nor JavaScript supports seconds in timezone offsets
          // so this token always has the same output as `xxx`
          case "xxxxx":
          case "xxx":
          // Hours and minutes with `:` delimiter
          default:
            return formatTimezone(timezoneOffset, ":");
        }
      },
      // Timezone (GMT)
      O: function O(date, token, _localize, options) {
        var originalDate = options._originalDate || date;
        var timezoneOffset = originalDate.getTimezoneOffset();
        switch (token) {
          // Short
          case "O":
          case "OO":
          case "OOO":
            return "GMT" + formatTimezoneShort(timezoneOffset, ":");
          // Long
          case "OOOO":
          default:
            return "GMT" + formatTimezone(timezoneOffset, ":");
        }
      },
      // Timezone (specific non-location)
      z: function z(date, token, _localize, options) {
        var originalDate = options._originalDate || date;
        var timezoneOffset = originalDate.getTimezoneOffset();
        switch (token) {
          // Short
          case "z":
          case "zz":
          case "zzz":
            return "GMT" + formatTimezoneShort(timezoneOffset, ":");
          // Long
          case "zzzz":
          default:
            return "GMT" + formatTimezone(timezoneOffset, ":");
        }
      },
      // Seconds timestamp
      t: function t(date, token, _localize, options) {
        var originalDate = options._originalDate || date;
        var timestamp = Math.floor(originalDate.getTime() / 1e3);
        return (0, _index6.default)(timestamp, token.length);
      },
      // Milliseconds timestamp
      T: function T(date, token, _localize, options) {
        var originalDate = options._originalDate || date;
        var timestamp = originalDate.getTime();
        return (0, _index6.default)(timestamp, token.length);
      }
    };
    function formatTimezoneShort(offset, dirtyDelimiter) {
      var sign = offset > 0 ? "-" : "+";
      var absOffset = Math.abs(offset);
      var hours = Math.floor(absOffset / 60);
      var minutes = absOffset % 60;
      if (minutes === 0) {
        return sign + String(hours);
      }
      var delimiter = dirtyDelimiter || "";
      return sign + String(hours) + delimiter + (0, _index6.default)(minutes, 2);
    }
    function formatTimezoneWithOptionalMinutes(offset, dirtyDelimiter) {
      if (offset % 60 === 0) {
        var sign = offset > 0 ? "-" : "+";
        return sign + (0, _index6.default)(Math.abs(offset) / 60, 2);
      }
      return formatTimezone(offset, dirtyDelimiter);
    }
    function formatTimezone(offset, dirtyDelimiter) {
      var delimiter = dirtyDelimiter || "";
      var sign = offset > 0 ? "-" : "+";
      var absOffset = Math.abs(offset);
      var hours = (0, _index6.default)(Math.floor(absOffset / 60), 2);
      var minutes = (0, _index6.default)(absOffset % 60, 2);
      return sign + hours + delimiter + minutes;
    }
    var _default = formatters;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/format/longFormatters/index.js
var require_longFormatters = __commonJS({
  "node_modules/date-fns/_lib/format/longFormatters/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var dateLongFormatter = function dateLongFormatter2(pattern, formatLong) {
      switch (pattern) {
        case "P":
          return formatLong.date({
            width: "short"
          });
        case "PP":
          return formatLong.date({
            width: "medium"
          });
        case "PPP":
          return formatLong.date({
            width: "long"
          });
        case "PPPP":
        default:
          return formatLong.date({
            width: "full"
          });
      }
    };
    var timeLongFormatter = function timeLongFormatter2(pattern, formatLong) {
      switch (pattern) {
        case "p":
          return formatLong.time({
            width: "short"
          });
        case "pp":
          return formatLong.time({
            width: "medium"
          });
        case "ppp":
          return formatLong.time({
            width: "long"
          });
        case "pppp":
        default:
          return formatLong.time({
            width: "full"
          });
      }
    };
    var dateTimeLongFormatter = function dateTimeLongFormatter2(pattern, formatLong) {
      var matchResult = pattern.match(/(P+)(p+)?/) || [];
      var datePattern = matchResult[1];
      var timePattern = matchResult[2];
      if (!timePattern) {
        return dateLongFormatter(pattern, formatLong);
      }
      var dateTimeFormat;
      switch (datePattern) {
        case "P":
          dateTimeFormat = formatLong.dateTime({
            width: "short"
          });
          break;
        case "PP":
          dateTimeFormat = formatLong.dateTime({
            width: "medium"
          });
          break;
        case "PPP":
          dateTimeFormat = formatLong.dateTime({
            width: "long"
          });
          break;
        case "PPPP":
        default:
          dateTimeFormat = formatLong.dateTime({
            width: "full"
          });
          break;
      }
      return dateTimeFormat.replace("{{date}}", dateLongFormatter(datePattern, formatLong)).replace("{{time}}", timeLongFormatter(timePattern, formatLong));
    };
    var longFormatters = {
      p: timeLongFormatter,
      P: dateTimeLongFormatter
    };
    var _default = longFormatters;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/protectedTokens/index.js
var require_protectedTokens = __commonJS({
  "node_modules/date-fns/_lib/protectedTokens/index.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.isProtectedDayOfYearToken = isProtectedDayOfYearToken;
    exports2.isProtectedWeekYearToken = isProtectedWeekYearToken;
    exports2.throwProtectedError = throwProtectedError;
    var protectedDayOfYearTokens = ["D", "DD"];
    var protectedWeekYearTokens = ["YY", "YYYY"];
    function isProtectedDayOfYearToken(token) {
      return protectedDayOfYearTokens.indexOf(token) !== -1;
    }
    function isProtectedWeekYearToken(token) {
      return protectedWeekYearTokens.indexOf(token) !== -1;
    }
    function throwProtectedError(token, format2, input) {
      if (token === "YYYY") {
        throw new RangeError("Use `yyyy` instead of `YYYY` (in `".concat(format2, "`) for formatting years to the input `").concat(input, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
      } else if (token === "YY") {
        throw new RangeError("Use `yy` instead of `YY` (in `".concat(format2, "`) for formatting years to the input `").concat(input, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
      } else if (token === "D") {
        throw new RangeError("Use `d` instead of `D` (in `".concat(format2, "`) for formatting days of the month to the input `").concat(input, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
      } else if (token === "DD") {
        throw new RangeError("Use `dd` instead of `DD` (in `".concat(format2, "`) for formatting days of the month to the input `").concat(input, "`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md"));
      }
    }
  }
});

// node_modules/date-fns/locale/en-US/_lib/formatDistance/index.js
var require_formatDistance = __commonJS({
  "node_modules/date-fns/locale/en-US/_lib/formatDistance/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var formatDistanceLocale = {
      lessThanXSeconds: {
        one: "less than a second",
        other: "less than {{count}} seconds"
      },
      xSeconds: {
        one: "1 second",
        other: "{{count}} seconds"
      },
      halfAMinute: "half a minute",
      lessThanXMinutes: {
        one: "less than a minute",
        other: "less than {{count}} minutes"
      },
      xMinutes: {
        one: "1 minute",
        other: "{{count}} minutes"
      },
      aboutXHours: {
        one: "about 1 hour",
        other: "about {{count}} hours"
      },
      xHours: {
        one: "1 hour",
        other: "{{count}} hours"
      },
      xDays: {
        one: "1 day",
        other: "{{count}} days"
      },
      aboutXWeeks: {
        one: "about 1 week",
        other: "about {{count}} weeks"
      },
      xWeeks: {
        one: "1 week",
        other: "{{count}} weeks"
      },
      aboutXMonths: {
        one: "about 1 month",
        other: "about {{count}} months"
      },
      xMonths: {
        one: "1 month",
        other: "{{count}} months"
      },
      aboutXYears: {
        one: "about 1 year",
        other: "about {{count}} years"
      },
      xYears: {
        one: "1 year",
        other: "{{count}} years"
      },
      overXYears: {
        one: "over 1 year",
        other: "over {{count}} years"
      },
      almostXYears: {
        one: "almost 1 year",
        other: "almost {{count}} years"
      }
    };
    var formatDistance = function formatDistance2(token, count, options) {
      var result;
      var tokenValue = formatDistanceLocale[token];
      if (typeof tokenValue === "string") {
        result = tokenValue;
      } else if (count === 1) {
        result = tokenValue.one;
      } else {
        result = tokenValue.other.replace("{{count}}", count.toString());
      }
      if (options !== null && options !== void 0 && options.addSuffix) {
        if (options.comparison && options.comparison > 0) {
          return "in " + result;
        } else {
          return result + " ago";
        }
      }
      return result;
    };
    var _default = formatDistance;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/_lib/buildFormatLongFn/index.js
var require_buildFormatLongFn = __commonJS({
  "node_modules/date-fns/locale/_lib/buildFormatLongFn/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = buildFormatLongFn;
    function buildFormatLongFn(args) {
      return function() {
        var options = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {};
        var width = options.width ? String(options.width) : args.defaultWidth;
        var format2 = args.formats[width] || args.formats[args.defaultWidth];
        return format2;
      };
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/en-US/_lib/formatLong/index.js
var require_formatLong = __commonJS({
  "node_modules/date-fns/locale/en-US/_lib/formatLong/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_buildFormatLongFn());
    var dateFormats = {
      full: "EEEE, MMMM do, y",
      long: "MMMM do, y",
      medium: "MMM d, y",
      short: "MM/dd/yyyy"
    };
    var timeFormats = {
      full: "h:mm:ss a zzzz",
      long: "h:mm:ss a z",
      medium: "h:mm:ss a",
      short: "h:mm a"
    };
    var dateTimeFormats = {
      full: "{{date}} 'at' {{time}}",
      long: "{{date}} 'at' {{time}}",
      medium: "{{date}}, {{time}}",
      short: "{{date}}, {{time}}"
    };
    var formatLong = {
      date: (0, _index.default)({
        formats: dateFormats,
        defaultWidth: "full"
      }),
      time: (0, _index.default)({
        formats: timeFormats,
        defaultWidth: "full"
      }),
      dateTime: (0, _index.default)({
        formats: dateTimeFormats,
        defaultWidth: "full"
      })
    };
    var _default = formatLong;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/en-US/_lib/formatRelative/index.js
var require_formatRelative = __commonJS({
  "node_modules/date-fns/locale/en-US/_lib/formatRelative/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var formatRelativeLocale = {
      lastWeek: "'last' eeee 'at' p",
      yesterday: "'yesterday at' p",
      today: "'today at' p",
      tomorrow: "'tomorrow at' p",
      nextWeek: "eeee 'at' p",
      other: "P"
    };
    var formatRelative = function formatRelative2(token, _date, _baseDate, _options) {
      return formatRelativeLocale[token];
    };
    var _default = formatRelative;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/_lib/buildLocalizeFn/index.js
var require_buildLocalizeFn = __commonJS({
  "node_modules/date-fns/locale/_lib/buildLocalizeFn/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = buildLocalizeFn;
    function buildLocalizeFn(args) {
      return function(dirtyIndex, options) {
        var context = options !== null && options !== void 0 && options.context ? String(options.context) : "standalone";
        var valuesArray;
        if (context === "formatting" && args.formattingValues) {
          var defaultWidth = args.defaultFormattingWidth || args.defaultWidth;
          var width = options !== null && options !== void 0 && options.width ? String(options.width) : defaultWidth;
          valuesArray = args.formattingValues[width] || args.formattingValues[defaultWidth];
        } else {
          var _defaultWidth = args.defaultWidth;
          var _width = options !== null && options !== void 0 && options.width ? String(options.width) : args.defaultWidth;
          valuesArray = args.values[_width] || args.values[_defaultWidth];
        }
        var index = args.argumentCallback ? args.argumentCallback(dirtyIndex) : dirtyIndex;
        return valuesArray[index];
      };
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/en-US/_lib/localize/index.js
var require_localize = __commonJS({
  "node_modules/date-fns/locale/en-US/_lib/localize/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_buildLocalizeFn());
    var eraValues = {
      narrow: ["B", "A"],
      abbreviated: ["BC", "AD"],
      wide: ["Before Christ", "Anno Domini"]
    };
    var quarterValues = {
      narrow: ["1", "2", "3", "4"],
      abbreviated: ["Q1", "Q2", "Q3", "Q4"],
      wide: ["1st quarter", "2nd quarter", "3rd quarter", "4th quarter"]
    };
    var monthValues = {
      narrow: ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
      abbreviated: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
      wide: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    };
    var dayValues = {
      narrow: ["S", "M", "T", "W", "T", "F", "S"],
      short: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
      abbreviated: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
      wide: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    };
    var dayPeriodValues = {
      narrow: {
        am: "a",
        pm: "p",
        midnight: "mi",
        noon: "n",
        morning: "morning",
        afternoon: "afternoon",
        evening: "evening",
        night: "night"
      },
      abbreviated: {
        am: "AM",
        pm: "PM",
        midnight: "midnight",
        noon: "noon",
        morning: "morning",
        afternoon: "afternoon",
        evening: "evening",
        night: "night"
      },
      wide: {
        am: "a.m.",
        pm: "p.m.",
        midnight: "midnight",
        noon: "noon",
        morning: "morning",
        afternoon: "afternoon",
        evening: "evening",
        night: "night"
      }
    };
    var formattingDayPeriodValues = {
      narrow: {
        am: "a",
        pm: "p",
        midnight: "mi",
        noon: "n",
        morning: "in the morning",
        afternoon: "in the afternoon",
        evening: "in the evening",
        night: "at night"
      },
      abbreviated: {
        am: "AM",
        pm: "PM",
        midnight: "midnight",
        noon: "noon",
        morning: "in the morning",
        afternoon: "in the afternoon",
        evening: "in the evening",
        night: "at night"
      },
      wide: {
        am: "a.m.",
        pm: "p.m.",
        midnight: "midnight",
        noon: "noon",
        morning: "in the morning",
        afternoon: "in the afternoon",
        evening: "in the evening",
        night: "at night"
      }
    };
    var ordinalNumber = function ordinalNumber2(dirtyNumber, _options) {
      var number = Number(dirtyNumber);
      var rem100 = number % 100;
      if (rem100 > 20 || rem100 < 10) {
        switch (rem100 % 10) {
          case 1:
            return number + "st";
          case 2:
            return number + "nd";
          case 3:
            return number + "rd";
        }
      }
      return number + "th";
    };
    var localize = {
      ordinalNumber,
      era: (0, _index.default)({
        values: eraValues,
        defaultWidth: "wide"
      }),
      quarter: (0, _index.default)({
        values: quarterValues,
        defaultWidth: "wide",
        argumentCallback: function argumentCallback(quarter) {
          return quarter - 1;
        }
      }),
      month: (0, _index.default)({
        values: monthValues,
        defaultWidth: "wide"
      }),
      day: (0, _index.default)({
        values: dayValues,
        defaultWidth: "wide"
      }),
      dayPeriod: (0, _index.default)({
        values: dayPeriodValues,
        defaultWidth: "wide",
        formattingValues: formattingDayPeriodValues,
        defaultFormattingWidth: "wide"
      })
    };
    var _default = localize;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/_lib/buildMatchFn/index.js
var require_buildMatchFn = __commonJS({
  "node_modules/date-fns/locale/_lib/buildMatchFn/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = buildMatchFn;
    function buildMatchFn(args) {
      return function(string) {
        var options = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
        var width = options.width;
        var matchPattern = width && args.matchPatterns[width] || args.matchPatterns[args.defaultMatchWidth];
        var matchResult = string.match(matchPattern);
        if (!matchResult) {
          return null;
        }
        var matchedString = matchResult[0];
        var parsePatterns = width && args.parsePatterns[width] || args.parsePatterns[args.defaultParseWidth];
        var key = Array.isArray(parsePatterns) ? findIndex(parsePatterns, function(pattern) {
          return pattern.test(matchedString);
        }) : findKey(parsePatterns, function(pattern) {
          return pattern.test(matchedString);
        });
        var value;
        value = args.valueCallback ? args.valueCallback(key) : key;
        value = options.valueCallback ? options.valueCallback(value) : value;
        var rest = string.slice(matchedString.length);
        return {
          value,
          rest
        };
      };
    }
    function findKey(object, predicate) {
      for (var key in object) {
        if (object.hasOwnProperty(key) && predicate(object[key])) {
          return key;
        }
      }
      return void 0;
    }
    function findIndex(array, predicate) {
      for (var key = 0; key < array.length; key++) {
        if (predicate(array[key])) {
          return key;
        }
      }
      return void 0;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/_lib/buildMatchPatternFn/index.js
var require_buildMatchPatternFn = __commonJS({
  "node_modules/date-fns/locale/_lib/buildMatchPatternFn/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = buildMatchPatternFn;
    function buildMatchPatternFn(args) {
      return function(string) {
        var options = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
        var matchResult = string.match(args.matchPattern);
        if (!matchResult) return null;
        var matchedString = matchResult[0];
        var parseResult = string.match(args.parsePattern);
        if (!parseResult) return null;
        var value = args.valueCallback ? args.valueCallback(parseResult[0]) : parseResult[0];
        value = options.valueCallback ? options.valueCallback(value) : value;
        var rest = string.slice(matchedString.length);
        return {
          value,
          rest
        };
      };
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/en-US/_lib/match/index.js
var require_match = __commonJS({
  "node_modules/date-fns/locale/en-US/_lib/match/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_buildMatchFn());
    var _index2 = _interopRequireDefault(require_buildMatchPatternFn());
    var matchOrdinalNumberPattern = /^(\d+)(th|st|nd|rd)?/i;
    var parseOrdinalNumberPattern = /\d+/i;
    var matchEraPatterns = {
      narrow: /^(b|a)/i,
      abbreviated: /^(b\.?\s?c\.?|b\.?\s?c\.?\s?e\.?|a\.?\s?d\.?|c\.?\s?e\.?)/i,
      wide: /^(before christ|before common era|anno domini|common era)/i
    };
    var parseEraPatterns = {
      any: [/^b/i, /^(a|c)/i]
    };
    var matchQuarterPatterns = {
      narrow: /^[1234]/i,
      abbreviated: /^q[1234]/i,
      wide: /^[1234](th|st|nd|rd)? quarter/i
    };
    var parseQuarterPatterns = {
      any: [/1/i, /2/i, /3/i, /4/i]
    };
    var matchMonthPatterns = {
      narrow: /^[jfmasond]/i,
      abbreviated: /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i,
      wide: /^(january|february|march|april|may|june|july|august|september|october|november|december)/i
    };
    var parseMonthPatterns = {
      narrow: [/^j/i, /^f/i, /^m/i, /^a/i, /^m/i, /^j/i, /^j/i, /^a/i, /^s/i, /^o/i, /^n/i, /^d/i],
      any: [/^ja/i, /^f/i, /^mar/i, /^ap/i, /^may/i, /^jun/i, /^jul/i, /^au/i, /^s/i, /^o/i, /^n/i, /^d/i]
    };
    var matchDayPatterns = {
      narrow: /^[smtwf]/i,
      short: /^(su|mo|tu|we|th|fr|sa)/i,
      abbreviated: /^(sun|mon|tue|wed|thu|fri|sat)/i,
      wide: /^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/i
    };
    var parseDayPatterns = {
      narrow: [/^s/i, /^m/i, /^t/i, /^w/i, /^t/i, /^f/i, /^s/i],
      any: [/^su/i, /^m/i, /^tu/i, /^w/i, /^th/i, /^f/i, /^sa/i]
    };
    var matchDayPeriodPatterns = {
      narrow: /^(a|p|mi|n|(in the|at) (morning|afternoon|evening|night))/i,
      any: /^([ap]\.?\s?m\.?|midnight|noon|(in the|at) (morning|afternoon|evening|night))/i
    };
    var parseDayPeriodPatterns = {
      any: {
        am: /^a/i,
        pm: /^p/i,
        midnight: /^mi/i,
        noon: /^no/i,
        morning: /morning/i,
        afternoon: /afternoon/i,
        evening: /evening/i,
        night: /night/i
      }
    };
    var match = {
      ordinalNumber: (0, _index2.default)({
        matchPattern: matchOrdinalNumberPattern,
        parsePattern: parseOrdinalNumberPattern,
        valueCallback: function valueCallback(value) {
          return parseInt(value, 10);
        }
      }),
      era: (0, _index.default)({
        matchPatterns: matchEraPatterns,
        defaultMatchWidth: "wide",
        parsePatterns: parseEraPatterns,
        defaultParseWidth: "any"
      }),
      quarter: (0, _index.default)({
        matchPatterns: matchQuarterPatterns,
        defaultMatchWidth: "wide",
        parsePatterns: parseQuarterPatterns,
        defaultParseWidth: "any",
        valueCallback: function valueCallback(index) {
          return index + 1;
        }
      }),
      month: (0, _index.default)({
        matchPatterns: matchMonthPatterns,
        defaultMatchWidth: "wide",
        parsePatterns: parseMonthPatterns,
        defaultParseWidth: "any"
      }),
      day: (0, _index.default)({
        matchPatterns: matchDayPatterns,
        defaultMatchWidth: "wide",
        parsePatterns: parseDayPatterns,
        defaultParseWidth: "any"
      }),
      dayPeriod: (0, _index.default)({
        matchPatterns: matchDayPeriodPatterns,
        defaultMatchWidth: "any",
        parsePatterns: parseDayPeriodPatterns,
        defaultParseWidth: "any"
      })
    };
    var _default = match;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/locale/en-US/index.js
var require_en_US = __commonJS({
  "node_modules/date-fns/locale/en-US/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_formatDistance());
    var _index2 = _interopRequireDefault(require_formatLong());
    var _index3 = _interopRequireDefault(require_formatRelative());
    var _index4 = _interopRequireDefault(require_localize());
    var _index5 = _interopRequireDefault(require_match());
    var locale = {
      code: "en-US",
      formatDistance: _index.default,
      formatLong: _index2.default,
      formatRelative: _index3.default,
      localize: _index4.default,
      match: _index5.default,
      options: {
        weekStartsOn: 0,
        firstWeekContainsDate: 1
      }
    };
    var _default = locale;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/defaultLocale/index.js
var require_defaultLocale = __commonJS({
  "node_modules/date-fns/_lib/defaultLocale/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = void 0;
    var _index = _interopRequireDefault(require_en_US());
    var _default = _index.default;
    exports2.default = _default;
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/format/index.js
var require_format = __commonJS({
  "node_modules/date-fns/format/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = format2;
    var _index = _interopRequireDefault(require_isValid());
    var _index2 = _interopRequireDefault(require_subMilliseconds());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_formatters());
    var _index5 = _interopRequireDefault(require_longFormatters());
    var _index6 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index7 = require_protectedTokens();
    var _index8 = _interopRequireDefault(require_toInteger());
    var _index9 = _interopRequireDefault(require_requiredArgs());
    var _index10 = require_defaultOptions();
    var _index11 = _interopRequireDefault(require_defaultLocale());
    var formattingTokensRegExp = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g;
    var longFormattingTokensRegExp = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g;
    var escapedStringRegExp = /^'([^]*?)'?$/;
    var doubleQuoteRegExp = /''/g;
    var unescapedLatinCharacterRegExp = /[a-zA-Z]/;
    function format2(dirtyDate, dirtyFormatStr, options) {
      var _ref, _options$locale, _ref2, _ref3, _ref4, _options$firstWeekCon, _options$locale2, _options$locale2$opti, _defaultOptions$local, _defaultOptions$local2, _ref5, _ref6, _ref7, _options$weekStartsOn, _options$locale3, _options$locale3$opti, _defaultOptions$local3, _defaultOptions$local4;
      (0, _index9.default)(2, arguments);
      var formatStr = String(dirtyFormatStr);
      var defaultOptions3 = (0, _index10.getDefaultOptions)();
      var locale = (_ref = (_options$locale = options === null || options === void 0 ? void 0 : options.locale) !== null && _options$locale !== void 0 ? _options$locale : defaultOptions3.locale) !== null && _ref !== void 0 ? _ref : _index11.default;
      var firstWeekContainsDate = (0, _index8.default)((_ref2 = (_ref3 = (_ref4 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale2 = options.locale) === null || _options$locale2 === void 0 ? void 0 : (_options$locale2$opti = _options$locale2.options) === null || _options$locale2$opti === void 0 ? void 0 : _options$locale2$opti.firstWeekContainsDate) !== null && _ref4 !== void 0 ? _ref4 : defaultOptions3.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : 1);
      if (!(firstWeekContainsDate >= 1 && firstWeekContainsDate <= 7)) {
        throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
      }
      var weekStartsOn = (0, _index8.default)((_ref5 = (_ref6 = (_ref7 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale3 = options.locale) === null || _options$locale3 === void 0 ? void 0 : (_options$locale3$opti = _options$locale3.options) === null || _options$locale3$opti === void 0 ? void 0 : _options$locale3$opti.weekStartsOn) !== null && _ref7 !== void 0 ? _ref7 : defaultOptions3.weekStartsOn) !== null && _ref6 !== void 0 ? _ref6 : (_defaultOptions$local3 = defaultOptions3.locale) === null || _defaultOptions$local3 === void 0 ? void 0 : (_defaultOptions$local4 = _defaultOptions$local3.options) === null || _defaultOptions$local4 === void 0 ? void 0 : _defaultOptions$local4.weekStartsOn) !== null && _ref5 !== void 0 ? _ref5 : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      if (!locale.localize) {
        throw new RangeError("locale must contain localize property");
      }
      if (!locale.formatLong) {
        throw new RangeError("locale must contain formatLong property");
      }
      var originalDate = (0, _index3.default)(dirtyDate);
      if (!(0, _index.default)(originalDate)) {
        throw new RangeError("Invalid time value");
      }
      var timezoneOffset = (0, _index6.default)(originalDate);
      var utcDate = (0, _index2.default)(originalDate, timezoneOffset);
      var formatterOptions = {
        firstWeekContainsDate,
        weekStartsOn,
        locale,
        _originalDate: originalDate
      };
      var result = formatStr.match(longFormattingTokensRegExp).map(function(substring) {
        var firstCharacter = substring[0];
        if (firstCharacter === "p" || firstCharacter === "P") {
          var longFormatter = _index5.default[firstCharacter];
          return longFormatter(substring, locale.formatLong);
        }
        return substring;
      }).join("").match(formattingTokensRegExp).map(function(substring) {
        if (substring === "''") {
          return "'";
        }
        var firstCharacter = substring[0];
        if (firstCharacter === "'") {
          return cleanEscapedString(substring);
        }
        var formatter = _index4.default[firstCharacter];
        if (formatter) {
          if (!(options !== null && options !== void 0 && options.useAdditionalWeekYearTokens) && (0, _index7.isProtectedWeekYearToken)(substring)) {
            (0, _index7.throwProtectedError)(substring, dirtyFormatStr, String(dirtyDate));
          }
          if (!(options !== null && options !== void 0 && options.useAdditionalDayOfYearTokens) && (0, _index7.isProtectedDayOfYearToken)(substring)) {
            (0, _index7.throwProtectedError)(substring, dirtyFormatStr, String(dirtyDate));
          }
          return formatter(utcDate, substring, locale.localize, formatterOptions);
        }
        if (firstCharacter.match(unescapedLatinCharacterRegExp)) {
          throw new RangeError("Format string contains an unescaped latin alphabet character `" + firstCharacter + "`");
        }
        return substring;
      }).join("");
      return result;
    }
    function cleanEscapedString(input) {
      var matched = input.match(escapedStringRegExp);
      if (!matched) {
        return input;
      }
      return matched[1].replace(doubleQuoteRegExp, "'");
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/assign/index.js
var require_assign = __commonJS({
  "node_modules/date-fns/_lib/assign/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = assign;
    function assign(target, object) {
      if (target == null) {
        throw new TypeError("assign requires that input parameter not be null or undefined");
      }
      for (var property in object) {
        if (Object.prototype.hasOwnProperty.call(object, property)) {
          ;
          target[property] = object[property];
        }
      }
      return target;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/_lib/cloneObject/index.js
var require_cloneObject = __commonJS({
  "node_modules/date-fns/_lib/cloneObject/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = cloneObject;
    var _index = _interopRequireDefault(require_assign());
    function cloneObject(object) {
      return (0, _index.default)({}, object);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatDistance/index.js
var require_formatDistance2 = __commonJS({
  "node_modules/date-fns/formatDistance/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatDistance;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_compareAsc());
    var _index3 = _interopRequireDefault(require_differenceInMonths());
    var _index4 = _interopRequireDefault(require_differenceInSeconds());
    var _index5 = _interopRequireDefault(require_defaultLocale());
    var _index6 = _interopRequireDefault(require_toDate());
    var _index7 = _interopRequireDefault(require_cloneObject());
    var _index8 = _interopRequireDefault(require_assign());
    var _index9 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index10 = _interopRequireDefault(require_requiredArgs());
    var MINUTES_IN_DAY = 1440;
    var MINUTES_IN_ALMOST_TWO_DAYS = 2520;
    var MINUTES_IN_MONTH = 43200;
    var MINUTES_IN_TWO_MONTHS = 86400;
    function formatDistance(dirtyDate, dirtyBaseDate, options) {
      var _ref, _options$locale;
      (0, _index10.default)(2, arguments);
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      var locale = (_ref = (_options$locale = options === null || options === void 0 ? void 0 : options.locale) !== null && _options$locale !== void 0 ? _options$locale : defaultOptions3.locale) !== null && _ref !== void 0 ? _ref : _index5.default;
      if (!locale.formatDistance) {
        throw new RangeError("locale must contain formatDistance property");
      }
      var comparison = (0, _index2.default)(dirtyDate, dirtyBaseDate);
      if (isNaN(comparison)) {
        throw new RangeError("Invalid time value");
      }
      var localizeOptions = (0, _index8.default)((0, _index7.default)(options), {
        addSuffix: Boolean(options === null || options === void 0 ? void 0 : options.addSuffix),
        comparison
      });
      var dateLeft;
      var dateRight;
      if (comparison > 0) {
        dateLeft = (0, _index6.default)(dirtyBaseDate);
        dateRight = (0, _index6.default)(dirtyDate);
      } else {
        dateLeft = (0, _index6.default)(dirtyDate);
        dateRight = (0, _index6.default)(dirtyBaseDate);
      }
      var seconds = (0, _index4.default)(dateRight, dateLeft);
      var offsetInSeconds = ((0, _index9.default)(dateRight) - (0, _index9.default)(dateLeft)) / 1e3;
      var minutes = Math.round((seconds - offsetInSeconds) / 60);
      var months;
      if (minutes < 2) {
        if (options !== null && options !== void 0 && options.includeSeconds) {
          if (seconds < 5) {
            return locale.formatDistance("lessThanXSeconds", 5, localizeOptions);
          } else if (seconds < 10) {
            return locale.formatDistance("lessThanXSeconds", 10, localizeOptions);
          } else if (seconds < 20) {
            return locale.formatDistance("lessThanXSeconds", 20, localizeOptions);
          } else if (seconds < 40) {
            return locale.formatDistance("halfAMinute", 0, localizeOptions);
          } else if (seconds < 60) {
            return locale.formatDistance("lessThanXMinutes", 1, localizeOptions);
          } else {
            return locale.formatDistance("xMinutes", 1, localizeOptions);
          }
        } else {
          if (minutes === 0) {
            return locale.formatDistance("lessThanXMinutes", 1, localizeOptions);
          } else {
            return locale.formatDistance("xMinutes", minutes, localizeOptions);
          }
        }
      } else if (minutes < 45) {
        return locale.formatDistance("xMinutes", minutes, localizeOptions);
      } else if (minutes < 90) {
        return locale.formatDistance("aboutXHours", 1, localizeOptions);
      } else if (minutes < MINUTES_IN_DAY) {
        var hours = Math.round(minutes / 60);
        return locale.formatDistance("aboutXHours", hours, localizeOptions);
      } else if (minutes < MINUTES_IN_ALMOST_TWO_DAYS) {
        return locale.formatDistance("xDays", 1, localizeOptions);
      } else if (minutes < MINUTES_IN_MONTH) {
        var days = Math.round(minutes / MINUTES_IN_DAY);
        return locale.formatDistance("xDays", days, localizeOptions);
      } else if (minutes < MINUTES_IN_TWO_MONTHS) {
        months = Math.round(minutes / MINUTES_IN_MONTH);
        return locale.formatDistance("aboutXMonths", months, localizeOptions);
      }
      months = (0, _index3.default)(dateRight, dateLeft);
      if (months < 12) {
        var nearestMonth = Math.round(minutes / MINUTES_IN_MONTH);
        return locale.formatDistance("xMonths", nearestMonth, localizeOptions);
      } else {
        var monthsSinceStartOfYear = months % 12;
        var years = Math.floor(months / 12);
        if (monthsSinceStartOfYear < 3) {
          return locale.formatDistance("aboutXYears", years, localizeOptions);
        } else if (monthsSinceStartOfYear < 9) {
          return locale.formatDistance("overXYears", years, localizeOptions);
        } else {
          return locale.formatDistance("almostXYears", years + 1, localizeOptions);
        }
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatDistanceStrict/index.js
var require_formatDistanceStrict = __commonJS({
  "node_modules/date-fns/formatDistanceStrict/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatDistanceStrict;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index3 = _interopRequireDefault(require_compareAsc());
    var _index4 = _interopRequireDefault(require_toDate());
    var _index5 = _interopRequireDefault(require_cloneObject());
    var _index6 = _interopRequireDefault(require_assign());
    var _index7 = _interopRequireDefault(require_defaultLocale());
    var _index8 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_MINUTE = 1e3 * 60;
    var MINUTES_IN_DAY = 60 * 24;
    var MINUTES_IN_MONTH = MINUTES_IN_DAY * 30;
    var MINUTES_IN_YEAR = MINUTES_IN_DAY * 365;
    function formatDistanceStrict(dirtyDate, dirtyBaseDate, options) {
      var _ref, _options$locale, _options$roundingMeth;
      (0, _index8.default)(2, arguments);
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      var locale = (_ref = (_options$locale = options === null || options === void 0 ? void 0 : options.locale) !== null && _options$locale !== void 0 ? _options$locale : defaultOptions3.locale) !== null && _ref !== void 0 ? _ref : _index7.default;
      if (!locale.formatDistance) {
        throw new RangeError("locale must contain localize.formatDistance property");
      }
      var comparison = (0, _index3.default)(dirtyDate, dirtyBaseDate);
      if (isNaN(comparison)) {
        throw new RangeError("Invalid time value");
      }
      var localizeOptions = (0, _index6.default)((0, _index5.default)(options), {
        addSuffix: Boolean(options === null || options === void 0 ? void 0 : options.addSuffix),
        comparison
      });
      var dateLeft;
      var dateRight;
      if (comparison > 0) {
        dateLeft = (0, _index4.default)(dirtyBaseDate);
        dateRight = (0, _index4.default)(dirtyDate);
      } else {
        dateLeft = (0, _index4.default)(dirtyDate);
        dateRight = (0, _index4.default)(dirtyBaseDate);
      }
      var roundingMethod = String((_options$roundingMeth = options === null || options === void 0 ? void 0 : options.roundingMethod) !== null && _options$roundingMeth !== void 0 ? _options$roundingMeth : "round");
      var roundingMethodFn;
      if (roundingMethod === "floor") {
        roundingMethodFn = Math.floor;
      } else if (roundingMethod === "ceil") {
        roundingMethodFn = Math.ceil;
      } else if (roundingMethod === "round") {
        roundingMethodFn = Math.round;
      } else {
        throw new RangeError("roundingMethod must be 'floor', 'ceil' or 'round'");
      }
      var milliseconds = dateRight.getTime() - dateLeft.getTime();
      var minutes = milliseconds / MILLISECONDS_IN_MINUTE;
      var timezoneOffset = (0, _index2.default)(dateRight) - (0, _index2.default)(dateLeft);
      var dstNormalizedMinutes = (milliseconds - timezoneOffset) / MILLISECONDS_IN_MINUTE;
      var defaultUnit = options === null || options === void 0 ? void 0 : options.unit;
      var unit;
      if (!defaultUnit) {
        if (minutes < 1) {
          unit = "second";
        } else if (minutes < 60) {
          unit = "minute";
        } else if (minutes < MINUTES_IN_DAY) {
          unit = "hour";
        } else if (dstNormalizedMinutes < MINUTES_IN_MONTH) {
          unit = "day";
        } else if (dstNormalizedMinutes < MINUTES_IN_YEAR) {
          unit = "month";
        } else {
          unit = "year";
        }
      } else {
        unit = String(defaultUnit);
      }
      if (unit === "second") {
        var seconds = roundingMethodFn(milliseconds / 1e3);
        return locale.formatDistance("xSeconds", seconds, localizeOptions);
      } else if (unit === "minute") {
        var roundedMinutes = roundingMethodFn(minutes);
        return locale.formatDistance("xMinutes", roundedMinutes, localizeOptions);
      } else if (unit === "hour") {
        var hours = roundingMethodFn(minutes / 60);
        return locale.formatDistance("xHours", hours, localizeOptions);
      } else if (unit === "day") {
        var days = roundingMethodFn(dstNormalizedMinutes / MINUTES_IN_DAY);
        return locale.formatDistance("xDays", days, localizeOptions);
      } else if (unit === "month") {
        var months = roundingMethodFn(dstNormalizedMinutes / MINUTES_IN_MONTH);
        return months === 12 && defaultUnit !== "month" ? locale.formatDistance("xYears", 1, localizeOptions) : locale.formatDistance("xMonths", months, localizeOptions);
      } else if (unit === "year") {
        var years = roundingMethodFn(dstNormalizedMinutes / MINUTES_IN_YEAR);
        return locale.formatDistance("xYears", years, localizeOptions);
      }
      throw new RangeError("unit must be 'second', 'minute', 'hour', 'day', 'month' or 'year'");
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatDistanceToNow/index.js
var require_formatDistanceToNow = __commonJS({
  "node_modules/date-fns/formatDistanceToNow/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatDistanceToNow;
    var _index = _interopRequireDefault(require_formatDistance2());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function formatDistanceToNow(dirtyDate, options) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, Date.now(), options);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatDistanceToNowStrict/index.js
var require_formatDistanceToNowStrict = __commonJS({
  "node_modules/date-fns/formatDistanceToNowStrict/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatDistanceToNowStrict;
    var _index = _interopRequireDefault(require_formatDistanceStrict());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function formatDistanceToNowStrict(dirtyDate, options) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, Date.now(), options);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatDuration/index.js
var require_formatDuration = __commonJS({
  "node_modules/date-fns/formatDuration/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatDuration;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_defaultLocale());
    var defaultFormat = ["years", "months", "weeks", "days", "hours", "minutes", "seconds"];
    function formatDuration(duration, options) {
      var _ref, _options$locale, _options$format, _options$zero, _options$delimiter;
      if (arguments.length < 1) {
        throw new TypeError("1 argument required, but only ".concat(arguments.length, " present"));
      }
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      var locale = (_ref = (_options$locale = options === null || options === void 0 ? void 0 : options.locale) !== null && _options$locale !== void 0 ? _options$locale : defaultOptions3.locale) !== null && _ref !== void 0 ? _ref : _index2.default;
      var format2 = (_options$format = options === null || options === void 0 ? void 0 : options.format) !== null && _options$format !== void 0 ? _options$format : defaultFormat;
      var zero = (_options$zero = options === null || options === void 0 ? void 0 : options.zero) !== null && _options$zero !== void 0 ? _options$zero : false;
      var delimiter = (_options$delimiter = options === null || options === void 0 ? void 0 : options.delimiter) !== null && _options$delimiter !== void 0 ? _options$delimiter : " ";
      if (!locale.formatDistance) {
        return "";
      }
      var result = format2.reduce(function(acc, unit) {
        var token = "x".concat(unit.replace(/(^.)/, function(m) {
          return m.toUpperCase();
        }));
        var value = duration[unit];
        if (typeof value === "number" && (zero || duration[unit])) {
          return acc.concat(locale.formatDistance(token, value));
        }
        return acc;
      }, []).join(delimiter);
      return result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatISO/index.js
var require_formatISO = __commonJS({
  "node_modules/date-fns/formatISO/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatISO2;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_addLeadingZeros());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function formatISO2(date, options) {
      var _options$format, _options$representati;
      (0, _index3.default)(1, arguments);
      var originalDate = (0, _index.default)(date);
      if (isNaN(originalDate.getTime())) {
        throw new RangeError("Invalid time value");
      }
      var format2 = String((_options$format = options === null || options === void 0 ? void 0 : options.format) !== null && _options$format !== void 0 ? _options$format : "extended");
      var representation = String((_options$representati = options === null || options === void 0 ? void 0 : options.representation) !== null && _options$representati !== void 0 ? _options$representati : "complete");
      if (format2 !== "extended" && format2 !== "basic") {
        throw new RangeError("format must be 'extended' or 'basic'");
      }
      if (representation !== "date" && representation !== "time" && representation !== "complete") {
        throw new RangeError("representation must be 'date', 'time', or 'complete'");
      }
      var result = "";
      var tzOffset = "";
      var dateDelimiter = format2 === "extended" ? "-" : "";
      var timeDelimiter = format2 === "extended" ? ":" : "";
      if (representation !== "time") {
        var day = (0, _index2.default)(originalDate.getDate(), 2);
        var month = (0, _index2.default)(originalDate.getMonth() + 1, 2);
        var year = (0, _index2.default)(originalDate.getFullYear(), 4);
        result = "".concat(year).concat(dateDelimiter).concat(month).concat(dateDelimiter).concat(day);
      }
      if (representation !== "date") {
        var offset = originalDate.getTimezoneOffset();
        if (offset !== 0) {
          var absoluteOffset = Math.abs(offset);
          var hourOffset = (0, _index2.default)(Math.floor(absoluteOffset / 60), 2);
          var minuteOffset = (0, _index2.default)(absoluteOffset % 60, 2);
          var sign = offset < 0 ? "+" : "-";
          tzOffset = "".concat(sign).concat(hourOffset, ":").concat(minuteOffset);
        } else {
          tzOffset = "Z";
        }
        var hour = (0, _index2.default)(originalDate.getHours(), 2);
        var minute = (0, _index2.default)(originalDate.getMinutes(), 2);
        var second = (0, _index2.default)(originalDate.getSeconds(), 2);
        var separator = result === "" ? "" : "T";
        var time = [hour, minute, second].join(timeDelimiter);
        result = "".concat(result).concat(separator).concat(time).concat(tzOffset);
      }
      return result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatISO9075/index.js
var require_formatISO9075 = __commonJS({
  "node_modules/date-fns/formatISO9075/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatISO9075;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_isValid());
    var _index3 = _interopRequireDefault(require_addLeadingZeros());
    function formatISO9075(dirtyDate, options) {
      var _options$format, _options$representati;
      if (arguments.length < 1) {
        throw new TypeError("1 argument required, but only ".concat(arguments.length, " present"));
      }
      var originalDate = (0, _index.default)(dirtyDate);
      if (!(0, _index2.default)(originalDate)) {
        throw new RangeError("Invalid time value");
      }
      var format2 = String((_options$format = options === null || options === void 0 ? void 0 : options.format) !== null && _options$format !== void 0 ? _options$format : "extended");
      var representation = String((_options$representati = options === null || options === void 0 ? void 0 : options.representation) !== null && _options$representati !== void 0 ? _options$representati : "complete");
      if (format2 !== "extended" && format2 !== "basic") {
        throw new RangeError("format must be 'extended' or 'basic'");
      }
      if (representation !== "date" && representation !== "time" && representation !== "complete") {
        throw new RangeError("representation must be 'date', 'time', or 'complete'");
      }
      var result = "";
      var dateDelimiter = format2 === "extended" ? "-" : "";
      var timeDelimiter = format2 === "extended" ? ":" : "";
      if (representation !== "time") {
        var day = (0, _index3.default)(originalDate.getDate(), 2);
        var month = (0, _index3.default)(originalDate.getMonth() + 1, 2);
        var year = (0, _index3.default)(originalDate.getFullYear(), 4);
        result = "".concat(year).concat(dateDelimiter).concat(month).concat(dateDelimiter).concat(day);
      }
      if (representation !== "date") {
        var hour = (0, _index3.default)(originalDate.getHours(), 2);
        var minute = (0, _index3.default)(originalDate.getMinutes(), 2);
        var second = (0, _index3.default)(originalDate.getSeconds(), 2);
        var separator = result === "" ? "" : " ";
        result = "".concat(result).concat(separator).concat(hour).concat(timeDelimiter).concat(minute).concat(timeDelimiter).concat(second);
      }
      return result;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatISODuration/index.js
var require_formatISODuration = __commonJS({
  "node_modules/date-fns/formatISODuration/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatISODuration;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_requiredArgs());
    function formatISODuration(duration) {
      (0, _index.default)(1, arguments);
      if ((0, _typeof2.default)(duration) !== "object") throw new Error("Duration must be an object");
      var _duration$years = duration.years, years = _duration$years === void 0 ? 0 : _duration$years, _duration$months = duration.months, months = _duration$months === void 0 ? 0 : _duration$months, _duration$days = duration.days, days = _duration$days === void 0 ? 0 : _duration$days, _duration$hours = duration.hours, hours = _duration$hours === void 0 ? 0 : _duration$hours, _duration$minutes = duration.minutes, minutes = _duration$minutes === void 0 ? 0 : _duration$minutes, _duration$seconds = duration.seconds, seconds = _duration$seconds === void 0 ? 0 : _duration$seconds;
      return "P".concat(years, "Y").concat(months, "M").concat(days, "DT").concat(hours, "H").concat(minutes, "M").concat(seconds, "S");
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatRFC3339/index.js
var require_formatRFC3339 = __commonJS({
  "node_modules/date-fns/formatRFC3339/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatRFC3339;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_isValid());
    var _index3 = _interopRequireDefault(require_addLeadingZeros());
    var _index4 = _interopRequireDefault(require_toInteger());
    function formatRFC3339(dirtyDate, options) {
      var _options$fractionDigi;
      if (arguments.length < 1) {
        throw new TypeError("1 arguments required, but only ".concat(arguments.length, " present"));
      }
      var originalDate = (0, _index.default)(dirtyDate);
      if (!(0, _index2.default)(originalDate)) {
        throw new RangeError("Invalid time value");
      }
      var fractionDigits = Number((_options$fractionDigi = options === null || options === void 0 ? void 0 : options.fractionDigits) !== null && _options$fractionDigi !== void 0 ? _options$fractionDigi : 0);
      if (!(fractionDigits >= 0 && fractionDigits <= 3)) {
        throw new RangeError("fractionDigits must be between 0 and 3 inclusively");
      }
      var day = (0, _index3.default)(originalDate.getDate(), 2);
      var month = (0, _index3.default)(originalDate.getMonth() + 1, 2);
      var year = originalDate.getFullYear();
      var hour = (0, _index3.default)(originalDate.getHours(), 2);
      var minute = (0, _index3.default)(originalDate.getMinutes(), 2);
      var second = (0, _index3.default)(originalDate.getSeconds(), 2);
      var fractionalSecond = "";
      if (fractionDigits > 0) {
        var milliseconds = originalDate.getMilliseconds();
        var fractionalSeconds = Math.floor(milliseconds * Math.pow(10, fractionDigits - 3));
        fractionalSecond = "." + (0, _index3.default)(fractionalSeconds, fractionDigits);
      }
      var offset = "";
      var tzOffset = originalDate.getTimezoneOffset();
      if (tzOffset !== 0) {
        var absoluteOffset = Math.abs(tzOffset);
        var hourOffset = (0, _index3.default)((0, _index4.default)(absoluteOffset / 60), 2);
        var minuteOffset = (0, _index3.default)(absoluteOffset % 60, 2);
        var sign = tzOffset < 0 ? "+" : "-";
        offset = "".concat(sign).concat(hourOffset, ":").concat(minuteOffset);
      } else {
        offset = "Z";
      }
      return "".concat(year, "-").concat(month, "-").concat(day, "T").concat(hour, ":").concat(minute, ":").concat(second).concat(fractionalSecond).concat(offset);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatRFC7231/index.js
var require_formatRFC7231 = __commonJS({
  "node_modules/date-fns/formatRFC7231/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatRFC7231;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_isValid());
    var _index3 = _interopRequireDefault(require_addLeadingZeros());
    var days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    function formatRFC7231(dirtyDate) {
      if (arguments.length < 1) {
        throw new TypeError("1 arguments required, but only ".concat(arguments.length, " present"));
      }
      var originalDate = (0, _index.default)(dirtyDate);
      if (!(0, _index2.default)(originalDate)) {
        throw new RangeError("Invalid time value");
      }
      var dayName = days[originalDate.getUTCDay()];
      var dayOfMonth = (0, _index3.default)(originalDate.getUTCDate(), 2);
      var monthName = months[originalDate.getUTCMonth()];
      var year = originalDate.getUTCFullYear();
      var hour = (0, _index3.default)(originalDate.getUTCHours(), 2);
      var minute = (0, _index3.default)(originalDate.getUTCMinutes(), 2);
      var second = (0, _index3.default)(originalDate.getUTCSeconds(), 2);
      return "".concat(dayName, ", ").concat(dayOfMonth, " ").concat(monthName, " ").concat(year, " ").concat(hour, ":").concat(minute, ":").concat(second, " GMT");
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/formatRelative/index.js
var require_formatRelative2 = __commonJS({
  "node_modules/date-fns/formatRelative/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = formatRelative;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index3 = _interopRequireDefault(require_format());
    var _index4 = _interopRequireDefault(require_defaultLocale());
    var _index5 = _interopRequireDefault(require_subMilliseconds());
    var _index6 = _interopRequireDefault(require_toDate());
    var _index7 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index8 = _interopRequireDefault(require_requiredArgs());
    var _index9 = _interopRequireDefault(require_toInteger());
    function formatRelative(dirtyDate, dirtyBaseDate, options) {
      var _ref, _options$locale, _ref2, _ref3, _ref4, _options$weekStartsOn, _options$locale2, _options$locale2$opti, _defaultOptions$local, _defaultOptions$local2;
      (0, _index8.default)(2, arguments);
      var date = (0, _index6.default)(dirtyDate);
      var baseDate = (0, _index6.default)(dirtyBaseDate);
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      var locale = (_ref = (_options$locale = options === null || options === void 0 ? void 0 : options.locale) !== null && _options$locale !== void 0 ? _options$locale : defaultOptions3.locale) !== null && _ref !== void 0 ? _ref : _index4.default;
      var weekStartsOn = (0, _index9.default)((_ref2 = (_ref3 = (_ref4 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale2 = options.locale) === null || _options$locale2 === void 0 ? void 0 : (_options$locale2$opti = _options$locale2.options) === null || _options$locale2$opti === void 0 ? void 0 : _options$locale2$opti.weekStartsOn) !== null && _ref4 !== void 0 ? _ref4 : defaultOptions3.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : 0);
      if (!locale.localize) {
        throw new RangeError("locale must contain localize property");
      }
      if (!locale.formatLong) {
        throw new RangeError("locale must contain formatLong property");
      }
      if (!locale.formatRelative) {
        throw new RangeError("locale must contain formatRelative property");
      }
      var diff = (0, _index2.default)(date, baseDate);
      if (isNaN(diff)) {
        throw new RangeError("Invalid time value");
      }
      var token;
      if (diff < -6) {
        token = "other";
      } else if (diff < -1) {
        token = "lastWeek";
      } else if (diff < 0) {
        token = "yesterday";
      } else if (diff < 1) {
        token = "today";
      } else if (diff < 2) {
        token = "tomorrow";
      } else if (diff < 7) {
        token = "nextWeek";
      } else {
        token = "other";
      }
      var utcDate = (0, _index5.default)(date, (0, _index7.default)(date));
      var utcBaseDate = (0, _index5.default)(baseDate, (0, _index7.default)(baseDate));
      var formatStr = locale.formatRelative(token, utcDate, utcBaseDate, {
        locale,
        weekStartsOn
      });
      return (0, _index3.default)(date, formatStr, {
        locale,
        weekStartsOn
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/fromUnixTime/index.js
var require_fromUnixTime = __commonJS({
  "node_modules/date-fns/fromUnixTime/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = fromUnixTime;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_toInteger());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function fromUnixTime(dirtyUnixTime) {
      (0, _index3.default)(1, arguments);
      var unixTime = (0, _index2.default)(dirtyUnixTime);
      return (0, _index.default)(unixTime * 1e3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDate/index.js
var require_getDate = __commonJS({
  "node_modules/date-fns/getDate/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDate;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getDate(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var dayOfMonth = date.getDate();
      return dayOfMonth;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDay/index.js
var require_getDay = __commonJS({
  "node_modules/date-fns/getDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDay;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getDay(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var day = date.getDay();
      return day;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDayOfYear/index.js
var require_getDayOfYear = __commonJS({
  "node_modules/date-fns/getDayOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDayOfYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_startOfYear());
    var _index3 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function getDayOfYear(dirtyDate) {
      (0, _index4.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var diff = (0, _index3.default)(date, (0, _index2.default)(date));
      var dayOfYear = diff + 1;
      return dayOfYear;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDaysInMonth/index.js
var require_getDaysInMonth = __commonJS({
  "node_modules/date-fns/getDaysInMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDaysInMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getDaysInMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      var monthIndex = date.getMonth();
      var lastDayOfMonth = /* @__PURE__ */ new Date(0);
      lastDayOfMonth.setFullYear(year, monthIndex + 1, 0);
      lastDayOfMonth.setHours(0, 0, 0, 0);
      return lastDayOfMonth.getDate();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isLeapYear/index.js
var require_isLeapYear = __commonJS({
  "node_modules/date-fns/isLeapYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isLeapYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isLeapYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      return year % 400 === 0 || year % 4 === 0 && year % 100 !== 0;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDaysInYear/index.js
var require_getDaysInYear = __commonJS({
  "node_modules/date-fns/getDaysInYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDaysInYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_isLeapYear());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function getDaysInYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      if (String(new Date(date)) === "Invalid Date") {
        return NaN;
      }
      return (0, _index2.default)(date) ? 366 : 365;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDecade/index.js
var require_getDecade = __commonJS({
  "node_modules/date-fns/getDecade/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDecade;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getDecade(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      var decade = Math.floor(year / 10) * 10;
      return decade;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getDefaultOptions/index.js
var require_getDefaultOptions = __commonJS({
  "node_modules/date-fns/getDefaultOptions/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getDefaultOptions;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_assign());
    function getDefaultOptions() {
      return (0, _index2.default)({}, (0, _index.getDefaultOptions)());
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getHours/index.js
var require_getHours = __commonJS({
  "node_modules/date-fns/getHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getHours;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getHours(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var hours = date.getHours();
      return hours;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getISODay/index.js
var require_getISODay = __commonJS({
  "node_modules/date-fns/getISODay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getISODay;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getISODay(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var day = date.getDay();
      if (day === 0) {
        day = 7;
      }
      return day;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getISOWeek/index.js
var require_getISOWeek = __commonJS({
  "node_modules/date-fns/getISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getISOWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_startOfISOWeek());
    var _index3 = _interopRequireDefault(require_startOfISOWeekYear());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function getISOWeek(dirtyDate) {
      (0, _index4.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var diff = (0, _index2.default)(date).getTime() - (0, _index3.default)(date).getTime();
      return Math.round(diff / MILLISECONDS_IN_WEEK) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getISOWeeksInYear/index.js
var require_getISOWeeksInYear = __commonJS({
  "node_modules/date-fns/getISOWeeksInYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getISOWeeksInYear;
    var _index = _interopRequireDefault(require_startOfISOWeekYear());
    var _index2 = _interopRequireDefault(require_addWeeks());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function getISOWeeksInYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var thisYear = (0, _index.default)(dirtyDate);
      var nextYear = (0, _index.default)((0, _index2.default)(thisYear, 60));
      var diff = nextYear.valueOf() - thisYear.valueOf();
      return Math.round(diff / MILLISECONDS_IN_WEEK);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getMilliseconds/index.js
var require_getMilliseconds = __commonJS({
  "node_modules/date-fns/getMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getMilliseconds;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getMilliseconds(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var milliseconds = date.getMilliseconds();
      return milliseconds;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getMinutes/index.js
var require_getMinutes = __commonJS({
  "node_modules/date-fns/getMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getMinutes;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getMinutes(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var minutes = date.getMinutes();
      return minutes;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getMonth/index.js
var require_getMonth = __commonJS({
  "node_modules/date-fns/getMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var month = date.getMonth();
      return month;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getOverlappingDaysInIntervals/index.js
var require_getOverlappingDaysInIntervals = __commonJS({
  "node_modules/date-fns/getOverlappingDaysInIntervals/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getOverlappingDaysInIntervals;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_DAY = 24 * 60 * 60 * 1e3;
    function getOverlappingDaysInIntervals(dirtyIntervalLeft, dirtyIntervalRight) {
      (0, _index2.default)(2, arguments);
      var intervalLeft = dirtyIntervalLeft || {};
      var intervalRight = dirtyIntervalRight || {};
      var leftStartTime = (0, _index.default)(intervalLeft.start).getTime();
      var leftEndTime = (0, _index.default)(intervalLeft.end).getTime();
      var rightStartTime = (0, _index.default)(intervalRight.start).getTime();
      var rightEndTime = (0, _index.default)(intervalRight.end).getTime();
      if (!(leftStartTime <= leftEndTime && rightStartTime <= rightEndTime)) {
        throw new RangeError("Invalid interval");
      }
      var isOverlapping = leftStartTime < rightEndTime && rightStartTime < leftEndTime;
      if (!isOverlapping) {
        return 0;
      }
      var overlapStartDate = rightStartTime < leftStartTime ? leftStartTime : rightStartTime;
      var overlapEndDate = rightEndTime > leftEndTime ? leftEndTime : rightEndTime;
      var differenceInMs = overlapEndDate - overlapStartDate;
      return Math.ceil(differenceInMs / MILLISECONDS_IN_DAY);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getSeconds/index.js
var require_getSeconds = __commonJS({
  "node_modules/date-fns/getSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getSeconds;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getSeconds(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var seconds = date.getSeconds();
      return seconds;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getTime/index.js
var require_getTime = __commonJS({
  "node_modules/date-fns/getTime/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getTime;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getTime(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var timestamp = date.getTime();
      return timestamp;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getUnixTime/index.js
var require_getUnixTime = __commonJS({
  "node_modules/date-fns/getUnixTime/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getUnixTime;
    var _index = _interopRequireDefault(require_getTime());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getUnixTime(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return Math.floor((0, _index.default)(dirtyDate) / 1e3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getWeekYear/index.js
var require_getWeekYear = __commonJS({
  "node_modules/date-fns/getWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getWeekYear;
    var _index = _interopRequireDefault(require_startOfWeek());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var _index5 = require_defaultOptions();
    function getWeekYear(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$firstWeekCon, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index4.default)(1, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var year = date.getFullYear();
      var defaultOptions3 = (0, _index5.getDefaultOptions)();
      var firstWeekContainsDate = (0, _index3.default)((_ref = (_ref2 = (_ref3 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref !== void 0 ? _ref : 1);
      if (!(firstWeekContainsDate >= 1 && firstWeekContainsDate <= 7)) {
        throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
      }
      var firstWeekOfNextYear = /* @__PURE__ */ new Date(0);
      firstWeekOfNextYear.setFullYear(year + 1, 0, firstWeekContainsDate);
      firstWeekOfNextYear.setHours(0, 0, 0, 0);
      var startOfNextYear = (0, _index.default)(firstWeekOfNextYear, options);
      var firstWeekOfThisYear = /* @__PURE__ */ new Date(0);
      firstWeekOfThisYear.setFullYear(year, 0, firstWeekContainsDate);
      firstWeekOfThisYear.setHours(0, 0, 0, 0);
      var startOfThisYear = (0, _index.default)(firstWeekOfThisYear, options);
      if (date.getTime() >= startOfNextYear.getTime()) {
        return year + 1;
      } else if (date.getTime() >= startOfThisYear.getTime()) {
        return year;
      } else {
        return year - 1;
      }
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfWeekYear/index.js
var require_startOfWeekYear = __commonJS({
  "node_modules/date-fns/startOfWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfWeekYear;
    var _index = _interopRequireDefault(require_getWeekYear());
    var _index2 = _interopRequireDefault(require_startOfWeek());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var _index5 = require_defaultOptions();
    function startOfWeekYear(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$firstWeekCon, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index4.default)(1, arguments);
      var defaultOptions3 = (0, _index5.getDefaultOptions)();
      var firstWeekContainsDate = (0, _index3.default)((_ref = (_ref2 = (_ref3 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref !== void 0 ? _ref : 1);
      var year = (0, _index.default)(dirtyDate, options);
      var firstWeek = /* @__PURE__ */ new Date(0);
      firstWeek.setFullYear(year, 0, firstWeekContainsDate);
      firstWeek.setHours(0, 0, 0, 0);
      var date = (0, _index2.default)(firstWeek, options);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getWeek/index.js
var require_getWeek = __commonJS({
  "node_modules/date-fns/getWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getWeek;
    var _index = _interopRequireDefault(require_startOfWeek());
    var _index2 = _interopRequireDefault(require_startOfWeekYear());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var MILLISECONDS_IN_WEEK = 6048e5;
    function getWeek(dirtyDate, options) {
      (0, _index4.default)(1, arguments);
      var date = (0, _index3.default)(dirtyDate);
      var diff = (0, _index.default)(date, options).getTime() - (0, _index2.default)(date, options).getTime();
      return Math.round(diff / MILLISECONDS_IN_WEEK) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getWeekOfMonth/index.js
var require_getWeekOfMonth = __commonJS({
  "node_modules/date-fns/getWeekOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getWeekOfMonth;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_getDate());
    var _index3 = _interopRequireDefault(require_getDay());
    var _index4 = _interopRequireDefault(require_startOfMonth());
    var _index5 = _interopRequireDefault(require_requiredArgs());
    var _index6 = _interopRequireDefault(require_toInteger());
    function getWeekOfMonth(date, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index5.default)(1, arguments);
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      var weekStartsOn = (0, _index6.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      var currentDayOfMonth = (0, _index2.default)(date);
      if (isNaN(currentDayOfMonth)) return NaN;
      var startWeekDay = (0, _index3.default)((0, _index4.default)(date));
      var lastDayOfFirstWeek = weekStartsOn - startWeekDay;
      if (lastDayOfFirstWeek <= 0) lastDayOfFirstWeek += 7;
      var remainingDaysAfterFirstWeek = currentDayOfMonth - lastDayOfFirstWeek;
      return Math.ceil(remainingDaysAfterFirstWeek / 7) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfMonth/index.js
var require_lastDayOfMonth = __commonJS({
  "node_modules/date-fns/lastDayOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function lastDayOfMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var month = date.getMonth();
      date.setFullYear(date.getFullYear(), month + 1, 0);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getWeeksInMonth/index.js
var require_getWeeksInMonth = __commonJS({
  "node_modules/date-fns/getWeeksInMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getWeeksInMonth;
    var _index = _interopRequireDefault(require_differenceInCalendarWeeks());
    var _index2 = _interopRequireDefault(require_lastDayOfMonth());
    var _index3 = _interopRequireDefault(require_startOfMonth());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function getWeeksInMonth(date, options) {
      (0, _index4.default)(1, arguments);
      return (0, _index.default)((0, _index2.default)(date), (0, _index3.default)(date), options) + 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/getYear/index.js
var require_getYear = __commonJS({
  "node_modules/date-fns/getYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = getYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function getYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getFullYear();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/hoursToMilliseconds/index.js
var require_hoursToMilliseconds = __commonJS({
  "node_modules/date-fns/hoursToMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = hoursToMilliseconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function hoursToMilliseconds(hours) {
      (0, _index.default)(1, arguments);
      return Math.floor(hours * _index2.millisecondsInHour);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/hoursToMinutes/index.js
var require_hoursToMinutes = __commonJS({
  "node_modules/date-fns/hoursToMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = hoursToMinutes;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function hoursToMinutes(hours) {
      (0, _index.default)(1, arguments);
      return Math.floor(hours * _index2.minutesInHour);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/hoursToSeconds/index.js
var require_hoursToSeconds = __commonJS({
  "node_modules/date-fns/hoursToSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = hoursToSeconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function hoursToSeconds(hours) {
      (0, _index.default)(1, arguments);
      return Math.floor(hours * _index2.secondsInHour);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/intervalToDuration/index.js
var require_intervalToDuration = __commonJS({
  "node_modules/date-fns/intervalToDuration/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = intervalToDuration;
    var _index = _interopRequireDefault(require_compareAsc());
    var _index2 = _interopRequireDefault(require_add());
    var _index3 = _interopRequireDefault(require_differenceInDays());
    var _index4 = _interopRequireDefault(require_differenceInHours());
    var _index5 = _interopRequireDefault(require_differenceInMinutes());
    var _index6 = _interopRequireDefault(require_differenceInMonths());
    var _index7 = _interopRequireDefault(require_differenceInSeconds());
    var _index8 = _interopRequireDefault(require_differenceInYears());
    var _index9 = _interopRequireDefault(require_toDate());
    var _index10 = _interopRequireDefault(require_requiredArgs());
    function intervalToDuration(interval) {
      (0, _index10.default)(1, arguments);
      var start = (0, _index9.default)(interval.start);
      var end = (0, _index9.default)(interval.end);
      if (isNaN(start.getTime())) throw new RangeError("Start Date is invalid");
      if (isNaN(end.getTime())) throw new RangeError("End Date is invalid");
      var duration = {};
      duration.years = Math.abs((0, _index8.default)(end, start));
      var sign = (0, _index.default)(end, start);
      var remainingMonths = (0, _index2.default)(start, {
        years: sign * duration.years
      });
      duration.months = Math.abs((0, _index6.default)(end, remainingMonths));
      var remainingDays = (0, _index2.default)(remainingMonths, {
        months: sign * duration.months
      });
      duration.days = Math.abs((0, _index3.default)(end, remainingDays));
      var remainingHours = (0, _index2.default)(remainingDays, {
        days: sign * duration.days
      });
      duration.hours = Math.abs((0, _index4.default)(end, remainingHours));
      var remainingMinutes = (0, _index2.default)(remainingHours, {
        hours: sign * duration.hours
      });
      duration.minutes = Math.abs((0, _index5.default)(end, remainingMinutes));
      var remainingSeconds = (0, _index2.default)(remainingMinutes, {
        minutes: sign * duration.minutes
      });
      duration.seconds = Math.abs((0, _index7.default)(end, remainingSeconds));
      return duration;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/intlFormat/index.js
var require_intlFormat = __commonJS({
  "node_modules/date-fns/intlFormat/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = intlFormat;
    var _index = _interopRequireDefault(require_requiredArgs());
    function intlFormat(date, formatOrLocale, localeOptions) {
      var _localeOptions;
      (0, _index.default)(1, arguments);
      var formatOptions;
      if (isFormatOptions(formatOrLocale)) {
        formatOptions = formatOrLocale;
      } else {
        localeOptions = formatOrLocale;
      }
      return new Intl.DateTimeFormat((_localeOptions = localeOptions) === null || _localeOptions === void 0 ? void 0 : _localeOptions.locale, formatOptions).format(date);
    }
    function isFormatOptions(opts) {
      return opts !== void 0 && !("locale" in opts);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/intlFormatDistance/index.js
var require_intlFormatDistance = __commonJS({
  "node_modules/date-fns/intlFormatDistance/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = intlFormatDistance;
    var _index = require_constants();
    var _index2 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index3 = _interopRequireDefault(require_differenceInCalendarMonths());
    var _index4 = _interopRequireDefault(require_differenceInCalendarQuarters());
    var _index5 = _interopRequireDefault(require_differenceInCalendarWeeks());
    var _index6 = _interopRequireDefault(require_differenceInCalendarYears());
    var _index7 = _interopRequireDefault(require_differenceInHours());
    var _index8 = _interopRequireDefault(require_differenceInMinutes());
    var _index9 = _interopRequireDefault(require_differenceInSeconds());
    var _index10 = _interopRequireDefault(require_toDate());
    var _index11 = _interopRequireDefault(require_requiredArgs());
    function intlFormatDistance(date, baseDate, options) {
      (0, _index11.default)(2, arguments);
      var value = 0;
      var unit;
      var dateLeft = (0, _index10.default)(date);
      var dateRight = (0, _index10.default)(baseDate);
      if (!(options !== null && options !== void 0 && options.unit)) {
        var diffInSeconds = (0, _index9.default)(dateLeft, dateRight);
        if (Math.abs(diffInSeconds) < _index.secondsInMinute) {
          value = (0, _index9.default)(dateLeft, dateRight);
          unit = "second";
        } else if (Math.abs(diffInSeconds) < _index.secondsInHour) {
          value = (0, _index8.default)(dateLeft, dateRight);
          unit = "minute";
        } else if (Math.abs(diffInSeconds) < _index.secondsInDay && Math.abs((0, _index2.default)(dateLeft, dateRight)) < 1) {
          value = (0, _index7.default)(dateLeft, dateRight);
          unit = "hour";
        } else if (Math.abs(diffInSeconds) < _index.secondsInWeek && (value = (0, _index2.default)(dateLeft, dateRight)) && Math.abs(value) < 7) {
          unit = "day";
        } else if (Math.abs(diffInSeconds) < _index.secondsInMonth) {
          value = (0, _index5.default)(dateLeft, dateRight);
          unit = "week";
        } else if (Math.abs(diffInSeconds) < _index.secondsInQuarter) {
          value = (0, _index3.default)(dateLeft, dateRight);
          unit = "month";
        } else if (Math.abs(diffInSeconds) < _index.secondsInYear) {
          if ((0, _index4.default)(dateLeft, dateRight) < 4) {
            value = (0, _index4.default)(dateLeft, dateRight);
            unit = "quarter";
          } else {
            value = (0, _index6.default)(dateLeft, dateRight);
            unit = "year";
          }
        } else {
          value = (0, _index6.default)(dateLeft, dateRight);
          unit = "year";
        }
      } else {
        unit = options === null || options === void 0 ? void 0 : options.unit;
        if (unit === "second") {
          value = (0, _index9.default)(dateLeft, dateRight);
        } else if (unit === "minute") {
          value = (0, _index8.default)(dateLeft, dateRight);
        } else if (unit === "hour") {
          value = (0, _index7.default)(dateLeft, dateRight);
        } else if (unit === "day") {
          value = (0, _index2.default)(dateLeft, dateRight);
        } else if (unit === "week") {
          value = (0, _index5.default)(dateLeft, dateRight);
        } else if (unit === "month") {
          value = (0, _index3.default)(dateLeft, dateRight);
        } else if (unit === "quarter") {
          value = (0, _index4.default)(dateLeft, dateRight);
        } else if (unit === "year") {
          value = (0, _index6.default)(dateLeft, dateRight);
        }
      }
      var rtf = new Intl.RelativeTimeFormat(options === null || options === void 0 ? void 0 : options.locale, {
        localeMatcher: options === null || options === void 0 ? void 0 : options.localeMatcher,
        numeric: (options === null || options === void 0 ? void 0 : options.numeric) || "auto",
        style: options === null || options === void 0 ? void 0 : options.style
      });
      return rtf.format(value, unit);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isAfter/index.js
var require_isAfter = __commonJS({
  "node_modules/date-fns/isAfter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isAfter;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isAfter(dirtyDate, dirtyDateToCompare) {
      (0, _index2.default)(2, arguments);
      var date = (0, _index.default)(dirtyDate);
      var dateToCompare = (0, _index.default)(dirtyDateToCompare);
      return date.getTime() > dateToCompare.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isBefore/index.js
var require_isBefore = __commonJS({
  "node_modules/date-fns/isBefore/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isBefore;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isBefore(dirtyDate, dirtyDateToCompare) {
      (0, _index2.default)(2, arguments);
      var date = (0, _index.default)(dirtyDate);
      var dateToCompare = (0, _index.default)(dirtyDateToCompare);
      return date.getTime() < dateToCompare.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isEqual/index.js
var require_isEqual = __commonJS({
  "node_modules/date-fns/isEqual/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isEqual;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isEqual(dirtyLeftDate, dirtyRightDate) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyLeftDate);
      var dateRight = (0, _index.default)(dirtyRightDate);
      return dateLeft.getTime() === dateRight.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isExists/index.js
var require_isExists = __commonJS({
  "node_modules/date-fns/isExists/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isExists;
    function isExists(year, month, day) {
      if (arguments.length < 3) {
        throw new TypeError("3 argument required, but only " + arguments.length + " present");
      }
      var date = new Date(year, month, day);
      return date.getFullYear() === year && date.getMonth() === month && date.getDate() === day;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isFirstDayOfMonth/index.js
var require_isFirstDayOfMonth = __commonJS({
  "node_modules/date-fns/isFirstDayOfMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isFirstDayOfMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isFirstDayOfMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDate() === 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isFriday/index.js
var require_isFriday = __commonJS({
  "node_modules/date-fns/isFriday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isFriday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isFriday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDay() === 5;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isFuture/index.js
var require_isFuture = __commonJS({
  "node_modules/date-fns/isFuture/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isFuture;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isFuture(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getTime() > Date.now();
    }
    module.exports = exports2.default;
  }
});

// node_modules/@babel/runtime/helpers/arrayLikeToArray.js
var require_arrayLikeToArray = __commonJS({
  "node_modules/@babel/runtime/helpers/arrayLikeToArray.js"(exports2, module) {
    function _arrayLikeToArray(r, a) {
      (null == a || a > r.length) && (a = r.length);
      for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e];
      return n;
    }
    module.exports = _arrayLikeToArray, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/unsupportedIterableToArray.js
var require_unsupportedIterableToArray = __commonJS({
  "node_modules/@babel/runtime/helpers/unsupportedIterableToArray.js"(exports2, module) {
    var arrayLikeToArray = require_arrayLikeToArray();
    function _unsupportedIterableToArray(r, a) {
      if (r) {
        if ("string" == typeof r) return arrayLikeToArray(r, a);
        var t = {}.toString.call(r).slice(8, -1);
        return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? arrayLikeToArray(r, a) : void 0;
      }
    }
    module.exports = _unsupportedIterableToArray, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/createForOfIteratorHelper.js
var require_createForOfIteratorHelper = __commonJS({
  "node_modules/@babel/runtime/helpers/createForOfIteratorHelper.js"(exports2, module) {
    var unsupportedIterableToArray = require_unsupportedIterableToArray();
    function _createForOfIteratorHelper(r, e) {
      var t = "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"];
      if (!t) {
        if (Array.isArray(r) || (t = unsupportedIterableToArray(r)) || e && r && "number" == typeof r.length) {
          t && (r = t);
          var _n = 0, F = function F2() {
          };
          return {
            s: F,
            n: function n() {
              return _n >= r.length ? {
                done: true
              } : {
                done: false,
                value: r[_n++]
              };
            },
            e: function e2(r2) {
              throw r2;
            },
            f: F
          };
        }
        throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
      }
      var o, a = true, u = false;
      return {
        s: function s() {
          t = t.call(r);
        },
        n: function n() {
          var r2 = t.next();
          return a = r2.done, r2;
        },
        e: function e2(r2) {
          u = true, o = r2;
        },
        f: function f() {
          try {
            a || null == t["return"] || t["return"]();
          } finally {
            if (u) throw o;
          }
        }
      };
    }
    module.exports = _createForOfIteratorHelper, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/assertThisInitialized.js
var require_assertThisInitialized = __commonJS({
  "node_modules/@babel/runtime/helpers/assertThisInitialized.js"(exports2, module) {
    function _assertThisInitialized(e) {
      if (void 0 === e) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
      return e;
    }
    module.exports = _assertThisInitialized, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/setPrototypeOf.js
var require_setPrototypeOf = __commonJS({
  "node_modules/@babel/runtime/helpers/setPrototypeOf.js"(exports2, module) {
    function _setPrototypeOf(t, e) {
      return module.exports = _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(t2, e2) {
        return t2.__proto__ = e2, t2;
      }, module.exports.__esModule = true, module.exports["default"] = module.exports, _setPrototypeOf(t, e);
    }
    module.exports = _setPrototypeOf, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/inherits.js
var require_inherits = __commonJS({
  "node_modules/@babel/runtime/helpers/inherits.js"(exports2, module) {
    var setPrototypeOf = require_setPrototypeOf();
    function _inherits(t, e) {
      if ("function" != typeof e && null !== e) throw new TypeError("Super expression must either be null or a function");
      t.prototype = Object.create(e && e.prototype, {
        constructor: {
          value: t,
          writable: true,
          configurable: true
        }
      }), Object.defineProperty(t, "prototype", {
        writable: false
      }), e && setPrototypeOf(t, e);
    }
    module.exports = _inherits, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/getPrototypeOf.js
var require_getPrototypeOf = __commonJS({
  "node_modules/@babel/runtime/helpers/getPrototypeOf.js"(exports2, module) {
    function _getPrototypeOf(t) {
      return module.exports = _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t2) {
        return t2.__proto__ || Object.getPrototypeOf(t2);
      }, module.exports.__esModule = true, module.exports["default"] = module.exports, _getPrototypeOf(t);
    }
    module.exports = _getPrototypeOf, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/isNativeReflectConstruct.js
var require_isNativeReflectConstruct = __commonJS({
  "node_modules/@babel/runtime/helpers/isNativeReflectConstruct.js"(exports2, module) {
    function _isNativeReflectConstruct() {
      try {
        var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
        }));
      } catch (t2) {
      }
      return (module.exports = _isNativeReflectConstruct = function _isNativeReflectConstruct2() {
        return !!t;
      }, module.exports.__esModule = true, module.exports["default"] = module.exports)();
    }
    module.exports = _isNativeReflectConstruct, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/possibleConstructorReturn.js
var require_possibleConstructorReturn = __commonJS({
  "node_modules/@babel/runtime/helpers/possibleConstructorReturn.js"(exports2, module) {
    var _typeof = require_typeof()["default"];
    var assertThisInitialized = require_assertThisInitialized();
    function _possibleConstructorReturn(t, e) {
      if (e && ("object" == _typeof(e) || "function" == typeof e)) return e;
      if (void 0 !== e) throw new TypeError("Derived constructors may only return object or undefined");
      return assertThisInitialized(t);
    }
    module.exports = _possibleConstructorReturn, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/createSuper.js
var require_createSuper = __commonJS({
  "node_modules/@babel/runtime/helpers/createSuper.js"(exports2, module) {
    var getPrototypeOf = require_getPrototypeOf();
    var isNativeReflectConstruct = require_isNativeReflectConstruct();
    var possibleConstructorReturn = require_possibleConstructorReturn();
    function _createSuper(t) {
      var r = isNativeReflectConstruct();
      return function() {
        var e, o = getPrototypeOf(t);
        if (r) {
          var s = getPrototypeOf(this).constructor;
          e = Reflect.construct(o, arguments, s);
        } else e = o.apply(this, arguments);
        return possibleConstructorReturn(this, e);
      };
    }
    module.exports = _createSuper, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/classCallCheck.js
var require_classCallCheck = __commonJS({
  "node_modules/@babel/runtime/helpers/classCallCheck.js"(exports2, module) {
    function _classCallCheck(a, n) {
      if (!(a instanceof n)) throw new TypeError("Cannot call a class as a function");
    }
    module.exports = _classCallCheck, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/toPrimitive.js
var require_toPrimitive = __commonJS({
  "node_modules/@babel/runtime/helpers/toPrimitive.js"(exports2, module) {
    var _typeof = require_typeof()["default"];
    function toPrimitive(t, r) {
      if ("object" != _typeof(t) || !t) return t;
      var e = t[Symbol.toPrimitive];
      if (void 0 !== e) {
        var i = e.call(t, r || "default");
        if ("object" != _typeof(i)) return i;
        throw new TypeError("@@toPrimitive must return a primitive value.");
      }
      return ("string" === r ? String : Number)(t);
    }
    module.exports = toPrimitive, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/toPropertyKey.js
var require_toPropertyKey = __commonJS({
  "node_modules/@babel/runtime/helpers/toPropertyKey.js"(exports2, module) {
    var _typeof = require_typeof()["default"];
    var toPrimitive = require_toPrimitive();
    function toPropertyKey(t) {
      var i = toPrimitive(t, "string");
      return "symbol" == _typeof(i) ? i : i + "";
    }
    module.exports = toPropertyKey, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/createClass.js
var require_createClass = __commonJS({
  "node_modules/@babel/runtime/helpers/createClass.js"(exports2, module) {
    var toPropertyKey = require_toPropertyKey();
    function _defineProperties(e, r) {
      for (var t = 0; t < r.length; t++) {
        var o = r[t];
        o.enumerable = o.enumerable || false, o.configurable = true, "value" in o && (o.writable = true), Object.defineProperty(e, toPropertyKey(o.key), o);
      }
    }
    function _createClass(e, r, t) {
      return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, "prototype", {
        writable: false
      }), e;
    }
    module.exports = _createClass, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/@babel/runtime/helpers/defineProperty.js
var require_defineProperty = __commonJS({
  "node_modules/@babel/runtime/helpers/defineProperty.js"(exports2, module) {
    var toPropertyKey = require_toPropertyKey();
    function _defineProperty(e, r, t) {
      return (r = toPropertyKey(r)) in e ? Object.defineProperty(e, r, {
        value: t,
        enumerable: true,
        configurable: true,
        writable: true
      }) : e[r] = t, e;
    }
    module.exports = _defineProperty, module.exports.__esModule = true, module.exports["default"] = module.exports;
  }
});

// node_modules/date-fns/parse/_lib/Setter.js
var require_Setter = __commonJS({
  "node_modules/date-fns/parse/_lib/Setter.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ValueSetter = exports2.Setter = exports2.DateToSystemTimezoneSetter = void 0;
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var TIMEZONE_UNIT_PRIORITY = 10;
    var Setter = /* @__PURE__ */ (function() {
      function Setter2() {
        (0, _classCallCheck2.default)(this, Setter2);
        (0, _defineProperty2.default)(this, "priority", void 0);
        (0, _defineProperty2.default)(this, "subPriority", 0);
      }
      (0, _createClass2.default)(Setter2, [{
        key: "validate",
        value: function validate2(_utcDate, _options) {
          return true;
        }
      }]);
      return Setter2;
    })();
    exports2.Setter = Setter;
    var ValueSetter = /* @__PURE__ */ (function(_Setter) {
      (0, _inherits2.default)(ValueSetter2, _Setter);
      var _super = (0, _createSuper2.default)(ValueSetter2);
      function ValueSetter2(value, validateValue, setValue, priority, subPriority) {
        var _this;
        (0, _classCallCheck2.default)(this, ValueSetter2);
        _this = _super.call(this);
        _this.value = value;
        _this.validateValue = validateValue;
        _this.setValue = setValue;
        _this.priority = priority;
        if (subPriority) {
          _this.subPriority = subPriority;
        }
        return _this;
      }
      (0, _createClass2.default)(ValueSetter2, [{
        key: "validate",
        value: function validate2(utcDate, options) {
          return this.validateValue(utcDate, this.value, options);
        }
      }, {
        key: "set",
        value: function set(utcDate, flags, options) {
          return this.setValue(utcDate, flags, this.value, options);
        }
      }]);
      return ValueSetter2;
    })(Setter);
    exports2.ValueSetter = ValueSetter;
    var DateToSystemTimezoneSetter = /* @__PURE__ */ (function(_Setter2) {
      (0, _inherits2.default)(DateToSystemTimezoneSetter2, _Setter2);
      var _super2 = (0, _createSuper2.default)(DateToSystemTimezoneSetter2);
      function DateToSystemTimezoneSetter2() {
        var _this2;
        (0, _classCallCheck2.default)(this, DateToSystemTimezoneSetter2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this2 = _super2.call.apply(_super2, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this2), "priority", TIMEZONE_UNIT_PRIORITY);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this2), "subPriority", -1);
        return _this2;
      }
      (0, _createClass2.default)(DateToSystemTimezoneSetter2, [{
        key: "set",
        value: function set(date, flags) {
          if (flags.timestampIsSet) {
            return date;
          }
          var convertedDate = /* @__PURE__ */ new Date(0);
          convertedDate.setFullYear(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
          convertedDate.setHours(date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds(), date.getUTCMilliseconds());
          return convertedDate;
        }
      }]);
      return DateToSystemTimezoneSetter2;
    })(Setter);
    exports2.DateToSystemTimezoneSetter = DateToSystemTimezoneSetter;
  }
});

// node_modules/date-fns/parse/_lib/Parser.js
var require_Parser = __commonJS({
  "node_modules/date-fns/parse/_lib/Parser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.Parser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Setter = require_Setter();
    var Parser = /* @__PURE__ */ (function() {
      function Parser2() {
        (0, _classCallCheck2.default)(this, Parser2);
        (0, _defineProperty2.default)(this, "incompatibleTokens", void 0);
        (0, _defineProperty2.default)(this, "priority", void 0);
        (0, _defineProperty2.default)(this, "subPriority", void 0);
      }
      (0, _createClass2.default)(Parser2, [{
        key: "run",
        value: function run(dateString, token, match, options) {
          var result = this.parse(dateString, token, match, options);
          if (!result) {
            return null;
          }
          return {
            setter: new _Setter.ValueSetter(result.value, this.validate, this.set, this.priority, this.subPriority),
            rest: result.rest
          };
        }
      }, {
        key: "validate",
        value: function validate2(_utcDate, _value, _options) {
          return true;
        }
      }]);
      return Parser2;
    })();
    exports2.Parser = Parser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/EraParser.js
var require_EraParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/EraParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.EraParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var EraParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(EraParser2, _Parser);
      var _super = (0, _createSuper2.default)(EraParser2);
      function EraParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, EraParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 140);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["R", "u", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(EraParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            // AD, BC
            case "G":
            case "GG":
            case "GGG":
              return match.era(dateString, {
                width: "abbreviated"
              }) || match.era(dateString, {
                width: "narrow"
              });
            // A, B
            case "GGGGG":
              return match.era(dateString, {
                width: "narrow"
              });
            // Anno Domini, Before Christ
            case "GGGG":
            default:
              return match.era(dateString, {
                width: "wide"
              }) || match.era(dateString, {
                width: "abbreviated"
              }) || match.era(dateString, {
                width: "narrow"
              });
          }
        }
      }, {
        key: "set",
        value: function set(date, flags, value) {
          flags.era = value;
          date.setUTCFullYear(value, 0, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return EraParser2;
    })(_Parser2.Parser);
    exports2.EraParser = EraParser;
  }
});

// node_modules/date-fns/parse/_lib/constants.js
var require_constants2 = __commonJS({
  "node_modules/date-fns/parse/_lib/constants.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.timezonePatterns = exports2.numericPatterns = void 0;
    var numericPatterns = {
      month: /^(1[0-2]|0?\d)/,
      // 0 to 12
      date: /^(3[0-1]|[0-2]?\d)/,
      // 0 to 31
      dayOfYear: /^(36[0-6]|3[0-5]\d|[0-2]?\d?\d)/,
      // 0 to 366
      week: /^(5[0-3]|[0-4]?\d)/,
      // 0 to 53
      hour23h: /^(2[0-3]|[0-1]?\d)/,
      // 0 to 23
      hour24h: /^(2[0-4]|[0-1]?\d)/,
      // 0 to 24
      hour11h: /^(1[0-1]|0?\d)/,
      // 0 to 11
      hour12h: /^(1[0-2]|0?\d)/,
      // 0 to 12
      minute: /^[0-5]?\d/,
      // 0 to 59
      second: /^[0-5]?\d/,
      // 0 to 59
      singleDigit: /^\d/,
      // 0 to 9
      twoDigits: /^\d{1,2}/,
      // 0 to 99
      threeDigits: /^\d{1,3}/,
      // 0 to 999
      fourDigits: /^\d{1,4}/,
      // 0 to 9999
      anyDigitsSigned: /^-?\d+/,
      singleDigitSigned: /^-?\d/,
      // 0 to 9, -0 to -9
      twoDigitsSigned: /^-?\d{1,2}/,
      // 0 to 99, -0 to -99
      threeDigitsSigned: /^-?\d{1,3}/,
      // 0 to 999, -0 to -999
      fourDigitsSigned: /^-?\d{1,4}/
      // 0 to 9999, -0 to -9999
    };
    exports2.numericPatterns = numericPatterns;
    var timezonePatterns = {
      basicOptionalMinutes: /^([+-])(\d{2})(\d{2})?|Z/,
      basic: /^([+-])(\d{2})(\d{2})|Z/,
      basicOptionalSeconds: /^([+-])(\d{2})(\d{2})((\d{2}))?|Z/,
      extended: /^([+-])(\d{2}):(\d{2})|Z/,
      extendedOptionalSeconds: /^([+-])(\d{2}):(\d{2})(:(\d{2}))?|Z/
    };
    exports2.timezonePatterns = timezonePatterns;
  }
});

// node_modules/date-fns/parse/_lib/utils.js
var require_utils = __commonJS({
  "node_modules/date-fns/parse/_lib/utils.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.dayPeriodEnumToHours = dayPeriodEnumToHours;
    exports2.isLeapYearIndex = isLeapYearIndex;
    exports2.mapValue = mapValue;
    exports2.normalizeTwoDigitYear = normalizeTwoDigitYear;
    exports2.parseAnyDigitsSigned = parseAnyDigitsSigned;
    exports2.parseNDigits = parseNDigits;
    exports2.parseNDigitsSigned = parseNDigitsSigned;
    exports2.parseNumericPattern = parseNumericPattern;
    exports2.parseTimezonePattern = parseTimezonePattern;
    var _index = require_constants();
    var _constants = require_constants2();
    function mapValue(parseFnResult, mapFn) {
      if (!parseFnResult) {
        return parseFnResult;
      }
      return {
        value: mapFn(parseFnResult.value),
        rest: parseFnResult.rest
      };
    }
    function parseNumericPattern(pattern, dateString) {
      var matchResult = dateString.match(pattern);
      if (!matchResult) {
        return null;
      }
      return {
        value: parseInt(matchResult[0], 10),
        rest: dateString.slice(matchResult[0].length)
      };
    }
    function parseTimezonePattern(pattern, dateString) {
      var matchResult = dateString.match(pattern);
      if (!matchResult) {
        return null;
      }
      if (matchResult[0] === "Z") {
        return {
          value: 0,
          rest: dateString.slice(1)
        };
      }
      var sign = matchResult[1] === "+" ? 1 : -1;
      var hours = matchResult[2] ? parseInt(matchResult[2], 10) : 0;
      var minutes = matchResult[3] ? parseInt(matchResult[3], 10) : 0;
      var seconds = matchResult[5] ? parseInt(matchResult[5], 10) : 0;
      return {
        value: sign * (hours * _index.millisecondsInHour + minutes * _index.millisecondsInMinute + seconds * _index.millisecondsInSecond),
        rest: dateString.slice(matchResult[0].length)
      };
    }
    function parseAnyDigitsSigned(dateString) {
      return parseNumericPattern(_constants.numericPatterns.anyDigitsSigned, dateString);
    }
    function parseNDigits(n, dateString) {
      switch (n) {
        case 1:
          return parseNumericPattern(_constants.numericPatterns.singleDigit, dateString);
        case 2:
          return parseNumericPattern(_constants.numericPatterns.twoDigits, dateString);
        case 3:
          return parseNumericPattern(_constants.numericPatterns.threeDigits, dateString);
        case 4:
          return parseNumericPattern(_constants.numericPatterns.fourDigits, dateString);
        default:
          return parseNumericPattern(new RegExp("^\\d{1," + n + "}"), dateString);
      }
    }
    function parseNDigitsSigned(n, dateString) {
      switch (n) {
        case 1:
          return parseNumericPattern(_constants.numericPatterns.singleDigitSigned, dateString);
        case 2:
          return parseNumericPattern(_constants.numericPatterns.twoDigitsSigned, dateString);
        case 3:
          return parseNumericPattern(_constants.numericPatterns.threeDigitsSigned, dateString);
        case 4:
          return parseNumericPattern(_constants.numericPatterns.fourDigitsSigned, dateString);
        default:
          return parseNumericPattern(new RegExp("^-?\\d{1," + n + "}"), dateString);
      }
    }
    function dayPeriodEnumToHours(dayPeriod) {
      switch (dayPeriod) {
        case "morning":
          return 4;
        case "evening":
          return 17;
        case "pm":
        case "noon":
        case "afternoon":
          return 12;
        case "am":
        case "midnight":
        case "night":
        default:
          return 0;
      }
    }
    function normalizeTwoDigitYear(twoDigitYear, currentYear) {
      var isCommonEra = currentYear > 0;
      var absCurrentYear = isCommonEra ? currentYear : 1 - currentYear;
      var result;
      if (absCurrentYear <= 50) {
        result = twoDigitYear || 100;
      } else {
        var rangeEnd = absCurrentYear + 50;
        var rangeEndCentury = Math.floor(rangeEnd / 100) * 100;
        var isPreviousCentury = twoDigitYear >= rangeEnd % 100;
        result = twoDigitYear + rangeEndCentury - (isPreviousCentury ? 100 : 0);
      }
      return isCommonEra ? result : 1 - result;
    }
    function isLeapYearIndex(year) {
      return year % 400 === 0 || year % 4 === 0 && year % 100 !== 0;
    }
  }
});

// node_modules/date-fns/parse/_lib/parsers/YearParser.js
var require_YearParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/YearParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.YearParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var YearParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(YearParser2, _Parser);
      var _super = (0, _createSuper2.default)(YearParser2);
      function YearParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, YearParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 130);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "u", "w", "I", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(YearParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          var valueCallback = function valueCallback2(year) {
            return {
              year,
              isTwoDigitYear: token === "yy"
            };
          };
          switch (token) {
            case "y":
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(4, dateString), valueCallback);
            case "yo":
              return (0, _utils.mapValue)(match.ordinalNumber(dateString, {
                unit: "year"
              }), valueCallback);
            default:
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(token.length, dateString), valueCallback);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value.isTwoDigitYear || value.year > 0;
        }
      }, {
        key: "set",
        value: function set(date, flags, value) {
          var currentYear = date.getUTCFullYear();
          if (value.isTwoDigitYear) {
            var normalizedTwoDigitYear = (0, _utils.normalizeTwoDigitYear)(value.year, currentYear);
            date.setUTCFullYear(normalizedTwoDigitYear, 0, 1);
            date.setUTCHours(0, 0, 0, 0);
            return date;
          }
          var year = !("era" in flags) || flags.era === 1 ? value.year : 1 - value.year;
          date.setUTCFullYear(year, 0, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return YearParser2;
    })(_Parser2.Parser);
    exports2.YearParser = YearParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/LocalWeekYearParser.js
var require_LocalWeekYearParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/LocalWeekYearParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.LocalWeekYearParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_getUTCWeekYear());
    var _index2 = _interopRequireDefault(require_startOfUTCWeek());
    var LocalWeekYearParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(LocalWeekYearParser2, _Parser);
      var _super = (0, _createSuper2.default)(LocalWeekYearParser2);
      function LocalWeekYearParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, LocalWeekYearParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 130);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["y", "R", "u", "Q", "q", "M", "L", "I", "d", "D", "i", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(LocalWeekYearParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          var valueCallback = function valueCallback2(year) {
            return {
              year,
              isTwoDigitYear: token === "YY"
            };
          };
          switch (token) {
            case "Y":
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(4, dateString), valueCallback);
            case "Yo":
              return (0, _utils.mapValue)(match.ordinalNumber(dateString, {
                unit: "year"
              }), valueCallback);
            default:
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(token.length, dateString), valueCallback);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value.isTwoDigitYear || value.year > 0;
        }
      }, {
        key: "set",
        value: function set(date, flags, value, options) {
          var currentYear = (0, _index.default)(date, options);
          if (value.isTwoDigitYear) {
            var normalizedTwoDigitYear = (0, _utils.normalizeTwoDigitYear)(value.year, currentYear);
            date.setUTCFullYear(normalizedTwoDigitYear, 0, options.firstWeekContainsDate);
            date.setUTCHours(0, 0, 0, 0);
            return (0, _index2.default)(date, options);
          }
          var year = !("era" in flags) || flags.era === 1 ? value.year : 1 - value.year;
          date.setUTCFullYear(year, 0, options.firstWeekContainsDate);
          date.setUTCHours(0, 0, 0, 0);
          return (0, _index2.default)(date, options);
        }
      }]);
      return LocalWeekYearParser2;
    })(_Parser2.Parser);
    exports2.LocalWeekYearParser = LocalWeekYearParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/ISOWeekYearParser.js
var require_ISOWeekYearParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/ISOWeekYearParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ISOWeekYearParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_startOfUTCISOWeek());
    var ISOWeekYearParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(ISOWeekYearParser2, _Parser);
      var _super = (0, _createSuper2.default)(ISOWeekYearParser2);
      function ISOWeekYearParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, ISOWeekYearParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 130);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["G", "y", "Y", "u", "Q", "q", "M", "L", "w", "d", "D", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(ISOWeekYearParser2, [{
        key: "parse",
        value: function parse(dateString, token) {
          if (token === "R") {
            return (0, _utils.parseNDigitsSigned)(4, dateString);
          }
          return (0, _utils.parseNDigitsSigned)(token.length, dateString);
        }
      }, {
        key: "set",
        value: function set(_date, _flags, value) {
          var firstWeekOfYear = /* @__PURE__ */ new Date(0);
          firstWeekOfYear.setUTCFullYear(value, 0, 4);
          firstWeekOfYear.setUTCHours(0, 0, 0, 0);
          return (0, _index.default)(firstWeekOfYear);
        }
      }]);
      return ISOWeekYearParser2;
    })(_Parser2.Parser);
    exports2.ISOWeekYearParser = ISOWeekYearParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/ExtendedYearParser.js
var require_ExtendedYearParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/ExtendedYearParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ExtendedYearParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var ExtendedYearParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(ExtendedYearParser2, _Parser);
      var _super = (0, _createSuper2.default)(ExtendedYearParser2);
      function ExtendedYearParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, ExtendedYearParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 130);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["G", "y", "Y", "R", "w", "I", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(ExtendedYearParser2, [{
        key: "parse",
        value: function parse(dateString, token) {
          if (token === "u") {
            return (0, _utils.parseNDigitsSigned)(4, dateString);
          }
          return (0, _utils.parseNDigitsSigned)(token.length, dateString);
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCFullYear(value, 0, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return ExtendedYearParser2;
    })(_Parser2.Parser);
    exports2.ExtendedYearParser = ExtendedYearParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/QuarterParser.js
var require_QuarterParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/QuarterParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.QuarterParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var QuarterParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(QuarterParser2, _Parser);
      var _super = (0, _createSuper2.default)(QuarterParser2);
      function QuarterParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, QuarterParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 120);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "q", "M", "L", "w", "I", "d", "D", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(QuarterParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            // 1, 2, 3, 4
            case "Q":
            case "QQ":
              return (0, _utils.parseNDigits)(token.length, dateString);
            // 1st, 2nd, 3rd, 4th
            case "Qo":
              return match.ordinalNumber(dateString, {
                unit: "quarter"
              });
            // Q1, Q2, Q3, Q4
            case "QQQ":
              return match.quarter(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.quarter(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // 1, 2, 3, 4 (narrow quarter; could be not numerical)
            case "QQQQQ":
              return match.quarter(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // 1st quarter, 2nd quarter, ...
            case "QQQQ":
            default:
              return match.quarter(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.quarter(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.quarter(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 4;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMonth((value - 1) * 3, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return QuarterParser2;
    })(_Parser2.Parser);
    exports2.QuarterParser = QuarterParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/StandAloneQuarterParser.js
var require_StandAloneQuarterParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/StandAloneQuarterParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.StandAloneQuarterParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var StandAloneQuarterParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(StandAloneQuarterParser2, _Parser);
      var _super = (0, _createSuper2.default)(StandAloneQuarterParser2);
      function StandAloneQuarterParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, StandAloneQuarterParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 120);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "Q", "M", "L", "w", "I", "d", "D", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(StandAloneQuarterParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            // 1, 2, 3, 4
            case "q":
            case "qq":
              return (0, _utils.parseNDigits)(token.length, dateString);
            // 1st, 2nd, 3rd, 4th
            case "qo":
              return match.ordinalNumber(dateString, {
                unit: "quarter"
              });
            // Q1, Q2, Q3, Q4
            case "qqq":
              return match.quarter(dateString, {
                width: "abbreviated",
                context: "standalone"
              }) || match.quarter(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // 1, 2, 3, 4 (narrow quarter; could be not numerical)
            case "qqqqq":
              return match.quarter(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // 1st quarter, 2nd quarter, ...
            case "qqqq":
            default:
              return match.quarter(dateString, {
                width: "wide",
                context: "standalone"
              }) || match.quarter(dateString, {
                width: "abbreviated",
                context: "standalone"
              }) || match.quarter(dateString, {
                width: "narrow",
                context: "standalone"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 4;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMonth((value - 1) * 3, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return StandAloneQuarterParser2;
    })(_Parser2.Parser);
    exports2.StandAloneQuarterParser = StandAloneQuarterParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/MonthParser.js
var require_MonthParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/MonthParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.MonthParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _utils = require_utils();
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var MonthParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(MonthParser2, _Parser);
      var _super = (0, _createSuper2.default)(MonthParser2);
      function MonthParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, MonthParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "q", "Q", "L", "w", "I", "D", "i", "e", "c", "t", "T"]);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 110);
        return _this;
      }
      (0, _createClass2.default)(MonthParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          var valueCallback = function valueCallback2(value) {
            return value - 1;
          };
          switch (token) {
            // 1, 2, ..., 12
            case "M":
              return (0, _utils.mapValue)((0, _utils.parseNumericPattern)(_constants.numericPatterns.month, dateString), valueCallback);
            // 01, 02, ..., 12
            case "MM":
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(2, dateString), valueCallback);
            // 1st, 2nd, ..., 12th
            case "Mo":
              return (0, _utils.mapValue)(match.ordinalNumber(dateString, {
                unit: "month"
              }), valueCallback);
            // Jan, Feb, ..., Dec
            case "MMM":
              return match.month(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.month(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // J, F, ..., D
            case "MMMMM":
              return match.month(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // January, February, ..., December
            case "MMMM":
            default:
              return match.month(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.month(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.month(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 11;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMonth(value, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return MonthParser2;
    })(_Parser2.Parser);
    exports2.MonthParser = MonthParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/StandAloneMonthParser.js
var require_StandAloneMonthParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/StandAloneMonthParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.StandAloneMonthParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var StandAloneMonthParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(StandAloneMonthParser2, _Parser);
      var _super = (0, _createSuper2.default)(StandAloneMonthParser2);
      function StandAloneMonthParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, StandAloneMonthParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 110);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "q", "Q", "M", "w", "I", "D", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(StandAloneMonthParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          var valueCallback = function valueCallback2(value) {
            return value - 1;
          };
          switch (token) {
            // 1, 2, ..., 12
            case "L":
              return (0, _utils.mapValue)((0, _utils.parseNumericPattern)(_constants.numericPatterns.month, dateString), valueCallback);
            // 01, 02, ..., 12
            case "LL":
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(2, dateString), valueCallback);
            // 1st, 2nd, ..., 12th
            case "Lo":
              return (0, _utils.mapValue)(match.ordinalNumber(dateString, {
                unit: "month"
              }), valueCallback);
            // Jan, Feb, ..., Dec
            case "LLL":
              return match.month(dateString, {
                width: "abbreviated",
                context: "standalone"
              }) || match.month(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // J, F, ..., D
            case "LLLLL":
              return match.month(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // January, February, ..., December
            case "LLLL":
            default:
              return match.month(dateString, {
                width: "wide",
                context: "standalone"
              }) || match.month(dateString, {
                width: "abbreviated",
                context: "standalone"
              }) || match.month(dateString, {
                width: "narrow",
                context: "standalone"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 11;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMonth(value, 1);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return StandAloneMonthParser2;
    })(_Parser2.Parser);
    exports2.StandAloneMonthParser = StandAloneMonthParser;
  }
});

// node_modules/date-fns/_lib/setUTCWeek/index.js
var require_setUTCWeek = __commonJS({
  "node_modules/date-fns/_lib/setUTCWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setUTCWeek;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_getUTCWeek());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function setUTCWeek(dirtyDate, dirtyWeek, options) {
      (0, _index4.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var week = (0, _index.default)(dirtyWeek);
      var diff = (0, _index3.default)(date, options) - week;
      date.setUTCDate(date.getUTCDate() - diff * 7);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/parse/_lib/parsers/LocalWeekParser.js
var require_LocalWeekParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/LocalWeekParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.LocalWeekParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_setUTCWeek());
    var _index2 = _interopRequireDefault(require_startOfUTCWeek());
    var LocalWeekParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(LocalWeekParser2, _Parser);
      var _super = (0, _createSuper2.default)(LocalWeekParser2);
      function LocalWeekParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, LocalWeekParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 100);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["y", "R", "u", "q", "Q", "M", "L", "I", "d", "D", "i", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(LocalWeekParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "w":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.week, dateString);
            case "wo":
              return match.ordinalNumber(dateString, {
                unit: "week"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 53;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value, options) {
          return (0, _index2.default)((0, _index.default)(date, value, options), options);
        }
      }]);
      return LocalWeekParser2;
    })(_Parser2.Parser);
    exports2.LocalWeekParser = LocalWeekParser;
  }
});

// node_modules/date-fns/_lib/setUTCISOWeek/index.js
var require_setUTCISOWeek = __commonJS({
  "node_modules/date-fns/_lib/setUTCISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setUTCISOWeek;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_getUTCISOWeek());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function setUTCISOWeek(dirtyDate, dirtyISOWeek) {
      (0, _index4.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var isoWeek = (0, _index.default)(dirtyISOWeek);
      var diff = (0, _index3.default)(date) - isoWeek;
      date.setUTCDate(date.getUTCDate() - diff * 7);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/parse/_lib/parsers/ISOWeekParser.js
var require_ISOWeekParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/ISOWeekParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ISOWeekParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_setUTCISOWeek());
    var _index2 = _interopRequireDefault(require_startOfUTCISOWeek());
    var ISOWeekParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(ISOWeekParser2, _Parser);
      var _super = (0, _createSuper2.default)(ISOWeekParser2);
      function ISOWeekParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, ISOWeekParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 100);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["y", "Y", "u", "q", "Q", "M", "L", "w", "d", "D", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(ISOWeekParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "I":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.week, dateString);
            case "Io":
              return match.ordinalNumber(dateString, {
                unit: "week"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 53;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          return (0, _index2.default)((0, _index.default)(date, value));
        }
      }]);
      return ISOWeekParser2;
    })(_Parser2.Parser);
    exports2.ISOWeekParser = ISOWeekParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/DateParser.js
var require_DateParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/DateParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.DateParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _utils = require_utils();
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    var DAYS_IN_MONTH_LEAP_YEAR = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    var DateParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(DateParser2, _Parser);
      var _super = (0, _createSuper2.default)(DateParser2);
      function DateParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, DateParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 90);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "subPriority", 1);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "q", "Q", "w", "I", "D", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(DateParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "d":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.date, dateString);
            case "do":
              return match.ordinalNumber(dateString, {
                unit: "date"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(date, value) {
          var year = date.getUTCFullYear();
          var isLeapYear = (0, _utils.isLeapYearIndex)(year);
          var month = date.getUTCMonth();
          if (isLeapYear) {
            return value >= 1 && value <= DAYS_IN_MONTH_LEAP_YEAR[month];
          } else {
            return value >= 1 && value <= DAYS_IN_MONTH[month];
          }
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCDate(value);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return DateParser2;
    })(_Parser2.Parser);
    exports2.DateParser = DateParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/DayOfYearParser.js
var require_DayOfYearParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/DayOfYearParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.DayOfYearParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var DayOfYearParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(DayOfYearParser2, _Parser);
      var _super = (0, _createSuper2.default)(DayOfYearParser2);
      function DayOfYearParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, DayOfYearParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 90);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "subpriority", 1);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["Y", "R", "q", "Q", "M", "L", "w", "I", "d", "E", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(DayOfYearParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "D":
            case "DD":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.dayOfYear, dateString);
            case "Do":
              return match.ordinalNumber(dateString, {
                unit: "date"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(date, value) {
          var year = date.getUTCFullYear();
          var isLeapYear = (0, _utils.isLeapYearIndex)(year);
          if (isLeapYear) {
            return value >= 1 && value <= 366;
          } else {
            return value >= 1 && value <= 365;
          }
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMonth(0, value);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return DayOfYearParser2;
    })(_Parser2.Parser);
    exports2.DayOfYearParser = DayOfYearParser;
  }
});

// node_modules/date-fns/_lib/setUTCDay/index.js
var require_setUTCDay = __commonJS({
  "node_modules/date-fns/_lib/setUTCDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setUTCDay;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = require_defaultOptions();
    function setUTCDay(dirtyDate, dirtyDay, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index2.default)(2, arguments);
      var defaultOptions3 = (0, _index4.getDefaultOptions)();
      var weekStartsOn = (0, _index3.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      var date = (0, _index.default)(dirtyDate);
      var day = (0, _index3.default)(dirtyDay);
      var currentDay = date.getUTCDay();
      var remainder = day % 7;
      var dayIndex = (remainder + 7) % 7;
      var diff = (dayIndex < weekStartsOn ? 7 : 0) + day - currentDay;
      date.setUTCDate(date.getUTCDate() + diff);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/parse/_lib/parsers/DayParser.js
var require_DayParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/DayParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.DayParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _index = _interopRequireDefault(require_setUTCDay());
    var DayParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(DayParser2, _Parser);
      var _super = (0, _createSuper2.default)(DayParser2);
      function DayParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, DayParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 90);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["D", "i", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(DayParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            // Tue
            case "E":
            case "EE":
            case "EEE":
              return match.day(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // T
            case "EEEEE":
              return match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // Tu
            case "EEEEEE":
              return match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // Tuesday
            case "EEEE":
            default:
              return match.day(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.day(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 6;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value, options) {
          date = (0, _index.default)(date, value, options);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return DayParser2;
    })(_Parser2.Parser);
    exports2.DayParser = DayParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/LocalDayParser.js
var require_LocalDayParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/LocalDayParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.LocalDayParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_setUTCDay());
    var LocalDayParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(LocalDayParser2, _Parser);
      var _super = (0, _createSuper2.default)(LocalDayParser2);
      function LocalDayParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, LocalDayParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 90);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["y", "R", "u", "q", "Q", "M", "L", "I", "d", "D", "E", "i", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(LocalDayParser2, [{
        key: "parse",
        value: function parse(dateString, token, match, options) {
          var valueCallback = function valueCallback2(value) {
            var wholeWeekDays = Math.floor((value - 1) / 7) * 7;
            return (value + options.weekStartsOn + 6) % 7 + wholeWeekDays;
          };
          switch (token) {
            // 3
            case "e":
            case "ee":
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(token.length, dateString), valueCallback);
            // 3rd
            case "eo":
              return (0, _utils.mapValue)(match.ordinalNumber(dateString, {
                unit: "day"
              }), valueCallback);
            // Tue
            case "eee":
              return match.day(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // T
            case "eeeee":
              return match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // Tu
            case "eeeeee":
              return match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
            // Tuesday
            case "eeee":
            default:
              return match.day(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.day(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 6;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value, options) {
          date = (0, _index.default)(date, value, options);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return LocalDayParser2;
    })(_Parser2.Parser);
    exports2.LocalDayParser = LocalDayParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/StandAloneLocalDayParser.js
var require_StandAloneLocalDayParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/StandAloneLocalDayParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.StandAloneLocalDayParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_setUTCDay());
    var StandAloneLocalDayParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(StandAloneLocalDayParser2, _Parser);
      var _super = (0, _createSuper2.default)(StandAloneLocalDayParser2);
      function StandAloneLocalDayParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, StandAloneLocalDayParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 90);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["y", "R", "u", "q", "Q", "M", "L", "I", "d", "D", "E", "i", "e", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(StandAloneLocalDayParser2, [{
        key: "parse",
        value: function parse(dateString, token, match, options) {
          var valueCallback = function valueCallback2(value) {
            var wholeWeekDays = Math.floor((value - 1) / 7) * 7;
            return (value + options.weekStartsOn + 6) % 7 + wholeWeekDays;
          };
          switch (token) {
            // 3
            case "c":
            case "cc":
              return (0, _utils.mapValue)((0, _utils.parseNDigits)(token.length, dateString), valueCallback);
            // 3rd
            case "co":
              return (0, _utils.mapValue)(match.ordinalNumber(dateString, {
                unit: "day"
              }), valueCallback);
            // Tue
            case "ccc":
              return match.day(dateString, {
                width: "abbreviated",
                context: "standalone"
              }) || match.day(dateString, {
                width: "short",
                context: "standalone"
              }) || match.day(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // T
            case "ccccc":
              return match.day(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // Tu
            case "cccccc":
              return match.day(dateString, {
                width: "short",
                context: "standalone"
              }) || match.day(dateString, {
                width: "narrow",
                context: "standalone"
              });
            // Tuesday
            case "cccc":
            default:
              return match.day(dateString, {
                width: "wide",
                context: "standalone"
              }) || match.day(dateString, {
                width: "abbreviated",
                context: "standalone"
              }) || match.day(dateString, {
                width: "short",
                context: "standalone"
              }) || match.day(dateString, {
                width: "narrow",
                context: "standalone"
              });
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 6;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value, options) {
          date = (0, _index.default)(date, value, options);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return StandAloneLocalDayParser2;
    })(_Parser2.Parser);
    exports2.StandAloneLocalDayParser = StandAloneLocalDayParser;
  }
});

// node_modules/date-fns/_lib/setUTCISODay/index.js
var require_setUTCISODay = __commonJS({
  "node_modules/date-fns/_lib/setUTCISODay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setUTCISODay;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function setUTCISODay(dirtyDate, dirtyDay) {
      (0, _index2.default)(2, arguments);
      var day = (0, _index3.default)(dirtyDay);
      if (day % 7 === 0) {
        day = day - 7;
      }
      var weekStartsOn = 1;
      var date = (0, _index.default)(dirtyDate);
      var currentDay = date.getUTCDay();
      var remainder = day % 7;
      var dayIndex = (remainder + 7) % 7;
      var diff = (dayIndex < weekStartsOn ? 7 : 0) + day - currentDay;
      date.setUTCDate(date.getUTCDate() + diff);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/parse/_lib/parsers/ISODayParser.js
var require_ISODayParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/ISODayParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ISODayParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var _index = _interopRequireDefault(require_setUTCISODay());
    var ISODayParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(ISODayParser2, _Parser);
      var _super = (0, _createSuper2.default)(ISODayParser2);
      function ISODayParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, ISODayParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 90);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["y", "Y", "u", "q", "Q", "M", "L", "w", "d", "D", "E", "e", "c", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(ISODayParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          var valueCallback = function valueCallback2(value) {
            if (value === 0) {
              return 7;
            }
            return value;
          };
          switch (token) {
            // 2
            case "i":
            case "ii":
              return (0, _utils.parseNDigits)(token.length, dateString);
            // 2nd
            case "io":
              return match.ordinalNumber(dateString, {
                unit: "day"
              });
            // Tue
            case "iii":
              return (0, _utils.mapValue)(match.day(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              }), valueCallback);
            // T
            case "iiiii":
              return (0, _utils.mapValue)(match.day(dateString, {
                width: "narrow",
                context: "formatting"
              }), valueCallback);
            // Tu
            case "iiiiii":
              return (0, _utils.mapValue)(match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              }), valueCallback);
            // Tuesday
            case "iiii":
            default:
              return (0, _utils.mapValue)(match.day(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.day(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.day(dateString, {
                width: "short",
                context: "formatting"
              }) || match.day(dateString, {
                width: "narrow",
                context: "formatting"
              }), valueCallback);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 7;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date = (0, _index.default)(date, value);
          date.setUTCHours(0, 0, 0, 0);
          return date;
        }
      }]);
      return ISODayParser2;
    })(_Parser2.Parser);
    exports2.ISODayParser = ISODayParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/AMPMParser.js
var require_AMPMParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/AMPMParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.AMPMParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var AMPMParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(AMPMParser2, _Parser);
      var _super = (0, _createSuper2.default)(AMPMParser2);
      function AMPMParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, AMPMParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 80);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["b", "B", "H", "k", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(AMPMParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "a":
            case "aa":
            case "aaa":
              return match.dayPeriod(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
            case "aaaaa":
              return match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
            case "aaaa":
            default:
              return match.dayPeriod(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCHours((0, _utils.dayPeriodEnumToHours)(value), 0, 0, 0);
          return date;
        }
      }]);
      return AMPMParser2;
    })(_Parser2.Parser);
    exports2.AMPMParser = AMPMParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/AMPMMidnightParser.js
var require_AMPMMidnightParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/AMPMMidnightParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.AMPMMidnightParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var AMPMMidnightParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(AMPMMidnightParser2, _Parser);
      var _super = (0, _createSuper2.default)(AMPMMidnightParser2);
      function AMPMMidnightParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, AMPMMidnightParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 80);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["a", "B", "H", "k", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(AMPMMidnightParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "b":
            case "bb":
            case "bbb":
              return match.dayPeriod(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
            case "bbbbb":
              return match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
            case "bbbb":
            default:
              return match.dayPeriod(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCHours((0, _utils.dayPeriodEnumToHours)(value), 0, 0, 0);
          return date;
        }
      }]);
      return AMPMMidnightParser2;
    })(_Parser2.Parser);
    exports2.AMPMMidnightParser = AMPMMidnightParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/DayPeriodParser.js
var require_DayPeriodParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/DayPeriodParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.DayPeriodParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var DayPeriodParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(DayPeriodParser2, _Parser);
      var _super = (0, _createSuper2.default)(DayPeriodParser2);
      function DayPeriodParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, DayPeriodParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 80);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["a", "b", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(DayPeriodParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "B":
            case "BB":
            case "BBB":
              return match.dayPeriod(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
            case "BBBBB":
              return match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
            case "BBBB":
            default:
              return match.dayPeriod(dateString, {
                width: "wide",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "abbreviated",
                context: "formatting"
              }) || match.dayPeriod(dateString, {
                width: "narrow",
                context: "formatting"
              });
          }
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCHours((0, _utils.dayPeriodEnumToHours)(value), 0, 0, 0);
          return date;
        }
      }]);
      return DayPeriodParser2;
    })(_Parser2.Parser);
    exports2.DayPeriodParser = DayPeriodParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/Hour1to12Parser.js
var require_Hour1to12Parser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/Hour1to12Parser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.Hour1to12Parser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var Hour1to12Parser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(Hour1to12Parser2, _Parser);
      var _super = (0, _createSuper2.default)(Hour1to12Parser2);
      function Hour1to12Parser2() {
        var _this;
        (0, _classCallCheck2.default)(this, Hour1to12Parser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 70);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["H", "K", "k", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(Hour1to12Parser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "h":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.hour12h, dateString);
            case "ho":
              return match.ordinalNumber(dateString, {
                unit: "hour"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 12;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          var isPM = date.getUTCHours() >= 12;
          if (isPM && value < 12) {
            date.setUTCHours(value + 12, 0, 0, 0);
          } else if (!isPM && value === 12) {
            date.setUTCHours(0, 0, 0, 0);
          } else {
            date.setUTCHours(value, 0, 0, 0);
          }
          return date;
        }
      }]);
      return Hour1to12Parser2;
    })(_Parser2.Parser);
    exports2.Hour1to12Parser = Hour1to12Parser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/Hour0to23Parser.js
var require_Hour0to23Parser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/Hour0to23Parser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.Hour0to23Parser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var Hour0to23Parser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(Hour0to23Parser2, _Parser);
      var _super = (0, _createSuper2.default)(Hour0to23Parser2);
      function Hour0to23Parser2() {
        var _this;
        (0, _classCallCheck2.default)(this, Hour0to23Parser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 70);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["a", "b", "h", "K", "k", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(Hour0to23Parser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "H":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.hour23h, dateString);
            case "Ho":
              return match.ordinalNumber(dateString, {
                unit: "hour"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 23;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCHours(value, 0, 0, 0);
          return date;
        }
      }]);
      return Hour0to23Parser2;
    })(_Parser2.Parser);
    exports2.Hour0to23Parser = Hour0to23Parser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/Hour0To11Parser.js
var require_Hour0To11Parser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/Hour0To11Parser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.Hour0To11Parser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var Hour0To11Parser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(Hour0To11Parser2, _Parser);
      var _super = (0, _createSuper2.default)(Hour0To11Parser2);
      function Hour0To11Parser2() {
        var _this;
        (0, _classCallCheck2.default)(this, Hour0To11Parser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 70);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["h", "H", "k", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(Hour0To11Parser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "K":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.hour11h, dateString);
            case "Ko":
              return match.ordinalNumber(dateString, {
                unit: "hour"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 11;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          var isPM = date.getUTCHours() >= 12;
          if (isPM && value < 12) {
            date.setUTCHours(value + 12, 0, 0, 0);
          } else {
            date.setUTCHours(value, 0, 0, 0);
          }
          return date;
        }
      }]);
      return Hour0To11Parser2;
    })(_Parser2.Parser);
    exports2.Hour0To11Parser = Hour0To11Parser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/Hour1To24Parser.js
var require_Hour1To24Parser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/Hour1To24Parser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.Hour1To24Parser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var Hour1To24Parser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(Hour1To24Parser2, _Parser);
      var _super = (0, _createSuper2.default)(Hour1To24Parser2);
      function Hour1To24Parser2() {
        var _this;
        (0, _classCallCheck2.default)(this, Hour1To24Parser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 70);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["a", "b", "h", "H", "K", "t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(Hour1To24Parser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "k":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.hour24h, dateString);
            case "ko":
              return match.ordinalNumber(dateString, {
                unit: "hour"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 1 && value <= 24;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          var hours = value <= 24 ? value % 24 : value;
          date.setUTCHours(hours, 0, 0, 0);
          return date;
        }
      }]);
      return Hour1To24Parser2;
    })(_Parser2.Parser);
    exports2.Hour1To24Parser = Hour1To24Parser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/MinuteParser.js
var require_MinuteParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/MinuteParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.MinuteParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var MinuteParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(MinuteParser2, _Parser);
      var _super = (0, _createSuper2.default)(MinuteParser2);
      function MinuteParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, MinuteParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 60);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(MinuteParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "m":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.minute, dateString);
            case "mo":
              return match.ordinalNumber(dateString, {
                unit: "minute"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 59;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMinutes(value, 0, 0);
          return date;
        }
      }]);
      return MinuteParser2;
    })(_Parser2.Parser);
    exports2.MinuteParser = MinuteParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/SecondParser.js
var require_SecondParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/SecondParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.SecondParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var SecondParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(SecondParser2, _Parser);
      var _super = (0, _createSuper2.default)(SecondParser2);
      function SecondParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, SecondParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 50);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(SecondParser2, [{
        key: "parse",
        value: function parse(dateString, token, match) {
          switch (token) {
            case "s":
              return (0, _utils.parseNumericPattern)(_constants.numericPatterns.second, dateString);
            case "so":
              return match.ordinalNumber(dateString, {
                unit: "second"
              });
            default:
              return (0, _utils.parseNDigits)(token.length, dateString);
          }
        }
      }, {
        key: "validate",
        value: function validate2(_date, value) {
          return value >= 0 && value <= 59;
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCSeconds(value, 0);
          return date;
        }
      }]);
      return SecondParser2;
    })(_Parser2.Parser);
    exports2.SecondParser = SecondParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/FractionOfSecondParser.js
var require_FractionOfSecondParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/FractionOfSecondParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.FractionOfSecondParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var FractionOfSecondParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(FractionOfSecondParser2, _Parser);
      var _super = (0, _createSuper2.default)(FractionOfSecondParser2);
      function FractionOfSecondParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, FractionOfSecondParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 30);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["t", "T"]);
        return _this;
      }
      (0, _createClass2.default)(FractionOfSecondParser2, [{
        key: "parse",
        value: function parse(dateString, token) {
          var valueCallback = function valueCallback2(value) {
            return Math.floor(value * Math.pow(10, -token.length + 3));
          };
          return (0, _utils.mapValue)((0, _utils.parseNDigits)(token.length, dateString), valueCallback);
        }
      }, {
        key: "set",
        value: function set(date, _flags, value) {
          date.setUTCMilliseconds(value);
          return date;
        }
      }]);
      return FractionOfSecondParser2;
    })(_Parser2.Parser);
    exports2.FractionOfSecondParser = FractionOfSecondParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/ISOTimezoneWithZParser.js
var require_ISOTimezoneWithZParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/ISOTimezoneWithZParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ISOTimezoneWithZParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var ISOTimezoneWithZParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(ISOTimezoneWithZParser2, _Parser);
      var _super = (0, _createSuper2.default)(ISOTimezoneWithZParser2);
      function ISOTimezoneWithZParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, ISOTimezoneWithZParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 10);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["t", "T", "x"]);
        return _this;
      }
      (0, _createClass2.default)(ISOTimezoneWithZParser2, [{
        key: "parse",
        value: function parse(dateString, token) {
          switch (token) {
            case "X":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.basicOptionalMinutes, dateString);
            case "XX":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.basic, dateString);
            case "XXXX":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.basicOptionalSeconds, dateString);
            case "XXXXX":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.extendedOptionalSeconds, dateString);
            case "XXX":
            default:
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.extended, dateString);
          }
        }
      }, {
        key: "set",
        value: function set(date, flags, value) {
          if (flags.timestampIsSet) {
            return date;
          }
          return new Date(date.getTime() - value);
        }
      }]);
      return ISOTimezoneWithZParser2;
    })(_Parser2.Parser);
    exports2.ISOTimezoneWithZParser = ISOTimezoneWithZParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/ISOTimezoneParser.js
var require_ISOTimezoneParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/ISOTimezoneParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.ISOTimezoneParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _constants = require_constants2();
    var _utils = require_utils();
    var ISOTimezoneParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(ISOTimezoneParser2, _Parser);
      var _super = (0, _createSuper2.default)(ISOTimezoneParser2);
      function ISOTimezoneParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, ISOTimezoneParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 10);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", ["t", "T", "X"]);
        return _this;
      }
      (0, _createClass2.default)(ISOTimezoneParser2, [{
        key: "parse",
        value: function parse(dateString, token) {
          switch (token) {
            case "x":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.basicOptionalMinutes, dateString);
            case "xx":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.basic, dateString);
            case "xxxx":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.basicOptionalSeconds, dateString);
            case "xxxxx":
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.extendedOptionalSeconds, dateString);
            case "xxx":
            default:
              return (0, _utils.parseTimezonePattern)(_constants.timezonePatterns.extended, dateString);
          }
        }
      }, {
        key: "set",
        value: function set(date, flags, value) {
          if (flags.timestampIsSet) {
            return date;
          }
          return new Date(date.getTime() - value);
        }
      }]);
      return ISOTimezoneParser2;
    })(_Parser2.Parser);
    exports2.ISOTimezoneParser = ISOTimezoneParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/TimestampSecondsParser.js
var require_TimestampSecondsParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/TimestampSecondsParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.TimestampSecondsParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var TimestampSecondsParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(TimestampSecondsParser2, _Parser);
      var _super = (0, _createSuper2.default)(TimestampSecondsParser2);
      function TimestampSecondsParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, TimestampSecondsParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 40);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", "*");
        return _this;
      }
      (0, _createClass2.default)(TimestampSecondsParser2, [{
        key: "parse",
        value: function parse(dateString) {
          return (0, _utils.parseAnyDigitsSigned)(dateString);
        }
      }, {
        key: "set",
        value: function set(_date, _flags, value) {
          return [new Date(value * 1e3), {
            timestampIsSet: true
          }];
        }
      }]);
      return TimestampSecondsParser2;
    })(_Parser2.Parser);
    exports2.TimestampSecondsParser = TimestampSecondsParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/TimestampMillisecondsParser.js
var require_TimestampMillisecondsParser = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/TimestampMillisecondsParser.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.TimestampMillisecondsParser = void 0;
    var _classCallCheck2 = _interopRequireDefault(require_classCallCheck());
    var _createClass2 = _interopRequireDefault(require_createClass());
    var _assertThisInitialized2 = _interopRequireDefault(require_assertThisInitialized());
    var _inherits2 = _interopRequireDefault(require_inherits());
    var _createSuper2 = _interopRequireDefault(require_createSuper());
    var _defineProperty2 = _interopRequireDefault(require_defineProperty());
    var _Parser2 = require_Parser();
    var _utils = require_utils();
    var TimestampMillisecondsParser = /* @__PURE__ */ (function(_Parser) {
      (0, _inherits2.default)(TimestampMillisecondsParser2, _Parser);
      var _super = (0, _createSuper2.default)(TimestampMillisecondsParser2);
      function TimestampMillisecondsParser2() {
        var _this;
        (0, _classCallCheck2.default)(this, TimestampMillisecondsParser2);
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }
        _this = _super.call.apply(_super, [this].concat(args));
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "priority", 20);
        (0, _defineProperty2.default)((0, _assertThisInitialized2.default)(_this), "incompatibleTokens", "*");
        return _this;
      }
      (0, _createClass2.default)(TimestampMillisecondsParser2, [{
        key: "parse",
        value: function parse(dateString) {
          return (0, _utils.parseAnyDigitsSigned)(dateString);
        }
      }, {
        key: "set",
        value: function set(_date, _flags, value) {
          return [new Date(value), {
            timestampIsSet: true
          }];
        }
      }]);
      return TimestampMillisecondsParser2;
    })(_Parser2.Parser);
    exports2.TimestampMillisecondsParser = TimestampMillisecondsParser;
  }
});

// node_modules/date-fns/parse/_lib/parsers/index.js
var require_parsers = __commonJS({
  "node_modules/date-fns/parse/_lib/parsers/index.js"(exports2) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.parsers = void 0;
    var _EraParser = require_EraParser();
    var _YearParser = require_YearParser();
    var _LocalWeekYearParser = require_LocalWeekYearParser();
    var _ISOWeekYearParser = require_ISOWeekYearParser();
    var _ExtendedYearParser = require_ExtendedYearParser();
    var _QuarterParser = require_QuarterParser();
    var _StandAloneQuarterParser = require_StandAloneQuarterParser();
    var _MonthParser = require_MonthParser();
    var _StandAloneMonthParser = require_StandAloneMonthParser();
    var _LocalWeekParser = require_LocalWeekParser();
    var _ISOWeekParser = require_ISOWeekParser();
    var _DateParser = require_DateParser();
    var _DayOfYearParser = require_DayOfYearParser();
    var _DayParser = require_DayParser();
    var _LocalDayParser = require_LocalDayParser();
    var _StandAloneLocalDayParser = require_StandAloneLocalDayParser();
    var _ISODayParser = require_ISODayParser();
    var _AMPMParser = require_AMPMParser();
    var _AMPMMidnightParser = require_AMPMMidnightParser();
    var _DayPeriodParser = require_DayPeriodParser();
    var _Hour1to12Parser = require_Hour1to12Parser();
    var _Hour0to23Parser = require_Hour0to23Parser();
    var _Hour0To11Parser = require_Hour0To11Parser();
    var _Hour1To24Parser = require_Hour1To24Parser();
    var _MinuteParser = require_MinuteParser();
    var _SecondParser = require_SecondParser();
    var _FractionOfSecondParser = require_FractionOfSecondParser();
    var _ISOTimezoneWithZParser = require_ISOTimezoneWithZParser();
    var _ISOTimezoneParser = require_ISOTimezoneParser();
    var _TimestampSecondsParser = require_TimestampSecondsParser();
    var _TimestampMillisecondsParser = require_TimestampMillisecondsParser();
    var parsers = {
      G: new _EraParser.EraParser(),
      y: new _YearParser.YearParser(),
      Y: new _LocalWeekYearParser.LocalWeekYearParser(),
      R: new _ISOWeekYearParser.ISOWeekYearParser(),
      u: new _ExtendedYearParser.ExtendedYearParser(),
      Q: new _QuarterParser.QuarterParser(),
      q: new _StandAloneQuarterParser.StandAloneQuarterParser(),
      M: new _MonthParser.MonthParser(),
      L: new _StandAloneMonthParser.StandAloneMonthParser(),
      w: new _LocalWeekParser.LocalWeekParser(),
      I: new _ISOWeekParser.ISOWeekParser(),
      d: new _DateParser.DateParser(),
      D: new _DayOfYearParser.DayOfYearParser(),
      E: new _DayParser.DayParser(),
      e: new _LocalDayParser.LocalDayParser(),
      c: new _StandAloneLocalDayParser.StandAloneLocalDayParser(),
      i: new _ISODayParser.ISODayParser(),
      a: new _AMPMParser.AMPMParser(),
      b: new _AMPMMidnightParser.AMPMMidnightParser(),
      B: new _DayPeriodParser.DayPeriodParser(),
      h: new _Hour1to12Parser.Hour1to12Parser(),
      H: new _Hour0to23Parser.Hour0to23Parser(),
      K: new _Hour0To11Parser.Hour0To11Parser(),
      k: new _Hour1To24Parser.Hour1To24Parser(),
      m: new _MinuteParser.MinuteParser(),
      s: new _SecondParser.SecondParser(),
      S: new _FractionOfSecondParser.FractionOfSecondParser(),
      X: new _ISOTimezoneWithZParser.ISOTimezoneWithZParser(),
      x: new _ISOTimezoneParser.ISOTimezoneParser(),
      t: new _TimestampSecondsParser.TimestampSecondsParser(),
      T: new _TimestampMillisecondsParser.TimestampMillisecondsParser()
    };
    exports2.parsers = parsers;
  }
});

// node_modules/date-fns/parse/index.js
var require_parse = __commonJS({
  "node_modules/date-fns/parse/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = parse;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _createForOfIteratorHelper2 = _interopRequireDefault(require_createForOfIteratorHelper());
    var _index = _interopRequireDefault(require_defaultLocale());
    var _index2 = _interopRequireDefault(require_subMilliseconds());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_assign());
    var _index5 = _interopRequireDefault(require_longFormatters());
    var _index6 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index7 = require_protectedTokens();
    var _index8 = _interopRequireDefault(require_toInteger());
    var _index9 = _interopRequireDefault(require_requiredArgs());
    var _Setter = require_Setter();
    var _index10 = require_parsers();
    var _index11 = require_defaultOptions();
    var formattingTokensRegExp = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g;
    var longFormattingTokensRegExp = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g;
    var escapedStringRegExp = /^'([^]*?)'?$/;
    var doubleQuoteRegExp = /''/g;
    var notWhitespaceRegExp = /\S/;
    var unescapedLatinCharacterRegExp = /[a-zA-Z]/;
    function parse(dirtyDateString, dirtyFormatString, dirtyReferenceDate, options) {
      var _ref, _options$locale, _ref2, _ref3, _ref4, _options$firstWeekCon, _options$locale2, _options$locale2$opti, _defaultOptions$local, _defaultOptions$local2, _ref5, _ref6, _ref7, _options$weekStartsOn, _options$locale3, _options$locale3$opti, _defaultOptions$local3, _defaultOptions$local4;
      (0, _index9.default)(3, arguments);
      var dateString = String(dirtyDateString);
      var formatString = String(dirtyFormatString);
      var defaultOptions3 = (0, _index11.getDefaultOptions)();
      var locale = (_ref = (_options$locale = options === null || options === void 0 ? void 0 : options.locale) !== null && _options$locale !== void 0 ? _options$locale : defaultOptions3.locale) !== null && _ref !== void 0 ? _ref : _index.default;
      if (!locale.match) {
        throw new RangeError("locale must contain match property");
      }
      var firstWeekContainsDate = (0, _index8.default)((_ref2 = (_ref3 = (_ref4 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale2 = options.locale) === null || _options$locale2 === void 0 ? void 0 : (_options$locale2$opti = _options$locale2.options) === null || _options$locale2$opti === void 0 ? void 0 : _options$locale2$opti.firstWeekContainsDate) !== null && _ref4 !== void 0 ? _ref4 : defaultOptions3.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : 1);
      if (!(firstWeekContainsDate >= 1 && firstWeekContainsDate <= 7)) {
        throw new RangeError("firstWeekContainsDate must be between 1 and 7 inclusively");
      }
      var weekStartsOn = (0, _index8.default)((_ref5 = (_ref6 = (_ref7 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale3 = options.locale) === null || _options$locale3 === void 0 ? void 0 : (_options$locale3$opti = _options$locale3.options) === null || _options$locale3$opti === void 0 ? void 0 : _options$locale3$opti.weekStartsOn) !== null && _ref7 !== void 0 ? _ref7 : defaultOptions3.weekStartsOn) !== null && _ref6 !== void 0 ? _ref6 : (_defaultOptions$local3 = defaultOptions3.locale) === null || _defaultOptions$local3 === void 0 ? void 0 : (_defaultOptions$local4 = _defaultOptions$local3.options) === null || _defaultOptions$local4 === void 0 ? void 0 : _defaultOptions$local4.weekStartsOn) !== null && _ref5 !== void 0 ? _ref5 : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      if (formatString === "") {
        if (dateString === "") {
          return (0, _index3.default)(dirtyReferenceDate);
        } else {
          return /* @__PURE__ */ new Date(NaN);
        }
      }
      var subFnOptions = {
        firstWeekContainsDate,
        weekStartsOn,
        locale
      };
      var setters = [new _Setter.DateToSystemTimezoneSetter()];
      var tokens = formatString.match(longFormattingTokensRegExp).map(function(substring) {
        var firstCharacter = substring[0];
        if (firstCharacter in _index5.default) {
          var longFormatter = _index5.default[firstCharacter];
          return longFormatter(substring, locale.formatLong);
        }
        return substring;
      }).join("").match(formattingTokensRegExp);
      var usedTokens = [];
      var _iterator = (0, _createForOfIteratorHelper2.default)(tokens), _step;
      try {
        var _loop = function _loop2() {
          var token = _step.value;
          if (!(options !== null && options !== void 0 && options.useAdditionalWeekYearTokens) && (0, _index7.isProtectedWeekYearToken)(token)) {
            (0, _index7.throwProtectedError)(token, formatString, dirtyDateString);
          }
          if (!(options !== null && options !== void 0 && options.useAdditionalDayOfYearTokens) && (0, _index7.isProtectedDayOfYearToken)(token)) {
            (0, _index7.throwProtectedError)(token, formatString, dirtyDateString);
          }
          var firstCharacter = token[0];
          var parser2 = _index10.parsers[firstCharacter];
          if (parser2) {
            var incompatibleTokens = parser2.incompatibleTokens;
            if (Array.isArray(incompatibleTokens)) {
              var incompatibleToken = usedTokens.find(function(usedToken) {
                return incompatibleTokens.includes(usedToken.token) || usedToken.token === firstCharacter;
              });
              if (incompatibleToken) {
                throw new RangeError("The format string mustn't contain `".concat(incompatibleToken.fullToken, "` and `").concat(token, "` at the same time"));
              }
            } else if (parser2.incompatibleTokens === "*" && usedTokens.length > 0) {
              throw new RangeError("The format string mustn't contain `".concat(token, "` and any other token at the same time"));
            }
            usedTokens.push({
              token: firstCharacter,
              fullToken: token
            });
            var parseResult = parser2.run(dateString, token, locale.match, subFnOptions);
            if (!parseResult) {
              return {
                v: /* @__PURE__ */ new Date(NaN)
              };
            }
            setters.push(parseResult.setter);
            dateString = parseResult.rest;
          } else {
            if (firstCharacter.match(unescapedLatinCharacterRegExp)) {
              throw new RangeError("Format string contains an unescaped latin alphabet character `" + firstCharacter + "`");
            }
            if (token === "''") {
              token = "'";
            } else if (firstCharacter === "'") {
              token = cleanEscapedString(token);
            }
            if (dateString.indexOf(token) === 0) {
              dateString = dateString.slice(token.length);
            } else {
              return {
                v: /* @__PURE__ */ new Date(NaN)
              };
            }
          }
        };
        for (_iterator.s(); !(_step = _iterator.n()).done; ) {
          var _ret = _loop();
          if ((0, _typeof2.default)(_ret) === "object") return _ret.v;
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }
      if (dateString.length > 0 && notWhitespaceRegExp.test(dateString)) {
        return /* @__PURE__ */ new Date(NaN);
      }
      var uniquePrioritySetters = setters.map(function(setter2) {
        return setter2.priority;
      }).sort(function(a, b) {
        return b - a;
      }).filter(function(priority, index, array) {
        return array.indexOf(priority) === index;
      }).map(function(priority) {
        return setters.filter(function(setter2) {
          return setter2.priority === priority;
        }).sort(function(a, b) {
          return b.subPriority - a.subPriority;
        });
      }).map(function(setterArray) {
        return setterArray[0];
      });
      var date = (0, _index3.default)(dirtyReferenceDate);
      if (isNaN(date.getTime())) {
        return /* @__PURE__ */ new Date(NaN);
      }
      var utcDate = (0, _index2.default)(date, (0, _index6.default)(date));
      var flags = {};
      var _iterator2 = (0, _createForOfIteratorHelper2.default)(uniquePrioritySetters), _step2;
      try {
        for (_iterator2.s(); !(_step2 = _iterator2.n()).done; ) {
          var setter = _step2.value;
          if (!setter.validate(utcDate, subFnOptions)) {
            return /* @__PURE__ */ new Date(NaN);
          }
          var result = setter.set(utcDate, flags, subFnOptions);
          if (Array.isArray(result)) {
            utcDate = result[0];
            (0, _index4.default)(flags, result[1]);
          } else {
            utcDate = result;
          }
        }
      } catch (err) {
        _iterator2.e(err);
      } finally {
        _iterator2.f();
      }
      return utcDate;
    }
    function cleanEscapedString(input) {
      return input.match(escapedStringRegExp)[1].replace(doubleQuoteRegExp, "'");
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isMatch/index.js
var require_isMatch = __commonJS({
  "node_modules/date-fns/isMatch/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isMatch;
    var _index = _interopRequireDefault(require_parse());
    var _index2 = _interopRequireDefault(require_isValid());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function isMatch(dateString, formatString, options) {
      (0, _index3.default)(2, arguments);
      return (0, _index2.default)((0, _index.default)(dateString, formatString, /* @__PURE__ */ new Date(), options));
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isMonday/index.js
var require_isMonday = __commonJS({
  "node_modules/date-fns/isMonday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isMonday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isMonday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date).getDay() === 1;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isPast/index.js
var require_isPast = __commonJS({
  "node_modules/date-fns/isPast/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isPast;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isPast(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getTime() < Date.now();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfHour/index.js
var require_startOfHour = __commonJS({
  "node_modules/date-fns/startOfHour/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfHour;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfHour(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setMinutes(0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameHour/index.js
var require_isSameHour = __commonJS({
  "node_modules/date-fns/isSameHour/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameHour;
    var _index = _interopRequireDefault(require_startOfHour());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameHour(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfHour = (0, _index.default)(dirtyDateLeft);
      var dateRightStartOfHour = (0, _index.default)(dirtyDateRight);
      return dateLeftStartOfHour.getTime() === dateRightStartOfHour.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameWeek/index.js
var require_isSameWeek = __commonJS({
  "node_modules/date-fns/isSameWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameWeek;
    var _index = _interopRequireDefault(require_startOfWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameWeek(dirtyDateLeft, dirtyDateRight, options) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfWeek = (0, _index.default)(dirtyDateLeft, options);
      var dateRightStartOfWeek = (0, _index.default)(dirtyDateRight, options);
      return dateLeftStartOfWeek.getTime() === dateRightStartOfWeek.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameISOWeek/index.js
var require_isSameISOWeek = __commonJS({
  "node_modules/date-fns/isSameISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameISOWeek;
    var _index = _interopRequireDefault(require_isSameWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameISOWeek(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      return (0, _index.default)(dirtyDateLeft, dirtyDateRight, {
        weekStartsOn: 1
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameISOWeekYear/index.js
var require_isSameISOWeekYear = __commonJS({
  "node_modules/date-fns/isSameISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameISOWeekYear;
    var _index = _interopRequireDefault(require_startOfISOWeekYear());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameISOWeekYear(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfYear = (0, _index.default)(dirtyDateLeft);
      var dateRightStartOfYear = (0, _index.default)(dirtyDateRight);
      return dateLeftStartOfYear.getTime() === dateRightStartOfYear.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameMinute/index.js
var require_isSameMinute = __commonJS({
  "node_modules/date-fns/isSameMinute/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameMinute;
    var _index = _interopRequireDefault(require_startOfMinute());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameMinute(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfMinute = (0, _index.default)(dirtyDateLeft);
      var dateRightStartOfMinute = (0, _index.default)(dirtyDateRight);
      return dateLeftStartOfMinute.getTime() === dateRightStartOfMinute.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameMonth/index.js
var require_isSameMonth = __commonJS({
  "node_modules/date-fns/isSameMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameMonth;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameMonth(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      return dateLeft.getFullYear() === dateRight.getFullYear() && dateLeft.getMonth() === dateRight.getMonth();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameQuarter/index.js
var require_isSameQuarter = __commonJS({
  "node_modules/date-fns/isSameQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameQuarter;
    var _index = _interopRequireDefault(require_startOfQuarter());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameQuarter(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfQuarter = (0, _index.default)(dirtyDateLeft);
      var dateRightStartOfQuarter = (0, _index.default)(dirtyDateRight);
      return dateLeftStartOfQuarter.getTime() === dateRightStartOfQuarter.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfSecond/index.js
var require_startOfSecond = __commonJS({
  "node_modules/date-fns/startOfSecond/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfSecond;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfSecond(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      date.setMilliseconds(0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameSecond/index.js
var require_isSameSecond = __commonJS({
  "node_modules/date-fns/isSameSecond/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameSecond;
    var _index = _interopRequireDefault(require_startOfSecond());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameSecond(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeftStartOfSecond = (0, _index.default)(dirtyDateLeft);
      var dateRightStartOfSecond = (0, _index.default)(dirtyDateRight);
      return dateLeftStartOfSecond.getTime() === dateRightStartOfSecond.getTime();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isSameYear/index.js
var require_isSameYear = __commonJS({
  "node_modules/date-fns/isSameYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isSameYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isSameYear(dirtyDateLeft, dirtyDateRight) {
      (0, _index2.default)(2, arguments);
      var dateLeft = (0, _index.default)(dirtyDateLeft);
      var dateRight = (0, _index.default)(dirtyDateRight);
      return dateLeft.getFullYear() === dateRight.getFullYear();
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisHour/index.js
var require_isThisHour = __commonJS({
  "node_modules/date-fns/isThisHour/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisHour;
    var _index = _interopRequireDefault(require_isSameHour());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisHour(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(Date.now(), dirtyDate);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisISOWeek/index.js
var require_isThisISOWeek = __commonJS({
  "node_modules/date-fns/isThisISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisISOWeek;
    var _index = _interopRequireDefault(require_isSameISOWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisISOWeek(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, Date.now());
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisMinute/index.js
var require_isThisMinute = __commonJS({
  "node_modules/date-fns/isThisMinute/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisMinute;
    var _index = _interopRequireDefault(require_isSameMinute());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisMinute(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(Date.now(), dirtyDate);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisMonth/index.js
var require_isThisMonth = __commonJS({
  "node_modules/date-fns/isThisMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisMonth;
    var _index = _interopRequireDefault(require_isSameMonth());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisMonth(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(Date.now(), dirtyDate);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisQuarter/index.js
var require_isThisQuarter = __commonJS({
  "node_modules/date-fns/isThisQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisQuarter;
    var _index = _interopRequireDefault(require_isSameQuarter());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisQuarter(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(Date.now(), dirtyDate);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisSecond/index.js
var require_isThisSecond = __commonJS({
  "node_modules/date-fns/isThisSecond/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisSecond;
    var _index = _interopRequireDefault(require_isSameSecond());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisSecond(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(Date.now(), dirtyDate);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisWeek/index.js
var require_isThisWeek = __commonJS({
  "node_modules/date-fns/isThisWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisWeek;
    var _index = _interopRequireDefault(require_isSameWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisWeek(dirtyDate, options) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, Date.now(), options);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThisYear/index.js
var require_isThisYear = __commonJS({
  "node_modules/date-fns/isThisYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThisYear;
    var _index = _interopRequireDefault(require_isSameYear());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThisYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, Date.now());
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isThursday/index.js
var require_isThursday = __commonJS({
  "node_modules/date-fns/isThursday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isThursday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isThursday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDay() === 4;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isToday/index.js
var require_isToday = __commonJS({
  "node_modules/date-fns/isToday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isToday;
    var _index = _interopRequireDefault(require_isSameDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isToday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, Date.now());
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isTomorrow/index.js
var require_isTomorrow = __commonJS({
  "node_modules/date-fns/isTomorrow/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isTomorrow;
    var _index = _interopRequireDefault(require_addDays());
    var _index2 = _interopRequireDefault(require_isSameDay());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function isTomorrow(dirtyDate) {
      (0, _index3.default)(1, arguments);
      return (0, _index2.default)(dirtyDate, (0, _index.default)(Date.now(), 1));
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isTuesday/index.js
var require_isTuesday = __commonJS({
  "node_modules/date-fns/isTuesday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isTuesday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isTuesday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDay() === 2;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isWednesday/index.js
var require_isWednesday = __commonJS({
  "node_modules/date-fns/isWednesday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isWednesday;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isWednesday(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate).getDay() === 3;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isWithinInterval/index.js
var require_isWithinInterval = __commonJS({
  "node_modules/date-fns/isWithinInterval/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isWithinInterval;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function isWithinInterval(dirtyDate, interval) {
      (0, _index2.default)(2, arguments);
      var time = (0, _index.default)(dirtyDate).getTime();
      var startTime = (0, _index.default)(interval.start).getTime();
      var endTime = (0, _index.default)(interval.end).getTime();
      if (!(startTime <= endTime)) {
        throw new RangeError("Invalid interval");
      }
      return time >= startTime && time <= endTime;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subDays/index.js
var require_subDays = __commonJS({
  "node_modules/date-fns/subDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subDays;
    var _index = _interopRequireDefault(require_addDays());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function subDays(dirtyDate, dirtyAmount) {
      (0, _index2.default)(2, arguments);
      var amount = (0, _index3.default)(dirtyAmount);
      return (0, _index.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/isYesterday/index.js
var require_isYesterday = __commonJS({
  "node_modules/date-fns/isYesterday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = isYesterday;
    var _index = _interopRequireDefault(require_isSameDay());
    var _index2 = _interopRequireDefault(require_subDays());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function isYesterday(dirtyDate) {
      (0, _index3.default)(1, arguments);
      return (0, _index.default)(dirtyDate, (0, _index2.default)(Date.now(), 1));
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfDecade/index.js
var require_lastDayOfDecade = __commonJS({
  "node_modules/date-fns/lastDayOfDecade/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfDecade;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function lastDayOfDecade(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      var decade = 9 + Math.floor(year / 10) * 10;
      date.setFullYear(decade + 1, 0, 0);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfWeek/index.js
var require_lastDayOfWeek = __commonJS({
  "node_modules/date-fns/lastDayOfWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfWeek;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_toInteger());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var _index4 = require_defaultOptions();
    function lastDayOfWeek(dirtyDate, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index3.default)(1, arguments);
      var defaultOptions3 = (0, _index4.getDefaultOptions)();
      var weekStartsOn = (0, _index2.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6");
      }
      var date = (0, _index.default)(dirtyDate);
      var day = date.getDay();
      var diff = (day < weekStartsOn ? -7 : 0) + 6 - (day - weekStartsOn);
      date.setHours(0, 0, 0, 0);
      date.setDate(date.getDate() + diff);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfISOWeek/index.js
var require_lastDayOfISOWeek = __commonJS({
  "node_modules/date-fns/lastDayOfISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfISOWeek;
    var _index = _interopRequireDefault(require_lastDayOfWeek());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function lastDayOfISOWeek(dirtyDate) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(dirtyDate, {
        weekStartsOn: 1
      });
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfISOWeekYear/index.js
var require_lastDayOfISOWeekYear = __commonJS({
  "node_modules/date-fns/lastDayOfISOWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfISOWeekYear;
    var _index = _interopRequireDefault(require_getISOWeekYear());
    var _index2 = _interopRequireDefault(require_startOfISOWeek());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function lastDayOfISOWeekYear(dirtyDate) {
      (0, _index3.default)(1, arguments);
      var year = (0, _index.default)(dirtyDate);
      var fourthOfJanuary = /* @__PURE__ */ new Date(0);
      fourthOfJanuary.setFullYear(year + 1, 0, 4);
      fourthOfJanuary.setHours(0, 0, 0, 0);
      var date = (0, _index2.default)(fourthOfJanuary);
      date.setDate(date.getDate() - 1);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfQuarter/index.js
var require_lastDayOfQuarter = __commonJS({
  "node_modules/date-fns/lastDayOfQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfQuarter;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function lastDayOfQuarter(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var currentMonth = date.getMonth();
      var month = currentMonth - currentMonth % 3 + 3;
      date.setMonth(month, 0);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lastDayOfYear/index.js
var require_lastDayOfYear = __commonJS({
  "node_modules/date-fns/lastDayOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lastDayOfYear;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function lastDayOfYear(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      date.setFullYear(year + 1, 0, 0);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/lightFormat/index.js
var require_lightFormat = __commonJS({
  "node_modules/date-fns/lightFormat/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = lightFormat;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_lightFormatters());
    var _index3 = _interopRequireDefault(require_getTimezoneOffsetInMilliseconds());
    var _index4 = _interopRequireDefault(require_isValid());
    var _index5 = _interopRequireDefault(require_subMilliseconds());
    var _index6 = _interopRequireDefault(require_requiredArgs());
    var formattingTokensRegExp = /(\w)\1*|''|'(''|[^'])+('|$)|./g;
    var escapedStringRegExp = /^'([^]*?)'?$/;
    var doubleQuoteRegExp = /''/g;
    var unescapedLatinCharacterRegExp = /[a-zA-Z]/;
    function lightFormat(dirtyDate, formatStr) {
      (0, _index6.default)(2, arguments);
      var originalDate = (0, _index.default)(dirtyDate);
      if (!(0, _index4.default)(originalDate)) {
        throw new RangeError("Invalid time value");
      }
      var timezoneOffset = (0, _index3.default)(originalDate);
      var utcDate = (0, _index5.default)(originalDate, timezoneOffset);
      var tokens = formatStr.match(formattingTokensRegExp);
      if (!tokens) return "";
      var result = tokens.map(function(substring) {
        if (substring === "''") {
          return "'";
        }
        var firstCharacter = substring[0];
        if (firstCharacter === "'") {
          return cleanEscapedString(substring);
        }
        var formatter = _index2.default[firstCharacter];
        if (formatter) {
          return formatter(utcDate, substring);
        }
        if (firstCharacter.match(unescapedLatinCharacterRegExp)) {
          throw new RangeError("Format string contains an unescaped latin alphabet character `" + firstCharacter + "`");
        }
        return substring;
      }).join("");
      return result;
    }
    function cleanEscapedString(input) {
      var matches = input.match(escapedStringRegExp);
      if (!matches) {
        return input;
      }
      return matches[1].replace(doubleQuoteRegExp, "'");
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/milliseconds/index.js
var require_milliseconds = __commonJS({
  "node_modules/date-fns/milliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = milliseconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var daysInYear = 365.2425;
    function milliseconds(_ref) {
      var years = _ref.years, months = _ref.months, weeks = _ref.weeks, days = _ref.days, hours = _ref.hours, minutes = _ref.minutes, seconds = _ref.seconds;
      (0, _index.default)(1, arguments);
      var totalDays = 0;
      if (years) totalDays += years * daysInYear;
      if (months) totalDays += months * (daysInYear / 12);
      if (weeks) totalDays += weeks * 7;
      if (days) totalDays += days;
      var totalSeconds = totalDays * 24 * 60 * 60;
      if (hours) totalSeconds += hours * 60 * 60;
      if (minutes) totalSeconds += minutes * 60;
      if (seconds) totalSeconds += seconds;
      return Math.round(totalSeconds * 1e3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/millisecondsToHours/index.js
var require_millisecondsToHours = __commonJS({
  "node_modules/date-fns/millisecondsToHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = millisecondsToHours;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function millisecondsToHours(milliseconds) {
      (0, _index.default)(1, arguments);
      var hours = milliseconds / _index2.millisecondsInHour;
      return Math.floor(hours);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/millisecondsToMinutes/index.js
var require_millisecondsToMinutes = __commonJS({
  "node_modules/date-fns/millisecondsToMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = millisecondsToMinutes;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function millisecondsToMinutes(milliseconds) {
      (0, _index.default)(1, arguments);
      var minutes = milliseconds / _index2.millisecondsInMinute;
      return Math.floor(minutes);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/millisecondsToSeconds/index.js
var require_millisecondsToSeconds = __commonJS({
  "node_modules/date-fns/millisecondsToSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = millisecondsToSeconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function millisecondsToSeconds(milliseconds) {
      (0, _index.default)(1, arguments);
      var seconds = milliseconds / _index2.millisecondsInSecond;
      return Math.floor(seconds);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/minutesToHours/index.js
var require_minutesToHours = __commonJS({
  "node_modules/date-fns/minutesToHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = minutesToHours;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function minutesToHours(minutes) {
      (0, _index.default)(1, arguments);
      var hours = minutes / _index2.minutesInHour;
      return Math.floor(hours);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/minutesToMilliseconds/index.js
var require_minutesToMilliseconds = __commonJS({
  "node_modules/date-fns/minutesToMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = minutesToMilliseconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function minutesToMilliseconds(minutes) {
      (0, _index.default)(1, arguments);
      return Math.floor(minutes * _index2.millisecondsInMinute);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/minutesToSeconds/index.js
var require_minutesToSeconds = __commonJS({
  "node_modules/date-fns/minutesToSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = minutesToSeconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function minutesToSeconds(minutes) {
      (0, _index.default)(1, arguments);
      return Math.floor(minutes * _index2.secondsInMinute);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/monthsToQuarters/index.js
var require_monthsToQuarters = __commonJS({
  "node_modules/date-fns/monthsToQuarters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = monthsToQuarters;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function monthsToQuarters(months) {
      (0, _index.default)(1, arguments);
      var quarters = months / _index2.monthsInQuarter;
      return Math.floor(quarters);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/monthsToYears/index.js
var require_monthsToYears = __commonJS({
  "node_modules/date-fns/monthsToYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = monthsToYears;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function monthsToYears(months) {
      (0, _index.default)(1, arguments);
      var years = months / _index2.monthsInYear;
      return Math.floor(years);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextDay/index.js
var require_nextDay = __commonJS({
  "node_modules/date-fns/nextDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextDay;
    var _index = _interopRequireDefault(require_addDays());
    var _index2 = _interopRequireDefault(require_getDay());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function nextDay(date, day) {
      (0, _index3.default)(2, arguments);
      var delta = day - (0, _index2.default)(date);
      if (delta <= 0) delta += 7;
      return (0, _index.default)(date, delta);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextFriday/index.js
var require_nextFriday = __commonJS({
  "node_modules/date-fns/nextFriday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextFriday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextFriday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 5);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextMonday/index.js
var require_nextMonday = __commonJS({
  "node_modules/date-fns/nextMonday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextMonday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextMonday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 1);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextSaturday/index.js
var require_nextSaturday = __commonJS({
  "node_modules/date-fns/nextSaturday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextSaturday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextSaturday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 6);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextSunday/index.js
var require_nextSunday = __commonJS({
  "node_modules/date-fns/nextSunday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextSunday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextSunday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 0);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextThursday/index.js
var require_nextThursday = __commonJS({
  "node_modules/date-fns/nextThursday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextThursday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextThursday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 4);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextTuesday/index.js
var require_nextTuesday = __commonJS({
  "node_modules/date-fns/nextTuesday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextTuesday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextTuesday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 2);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/nextWednesday/index.js
var require_nextWednesday = __commonJS({
  "node_modules/date-fns/nextWednesday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = nextWednesday;
    var _index = _interopRequireDefault(require_nextDay());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function nextWednesday(date) {
      (0, _index2.default)(1, arguments);
      return (0, _index.default)(date, 3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/parseISO/index.js
var require_parseISO = __commonJS({
  "node_modules/date-fns/parseISO/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = parseISO;
    var _index = require_constants();
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function parseISO(argument, options) {
      var _options$additionalDi;
      (0, _index2.default)(1, arguments);
      var additionalDigits = (0, _index3.default)((_options$additionalDi = options === null || options === void 0 ? void 0 : options.additionalDigits) !== null && _options$additionalDi !== void 0 ? _options$additionalDi : 2);
      if (additionalDigits !== 2 && additionalDigits !== 1 && additionalDigits !== 0) {
        throw new RangeError("additionalDigits must be 0, 1 or 2");
      }
      if (!(typeof argument === "string" || Object.prototype.toString.call(argument) === "[object String]")) {
        return /* @__PURE__ */ new Date(NaN);
      }
      var dateStrings = splitDateString(argument);
      var date;
      if (dateStrings.date) {
        var parseYearResult = parseYear(dateStrings.date, additionalDigits);
        date = parseDate(parseYearResult.restDateString, parseYearResult.year);
      }
      if (!date || isNaN(date.getTime())) {
        return /* @__PURE__ */ new Date(NaN);
      }
      var timestamp = date.getTime();
      var time = 0;
      var offset;
      if (dateStrings.time) {
        time = parseTime(dateStrings.time);
        if (isNaN(time)) {
          return /* @__PURE__ */ new Date(NaN);
        }
      }
      if (dateStrings.timezone) {
        offset = parseTimezone(dateStrings.timezone);
        if (isNaN(offset)) {
          return /* @__PURE__ */ new Date(NaN);
        }
      } else {
        var dirtyDate = new Date(timestamp + time);
        var result = /* @__PURE__ */ new Date(0);
        result.setFullYear(dirtyDate.getUTCFullYear(), dirtyDate.getUTCMonth(), dirtyDate.getUTCDate());
        result.setHours(dirtyDate.getUTCHours(), dirtyDate.getUTCMinutes(), dirtyDate.getUTCSeconds(), dirtyDate.getUTCMilliseconds());
        return result;
      }
      return new Date(timestamp + time + offset);
    }
    var patterns = {
      dateTimeDelimiter: /[T ]/,
      timeZoneDelimiter: /[Z ]/i,
      timezone: /([Z+-].*)$/
    };
    var dateRegex = /^-?(?:(\d{3})|(\d{2})(?:-?(\d{2}))?|W(\d{2})(?:-?(\d{1}))?|)$/;
    var timeRegex = /^(\d{2}(?:[.,]\d*)?)(?::?(\d{2}(?:[.,]\d*)?))?(?::?(\d{2}(?:[.,]\d*)?))?$/;
    var timezoneRegex = /^([+-])(\d{2})(?::?(\d{2}))?$/;
    function splitDateString(dateString) {
      var dateStrings = {};
      var array = dateString.split(patterns.dateTimeDelimiter);
      var timeString;
      if (array.length > 2) {
        return dateStrings;
      }
      if (/:/.test(array[0])) {
        timeString = array[0];
      } else {
        dateStrings.date = array[0];
        timeString = array[1];
        if (patterns.timeZoneDelimiter.test(dateStrings.date)) {
          dateStrings.date = dateString.split(patterns.timeZoneDelimiter)[0];
          timeString = dateString.substr(dateStrings.date.length, dateString.length);
        }
      }
      if (timeString) {
        var token = patterns.timezone.exec(timeString);
        if (token) {
          dateStrings.time = timeString.replace(token[1], "");
          dateStrings.timezone = token[1];
        } else {
          dateStrings.time = timeString;
        }
      }
      return dateStrings;
    }
    function parseYear(dateString, additionalDigits) {
      var regex = new RegExp("^(?:(\\d{4}|[+-]\\d{" + (4 + additionalDigits) + "})|(\\d{2}|[+-]\\d{" + (2 + additionalDigits) + "})$)");
      var captures = dateString.match(regex);
      if (!captures) return {
        year: NaN,
        restDateString: ""
      };
      var year = captures[1] ? parseInt(captures[1]) : null;
      var century = captures[2] ? parseInt(captures[2]) : null;
      return {
        year: century === null ? year : century * 100,
        restDateString: dateString.slice((captures[1] || captures[2]).length)
      };
    }
    function parseDate(dateString, year) {
      if (year === null) return /* @__PURE__ */ new Date(NaN);
      var captures = dateString.match(dateRegex);
      if (!captures) return /* @__PURE__ */ new Date(NaN);
      var isWeekDate = !!captures[4];
      var dayOfYear = parseDateUnit(captures[1]);
      var month = parseDateUnit(captures[2]) - 1;
      var day = parseDateUnit(captures[3]);
      var week = parseDateUnit(captures[4]);
      var dayOfWeek = parseDateUnit(captures[5]) - 1;
      if (isWeekDate) {
        if (!validateWeekDate(year, week, dayOfWeek)) {
          return /* @__PURE__ */ new Date(NaN);
        }
        return dayOfISOWeekYear(year, week, dayOfWeek);
      } else {
        var date = /* @__PURE__ */ new Date(0);
        if (!validateDate(year, month, day) || !validateDayOfYearDate(year, dayOfYear)) {
          return /* @__PURE__ */ new Date(NaN);
        }
        date.setUTCFullYear(year, month, Math.max(dayOfYear, day));
        return date;
      }
    }
    function parseDateUnit(value) {
      return value ? parseInt(value) : 1;
    }
    function parseTime(timeString) {
      var captures = timeString.match(timeRegex);
      if (!captures) return NaN;
      var hours = parseTimeUnit(captures[1]);
      var minutes = parseTimeUnit(captures[2]);
      var seconds = parseTimeUnit(captures[3]);
      if (!validateTime(hours, minutes, seconds)) {
        return NaN;
      }
      return hours * _index.millisecondsInHour + minutes * _index.millisecondsInMinute + seconds * 1e3;
    }
    function parseTimeUnit(value) {
      return value && parseFloat(value.replace(",", ".")) || 0;
    }
    function parseTimezone(timezoneString) {
      if (timezoneString === "Z") return 0;
      var captures = timezoneString.match(timezoneRegex);
      if (!captures) return 0;
      var sign = captures[1] === "+" ? -1 : 1;
      var hours = parseInt(captures[2]);
      var minutes = captures[3] && parseInt(captures[3]) || 0;
      if (!validateTimezone(hours, minutes)) {
        return NaN;
      }
      return sign * (hours * _index.millisecondsInHour + minutes * _index.millisecondsInMinute);
    }
    function dayOfISOWeekYear(isoWeekYear, week, day) {
      var date = /* @__PURE__ */ new Date(0);
      date.setUTCFullYear(isoWeekYear, 0, 4);
      var fourthOfJanuaryDay = date.getUTCDay() || 7;
      var diff = (week - 1) * 7 + day + 1 - fourthOfJanuaryDay;
      date.setUTCDate(date.getUTCDate() + diff);
      return date;
    }
    var daysInMonths = [31, null, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    function isLeapYearIndex(year) {
      return year % 400 === 0 || year % 4 === 0 && year % 100 !== 0;
    }
    function validateDate(year, month, date) {
      return month >= 0 && month <= 11 && date >= 1 && date <= (daysInMonths[month] || (isLeapYearIndex(year) ? 29 : 28));
    }
    function validateDayOfYearDate(year, dayOfYear) {
      return dayOfYear >= 1 && dayOfYear <= (isLeapYearIndex(year) ? 366 : 365);
    }
    function validateWeekDate(_year, week, day) {
      return week >= 1 && week <= 53 && day >= 0 && day <= 6;
    }
    function validateTime(hours, minutes, seconds) {
      if (hours === 24) {
        return minutes === 0 && seconds === 0;
      }
      return seconds >= 0 && seconds < 60 && minutes >= 0 && minutes < 60 && hours >= 0 && hours < 25;
    }
    function validateTimezone(_hours, minutes) {
      return minutes >= 0 && minutes <= 59;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/parseJSON/index.js
var require_parseJSON = __commonJS({
  "node_modules/date-fns/parseJSON/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = parseJSON;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function parseJSON(argument) {
      (0, _index2.default)(1, arguments);
      if (typeof argument === "string") {
        var parts = argument.match(/(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:\.(\d{0,7}))?(?:Z|(.)(\d{2}):?(\d{2})?)?/);
        if (parts) {
          return new Date(Date.UTC(+parts[1], +parts[2] - 1, +parts[3], +parts[4] - (+parts[9] || 0) * (parts[8] == "-" ? -1 : 1), +parts[5] - (+parts[10] || 0) * (parts[8] == "-" ? -1 : 1), +parts[6], +((parts[7] || "0") + "00").substring(0, 3)));
        }
        return /* @__PURE__ */ new Date(NaN);
      }
      return (0, _index.default)(argument);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousDay/index.js
var require_previousDay = __commonJS({
  "node_modules/date-fns/previousDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousDay;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_getDay());
    var _index3 = _interopRequireDefault(require_subDays());
    function previousDay(date, day) {
      (0, _index.default)(2, arguments);
      var delta = (0, _index2.default)(date) - day;
      if (delta <= 0) delta += 7;
      return (0, _index3.default)(date, delta);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousFriday/index.js
var require_previousFriday = __commonJS({
  "node_modules/date-fns/previousFriday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousFriday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousFriday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 5);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousMonday/index.js
var require_previousMonday = __commonJS({
  "node_modules/date-fns/previousMonday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousMonday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousMonday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 1);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousSaturday/index.js
var require_previousSaturday = __commonJS({
  "node_modules/date-fns/previousSaturday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousSaturday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousSaturday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 6);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousSunday/index.js
var require_previousSunday = __commonJS({
  "node_modules/date-fns/previousSunday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousSunday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousSunday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 0);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousThursday/index.js
var require_previousThursday = __commonJS({
  "node_modules/date-fns/previousThursday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousThursday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousThursday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 4);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousTuesday/index.js
var require_previousTuesday = __commonJS({
  "node_modules/date-fns/previousTuesday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousTuesday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousTuesday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 2);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/previousWednesday/index.js
var require_previousWednesday = __commonJS({
  "node_modules/date-fns/previousWednesday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = previousWednesday;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = _interopRequireDefault(require_previousDay());
    function previousWednesday(date) {
      (0, _index.default)(1, arguments);
      return (0, _index2.default)(date, 3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/quartersToMonths/index.js
var require_quartersToMonths = __commonJS({
  "node_modules/date-fns/quartersToMonths/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = quartersToMonths;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function quartersToMonths(quarters) {
      (0, _index.default)(1, arguments);
      return Math.floor(quarters * _index2.monthsInQuarter);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/quartersToYears/index.js
var require_quartersToYears = __commonJS({
  "node_modules/date-fns/quartersToYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = quartersToYears;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function quartersToYears(quarters) {
      (0, _index.default)(1, arguments);
      var years = quarters / _index2.quartersInYear;
      return Math.floor(years);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/roundToNearestMinutes/index.js
var require_roundToNearestMinutes = __commonJS({
  "node_modules/date-fns/roundToNearestMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = roundToNearestMinutes;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = require_roundingMethods();
    var _index3 = _interopRequireDefault(require_toInteger());
    function roundToNearestMinutes(dirtyDate, options) {
      var _options$nearestTo;
      if (arguments.length < 1) {
        throw new TypeError("1 argument required, but only none provided present");
      }
      var nearestTo = (0, _index3.default)((_options$nearestTo = options === null || options === void 0 ? void 0 : options.nearestTo) !== null && _options$nearestTo !== void 0 ? _options$nearestTo : 1);
      if (nearestTo < 1 || nearestTo > 30) {
        throw new RangeError("`options.nearestTo` must be between 1 and 30");
      }
      var date = (0, _index.default)(dirtyDate);
      var seconds = date.getSeconds();
      var minutes = date.getMinutes() + seconds / 60;
      var roundingMethod = (0, _index2.getRoundingMethod)(options === null || options === void 0 ? void 0 : options.roundingMethod);
      var roundedMinutes = roundingMethod(minutes / nearestTo) * nearestTo;
      var remainderMinutes = minutes % nearestTo;
      var addedMinutes = Math.round(remainderMinutes / nearestTo) * nearestTo;
      return new Date(date.getFullYear(), date.getMonth(), date.getDate(), date.getHours(), roundedMinutes + addedMinutes);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/secondsToHours/index.js
var require_secondsToHours = __commonJS({
  "node_modules/date-fns/secondsToHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = secondsToHours;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function secondsToHours(seconds) {
      (0, _index.default)(1, arguments);
      var hours = seconds / _index2.secondsInHour;
      return Math.floor(hours);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/secondsToMilliseconds/index.js
var require_secondsToMilliseconds = __commonJS({
  "node_modules/date-fns/secondsToMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = secondsToMilliseconds;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function secondsToMilliseconds(seconds) {
      (0, _index.default)(1, arguments);
      return seconds * _index2.millisecondsInSecond;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/secondsToMinutes/index.js
var require_secondsToMinutes = __commonJS({
  "node_modules/date-fns/secondsToMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = secondsToMinutes;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function secondsToMinutes(seconds) {
      (0, _index.default)(1, arguments);
      var minutes = seconds / _index2.secondsInMinute;
      return Math.floor(minutes);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setMonth/index.js
var require_setMonth = __commonJS({
  "node_modules/date-fns/setMonth/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setMonth;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_getDaysInMonth());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function setMonth(dirtyDate, dirtyMonth) {
      (0, _index4.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var month = (0, _index.default)(dirtyMonth);
      var year = date.getFullYear();
      var day = date.getDate();
      var dateWithDesiredMonth = /* @__PURE__ */ new Date(0);
      dateWithDesiredMonth.setFullYear(year, month, 15);
      dateWithDesiredMonth.setHours(0, 0, 0, 0);
      var daysInMonth = (0, _index3.default)(dateWithDesiredMonth);
      date.setMonth(month, Math.min(day, daysInMonth));
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/set/index.js
var require_set = __commonJS({
  "node_modules/date-fns/set/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = set;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_setMonth());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function set(dirtyDate, values) {
      (0, _index4.default)(2, arguments);
      if ((0, _typeof2.default)(values) !== "object" || values === null) {
        throw new RangeError("values parameter must be an object");
      }
      var date = (0, _index.default)(dirtyDate);
      if (isNaN(date.getTime())) {
        return /* @__PURE__ */ new Date(NaN);
      }
      if (values.year != null) {
        date.setFullYear(values.year);
      }
      if (values.month != null) {
        date = (0, _index2.default)(date, values.month);
      }
      if (values.date != null) {
        date.setDate((0, _index3.default)(values.date));
      }
      if (values.hours != null) {
        date.setHours((0, _index3.default)(values.hours));
      }
      if (values.minutes != null) {
        date.setMinutes((0, _index3.default)(values.minutes));
      }
      if (values.seconds != null) {
        date.setSeconds((0, _index3.default)(values.seconds));
      }
      if (values.milliseconds != null) {
        date.setMilliseconds((0, _index3.default)(values.milliseconds));
      }
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setDate/index.js
var require_setDate = __commonJS({
  "node_modules/date-fns/setDate/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setDate;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setDate(dirtyDate, dirtyDayOfMonth) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var dayOfMonth = (0, _index.default)(dirtyDayOfMonth);
      date.setDate(dayOfMonth);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setDay/index.js
var require_setDay = __commonJS({
  "node_modules/date-fns/setDay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setDay;
    var _index = _interopRequireDefault(require_addDays());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_toInteger());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    var _index5 = require_defaultOptions();
    function setDay(dirtyDate, dirtyDay, options) {
      var _ref, _ref2, _ref3, _options$weekStartsOn, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index4.default)(2, arguments);
      var defaultOptions3 = (0, _index5.getDefaultOptions)();
      var weekStartsOn = (0, _index3.default)((_ref = (_ref2 = (_ref3 = (_options$weekStartsOn = options === null || options === void 0 ? void 0 : options.weekStartsOn) !== null && _options$weekStartsOn !== void 0 ? _options$weekStartsOn : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.weekStartsOn) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.weekStartsOn) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.weekStartsOn) !== null && _ref !== void 0 ? _ref : 0);
      if (!(weekStartsOn >= 0 && weekStartsOn <= 6)) {
        throw new RangeError("weekStartsOn must be between 0 and 6 inclusively");
      }
      var date = (0, _index2.default)(dirtyDate);
      var day = (0, _index3.default)(dirtyDay);
      var currentDay = date.getDay();
      var remainder = day % 7;
      var dayIndex = (remainder + 7) % 7;
      var delta = 7 - weekStartsOn;
      var diff = day < 0 || day > 6 ? day - (currentDay + delta) % 7 : (dayIndex + delta) % 7 - (currentDay + delta) % 7;
      return (0, _index.default)(date, diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setDayOfYear/index.js
var require_setDayOfYear = __commonJS({
  "node_modules/date-fns/setDayOfYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setDayOfYear;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setDayOfYear(dirtyDate, dirtyDayOfYear) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var dayOfYear = (0, _index.default)(dirtyDayOfYear);
      date.setMonth(0);
      date.setDate(dayOfYear);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setDefaultOptions/index.js
var require_setDefaultOptions = __commonJS({
  "node_modules/date-fns/setDefaultOptions/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setDefaultOptions;
    var _index = require_defaultOptions();
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function setDefaultOptions(newOptions) {
      (0, _index2.default)(1, arguments);
      var result = {};
      var defaultOptions3 = (0, _index.getDefaultOptions)();
      for (var property in defaultOptions3) {
        if (Object.prototype.hasOwnProperty.call(defaultOptions3, property)) {
          ;
          result[property] = defaultOptions3[property];
        }
      }
      for (var _property in newOptions) {
        if (Object.prototype.hasOwnProperty.call(newOptions, _property)) {
          if (newOptions[_property] === void 0) {
            delete result[_property];
          } else {
            ;
            result[_property] = newOptions[_property];
          }
        }
      }
      (0, _index.setDefaultOptions)(result);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setHours/index.js
var require_setHours = __commonJS({
  "node_modules/date-fns/setHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setHours;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setHours(dirtyDate, dirtyHours) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var hours = (0, _index.default)(dirtyHours);
      date.setHours(hours);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setISODay/index.js
var require_setISODay = __commonJS({
  "node_modules/date-fns/setISODay/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setISODay;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_addDays());
    var _index4 = _interopRequireDefault(require_getISODay());
    var _index5 = _interopRequireDefault(require_requiredArgs());
    function setISODay(dirtyDate, dirtyDay) {
      (0, _index5.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var day = (0, _index.default)(dirtyDay);
      var currentDay = (0, _index4.default)(date);
      var diff = day - currentDay;
      return (0, _index3.default)(date, diff);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setISOWeek/index.js
var require_setISOWeek = __commonJS({
  "node_modules/date-fns/setISOWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setISOWeek;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_getISOWeek());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function setISOWeek(dirtyDate, dirtyISOWeek) {
      (0, _index4.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var isoWeek = (0, _index.default)(dirtyISOWeek);
      var diff = (0, _index3.default)(date) - isoWeek;
      date.setDate(date.getDate() - diff * 7);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setMilliseconds/index.js
var require_setMilliseconds = __commonJS({
  "node_modules/date-fns/setMilliseconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setMilliseconds;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setMilliseconds(dirtyDate, dirtyMilliseconds) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var milliseconds = (0, _index.default)(dirtyMilliseconds);
      date.setMilliseconds(milliseconds);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setMinutes/index.js
var require_setMinutes = __commonJS({
  "node_modules/date-fns/setMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setMinutes;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setMinutes(dirtyDate, dirtyMinutes) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var minutes = (0, _index.default)(dirtyMinutes);
      date.setMinutes(minutes);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setQuarter/index.js
var require_setQuarter = __commonJS({
  "node_modules/date-fns/setQuarter/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setQuarter;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_setMonth());
    var _index4 = _interopRequireDefault(require_requiredArgs());
    function setQuarter(dirtyDate, dirtyQuarter) {
      (0, _index4.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var quarter = (0, _index.default)(dirtyQuarter);
      var oldQuarter = Math.floor(date.getMonth() / 3) + 1;
      var diff = quarter - oldQuarter;
      return (0, _index3.default)(date, date.getMonth() + diff * 3);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setSeconds/index.js
var require_setSeconds = __commonJS({
  "node_modules/date-fns/setSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setSeconds;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setSeconds(dirtyDate, dirtySeconds) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var seconds = (0, _index.default)(dirtySeconds);
      date.setSeconds(seconds);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setWeek/index.js
var require_setWeek = __commonJS({
  "node_modules/date-fns/setWeek/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setWeek;
    var _index = _interopRequireDefault(require_getWeek());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var _index4 = _interopRequireDefault(require_toInteger());
    function setWeek(dirtyDate, dirtyWeek, options) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var week = (0, _index4.default)(dirtyWeek);
      var diff = (0, _index.default)(date, options) - week;
      date.setDate(date.getDate() - diff * 7);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setWeekYear/index.js
var require_setWeekYear = __commonJS({
  "node_modules/date-fns/setWeekYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setWeekYear;
    var _index = _interopRequireDefault(require_differenceInCalendarDays());
    var _index2 = _interopRequireDefault(require_startOfWeekYear());
    var _index3 = _interopRequireDefault(require_toDate());
    var _index4 = _interopRequireDefault(require_toInteger());
    var _index5 = _interopRequireDefault(require_requiredArgs());
    var _index6 = require_defaultOptions();
    function setWeekYear(dirtyDate, dirtyWeekYear, options) {
      var _ref, _ref2, _ref3, _options$firstWeekCon, _options$locale, _options$locale$optio, _defaultOptions$local, _defaultOptions$local2;
      (0, _index5.default)(2, arguments);
      var defaultOptions3 = (0, _index6.getDefaultOptions)();
      var firstWeekContainsDate = (0, _index4.default)((_ref = (_ref2 = (_ref3 = (_options$firstWeekCon = options === null || options === void 0 ? void 0 : options.firstWeekContainsDate) !== null && _options$firstWeekCon !== void 0 ? _options$firstWeekCon : options === null || options === void 0 ? void 0 : (_options$locale = options.locale) === null || _options$locale === void 0 ? void 0 : (_options$locale$optio = _options$locale.options) === null || _options$locale$optio === void 0 ? void 0 : _options$locale$optio.firstWeekContainsDate) !== null && _ref3 !== void 0 ? _ref3 : defaultOptions3.firstWeekContainsDate) !== null && _ref2 !== void 0 ? _ref2 : (_defaultOptions$local = defaultOptions3.locale) === null || _defaultOptions$local === void 0 ? void 0 : (_defaultOptions$local2 = _defaultOptions$local.options) === null || _defaultOptions$local2 === void 0 ? void 0 : _defaultOptions$local2.firstWeekContainsDate) !== null && _ref !== void 0 ? _ref : 1);
      var date = (0, _index3.default)(dirtyDate);
      var weekYear = (0, _index4.default)(dirtyWeekYear);
      var diff = (0, _index.default)(date, (0, _index2.default)(date, options));
      var firstWeek = /* @__PURE__ */ new Date(0);
      firstWeek.setFullYear(weekYear, 0, firstWeekContainsDate);
      firstWeek.setHours(0, 0, 0, 0);
      date = (0, _index2.default)(firstWeek, options);
      date.setDate(date.getDate() + diff);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/setYear/index.js
var require_setYear = __commonJS({
  "node_modules/date-fns/setYear/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = setYear;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_toDate());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function setYear(dirtyDate, dirtyYear) {
      (0, _index3.default)(2, arguments);
      var date = (0, _index2.default)(dirtyDate);
      var year = (0, _index.default)(dirtyYear);
      if (isNaN(date.getTime())) {
        return /* @__PURE__ */ new Date(NaN);
      }
      date.setFullYear(year);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfDecade/index.js
var require_startOfDecade = __commonJS({
  "node_modules/date-fns/startOfDecade/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfDecade;
    var _index = _interopRequireDefault(require_toDate());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    function startOfDecade(dirtyDate) {
      (0, _index2.default)(1, arguments);
      var date = (0, _index.default)(dirtyDate);
      var year = date.getFullYear();
      var decade = Math.floor(year / 10) * 10;
      date.setFullYear(decade, 0, 1);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfToday/index.js
var require_startOfToday = __commonJS({
  "node_modules/date-fns/startOfToday/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfToday;
    var _index = _interopRequireDefault(require_startOfDay());
    function startOfToday() {
      return (0, _index.default)(Date.now());
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfTomorrow/index.js
var require_startOfTomorrow = __commonJS({
  "node_modules/date-fns/startOfTomorrow/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfTomorrow;
    function startOfTomorrow() {
      var now = /* @__PURE__ */ new Date();
      var year = now.getFullYear();
      var month = now.getMonth();
      var day = now.getDate();
      var date = /* @__PURE__ */ new Date(0);
      date.setFullYear(year, month, day + 1);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/startOfYesterday/index.js
var require_startOfYesterday = __commonJS({
  "node_modules/date-fns/startOfYesterday/index.js"(exports2, module) {
    "use strict";
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = startOfYesterday;
    function startOfYesterday() {
      var now = /* @__PURE__ */ new Date();
      var year = now.getFullYear();
      var month = now.getMonth();
      var day = now.getDate();
      var date = /* @__PURE__ */ new Date(0);
      date.setFullYear(year, month, day - 1);
      date.setHours(0, 0, 0, 0);
      return date;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subMonths/index.js
var require_subMonths = __commonJS({
  "node_modules/date-fns/subMonths/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subMonths;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addMonths());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function subMonths(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/sub/index.js
var require_sub = __commonJS({
  "node_modules/date-fns/sub/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = sub;
    var _typeof2 = _interopRequireDefault(require_typeof());
    var _index = _interopRequireDefault(require_subDays());
    var _index2 = _interopRequireDefault(require_subMonths());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    var _index4 = _interopRequireDefault(require_toInteger());
    function sub(date, duration) {
      (0, _index3.default)(2, arguments);
      if (!duration || (0, _typeof2.default)(duration) !== "object") return /* @__PURE__ */ new Date(NaN);
      var years = duration.years ? (0, _index4.default)(duration.years) : 0;
      var months = duration.months ? (0, _index4.default)(duration.months) : 0;
      var weeks = duration.weeks ? (0, _index4.default)(duration.weeks) : 0;
      var days = duration.days ? (0, _index4.default)(duration.days) : 0;
      var hours = duration.hours ? (0, _index4.default)(duration.hours) : 0;
      var minutes = duration.minutes ? (0, _index4.default)(duration.minutes) : 0;
      var seconds = duration.seconds ? (0, _index4.default)(duration.seconds) : 0;
      var dateWithoutMonths = (0, _index2.default)(date, months + years * 12);
      var dateWithoutDays = (0, _index.default)(dateWithoutMonths, days + weeks * 7);
      var minutestoSub = minutes + hours * 60;
      var secondstoSub = seconds + minutestoSub * 60;
      var mstoSub = secondstoSub * 1e3;
      var finalDate = new Date(dateWithoutDays.getTime() - mstoSub);
      return finalDate;
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subBusinessDays/index.js
var require_subBusinessDays = __commonJS({
  "node_modules/date-fns/subBusinessDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subBusinessDays;
    var _index = _interopRequireDefault(require_addBusinessDays());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function subBusinessDays(dirtyDate, dirtyAmount) {
      (0, _index2.default)(2, arguments);
      var amount = (0, _index3.default)(dirtyAmount);
      return (0, _index.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subHours/index.js
var require_subHours = __commonJS({
  "node_modules/date-fns/subHours/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subHours;
    var _index = _interopRequireDefault(require_addHours());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function subHours(dirtyDate, dirtyAmount) {
      (0, _index2.default)(2, arguments);
      var amount = (0, _index3.default)(dirtyAmount);
      return (0, _index.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subMinutes/index.js
var require_subMinutes = __commonJS({
  "node_modules/date-fns/subMinutes/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subMinutes;
    var _index = _interopRequireDefault(require_addMinutes());
    var _index2 = _interopRequireDefault(require_requiredArgs());
    var _index3 = _interopRequireDefault(require_toInteger());
    function subMinutes(dirtyDate, dirtyAmount) {
      (0, _index2.default)(2, arguments);
      var amount = (0, _index3.default)(dirtyAmount);
      return (0, _index.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subQuarters/index.js
var require_subQuarters = __commonJS({
  "node_modules/date-fns/subQuarters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subQuarters;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addQuarters());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function subQuarters(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subSeconds/index.js
var require_subSeconds = __commonJS({
  "node_modules/date-fns/subSeconds/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subSeconds;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addSeconds());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function subSeconds(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subWeeks/index.js
var require_subWeeks = __commonJS({
  "node_modules/date-fns/subWeeks/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subWeeks;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addWeeks());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function subWeeks(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/subYears/index.js
var require_subYears = __commonJS({
  "node_modules/date-fns/subYears/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = subYears;
    var _index = _interopRequireDefault(require_toInteger());
    var _index2 = _interopRequireDefault(require_addYears());
    var _index3 = _interopRequireDefault(require_requiredArgs());
    function subYears(dirtyDate, dirtyAmount) {
      (0, _index3.default)(2, arguments);
      var amount = (0, _index.default)(dirtyAmount);
      return (0, _index2.default)(dirtyDate, -amount);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/weeksToDays/index.js
var require_weeksToDays = __commonJS({
  "node_modules/date-fns/weeksToDays/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = weeksToDays;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function weeksToDays(weeks) {
      (0, _index.default)(1, arguments);
      return Math.floor(weeks * _index2.daysInWeek);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/yearsToMonths/index.js
var require_yearsToMonths = __commonJS({
  "node_modules/date-fns/yearsToMonths/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = yearsToMonths;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function yearsToMonths(years) {
      (0, _index.default)(1, arguments);
      return Math.floor(years * _index2.monthsInYear);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/yearsToQuarters/index.js
var require_yearsToQuarters = __commonJS({
  "node_modules/date-fns/yearsToQuarters/index.js"(exports2, module) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    exports2.default = yearsToQuarters;
    var _index = _interopRequireDefault(require_requiredArgs());
    var _index2 = require_constants();
    function yearsToQuarters(years) {
      (0, _index.default)(1, arguments);
      return Math.floor(years * _index2.quartersInYear);
    }
    module.exports = exports2.default;
  }
});

// node_modules/date-fns/index.js
var require_date_fns = __commonJS({
  "node_modules/date-fns/index.js"(exports2) {
    "use strict";
    var _interopRequireDefault = require_interopRequireDefault().default;
    Object.defineProperty(exports2, "__esModule", {
      value: true
    });
    var _exportNames = {
      add: true,
      addBusinessDays: true,
      addDays: true,
      addHours: true,
      addISOWeekYears: true,
      addMilliseconds: true,
      addMinutes: true,
      addMonths: true,
      addQuarters: true,
      addSeconds: true,
      addWeeks: true,
      addYears: true,
      areIntervalsOverlapping: true,
      clamp: true,
      closestIndexTo: true,
      closestTo: true,
      compareAsc: true,
      compareDesc: true,
      daysToWeeks: true,
      differenceInBusinessDays: true,
      differenceInCalendarDays: true,
      differenceInCalendarISOWeekYears: true,
      differenceInCalendarISOWeeks: true,
      differenceInCalendarMonths: true,
      differenceInCalendarQuarters: true,
      differenceInCalendarWeeks: true,
      differenceInCalendarYears: true,
      differenceInDays: true,
      differenceInHours: true,
      differenceInISOWeekYears: true,
      differenceInMilliseconds: true,
      differenceInMinutes: true,
      differenceInMonths: true,
      differenceInQuarters: true,
      differenceInSeconds: true,
      differenceInWeeks: true,
      differenceInYears: true,
      eachDayOfInterval: true,
      eachHourOfInterval: true,
      eachMinuteOfInterval: true,
      eachMonthOfInterval: true,
      eachQuarterOfInterval: true,
      eachWeekOfInterval: true,
      eachWeekendOfInterval: true,
      eachWeekendOfMonth: true,
      eachWeekendOfYear: true,
      eachYearOfInterval: true,
      endOfDay: true,
      endOfDecade: true,
      endOfHour: true,
      endOfISOWeek: true,
      endOfISOWeekYear: true,
      endOfMinute: true,
      endOfMonth: true,
      endOfQuarter: true,
      endOfSecond: true,
      endOfToday: true,
      endOfTomorrow: true,
      endOfWeek: true,
      endOfYear: true,
      endOfYesterday: true,
      format: true,
      formatDistance: true,
      formatDistanceStrict: true,
      formatDistanceToNow: true,
      formatDistanceToNowStrict: true,
      formatDuration: true,
      formatISO: true,
      formatISO9075: true,
      formatISODuration: true,
      formatRFC3339: true,
      formatRFC7231: true,
      formatRelative: true,
      fromUnixTime: true,
      getDate: true,
      getDay: true,
      getDayOfYear: true,
      getDaysInMonth: true,
      getDaysInYear: true,
      getDecade: true,
      getDefaultOptions: true,
      getHours: true,
      getISODay: true,
      getISOWeek: true,
      getISOWeekYear: true,
      getISOWeeksInYear: true,
      getMilliseconds: true,
      getMinutes: true,
      getMonth: true,
      getOverlappingDaysInIntervals: true,
      getQuarter: true,
      getSeconds: true,
      getTime: true,
      getUnixTime: true,
      getWeek: true,
      getWeekOfMonth: true,
      getWeekYear: true,
      getWeeksInMonth: true,
      getYear: true,
      hoursToMilliseconds: true,
      hoursToMinutes: true,
      hoursToSeconds: true,
      intervalToDuration: true,
      intlFormat: true,
      intlFormatDistance: true,
      isAfter: true,
      isBefore: true,
      isDate: true,
      isEqual: true,
      isExists: true,
      isFirstDayOfMonth: true,
      isFriday: true,
      isFuture: true,
      isLastDayOfMonth: true,
      isLeapYear: true,
      isMatch: true,
      isMonday: true,
      isPast: true,
      isSameDay: true,
      isSameHour: true,
      isSameISOWeek: true,
      isSameISOWeekYear: true,
      isSameMinute: true,
      isSameMonth: true,
      isSameQuarter: true,
      isSameSecond: true,
      isSameWeek: true,
      isSameYear: true,
      isSaturday: true,
      isSunday: true,
      isThisHour: true,
      isThisISOWeek: true,
      isThisMinute: true,
      isThisMonth: true,
      isThisQuarter: true,
      isThisSecond: true,
      isThisWeek: true,
      isThisYear: true,
      isThursday: true,
      isToday: true,
      isTomorrow: true,
      isTuesday: true,
      isValid: true,
      isWednesday: true,
      isWeekend: true,
      isWithinInterval: true,
      isYesterday: true,
      lastDayOfDecade: true,
      lastDayOfISOWeek: true,
      lastDayOfISOWeekYear: true,
      lastDayOfMonth: true,
      lastDayOfQuarter: true,
      lastDayOfWeek: true,
      lastDayOfYear: true,
      lightFormat: true,
      max: true,
      milliseconds: true,
      millisecondsToHours: true,
      millisecondsToMinutes: true,
      millisecondsToSeconds: true,
      min: true,
      minutesToHours: true,
      minutesToMilliseconds: true,
      minutesToSeconds: true,
      monthsToQuarters: true,
      monthsToYears: true,
      nextDay: true,
      nextFriday: true,
      nextMonday: true,
      nextSaturday: true,
      nextSunday: true,
      nextThursday: true,
      nextTuesday: true,
      nextWednesday: true,
      parse: true,
      parseISO: true,
      parseJSON: true,
      previousDay: true,
      previousFriday: true,
      previousMonday: true,
      previousSaturday: true,
      previousSunday: true,
      previousThursday: true,
      previousTuesday: true,
      previousWednesday: true,
      quartersToMonths: true,
      quartersToYears: true,
      roundToNearestMinutes: true,
      secondsToHours: true,
      secondsToMilliseconds: true,
      secondsToMinutes: true,
      set: true,
      setDate: true,
      setDay: true,
      setDayOfYear: true,
      setDefaultOptions: true,
      setHours: true,
      setISODay: true,
      setISOWeek: true,
      setISOWeekYear: true,
      setMilliseconds: true,
      setMinutes: true,
      setMonth: true,
      setQuarter: true,
      setSeconds: true,
      setWeek: true,
      setWeekYear: true,
      setYear: true,
      startOfDay: true,
      startOfDecade: true,
      startOfHour: true,
      startOfISOWeek: true,
      startOfISOWeekYear: true,
      startOfMinute: true,
      startOfMonth: true,
      startOfQuarter: true,
      startOfSecond: true,
      startOfToday: true,
      startOfTomorrow: true,
      startOfWeek: true,
      startOfWeekYear: true,
      startOfYear: true,
      startOfYesterday: true,
      sub: true,
      subBusinessDays: true,
      subDays: true,
      subHours: true,
      subISOWeekYears: true,
      subMilliseconds: true,
      subMinutes: true,
      subMonths: true,
      subQuarters: true,
      subSeconds: true,
      subWeeks: true,
      subYears: true,
      toDate: true,
      weeksToDays: true,
      yearsToMonths: true,
      yearsToQuarters: true
    };
    Object.defineProperty(exports2, "add", {
      enumerable: true,
      get: function get() {
        return _index.default;
      }
    });
    Object.defineProperty(exports2, "addBusinessDays", {
      enumerable: true,
      get: function get() {
        return _index2.default;
      }
    });
    Object.defineProperty(exports2, "addDays", {
      enumerable: true,
      get: function get() {
        return _index3.default;
      }
    });
    Object.defineProperty(exports2, "addHours", {
      enumerable: true,
      get: function get() {
        return _index4.default;
      }
    });
    Object.defineProperty(exports2, "addISOWeekYears", {
      enumerable: true,
      get: function get() {
        return _index5.default;
      }
    });
    Object.defineProperty(exports2, "addMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index6.default;
      }
    });
    Object.defineProperty(exports2, "addMinutes", {
      enumerable: true,
      get: function get() {
        return _index7.default;
      }
    });
    Object.defineProperty(exports2, "addMonths", {
      enumerable: true,
      get: function get() {
        return _index8.default;
      }
    });
    Object.defineProperty(exports2, "addQuarters", {
      enumerable: true,
      get: function get() {
        return _index9.default;
      }
    });
    Object.defineProperty(exports2, "addSeconds", {
      enumerable: true,
      get: function get() {
        return _index10.default;
      }
    });
    Object.defineProperty(exports2, "addWeeks", {
      enumerable: true,
      get: function get() {
        return _index11.default;
      }
    });
    Object.defineProperty(exports2, "addYears", {
      enumerable: true,
      get: function get() {
        return _index12.default;
      }
    });
    Object.defineProperty(exports2, "areIntervalsOverlapping", {
      enumerable: true,
      get: function get() {
        return _index13.default;
      }
    });
    Object.defineProperty(exports2, "clamp", {
      enumerable: true,
      get: function get() {
        return _index14.default;
      }
    });
    Object.defineProperty(exports2, "closestIndexTo", {
      enumerable: true,
      get: function get() {
        return _index15.default;
      }
    });
    Object.defineProperty(exports2, "closestTo", {
      enumerable: true,
      get: function get() {
        return _index16.default;
      }
    });
    Object.defineProperty(exports2, "compareAsc", {
      enumerable: true,
      get: function get() {
        return _index17.default;
      }
    });
    Object.defineProperty(exports2, "compareDesc", {
      enumerable: true,
      get: function get() {
        return _index18.default;
      }
    });
    Object.defineProperty(exports2, "daysToWeeks", {
      enumerable: true,
      get: function get() {
        return _index19.default;
      }
    });
    Object.defineProperty(exports2, "differenceInBusinessDays", {
      enumerable: true,
      get: function get() {
        return _index20.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarDays", {
      enumerable: true,
      get: function get() {
        return _index21.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarISOWeekYears", {
      enumerable: true,
      get: function get() {
        return _index22.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarISOWeeks", {
      enumerable: true,
      get: function get() {
        return _index23.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarMonths", {
      enumerable: true,
      get: function get() {
        return _index24.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarQuarters", {
      enumerable: true,
      get: function get() {
        return _index25.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarWeeks", {
      enumerable: true,
      get: function get() {
        return _index26.default;
      }
    });
    Object.defineProperty(exports2, "differenceInCalendarYears", {
      enumerable: true,
      get: function get() {
        return _index27.default;
      }
    });
    Object.defineProperty(exports2, "differenceInDays", {
      enumerable: true,
      get: function get() {
        return _index28.default;
      }
    });
    Object.defineProperty(exports2, "differenceInHours", {
      enumerable: true,
      get: function get() {
        return _index29.default;
      }
    });
    Object.defineProperty(exports2, "differenceInISOWeekYears", {
      enumerable: true,
      get: function get() {
        return _index30.default;
      }
    });
    Object.defineProperty(exports2, "differenceInMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index31.default;
      }
    });
    Object.defineProperty(exports2, "differenceInMinutes", {
      enumerable: true,
      get: function get() {
        return _index32.default;
      }
    });
    Object.defineProperty(exports2, "differenceInMonths", {
      enumerable: true,
      get: function get() {
        return _index33.default;
      }
    });
    Object.defineProperty(exports2, "differenceInQuarters", {
      enumerable: true,
      get: function get() {
        return _index34.default;
      }
    });
    Object.defineProperty(exports2, "differenceInSeconds", {
      enumerable: true,
      get: function get() {
        return _index35.default;
      }
    });
    Object.defineProperty(exports2, "differenceInWeeks", {
      enumerable: true,
      get: function get() {
        return _index36.default;
      }
    });
    Object.defineProperty(exports2, "differenceInYears", {
      enumerable: true,
      get: function get() {
        return _index37.default;
      }
    });
    Object.defineProperty(exports2, "eachDayOfInterval", {
      enumerable: true,
      get: function get() {
        return _index38.default;
      }
    });
    Object.defineProperty(exports2, "eachHourOfInterval", {
      enumerable: true,
      get: function get() {
        return _index39.default;
      }
    });
    Object.defineProperty(exports2, "eachMinuteOfInterval", {
      enumerable: true,
      get: function get() {
        return _index40.default;
      }
    });
    Object.defineProperty(exports2, "eachMonthOfInterval", {
      enumerable: true,
      get: function get() {
        return _index41.default;
      }
    });
    Object.defineProperty(exports2, "eachQuarterOfInterval", {
      enumerable: true,
      get: function get() {
        return _index42.default;
      }
    });
    Object.defineProperty(exports2, "eachWeekOfInterval", {
      enumerable: true,
      get: function get() {
        return _index43.default;
      }
    });
    Object.defineProperty(exports2, "eachWeekendOfInterval", {
      enumerable: true,
      get: function get() {
        return _index44.default;
      }
    });
    Object.defineProperty(exports2, "eachWeekendOfMonth", {
      enumerable: true,
      get: function get() {
        return _index45.default;
      }
    });
    Object.defineProperty(exports2, "eachWeekendOfYear", {
      enumerable: true,
      get: function get() {
        return _index46.default;
      }
    });
    Object.defineProperty(exports2, "eachYearOfInterval", {
      enumerable: true,
      get: function get() {
        return _index47.default;
      }
    });
    Object.defineProperty(exports2, "endOfDay", {
      enumerable: true,
      get: function get() {
        return _index48.default;
      }
    });
    Object.defineProperty(exports2, "endOfDecade", {
      enumerable: true,
      get: function get() {
        return _index49.default;
      }
    });
    Object.defineProperty(exports2, "endOfHour", {
      enumerable: true,
      get: function get() {
        return _index50.default;
      }
    });
    Object.defineProperty(exports2, "endOfISOWeek", {
      enumerable: true,
      get: function get() {
        return _index51.default;
      }
    });
    Object.defineProperty(exports2, "endOfISOWeekYear", {
      enumerable: true,
      get: function get() {
        return _index52.default;
      }
    });
    Object.defineProperty(exports2, "endOfMinute", {
      enumerable: true,
      get: function get() {
        return _index53.default;
      }
    });
    Object.defineProperty(exports2, "endOfMonth", {
      enumerable: true,
      get: function get() {
        return _index54.default;
      }
    });
    Object.defineProperty(exports2, "endOfQuarter", {
      enumerable: true,
      get: function get() {
        return _index55.default;
      }
    });
    Object.defineProperty(exports2, "endOfSecond", {
      enumerable: true,
      get: function get() {
        return _index56.default;
      }
    });
    Object.defineProperty(exports2, "endOfToday", {
      enumerable: true,
      get: function get() {
        return _index57.default;
      }
    });
    Object.defineProperty(exports2, "endOfTomorrow", {
      enumerable: true,
      get: function get() {
        return _index58.default;
      }
    });
    Object.defineProperty(exports2, "endOfWeek", {
      enumerable: true,
      get: function get() {
        return _index59.default;
      }
    });
    Object.defineProperty(exports2, "endOfYear", {
      enumerable: true,
      get: function get() {
        return _index60.default;
      }
    });
    Object.defineProperty(exports2, "endOfYesterday", {
      enumerable: true,
      get: function get() {
        return _index61.default;
      }
    });
    Object.defineProperty(exports2, "format", {
      enumerable: true,
      get: function get() {
        return _index62.default;
      }
    });
    Object.defineProperty(exports2, "formatDistance", {
      enumerable: true,
      get: function get() {
        return _index63.default;
      }
    });
    Object.defineProperty(exports2, "formatDistanceStrict", {
      enumerable: true,
      get: function get() {
        return _index64.default;
      }
    });
    Object.defineProperty(exports2, "formatDistanceToNow", {
      enumerable: true,
      get: function get() {
        return _index65.default;
      }
    });
    Object.defineProperty(exports2, "formatDistanceToNowStrict", {
      enumerable: true,
      get: function get() {
        return _index66.default;
      }
    });
    Object.defineProperty(exports2, "formatDuration", {
      enumerable: true,
      get: function get() {
        return _index67.default;
      }
    });
    Object.defineProperty(exports2, "formatISO", {
      enumerable: true,
      get: function get() {
        return _index68.default;
      }
    });
    Object.defineProperty(exports2, "formatISO9075", {
      enumerable: true,
      get: function get() {
        return _index69.default;
      }
    });
    Object.defineProperty(exports2, "formatISODuration", {
      enumerable: true,
      get: function get() {
        return _index70.default;
      }
    });
    Object.defineProperty(exports2, "formatRFC3339", {
      enumerable: true,
      get: function get() {
        return _index71.default;
      }
    });
    Object.defineProperty(exports2, "formatRFC7231", {
      enumerable: true,
      get: function get() {
        return _index72.default;
      }
    });
    Object.defineProperty(exports2, "formatRelative", {
      enumerable: true,
      get: function get() {
        return _index73.default;
      }
    });
    Object.defineProperty(exports2, "fromUnixTime", {
      enumerable: true,
      get: function get() {
        return _index74.default;
      }
    });
    Object.defineProperty(exports2, "getDate", {
      enumerable: true,
      get: function get() {
        return _index75.default;
      }
    });
    Object.defineProperty(exports2, "getDay", {
      enumerable: true,
      get: function get() {
        return _index76.default;
      }
    });
    Object.defineProperty(exports2, "getDayOfYear", {
      enumerable: true,
      get: function get() {
        return _index77.default;
      }
    });
    Object.defineProperty(exports2, "getDaysInMonth", {
      enumerable: true,
      get: function get() {
        return _index78.default;
      }
    });
    Object.defineProperty(exports2, "getDaysInYear", {
      enumerable: true,
      get: function get() {
        return _index79.default;
      }
    });
    Object.defineProperty(exports2, "getDecade", {
      enumerable: true,
      get: function get() {
        return _index80.default;
      }
    });
    Object.defineProperty(exports2, "getDefaultOptions", {
      enumerable: true,
      get: function get() {
        return _index81.default;
      }
    });
    Object.defineProperty(exports2, "getHours", {
      enumerable: true,
      get: function get() {
        return _index82.default;
      }
    });
    Object.defineProperty(exports2, "getISODay", {
      enumerable: true,
      get: function get() {
        return _index83.default;
      }
    });
    Object.defineProperty(exports2, "getISOWeek", {
      enumerable: true,
      get: function get() {
        return _index84.default;
      }
    });
    Object.defineProperty(exports2, "getISOWeekYear", {
      enumerable: true,
      get: function get() {
        return _index85.default;
      }
    });
    Object.defineProperty(exports2, "getISOWeeksInYear", {
      enumerable: true,
      get: function get() {
        return _index86.default;
      }
    });
    Object.defineProperty(exports2, "getMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index87.default;
      }
    });
    Object.defineProperty(exports2, "getMinutes", {
      enumerable: true,
      get: function get() {
        return _index88.default;
      }
    });
    Object.defineProperty(exports2, "getMonth", {
      enumerable: true,
      get: function get() {
        return _index89.default;
      }
    });
    Object.defineProperty(exports2, "getOverlappingDaysInIntervals", {
      enumerable: true,
      get: function get() {
        return _index90.default;
      }
    });
    Object.defineProperty(exports2, "getQuarter", {
      enumerable: true,
      get: function get() {
        return _index91.default;
      }
    });
    Object.defineProperty(exports2, "getSeconds", {
      enumerable: true,
      get: function get() {
        return _index92.default;
      }
    });
    Object.defineProperty(exports2, "getTime", {
      enumerable: true,
      get: function get() {
        return _index93.default;
      }
    });
    Object.defineProperty(exports2, "getUnixTime", {
      enumerable: true,
      get: function get() {
        return _index94.default;
      }
    });
    Object.defineProperty(exports2, "getWeek", {
      enumerable: true,
      get: function get() {
        return _index95.default;
      }
    });
    Object.defineProperty(exports2, "getWeekOfMonth", {
      enumerable: true,
      get: function get() {
        return _index96.default;
      }
    });
    Object.defineProperty(exports2, "getWeekYear", {
      enumerable: true,
      get: function get() {
        return _index97.default;
      }
    });
    Object.defineProperty(exports2, "getWeeksInMonth", {
      enumerable: true,
      get: function get() {
        return _index98.default;
      }
    });
    Object.defineProperty(exports2, "getYear", {
      enumerable: true,
      get: function get() {
        return _index99.default;
      }
    });
    Object.defineProperty(exports2, "hoursToMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index100.default;
      }
    });
    Object.defineProperty(exports2, "hoursToMinutes", {
      enumerable: true,
      get: function get() {
        return _index101.default;
      }
    });
    Object.defineProperty(exports2, "hoursToSeconds", {
      enumerable: true,
      get: function get() {
        return _index102.default;
      }
    });
    Object.defineProperty(exports2, "intervalToDuration", {
      enumerable: true,
      get: function get() {
        return _index103.default;
      }
    });
    Object.defineProperty(exports2, "intlFormat", {
      enumerable: true,
      get: function get() {
        return _index104.default;
      }
    });
    Object.defineProperty(exports2, "intlFormatDistance", {
      enumerable: true,
      get: function get() {
        return _index105.default;
      }
    });
    Object.defineProperty(exports2, "isAfter", {
      enumerable: true,
      get: function get() {
        return _index106.default;
      }
    });
    Object.defineProperty(exports2, "isBefore", {
      enumerable: true,
      get: function get() {
        return _index107.default;
      }
    });
    Object.defineProperty(exports2, "isDate", {
      enumerable: true,
      get: function get() {
        return _index108.default;
      }
    });
    Object.defineProperty(exports2, "isEqual", {
      enumerable: true,
      get: function get() {
        return _index109.default;
      }
    });
    Object.defineProperty(exports2, "isExists", {
      enumerable: true,
      get: function get() {
        return _index110.default;
      }
    });
    Object.defineProperty(exports2, "isFirstDayOfMonth", {
      enumerable: true,
      get: function get() {
        return _index111.default;
      }
    });
    Object.defineProperty(exports2, "isFriday", {
      enumerable: true,
      get: function get() {
        return _index112.default;
      }
    });
    Object.defineProperty(exports2, "isFuture", {
      enumerable: true,
      get: function get() {
        return _index113.default;
      }
    });
    Object.defineProperty(exports2, "isLastDayOfMonth", {
      enumerable: true,
      get: function get() {
        return _index114.default;
      }
    });
    Object.defineProperty(exports2, "isLeapYear", {
      enumerable: true,
      get: function get() {
        return _index115.default;
      }
    });
    Object.defineProperty(exports2, "isMatch", {
      enumerable: true,
      get: function get() {
        return _index116.default;
      }
    });
    Object.defineProperty(exports2, "isMonday", {
      enumerable: true,
      get: function get() {
        return _index117.default;
      }
    });
    Object.defineProperty(exports2, "isPast", {
      enumerable: true,
      get: function get() {
        return _index118.default;
      }
    });
    Object.defineProperty(exports2, "isSameDay", {
      enumerable: true,
      get: function get() {
        return _index119.default;
      }
    });
    Object.defineProperty(exports2, "isSameHour", {
      enumerable: true,
      get: function get() {
        return _index120.default;
      }
    });
    Object.defineProperty(exports2, "isSameISOWeek", {
      enumerable: true,
      get: function get() {
        return _index121.default;
      }
    });
    Object.defineProperty(exports2, "isSameISOWeekYear", {
      enumerable: true,
      get: function get() {
        return _index122.default;
      }
    });
    Object.defineProperty(exports2, "isSameMinute", {
      enumerable: true,
      get: function get() {
        return _index123.default;
      }
    });
    Object.defineProperty(exports2, "isSameMonth", {
      enumerable: true,
      get: function get() {
        return _index124.default;
      }
    });
    Object.defineProperty(exports2, "isSameQuarter", {
      enumerable: true,
      get: function get() {
        return _index125.default;
      }
    });
    Object.defineProperty(exports2, "isSameSecond", {
      enumerable: true,
      get: function get() {
        return _index126.default;
      }
    });
    Object.defineProperty(exports2, "isSameWeek", {
      enumerable: true,
      get: function get() {
        return _index127.default;
      }
    });
    Object.defineProperty(exports2, "isSameYear", {
      enumerable: true,
      get: function get() {
        return _index128.default;
      }
    });
    Object.defineProperty(exports2, "isSaturday", {
      enumerable: true,
      get: function get() {
        return _index129.default;
      }
    });
    Object.defineProperty(exports2, "isSunday", {
      enumerable: true,
      get: function get() {
        return _index130.default;
      }
    });
    Object.defineProperty(exports2, "isThisHour", {
      enumerable: true,
      get: function get() {
        return _index131.default;
      }
    });
    Object.defineProperty(exports2, "isThisISOWeek", {
      enumerable: true,
      get: function get() {
        return _index132.default;
      }
    });
    Object.defineProperty(exports2, "isThisMinute", {
      enumerable: true,
      get: function get() {
        return _index133.default;
      }
    });
    Object.defineProperty(exports2, "isThisMonth", {
      enumerable: true,
      get: function get() {
        return _index134.default;
      }
    });
    Object.defineProperty(exports2, "isThisQuarter", {
      enumerable: true,
      get: function get() {
        return _index135.default;
      }
    });
    Object.defineProperty(exports2, "isThisSecond", {
      enumerable: true,
      get: function get() {
        return _index136.default;
      }
    });
    Object.defineProperty(exports2, "isThisWeek", {
      enumerable: true,
      get: function get() {
        return _index137.default;
      }
    });
    Object.defineProperty(exports2, "isThisYear", {
      enumerable: true,
      get: function get() {
        return _index138.default;
      }
    });
    Object.defineProperty(exports2, "isThursday", {
      enumerable: true,
      get: function get() {
        return _index139.default;
      }
    });
    Object.defineProperty(exports2, "isToday", {
      enumerable: true,
      get: function get() {
        return _index140.default;
      }
    });
    Object.defineProperty(exports2, "isTomorrow", {
      enumerable: true,
      get: function get() {
        return _index141.default;
      }
    });
    Object.defineProperty(exports2, "isTuesday", {
      enumerable: true,
      get: function get() {
        return _index142.default;
      }
    });
    Object.defineProperty(exports2, "isValid", {
      enumerable: true,
      get: function get() {
        return _index143.default;
      }
    });
    Object.defineProperty(exports2, "isWednesday", {
      enumerable: true,
      get: function get() {
        return _index144.default;
      }
    });
    Object.defineProperty(exports2, "isWeekend", {
      enumerable: true,
      get: function get() {
        return _index145.default;
      }
    });
    Object.defineProperty(exports2, "isWithinInterval", {
      enumerable: true,
      get: function get() {
        return _index146.default;
      }
    });
    Object.defineProperty(exports2, "isYesterday", {
      enumerable: true,
      get: function get() {
        return _index147.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfDecade", {
      enumerable: true,
      get: function get() {
        return _index148.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfISOWeek", {
      enumerable: true,
      get: function get() {
        return _index149.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfISOWeekYear", {
      enumerable: true,
      get: function get() {
        return _index150.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfMonth", {
      enumerable: true,
      get: function get() {
        return _index151.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfQuarter", {
      enumerable: true,
      get: function get() {
        return _index152.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfWeek", {
      enumerable: true,
      get: function get() {
        return _index153.default;
      }
    });
    Object.defineProperty(exports2, "lastDayOfYear", {
      enumerable: true,
      get: function get() {
        return _index154.default;
      }
    });
    Object.defineProperty(exports2, "lightFormat", {
      enumerable: true,
      get: function get() {
        return _index155.default;
      }
    });
    Object.defineProperty(exports2, "max", {
      enumerable: true,
      get: function get() {
        return _index156.default;
      }
    });
    Object.defineProperty(exports2, "milliseconds", {
      enumerable: true,
      get: function get() {
        return _index157.default;
      }
    });
    Object.defineProperty(exports2, "millisecondsToHours", {
      enumerable: true,
      get: function get() {
        return _index158.default;
      }
    });
    Object.defineProperty(exports2, "millisecondsToMinutes", {
      enumerable: true,
      get: function get() {
        return _index159.default;
      }
    });
    Object.defineProperty(exports2, "millisecondsToSeconds", {
      enumerable: true,
      get: function get() {
        return _index160.default;
      }
    });
    Object.defineProperty(exports2, "min", {
      enumerable: true,
      get: function get() {
        return _index161.default;
      }
    });
    Object.defineProperty(exports2, "minutesToHours", {
      enumerable: true,
      get: function get() {
        return _index162.default;
      }
    });
    Object.defineProperty(exports2, "minutesToMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index163.default;
      }
    });
    Object.defineProperty(exports2, "minutesToSeconds", {
      enumerable: true,
      get: function get() {
        return _index164.default;
      }
    });
    Object.defineProperty(exports2, "monthsToQuarters", {
      enumerable: true,
      get: function get() {
        return _index165.default;
      }
    });
    Object.defineProperty(exports2, "monthsToYears", {
      enumerable: true,
      get: function get() {
        return _index166.default;
      }
    });
    Object.defineProperty(exports2, "nextDay", {
      enumerable: true,
      get: function get() {
        return _index167.default;
      }
    });
    Object.defineProperty(exports2, "nextFriday", {
      enumerable: true,
      get: function get() {
        return _index168.default;
      }
    });
    Object.defineProperty(exports2, "nextMonday", {
      enumerable: true,
      get: function get() {
        return _index169.default;
      }
    });
    Object.defineProperty(exports2, "nextSaturday", {
      enumerable: true,
      get: function get() {
        return _index170.default;
      }
    });
    Object.defineProperty(exports2, "nextSunday", {
      enumerable: true,
      get: function get() {
        return _index171.default;
      }
    });
    Object.defineProperty(exports2, "nextThursday", {
      enumerable: true,
      get: function get() {
        return _index172.default;
      }
    });
    Object.defineProperty(exports2, "nextTuesday", {
      enumerable: true,
      get: function get() {
        return _index173.default;
      }
    });
    Object.defineProperty(exports2, "nextWednesday", {
      enumerable: true,
      get: function get() {
        return _index174.default;
      }
    });
    Object.defineProperty(exports2, "parse", {
      enumerable: true,
      get: function get() {
        return _index175.default;
      }
    });
    Object.defineProperty(exports2, "parseISO", {
      enumerable: true,
      get: function get() {
        return _index176.default;
      }
    });
    Object.defineProperty(exports2, "parseJSON", {
      enumerable: true,
      get: function get() {
        return _index177.default;
      }
    });
    Object.defineProperty(exports2, "previousDay", {
      enumerable: true,
      get: function get() {
        return _index178.default;
      }
    });
    Object.defineProperty(exports2, "previousFriday", {
      enumerable: true,
      get: function get() {
        return _index179.default;
      }
    });
    Object.defineProperty(exports2, "previousMonday", {
      enumerable: true,
      get: function get() {
        return _index180.default;
      }
    });
    Object.defineProperty(exports2, "previousSaturday", {
      enumerable: true,
      get: function get() {
        return _index181.default;
      }
    });
    Object.defineProperty(exports2, "previousSunday", {
      enumerable: true,
      get: function get() {
        return _index182.default;
      }
    });
    Object.defineProperty(exports2, "previousThursday", {
      enumerable: true,
      get: function get() {
        return _index183.default;
      }
    });
    Object.defineProperty(exports2, "previousTuesday", {
      enumerable: true,
      get: function get() {
        return _index184.default;
      }
    });
    Object.defineProperty(exports2, "previousWednesday", {
      enumerable: true,
      get: function get() {
        return _index185.default;
      }
    });
    Object.defineProperty(exports2, "quartersToMonths", {
      enumerable: true,
      get: function get() {
        return _index186.default;
      }
    });
    Object.defineProperty(exports2, "quartersToYears", {
      enumerable: true,
      get: function get() {
        return _index187.default;
      }
    });
    Object.defineProperty(exports2, "roundToNearestMinutes", {
      enumerable: true,
      get: function get() {
        return _index188.default;
      }
    });
    Object.defineProperty(exports2, "secondsToHours", {
      enumerable: true,
      get: function get() {
        return _index189.default;
      }
    });
    Object.defineProperty(exports2, "secondsToMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index190.default;
      }
    });
    Object.defineProperty(exports2, "secondsToMinutes", {
      enumerable: true,
      get: function get() {
        return _index191.default;
      }
    });
    Object.defineProperty(exports2, "set", {
      enumerable: true,
      get: function get() {
        return _index192.default;
      }
    });
    Object.defineProperty(exports2, "setDate", {
      enumerable: true,
      get: function get() {
        return _index193.default;
      }
    });
    Object.defineProperty(exports2, "setDay", {
      enumerable: true,
      get: function get() {
        return _index194.default;
      }
    });
    Object.defineProperty(exports2, "setDayOfYear", {
      enumerable: true,
      get: function get() {
        return _index195.default;
      }
    });
    Object.defineProperty(exports2, "setDefaultOptions", {
      enumerable: true,
      get: function get() {
        return _index196.default;
      }
    });
    Object.defineProperty(exports2, "setHours", {
      enumerable: true,
      get: function get() {
        return _index197.default;
      }
    });
    Object.defineProperty(exports2, "setISODay", {
      enumerable: true,
      get: function get() {
        return _index198.default;
      }
    });
    Object.defineProperty(exports2, "setISOWeek", {
      enumerable: true,
      get: function get() {
        return _index199.default;
      }
    });
    Object.defineProperty(exports2, "setISOWeekYear", {
      enumerable: true,
      get: function get() {
        return _index200.default;
      }
    });
    Object.defineProperty(exports2, "setMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index201.default;
      }
    });
    Object.defineProperty(exports2, "setMinutes", {
      enumerable: true,
      get: function get() {
        return _index202.default;
      }
    });
    Object.defineProperty(exports2, "setMonth", {
      enumerable: true,
      get: function get() {
        return _index203.default;
      }
    });
    Object.defineProperty(exports2, "setQuarter", {
      enumerable: true,
      get: function get() {
        return _index204.default;
      }
    });
    Object.defineProperty(exports2, "setSeconds", {
      enumerable: true,
      get: function get() {
        return _index205.default;
      }
    });
    Object.defineProperty(exports2, "setWeek", {
      enumerable: true,
      get: function get() {
        return _index206.default;
      }
    });
    Object.defineProperty(exports2, "setWeekYear", {
      enumerable: true,
      get: function get() {
        return _index207.default;
      }
    });
    Object.defineProperty(exports2, "setYear", {
      enumerable: true,
      get: function get() {
        return _index208.default;
      }
    });
    Object.defineProperty(exports2, "startOfDay", {
      enumerable: true,
      get: function get() {
        return _index209.default;
      }
    });
    Object.defineProperty(exports2, "startOfDecade", {
      enumerable: true,
      get: function get() {
        return _index210.default;
      }
    });
    Object.defineProperty(exports2, "startOfHour", {
      enumerable: true,
      get: function get() {
        return _index211.default;
      }
    });
    Object.defineProperty(exports2, "startOfISOWeek", {
      enumerable: true,
      get: function get() {
        return _index212.default;
      }
    });
    Object.defineProperty(exports2, "startOfISOWeekYear", {
      enumerable: true,
      get: function get() {
        return _index213.default;
      }
    });
    Object.defineProperty(exports2, "startOfMinute", {
      enumerable: true,
      get: function get() {
        return _index214.default;
      }
    });
    Object.defineProperty(exports2, "startOfMonth", {
      enumerable: true,
      get: function get() {
        return _index215.default;
      }
    });
    Object.defineProperty(exports2, "startOfQuarter", {
      enumerable: true,
      get: function get() {
        return _index216.default;
      }
    });
    Object.defineProperty(exports2, "startOfSecond", {
      enumerable: true,
      get: function get() {
        return _index217.default;
      }
    });
    Object.defineProperty(exports2, "startOfToday", {
      enumerable: true,
      get: function get() {
        return _index218.default;
      }
    });
    Object.defineProperty(exports2, "startOfTomorrow", {
      enumerable: true,
      get: function get() {
        return _index219.default;
      }
    });
    Object.defineProperty(exports2, "startOfWeek", {
      enumerable: true,
      get: function get() {
        return _index220.default;
      }
    });
    Object.defineProperty(exports2, "startOfWeekYear", {
      enumerable: true,
      get: function get() {
        return _index221.default;
      }
    });
    Object.defineProperty(exports2, "startOfYear", {
      enumerable: true,
      get: function get() {
        return _index222.default;
      }
    });
    Object.defineProperty(exports2, "startOfYesterday", {
      enumerable: true,
      get: function get() {
        return _index223.default;
      }
    });
    Object.defineProperty(exports2, "sub", {
      enumerable: true,
      get: function get() {
        return _index224.default;
      }
    });
    Object.defineProperty(exports2, "subBusinessDays", {
      enumerable: true,
      get: function get() {
        return _index225.default;
      }
    });
    Object.defineProperty(exports2, "subDays", {
      enumerable: true,
      get: function get() {
        return _index226.default;
      }
    });
    Object.defineProperty(exports2, "subHours", {
      enumerable: true,
      get: function get() {
        return _index227.default;
      }
    });
    Object.defineProperty(exports2, "subISOWeekYears", {
      enumerable: true,
      get: function get() {
        return _index228.default;
      }
    });
    Object.defineProperty(exports2, "subMilliseconds", {
      enumerable: true,
      get: function get() {
        return _index229.default;
      }
    });
    Object.defineProperty(exports2, "subMinutes", {
      enumerable: true,
      get: function get() {
        return _index230.default;
      }
    });
    Object.defineProperty(exports2, "subMonths", {
      enumerable: true,
      get: function get() {
        return _index231.default;
      }
    });
    Object.defineProperty(exports2, "subQuarters", {
      enumerable: true,
      get: function get() {
        return _index232.default;
      }
    });
    Object.defineProperty(exports2, "subSeconds", {
      enumerable: true,
      get: function get() {
        return _index233.default;
      }
    });
    Object.defineProperty(exports2, "subWeeks", {
      enumerable: true,
      get: function get() {
        return _index234.default;
      }
    });
    Object.defineProperty(exports2, "subYears", {
      enumerable: true,
      get: function get() {
        return _index235.default;
      }
    });
    Object.defineProperty(exports2, "toDate", {
      enumerable: true,
      get: function get() {
        return _index236.default;
      }
    });
    Object.defineProperty(exports2, "weeksToDays", {
      enumerable: true,
      get: function get() {
        return _index237.default;
      }
    });
    Object.defineProperty(exports2, "yearsToMonths", {
      enumerable: true,
      get: function get() {
        return _index238.default;
      }
    });
    Object.defineProperty(exports2, "yearsToQuarters", {
      enumerable: true,
      get: function get() {
        return _index239.default;
      }
    });
    var _index = _interopRequireDefault(require_add());
    var _index2 = _interopRequireDefault(require_addBusinessDays());
    var _index3 = _interopRequireDefault(require_addDays());
    var _index4 = _interopRequireDefault(require_addHours());
    var _index5 = _interopRequireDefault(require_addISOWeekYears());
    var _index6 = _interopRequireDefault(require_addMilliseconds());
    var _index7 = _interopRequireDefault(require_addMinutes());
    var _index8 = _interopRequireDefault(require_addMonths());
    var _index9 = _interopRequireDefault(require_addQuarters());
    var _index10 = _interopRequireDefault(require_addSeconds());
    var _index11 = _interopRequireDefault(require_addWeeks());
    var _index12 = _interopRequireDefault(require_addYears());
    var _index13 = _interopRequireDefault(require_areIntervalsOverlapping());
    var _index14 = _interopRequireDefault(require_clamp());
    var _index15 = _interopRequireDefault(require_closestIndexTo());
    var _index16 = _interopRequireDefault(require_closestTo());
    var _index17 = _interopRequireDefault(require_compareAsc());
    var _index18 = _interopRequireDefault(require_compareDesc());
    var _index19 = _interopRequireDefault(require_daysToWeeks());
    var _index20 = _interopRequireDefault(require_differenceInBusinessDays());
    var _index21 = _interopRequireDefault(require_differenceInCalendarDays());
    var _index22 = _interopRequireDefault(require_differenceInCalendarISOWeekYears());
    var _index23 = _interopRequireDefault(require_differenceInCalendarISOWeeks());
    var _index24 = _interopRequireDefault(require_differenceInCalendarMonths());
    var _index25 = _interopRequireDefault(require_differenceInCalendarQuarters());
    var _index26 = _interopRequireDefault(require_differenceInCalendarWeeks());
    var _index27 = _interopRequireDefault(require_differenceInCalendarYears());
    var _index28 = _interopRequireDefault(require_differenceInDays());
    var _index29 = _interopRequireDefault(require_differenceInHours());
    var _index30 = _interopRequireDefault(require_differenceInISOWeekYears());
    var _index31 = _interopRequireDefault(require_differenceInMilliseconds());
    var _index32 = _interopRequireDefault(require_differenceInMinutes());
    var _index33 = _interopRequireDefault(require_differenceInMonths());
    var _index34 = _interopRequireDefault(require_differenceInQuarters());
    var _index35 = _interopRequireDefault(require_differenceInSeconds());
    var _index36 = _interopRequireDefault(require_differenceInWeeks());
    var _index37 = _interopRequireDefault(require_differenceInYears());
    var _index38 = _interopRequireDefault(require_eachDayOfInterval());
    var _index39 = _interopRequireDefault(require_eachHourOfInterval());
    var _index40 = _interopRequireDefault(require_eachMinuteOfInterval());
    var _index41 = _interopRequireDefault(require_eachMonthOfInterval());
    var _index42 = _interopRequireDefault(require_eachQuarterOfInterval());
    var _index43 = _interopRequireDefault(require_eachWeekOfInterval());
    var _index44 = _interopRequireDefault(require_eachWeekendOfInterval());
    var _index45 = _interopRequireDefault(require_eachWeekendOfMonth());
    var _index46 = _interopRequireDefault(require_eachWeekendOfYear());
    var _index47 = _interopRequireDefault(require_eachYearOfInterval());
    var _index48 = _interopRequireDefault(require_endOfDay());
    var _index49 = _interopRequireDefault(require_endOfDecade());
    var _index50 = _interopRequireDefault(require_endOfHour());
    var _index51 = _interopRequireDefault(require_endOfISOWeek());
    var _index52 = _interopRequireDefault(require_endOfISOWeekYear());
    var _index53 = _interopRequireDefault(require_endOfMinute());
    var _index54 = _interopRequireDefault(require_endOfMonth());
    var _index55 = _interopRequireDefault(require_endOfQuarter());
    var _index56 = _interopRequireDefault(require_endOfSecond());
    var _index57 = _interopRequireDefault(require_endOfToday());
    var _index58 = _interopRequireDefault(require_endOfTomorrow());
    var _index59 = _interopRequireDefault(require_endOfWeek());
    var _index60 = _interopRequireDefault(require_endOfYear());
    var _index61 = _interopRequireDefault(require_endOfYesterday());
    var _index62 = _interopRequireDefault(require_format());
    var _index63 = _interopRequireDefault(require_formatDistance2());
    var _index64 = _interopRequireDefault(require_formatDistanceStrict());
    var _index65 = _interopRequireDefault(require_formatDistanceToNow());
    var _index66 = _interopRequireDefault(require_formatDistanceToNowStrict());
    var _index67 = _interopRequireDefault(require_formatDuration());
    var _index68 = _interopRequireDefault(require_formatISO());
    var _index69 = _interopRequireDefault(require_formatISO9075());
    var _index70 = _interopRequireDefault(require_formatISODuration());
    var _index71 = _interopRequireDefault(require_formatRFC3339());
    var _index72 = _interopRequireDefault(require_formatRFC7231());
    var _index73 = _interopRequireDefault(require_formatRelative2());
    var _index74 = _interopRequireDefault(require_fromUnixTime());
    var _index75 = _interopRequireDefault(require_getDate());
    var _index76 = _interopRequireDefault(require_getDay());
    var _index77 = _interopRequireDefault(require_getDayOfYear());
    var _index78 = _interopRequireDefault(require_getDaysInMonth());
    var _index79 = _interopRequireDefault(require_getDaysInYear());
    var _index80 = _interopRequireDefault(require_getDecade());
    var _index81 = _interopRequireDefault(require_getDefaultOptions());
    var _index82 = _interopRequireDefault(require_getHours());
    var _index83 = _interopRequireDefault(require_getISODay());
    var _index84 = _interopRequireDefault(require_getISOWeek());
    var _index85 = _interopRequireDefault(require_getISOWeekYear());
    var _index86 = _interopRequireDefault(require_getISOWeeksInYear());
    var _index87 = _interopRequireDefault(require_getMilliseconds());
    var _index88 = _interopRequireDefault(require_getMinutes());
    var _index89 = _interopRequireDefault(require_getMonth());
    var _index90 = _interopRequireDefault(require_getOverlappingDaysInIntervals());
    var _index91 = _interopRequireDefault(require_getQuarter());
    var _index92 = _interopRequireDefault(require_getSeconds());
    var _index93 = _interopRequireDefault(require_getTime());
    var _index94 = _interopRequireDefault(require_getUnixTime());
    var _index95 = _interopRequireDefault(require_getWeek());
    var _index96 = _interopRequireDefault(require_getWeekOfMonth());
    var _index97 = _interopRequireDefault(require_getWeekYear());
    var _index98 = _interopRequireDefault(require_getWeeksInMonth());
    var _index99 = _interopRequireDefault(require_getYear());
    var _index100 = _interopRequireDefault(require_hoursToMilliseconds());
    var _index101 = _interopRequireDefault(require_hoursToMinutes());
    var _index102 = _interopRequireDefault(require_hoursToSeconds());
    var _index103 = _interopRequireDefault(require_intervalToDuration());
    var _index104 = _interopRequireDefault(require_intlFormat());
    var _index105 = _interopRequireDefault(require_intlFormatDistance());
    var _index106 = _interopRequireDefault(require_isAfter());
    var _index107 = _interopRequireDefault(require_isBefore());
    var _index108 = _interopRequireDefault(require_isDate());
    var _index109 = _interopRequireDefault(require_isEqual());
    var _index110 = _interopRequireDefault(require_isExists());
    var _index111 = _interopRequireDefault(require_isFirstDayOfMonth());
    var _index112 = _interopRequireDefault(require_isFriday());
    var _index113 = _interopRequireDefault(require_isFuture());
    var _index114 = _interopRequireDefault(require_isLastDayOfMonth());
    var _index115 = _interopRequireDefault(require_isLeapYear());
    var _index116 = _interopRequireDefault(require_isMatch());
    var _index117 = _interopRequireDefault(require_isMonday());
    var _index118 = _interopRequireDefault(require_isPast());
    var _index119 = _interopRequireDefault(require_isSameDay());
    var _index120 = _interopRequireDefault(require_isSameHour());
    var _index121 = _interopRequireDefault(require_isSameISOWeek());
    var _index122 = _interopRequireDefault(require_isSameISOWeekYear());
    var _index123 = _interopRequireDefault(require_isSameMinute());
    var _index124 = _interopRequireDefault(require_isSameMonth());
    var _index125 = _interopRequireDefault(require_isSameQuarter());
    var _index126 = _interopRequireDefault(require_isSameSecond());
    var _index127 = _interopRequireDefault(require_isSameWeek());
    var _index128 = _interopRequireDefault(require_isSameYear());
    var _index129 = _interopRequireDefault(require_isSaturday());
    var _index130 = _interopRequireDefault(require_isSunday());
    var _index131 = _interopRequireDefault(require_isThisHour());
    var _index132 = _interopRequireDefault(require_isThisISOWeek());
    var _index133 = _interopRequireDefault(require_isThisMinute());
    var _index134 = _interopRequireDefault(require_isThisMonth());
    var _index135 = _interopRequireDefault(require_isThisQuarter());
    var _index136 = _interopRequireDefault(require_isThisSecond());
    var _index137 = _interopRequireDefault(require_isThisWeek());
    var _index138 = _interopRequireDefault(require_isThisYear());
    var _index139 = _interopRequireDefault(require_isThursday());
    var _index140 = _interopRequireDefault(require_isToday());
    var _index141 = _interopRequireDefault(require_isTomorrow());
    var _index142 = _interopRequireDefault(require_isTuesday());
    var _index143 = _interopRequireDefault(require_isValid());
    var _index144 = _interopRequireDefault(require_isWednesday());
    var _index145 = _interopRequireDefault(require_isWeekend());
    var _index146 = _interopRequireDefault(require_isWithinInterval());
    var _index147 = _interopRequireDefault(require_isYesterday());
    var _index148 = _interopRequireDefault(require_lastDayOfDecade());
    var _index149 = _interopRequireDefault(require_lastDayOfISOWeek());
    var _index150 = _interopRequireDefault(require_lastDayOfISOWeekYear());
    var _index151 = _interopRequireDefault(require_lastDayOfMonth());
    var _index152 = _interopRequireDefault(require_lastDayOfQuarter());
    var _index153 = _interopRequireDefault(require_lastDayOfWeek());
    var _index154 = _interopRequireDefault(require_lastDayOfYear());
    var _index155 = _interopRequireDefault(require_lightFormat());
    var _index156 = _interopRequireDefault(require_max());
    var _index157 = _interopRequireDefault(require_milliseconds());
    var _index158 = _interopRequireDefault(require_millisecondsToHours());
    var _index159 = _interopRequireDefault(require_millisecondsToMinutes());
    var _index160 = _interopRequireDefault(require_millisecondsToSeconds());
    var _index161 = _interopRequireDefault(require_min());
    var _index162 = _interopRequireDefault(require_minutesToHours());
    var _index163 = _interopRequireDefault(require_minutesToMilliseconds());
    var _index164 = _interopRequireDefault(require_minutesToSeconds());
    var _index165 = _interopRequireDefault(require_monthsToQuarters());
    var _index166 = _interopRequireDefault(require_monthsToYears());
    var _index167 = _interopRequireDefault(require_nextDay());
    var _index168 = _interopRequireDefault(require_nextFriday());
    var _index169 = _interopRequireDefault(require_nextMonday());
    var _index170 = _interopRequireDefault(require_nextSaturday());
    var _index171 = _interopRequireDefault(require_nextSunday());
    var _index172 = _interopRequireDefault(require_nextThursday());
    var _index173 = _interopRequireDefault(require_nextTuesday());
    var _index174 = _interopRequireDefault(require_nextWednesday());
    var _index175 = _interopRequireDefault(require_parse());
    var _index176 = _interopRequireDefault(require_parseISO());
    var _index177 = _interopRequireDefault(require_parseJSON());
    var _index178 = _interopRequireDefault(require_previousDay());
    var _index179 = _interopRequireDefault(require_previousFriday());
    var _index180 = _interopRequireDefault(require_previousMonday());
    var _index181 = _interopRequireDefault(require_previousSaturday());
    var _index182 = _interopRequireDefault(require_previousSunday());
    var _index183 = _interopRequireDefault(require_previousThursday());
    var _index184 = _interopRequireDefault(require_previousTuesday());
    var _index185 = _interopRequireDefault(require_previousWednesday());
    var _index186 = _interopRequireDefault(require_quartersToMonths());
    var _index187 = _interopRequireDefault(require_quartersToYears());
    var _index188 = _interopRequireDefault(require_roundToNearestMinutes());
    var _index189 = _interopRequireDefault(require_secondsToHours());
    var _index190 = _interopRequireDefault(require_secondsToMilliseconds());
    var _index191 = _interopRequireDefault(require_secondsToMinutes());
    var _index192 = _interopRequireDefault(require_set());
    var _index193 = _interopRequireDefault(require_setDate());
    var _index194 = _interopRequireDefault(require_setDay());
    var _index195 = _interopRequireDefault(require_setDayOfYear());
    var _index196 = _interopRequireDefault(require_setDefaultOptions());
    var _index197 = _interopRequireDefault(require_setHours());
    var _index198 = _interopRequireDefault(require_setISODay());
    var _index199 = _interopRequireDefault(require_setISOWeek());
    var _index200 = _interopRequireDefault(require_setISOWeekYear());
    var _index201 = _interopRequireDefault(require_setMilliseconds());
    var _index202 = _interopRequireDefault(require_setMinutes());
    var _index203 = _interopRequireDefault(require_setMonth());
    var _index204 = _interopRequireDefault(require_setQuarter());
    var _index205 = _interopRequireDefault(require_setSeconds());
    var _index206 = _interopRequireDefault(require_setWeek());
    var _index207 = _interopRequireDefault(require_setWeekYear());
    var _index208 = _interopRequireDefault(require_setYear());
    var _index209 = _interopRequireDefault(require_startOfDay());
    var _index210 = _interopRequireDefault(require_startOfDecade());
    var _index211 = _interopRequireDefault(require_startOfHour());
    var _index212 = _interopRequireDefault(require_startOfISOWeek());
    var _index213 = _interopRequireDefault(require_startOfISOWeekYear());
    var _index214 = _interopRequireDefault(require_startOfMinute());
    var _index215 = _interopRequireDefault(require_startOfMonth());
    var _index216 = _interopRequireDefault(require_startOfQuarter());
    var _index217 = _interopRequireDefault(require_startOfSecond());
    var _index218 = _interopRequireDefault(require_startOfToday());
    var _index219 = _interopRequireDefault(require_startOfTomorrow());
    var _index220 = _interopRequireDefault(require_startOfWeek());
    var _index221 = _interopRequireDefault(require_startOfWeekYear());
    var _index222 = _interopRequireDefault(require_startOfYear());
    var _index223 = _interopRequireDefault(require_startOfYesterday());
    var _index224 = _interopRequireDefault(require_sub());
    var _index225 = _interopRequireDefault(require_subBusinessDays());
    var _index226 = _interopRequireDefault(require_subDays());
    var _index227 = _interopRequireDefault(require_subHours());
    var _index228 = _interopRequireDefault(require_subISOWeekYears());
    var _index229 = _interopRequireDefault(require_subMilliseconds());
    var _index230 = _interopRequireDefault(require_subMinutes());
    var _index231 = _interopRequireDefault(require_subMonths());
    var _index232 = _interopRequireDefault(require_subQuarters());
    var _index233 = _interopRequireDefault(require_subSeconds());
    var _index234 = _interopRequireDefault(require_subWeeks());
    var _index235 = _interopRequireDefault(require_subYears());
    var _index236 = _interopRequireDefault(require_toDate());
    var _index237 = _interopRequireDefault(require_weeksToDays());
    var _index238 = _interopRequireDefault(require_yearsToMonths());
    var _index239 = _interopRequireDefault(require_yearsToQuarters());
    var _index240 = require_constants();
    Object.keys(_index240).forEach(function(key) {
      if (key === "default" || key === "__esModule") return;
      if (Object.prototype.hasOwnProperty.call(_exportNames, key)) return;
      if (key in exports2 && exports2[key] === _index240[key]) return;
      Object.defineProperty(exports2, key, {
        enumerable: true,
        get: function get() {
          return _index240[key];
        }
      });
    });
  }
});

// index.js
import process from "node:process";
import { Buffer as Buffer2 } from "node:buffer";

// node_modules/fast-xml-parser/src/util.js
var nameStartChar = ":A-Za-z_\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD";
var nameChar = nameStartChar + "\\-.\\d\\u00B7\\u0300-\\u036F\\u203F-\\u2040";
var nameRegexp = "[" + nameStartChar + "][" + nameChar + "]*";
var regexName = new RegExp("^" + nameRegexp + "$");
function getAllMatches(string, regex) {
  const matches = [];
  let match = regex.exec(string);
  while (match) {
    const allmatches = [];
    allmatches.startIndex = regex.lastIndex - match[0].length;
    const len = match.length;
    for (let index = 0; index < len; index++) {
      allmatches.push(match[index]);
    }
    matches.push(allmatches);
    match = regex.exec(string);
  }
  return matches;
}
var isName = function(string) {
  const match = regexName.exec(string);
  return !(match === null || typeof match === "undefined");
};
function isExist(v) {
  return typeof v !== "undefined";
}

// node_modules/fast-xml-parser/src/validator.js
var defaultOptions = {
  allowBooleanAttributes: false,
  //A tag can have attributes without any value
  unpairedTags: []
};
function validate(xmlData, options) {
  options = Object.assign({}, defaultOptions, options);
  const tags = [];
  let tagFound = false;
  let reachedRoot = false;
  if (xmlData[0] === "\uFEFF") {
    xmlData = xmlData.substr(1);
  }
  for (let i = 0; i < xmlData.length; i++) {
    if (xmlData[i] === "<" && xmlData[i + 1] === "?") {
      i += 2;
      i = readPI(xmlData, i);
      if (i.err) return i;
    } else if (xmlData[i] === "<") {
      let tagStartPos = i;
      i++;
      if (xmlData[i] === "!") {
        i = readCommentAndCDATA(xmlData, i);
        continue;
      } else {
        let closingTag = false;
        if (xmlData[i] === "/") {
          closingTag = true;
          i++;
        }
        let tagName = "";
        for (; i < xmlData.length && xmlData[i] !== ">" && xmlData[i] !== " " && xmlData[i] !== "	" && xmlData[i] !== "\n" && xmlData[i] !== "\r"; i++) {
          tagName += xmlData[i];
        }
        tagName = tagName.trim();
        if (tagName[tagName.length - 1] === "/") {
          tagName = tagName.substring(0, tagName.length - 1);
          i--;
        }
        if (!validateTagName(tagName)) {
          let msg;
          if (tagName.trim().length === 0) {
            msg = "Invalid space after '<'.";
          } else {
            msg = "Tag '" + tagName + "' is an invalid name.";
          }
          return getErrorObject("InvalidTag", msg, getLineNumberForPosition(xmlData, i));
        }
        const result = readAttributeStr(xmlData, i);
        if (result === false) {
          return getErrorObject("InvalidAttr", "Attributes for '" + tagName + "' have open quote.", getLineNumberForPosition(xmlData, i));
        }
        let attrStr = result.value;
        i = result.index;
        if (attrStr[attrStr.length - 1] === "/") {
          const attrStrStart = i - attrStr.length;
          attrStr = attrStr.substring(0, attrStr.length - 1);
          const isValid = validateAttributeString(attrStr, options);
          if (isValid === true) {
            tagFound = true;
          } else {
            return getErrorObject(isValid.err.code, isValid.err.msg, getLineNumberForPosition(xmlData, attrStrStart + isValid.err.line));
          }
        } else if (closingTag) {
          if (!result.tagClosed) {
            return getErrorObject("InvalidTag", "Closing tag '" + tagName + "' doesn't have proper closing.", getLineNumberForPosition(xmlData, i));
          } else if (attrStr.trim().length > 0) {
            return getErrorObject("InvalidTag", "Closing tag '" + tagName + "' can't have attributes or invalid starting.", getLineNumberForPosition(xmlData, tagStartPos));
          } else if (tags.length === 0) {
            return getErrorObject("InvalidTag", "Closing tag '" + tagName + "' has not been opened.", getLineNumberForPosition(xmlData, tagStartPos));
          } else {
            const otg = tags.pop();
            if (tagName !== otg.tagName) {
              let openPos = getLineNumberForPosition(xmlData, otg.tagStartPos);
              return getErrorObject(
                "InvalidTag",
                "Expected closing tag '" + otg.tagName + "' (opened in line " + openPos.line + ", col " + openPos.col + ") instead of closing tag '" + tagName + "'.",
                getLineNumberForPosition(xmlData, tagStartPos)
              );
            }
            if (tags.length == 0) {
              reachedRoot = true;
            }
          }
        } else {
          const isValid = validateAttributeString(attrStr, options);
          if (isValid !== true) {
            return getErrorObject(isValid.err.code, isValid.err.msg, getLineNumberForPosition(xmlData, i - attrStr.length + isValid.err.line));
          }
          if (reachedRoot === true) {
            return getErrorObject("InvalidXml", "Multiple possible root nodes found.", getLineNumberForPosition(xmlData, i));
          } else if (options.unpairedTags.indexOf(tagName) !== -1) {
          } else {
            tags.push({ tagName, tagStartPos });
          }
          tagFound = true;
        }
        for (i++; i < xmlData.length; i++) {
          if (xmlData[i] === "<") {
            if (xmlData[i + 1] === "!") {
              i++;
              i = readCommentAndCDATA(xmlData, i);
              continue;
            } else if (xmlData[i + 1] === "?") {
              i = readPI(xmlData, ++i);
              if (i.err) return i;
            } else {
              break;
            }
          } else if (xmlData[i] === "&") {
            const afterAmp = validateAmpersand(xmlData, i);
            if (afterAmp == -1)
              return getErrorObject("InvalidChar", "char '&' is not expected.", getLineNumberForPosition(xmlData, i));
            i = afterAmp;
          } else {
            if (reachedRoot === true && !isWhiteSpace(xmlData[i])) {
              return getErrorObject("InvalidXml", "Extra text at the end", getLineNumberForPosition(xmlData, i));
            }
          }
        }
        if (xmlData[i] === "<") {
          i--;
        }
      }
    } else {
      if (isWhiteSpace(xmlData[i])) {
        continue;
      }
      return getErrorObject("InvalidChar", "char '" + xmlData[i] + "' is not expected.", getLineNumberForPosition(xmlData, i));
    }
  }
  if (!tagFound) {
    return getErrorObject("InvalidXml", "Start tag expected.", 1);
  } else if (tags.length == 1) {
    return getErrorObject("InvalidTag", "Unclosed tag '" + tags[0].tagName + "'.", getLineNumberForPosition(xmlData, tags[0].tagStartPos));
  } else if (tags.length > 0) {
    return getErrorObject("InvalidXml", "Invalid '" + JSON.stringify(tags.map((t) => t.tagName), null, 4).replace(/\r?\n/g, "") + "' found.", { line: 1, col: 1 });
  }
  return true;
}
function isWhiteSpace(char) {
  return char === " " || char === "	" || char === "\n" || char === "\r";
}
function readPI(xmlData, i) {
  const start = i;
  for (; i < xmlData.length; i++) {
    if (xmlData[i] == "?" || xmlData[i] == " ") {
      const tagname = xmlData.substr(start, i - start);
      if (i > 5 && tagname === "xml") {
        return getErrorObject("InvalidXml", "XML declaration allowed only at the start of the document.", getLineNumberForPosition(xmlData, i));
      } else if (xmlData[i] == "?" && xmlData[i + 1] == ">") {
        i++;
        break;
      } else {
        continue;
      }
    }
  }
  return i;
}
function readCommentAndCDATA(xmlData, i) {
  if (xmlData.length > i + 5 && xmlData[i + 1] === "-" && xmlData[i + 2] === "-") {
    for (i += 3; i < xmlData.length; i++) {
      if (xmlData[i] === "-" && xmlData[i + 1] === "-" && xmlData[i + 2] === ">") {
        i += 2;
        break;
      }
    }
  } else if (xmlData.length > i + 8 && xmlData[i + 1] === "D" && xmlData[i + 2] === "O" && xmlData[i + 3] === "C" && xmlData[i + 4] === "T" && xmlData[i + 5] === "Y" && xmlData[i + 6] === "P" && xmlData[i + 7] === "E") {
    let angleBracketsCount = 1;
    for (i += 8; i < xmlData.length; i++) {
      if (xmlData[i] === "<") {
        angleBracketsCount++;
      } else if (xmlData[i] === ">") {
        angleBracketsCount--;
        if (angleBracketsCount === 0) {
          break;
        }
      }
    }
  } else if (xmlData.length > i + 9 && xmlData[i + 1] === "[" && xmlData[i + 2] === "C" && xmlData[i + 3] === "D" && xmlData[i + 4] === "A" && xmlData[i + 5] === "T" && xmlData[i + 6] === "A" && xmlData[i + 7] === "[") {
    for (i += 8; i < xmlData.length; i++) {
      if (xmlData[i] === "]" && xmlData[i + 1] === "]" && xmlData[i + 2] === ">") {
        i += 2;
        break;
      }
    }
  }
  return i;
}
var doubleQuote = '"';
var singleQuote = "'";
function readAttributeStr(xmlData, i) {
  let attrStr = "";
  let startChar = "";
  let tagClosed = false;
  for (; i < xmlData.length; i++) {
    if (xmlData[i] === doubleQuote || xmlData[i] === singleQuote) {
      if (startChar === "") {
        startChar = xmlData[i];
      } else if (startChar !== xmlData[i]) {
      } else {
        startChar = "";
      }
    } else if (xmlData[i] === ">") {
      if (startChar === "") {
        tagClosed = true;
        break;
      }
    }
    attrStr += xmlData[i];
  }
  if (startChar !== "") {
    return false;
  }
  return {
    value: attrStr,
    index: i,
    tagClosed
  };
}
var validAttrStrRegxp = new RegExp(`(\\s*)([^\\s=]+)(\\s*=)?(\\s*(['"])(([\\s\\S])*?)\\5)?`, "g");
function validateAttributeString(attrStr, options) {
  const matches = getAllMatches(attrStr, validAttrStrRegxp);
  const attrNames = {};
  for (let i = 0; i < matches.length; i++) {
    if (matches[i][1].length === 0) {
      return getErrorObject("InvalidAttr", "Attribute '" + matches[i][2] + "' has no space in starting.", getPositionFromMatch(matches[i]));
    } else if (matches[i][3] !== void 0 && matches[i][4] === void 0) {
      return getErrorObject("InvalidAttr", "Attribute '" + matches[i][2] + "' is without value.", getPositionFromMatch(matches[i]));
    } else if (matches[i][3] === void 0 && !options.allowBooleanAttributes) {
      return getErrorObject("InvalidAttr", "boolean attribute '" + matches[i][2] + "' is not allowed.", getPositionFromMatch(matches[i]));
    }
    const attrName = matches[i][2];
    if (!validateAttrName(attrName)) {
      return getErrorObject("InvalidAttr", "Attribute '" + attrName + "' is an invalid name.", getPositionFromMatch(matches[i]));
    }
    if (!attrNames.hasOwnProperty(attrName)) {
      attrNames[attrName] = 1;
    } else {
      return getErrorObject("InvalidAttr", "Attribute '" + attrName + "' is repeated.", getPositionFromMatch(matches[i]));
    }
  }
  return true;
}
function validateNumberAmpersand(xmlData, i) {
  let re = /\d/;
  if (xmlData[i] === "x") {
    i++;
    re = /[\da-fA-F]/;
  }
  for (; i < xmlData.length; i++) {
    if (xmlData[i] === ";")
      return i;
    if (!xmlData[i].match(re))
      break;
  }
  return -1;
}
function validateAmpersand(xmlData, i) {
  i++;
  if (xmlData[i] === ";")
    return -1;
  if (xmlData[i] === "#") {
    i++;
    return validateNumberAmpersand(xmlData, i);
  }
  let count = 0;
  for (; i < xmlData.length; i++, count++) {
    if (xmlData[i].match(/\w/) && count < 20)
      continue;
    if (xmlData[i] === ";")
      break;
    return -1;
  }
  return i;
}
function getErrorObject(code, message, lineNumber) {
  return {
    err: {
      code,
      msg: message,
      line: lineNumber.line || lineNumber,
      col: lineNumber.col
    }
  };
}
function validateAttrName(attrName) {
  return isName(attrName);
}
function validateTagName(tagname) {
  return isName(tagname);
}
function getLineNumberForPosition(xmlData, index) {
  const lines = xmlData.substring(0, index).split(/\r?\n/);
  return {
    line: lines.length,
    // column number is last line's length + 1, because column numbering starts at 1:
    col: lines[lines.length - 1].length + 1
  };
}
function getPositionFromMatch(match) {
  return match.startIndex + match[1].length;
}

// node_modules/fast-xml-parser/src/xmlparser/OptionsBuilder.js
var defaultOptions2 = {
  preserveOrder: false,
  attributeNamePrefix: "@_",
  attributesGroupName: false,
  textNodeName: "#text",
  ignoreAttributes: true,
  removeNSPrefix: false,
  // remove NS from tag name or attribute name if true
  allowBooleanAttributes: false,
  //a tag can have attributes without any value
  //ignoreRootElement : false,
  parseTagValue: true,
  parseAttributeValue: false,
  trimValues: true,
  //Trim string values of tag and attributes
  cdataPropName: false,
  numberParseOptions: {
    hex: true,
    leadingZeros: true,
    eNotation: true
  },
  tagValueProcessor: function(tagName, val) {
    return val;
  },
  attributeValueProcessor: function(attrName, val) {
    return val;
  },
  stopNodes: [],
  //nested tags will not be parsed even for errors
  alwaysCreateTextNode: false,
  isArray: () => false,
  commentPropName: false,
  unpairedTags: [],
  processEntities: true,
  htmlEntities: false,
  ignoreDeclaration: false,
  ignorePiTags: false,
  transformTagName: false,
  transformAttributeName: false,
  updateTag: function(tagName, jPath, attrs) {
    return tagName;
  },
  // skipEmptyListItem: false
  captureMetaData: false
};
var buildOptions = function(options) {
  return Object.assign({}, defaultOptions2, options);
};

// node_modules/fast-xml-parser/src/xmlparser/xmlNode.js
var METADATA_SYMBOL;
if (typeof Symbol !== "function") {
  METADATA_SYMBOL = "@@xmlMetadata";
} else {
  METADATA_SYMBOL = /* @__PURE__ */ Symbol("XML Node Metadata");
}
var XmlNode = class {
  constructor(tagname) {
    this.tagname = tagname;
    this.child = [];
    this[":@"] = {};
  }
  add(key, val) {
    if (key === "__proto__") key = "#__proto__";
    this.child.push({ [key]: val });
  }
  addChild(node, startIndex) {
    if (node.tagname === "__proto__") node.tagname = "#__proto__";
    if (node[":@"] && Object.keys(node[":@"]).length > 0) {
      this.child.push({ [node.tagname]: node.child, [":@"]: node[":@"] });
    } else {
      this.child.push({ [node.tagname]: node.child });
    }
    if (startIndex !== void 0) {
      this.child[this.child.length - 1][METADATA_SYMBOL] = { startIndex };
    }
  }
  /** symbol used for metadata */
  static getMetaDataSymbol() {
    return METADATA_SYMBOL;
  }
};

// node_modules/fast-xml-parser/src/xmlparser/DocTypeReader.js
var DocTypeReader = class {
  constructor(processEntities) {
    this.suppressValidationErr = !processEntities;
  }
  readDocType(xmlData, i) {
    const entities = {};
    if (xmlData[i + 3] === "O" && xmlData[i + 4] === "C" && xmlData[i + 5] === "T" && xmlData[i + 6] === "Y" && xmlData[i + 7] === "P" && xmlData[i + 8] === "E") {
      i = i + 9;
      let angleBracketsCount = 1;
      let hasBody = false, comment = false;
      let exp = "";
      for (; i < xmlData.length; i++) {
        if (xmlData[i] === "<" && !comment) {
          if (hasBody && hasSeq(xmlData, "!ENTITY", i)) {
            i += 7;
            let entityName, val;
            [entityName, val, i] = this.readEntityExp(xmlData, i + 1, this.suppressValidationErr);
            if (val.indexOf("&") === -1)
              entities[entityName] = {
                regx: RegExp(`&${entityName};`, "g"),
                val
              };
          } else if (hasBody && hasSeq(xmlData, "!ELEMENT", i)) {
            i += 8;
            const { index } = this.readElementExp(xmlData, i + 1);
            i = index;
          } else if (hasBody && hasSeq(xmlData, "!ATTLIST", i)) {
            i += 8;
          } else if (hasBody && hasSeq(xmlData, "!NOTATION", i)) {
            i += 9;
            const { index } = this.readNotationExp(xmlData, i + 1, this.suppressValidationErr);
            i = index;
          } else if (hasSeq(xmlData, "!--", i)) comment = true;
          else throw new Error(`Invalid DOCTYPE`);
          angleBracketsCount++;
          exp = "";
        } else if (xmlData[i] === ">") {
          if (comment) {
            if (xmlData[i - 1] === "-" && xmlData[i - 2] === "-") {
              comment = false;
              angleBracketsCount--;
            }
          } else {
            angleBracketsCount--;
          }
          if (angleBracketsCount === 0) {
            break;
          }
        } else if (xmlData[i] === "[") {
          hasBody = true;
        } else {
          exp += xmlData[i];
        }
      }
      if (angleBracketsCount !== 0) {
        throw new Error(`Unclosed DOCTYPE`);
      }
    } else {
      throw new Error(`Invalid Tag instead of DOCTYPE`);
    }
    return { entities, i };
  }
  readEntityExp(xmlData, i) {
    i = skipWhitespace(xmlData, i);
    let entityName = "";
    while (i < xmlData.length && !/\s/.test(xmlData[i]) && xmlData[i] !== '"' && xmlData[i] !== "'") {
      entityName += xmlData[i];
      i++;
    }
    validateEntityName(entityName);
    i = skipWhitespace(xmlData, i);
    if (!this.suppressValidationErr) {
      if (xmlData.substring(i, i + 6).toUpperCase() === "SYSTEM") {
        throw new Error("External entities are not supported");
      } else if (xmlData[i] === "%") {
        throw new Error("Parameter entities are not supported");
      }
    }
    let entityValue = "";
    [i, entityValue] = this.readIdentifierVal(xmlData, i, "entity");
    i--;
    return [entityName, entityValue, i];
  }
  readNotationExp(xmlData, i) {
    i = skipWhitespace(xmlData, i);
    let notationName = "";
    while (i < xmlData.length && !/\s/.test(xmlData[i])) {
      notationName += xmlData[i];
      i++;
    }
    !this.suppressValidationErr && validateEntityName(notationName);
    i = skipWhitespace(xmlData, i);
    const identifierType = xmlData.substring(i, i + 6).toUpperCase();
    if (!this.suppressValidationErr && identifierType !== "SYSTEM" && identifierType !== "PUBLIC") {
      throw new Error(`Expected SYSTEM or PUBLIC, found "${identifierType}"`);
    }
    i += identifierType.length;
    i = skipWhitespace(xmlData, i);
    let publicIdentifier = null;
    let systemIdentifier = null;
    if (identifierType === "PUBLIC") {
      [i, publicIdentifier] = this.readIdentifierVal(xmlData, i, "publicIdentifier");
      i = skipWhitespace(xmlData, i);
      if (xmlData[i] === '"' || xmlData[i] === "'") {
        [i, systemIdentifier] = this.readIdentifierVal(xmlData, i, "systemIdentifier");
      }
    } else if (identifierType === "SYSTEM") {
      [i, systemIdentifier] = this.readIdentifierVal(xmlData, i, "systemIdentifier");
      if (!this.suppressValidationErr && !systemIdentifier) {
        throw new Error("Missing mandatory system identifier for SYSTEM notation");
      }
    }
    return { notationName, publicIdentifier, systemIdentifier, index: --i };
  }
  readIdentifierVal(xmlData, i, type) {
    let identifierVal = "";
    const startChar = xmlData[i];
    if (startChar !== '"' && startChar !== "'") {
      throw new Error(`Expected quoted string, found "${startChar}"`);
    }
    i++;
    while (i < xmlData.length && xmlData[i] !== startChar) {
      identifierVal += xmlData[i];
      i++;
    }
    if (xmlData[i] !== startChar) {
      throw new Error(`Unterminated ${type} value`);
    }
    i++;
    return [i, identifierVal];
  }
  readElementExp(xmlData, i) {
    i = skipWhitespace(xmlData, i);
    let elementName = "";
    while (i < xmlData.length && !/\s/.test(xmlData[i])) {
      elementName += xmlData[i];
      i++;
    }
    if (!this.suppressValidationErr && !isName(elementName)) {
      throw new Error(`Invalid element name: "${elementName}"`);
    }
    i = skipWhitespace(xmlData, i);
    let contentModel = "";
    if (xmlData[i] === "E" && hasSeq(xmlData, "MPTY", i)) i += 4;
    else if (xmlData[i] === "A" && hasSeq(xmlData, "NY", i)) i += 2;
    else if (xmlData[i] === "(") {
      i++;
      while (i < xmlData.length && xmlData[i] !== ")") {
        contentModel += xmlData[i];
        i++;
      }
      if (xmlData[i] !== ")") {
        throw new Error("Unterminated content model");
      }
    } else if (!this.suppressValidationErr) {
      throw new Error(`Invalid Element Expression, found "${xmlData[i]}"`);
    }
    return {
      elementName,
      contentModel: contentModel.trim(),
      index: i
    };
  }
  readAttlistExp(xmlData, i) {
    i = skipWhitespace(xmlData, i);
    let elementName = "";
    while (i < xmlData.length && !/\s/.test(xmlData[i])) {
      elementName += xmlData[i];
      i++;
    }
    validateEntityName(elementName);
    i = skipWhitespace(xmlData, i);
    let attributeName = "";
    while (i < xmlData.length && !/\s/.test(xmlData[i])) {
      attributeName += xmlData[i];
      i++;
    }
    if (!validateEntityName(attributeName)) {
      throw new Error(`Invalid attribute name: "${attributeName}"`);
    }
    i = skipWhitespace(xmlData, i);
    let attributeType = "";
    if (xmlData.substring(i, i + 8).toUpperCase() === "NOTATION") {
      attributeType = "NOTATION";
      i += 8;
      i = skipWhitespace(xmlData, i);
      if (xmlData[i] !== "(") {
        throw new Error(`Expected '(', found "${xmlData[i]}"`);
      }
      i++;
      let allowedNotations = [];
      while (i < xmlData.length && xmlData[i] !== ")") {
        let notation = "";
        while (i < xmlData.length && xmlData[i] !== "|" && xmlData[i] !== ")") {
          notation += xmlData[i];
          i++;
        }
        notation = notation.trim();
        if (!validateEntityName(notation)) {
          throw new Error(`Invalid notation name: "${notation}"`);
        }
        allowedNotations.push(notation);
        if (xmlData[i] === "|") {
          i++;
          i = skipWhitespace(xmlData, i);
        }
      }
      if (xmlData[i] !== ")") {
        throw new Error("Unterminated list of notations");
      }
      i++;
      attributeType += " (" + allowedNotations.join("|") + ")";
    } else {
      while (i < xmlData.length && !/\s/.test(xmlData[i])) {
        attributeType += xmlData[i];
        i++;
      }
      const validTypes = ["CDATA", "ID", "IDREF", "IDREFS", "ENTITY", "ENTITIES", "NMTOKEN", "NMTOKENS"];
      if (!this.suppressValidationErr && !validTypes.includes(attributeType.toUpperCase())) {
        throw new Error(`Invalid attribute type: "${attributeType}"`);
      }
    }
    i = skipWhitespace(xmlData, i);
    let defaultValue = "";
    if (xmlData.substring(i, i + 8).toUpperCase() === "#REQUIRED") {
      defaultValue = "#REQUIRED";
      i += 8;
    } else if (xmlData.substring(i, i + 7).toUpperCase() === "#IMPLIED") {
      defaultValue = "#IMPLIED";
      i += 7;
    } else {
      [i, defaultValue] = this.readIdentifierVal(xmlData, i, "ATTLIST");
    }
    return {
      elementName,
      attributeName,
      attributeType,
      defaultValue,
      index: i
    };
  }
};
var skipWhitespace = (data, index) => {
  while (index < data.length && /\s/.test(data[index])) {
    index++;
  }
  return index;
};
function hasSeq(data, seq, i) {
  for (let j = 0; j < seq.length; j++) {
    if (seq[j] !== data[i + j + 1]) return false;
  }
  return true;
}
function validateEntityName(name) {
  if (isName(name))
    return name;
  else
    throw new Error(`Invalid entity name ${name}`);
}

// node_modules/strnum/strnum.js
var hexRegex = /^[-+]?0x[a-fA-F0-9]+$/;
var numRegex = /^([\-\+])?(0*)([0-9]*(\.[0-9]*)?)$/;
var consider = {
  hex: true,
  // oct: false,
  leadingZeros: true,
  decimalPoint: ".",
  eNotation: true
  //skipLike: /regex/
};
function toNumber(str, options = {}) {
  options = Object.assign({}, consider, options);
  if (!str || typeof str !== "string") return str;
  let trimmedStr = str.trim();
  if (options.skipLike !== void 0 && options.skipLike.test(trimmedStr)) return str;
  else if (str === "0") return 0;
  else if (options.hex && hexRegex.test(trimmedStr)) {
    return parse_int(trimmedStr, 16);
  } else if (trimmedStr.includes("e") || trimmedStr.includes("E")) {
    return resolveEnotation(str, trimmedStr, options);
  } else {
    const match = numRegex.exec(trimmedStr);
    if (match) {
      const sign = match[1] || "";
      const leadingZeros = match[2];
      let numTrimmedByZeros = trimZeros(match[3]);
      const decimalAdjacentToLeadingZeros = sign ? (
        // 0., -00., 000.
        str[leadingZeros.length + 1] === "."
      ) : str[leadingZeros.length] === ".";
      if (!options.leadingZeros && (leadingZeros.length > 1 || leadingZeros.length === 1 && !decimalAdjacentToLeadingZeros)) {
        return str;
      } else {
        const num = Number(trimmedStr);
        const parsedStr = String(num);
        if (num === 0) return num;
        if (parsedStr.search(/[eE]/) !== -1) {
          if (options.eNotation) return num;
          else return str;
        } else if (trimmedStr.indexOf(".") !== -1) {
          if (parsedStr === "0") return num;
          else if (parsedStr === numTrimmedByZeros) return num;
          else if (parsedStr === `${sign}${numTrimmedByZeros}`) return num;
          else return str;
        }
        let n = leadingZeros ? numTrimmedByZeros : trimmedStr;
        if (leadingZeros) {
          return n === parsedStr || sign + n === parsedStr ? num : str;
        } else {
          return n === parsedStr || n === sign + parsedStr ? num : str;
        }
      }
    } else {
      return str;
    }
  }
}
var eNotationRegx = /^([-+])?(0*)(\d*(\.\d*)?[eE][-\+]?\d+)$/;
function resolveEnotation(str, trimmedStr, options) {
  if (!options.eNotation) return str;
  const notation = trimmedStr.match(eNotationRegx);
  if (notation) {
    let sign = notation[1] || "";
    const eChar = notation[3].indexOf("e") === -1 ? "E" : "e";
    const leadingZeros = notation[2];
    const eAdjacentToLeadingZeros = sign ? (
      // 0E.
      str[leadingZeros.length + 1] === eChar
    ) : str[leadingZeros.length] === eChar;
    if (leadingZeros.length > 1 && eAdjacentToLeadingZeros) return str;
    else if (leadingZeros.length === 1 && (notation[3].startsWith(`.${eChar}`) || notation[3][0] === eChar)) {
      return Number(trimmedStr);
    } else if (options.leadingZeros && !eAdjacentToLeadingZeros) {
      trimmedStr = (notation[1] || "") + notation[3];
      return Number(trimmedStr);
    } else return str;
  } else {
    return str;
  }
}
function trimZeros(numStr) {
  if (numStr && numStr.indexOf(".") !== -1) {
    numStr = numStr.replace(/0+$/, "");
    if (numStr === ".") numStr = "0";
    else if (numStr[0] === ".") numStr = "0" + numStr;
    else if (numStr[numStr.length - 1] === ".") numStr = numStr.substring(0, numStr.length - 1);
    return numStr;
  }
  return numStr;
}
function parse_int(numStr, base) {
  if (parseInt) return parseInt(numStr, base);
  else if (Number.parseInt) return Number.parseInt(numStr, base);
  else if (window && window.parseInt) return window.parseInt(numStr, base);
  else throw new Error("parseInt, Number.parseInt, window.parseInt are not supported");
}

// node_modules/fast-xml-parser/src/ignoreAttributes.js
function getIgnoreAttributesFn(ignoreAttributes) {
  if (typeof ignoreAttributes === "function") {
    return ignoreAttributes;
  }
  if (Array.isArray(ignoreAttributes)) {
    return (attrName) => {
      for (const pattern of ignoreAttributes) {
        if (typeof pattern === "string" && attrName === pattern) {
          return true;
        }
        if (pattern instanceof RegExp && pattern.test(attrName)) {
          return true;
        }
      }
    };
  }
  return () => false;
}

// node_modules/fast-xml-parser/src/xmlparser/OrderedObjParser.js
var OrderedObjParser = class {
  constructor(options) {
    this.options = options;
    this.currentNode = null;
    this.tagsNodeStack = [];
    this.docTypeEntities = {};
    this.lastEntities = {
      "apos": { regex: /&(apos|#39|#x27);/g, val: "'" },
      "gt": { regex: /&(gt|#62|#x3E);/g, val: ">" },
      "lt": { regex: /&(lt|#60|#x3C);/g, val: "<" },
      "quot": { regex: /&(quot|#34|#x22);/g, val: '"' }
    };
    this.ampEntity = { regex: /&(amp|#38|#x26);/g, val: "&" };
    this.htmlEntities = {
      "space": { regex: /&(nbsp|#160);/g, val: " " },
      // "lt" : { regex: /&(lt|#60);/g, val: "<" },
      // "gt" : { regex: /&(gt|#62);/g, val: ">" },
      // "amp" : { regex: /&(amp|#38);/g, val: "&" },
      // "quot" : { regex: /&(quot|#34);/g, val: "\"" },
      // "apos" : { regex: /&(apos|#39);/g, val: "'" },
      "cent": { regex: /&(cent|#162);/g, val: "\xA2" },
      "pound": { regex: /&(pound|#163);/g, val: "\xA3" },
      "yen": { regex: /&(yen|#165);/g, val: "\xA5" },
      "euro": { regex: /&(euro|#8364);/g, val: "\u20AC" },
      "copyright": { regex: /&(copy|#169);/g, val: "\xA9" },
      "reg": { regex: /&(reg|#174);/g, val: "\xAE" },
      "inr": { regex: /&(inr|#8377);/g, val: "\u20B9" },
      "num_dec": { regex: /&#([0-9]{1,7});/g, val: (_, str) => fromCodePoint(str, 10, "&#") },
      "num_hex": { regex: /&#x([0-9a-fA-F]{1,6});/g, val: (_, str) => fromCodePoint(str, 16, "&#x") }
    };
    this.addExternalEntities = addExternalEntities;
    this.parseXml = parseXml;
    this.parseTextData = parseTextData;
    this.resolveNameSpace = resolveNameSpace;
    this.buildAttributesMap = buildAttributesMap;
    this.isItStopNode = isItStopNode;
    this.replaceEntitiesValue = replaceEntitiesValue;
    this.readStopNodeData = readStopNodeData;
    this.saveTextToParentTag = saveTextToParentTag;
    this.addChild = addChild;
    this.ignoreAttributesFn = getIgnoreAttributesFn(this.options.ignoreAttributes);
    if (this.options.stopNodes && this.options.stopNodes.length > 0) {
      this.stopNodesExact = /* @__PURE__ */ new Set();
      this.stopNodesWildcard = /* @__PURE__ */ new Set();
      for (let i = 0; i < this.options.stopNodes.length; i++) {
        const stopNodeExp = this.options.stopNodes[i];
        if (typeof stopNodeExp !== "string") continue;
        if (stopNodeExp.startsWith("*.")) {
          this.stopNodesWildcard.add(stopNodeExp.substring(2));
        } else {
          this.stopNodesExact.add(stopNodeExp);
        }
      }
    }
  }
};
function addExternalEntities(externalEntities) {
  const entKeys = Object.keys(externalEntities);
  for (let i = 0; i < entKeys.length; i++) {
    const ent = entKeys[i];
    this.lastEntities[ent] = {
      regex: new RegExp("&" + ent + ";", "g"),
      val: externalEntities[ent]
    };
  }
}
function parseTextData(val, tagName, jPath, dontTrim, hasAttributes, isLeafNode, escapeEntities) {
  if (val !== void 0) {
    if (this.options.trimValues && !dontTrim) {
      val = val.trim();
    }
    if (val.length > 0) {
      if (!escapeEntities) val = this.replaceEntitiesValue(val);
      const newval = this.options.tagValueProcessor(tagName, val, jPath, hasAttributes, isLeafNode);
      if (newval === null || newval === void 0) {
        return val;
      } else if (typeof newval !== typeof val || newval !== val) {
        return newval;
      } else if (this.options.trimValues) {
        return parseValue(val, this.options.parseTagValue, this.options.numberParseOptions);
      } else {
        const trimmedVal = val.trim();
        if (trimmedVal === val) {
          return parseValue(val, this.options.parseTagValue, this.options.numberParseOptions);
        } else {
          return val;
        }
      }
    }
  }
}
function resolveNameSpace(tagname) {
  if (this.options.removeNSPrefix) {
    const tags = tagname.split(":");
    const prefix = tagname.charAt(0) === "/" ? "/" : "";
    if (tags[0] === "xmlns") {
      return "";
    }
    if (tags.length === 2) {
      tagname = prefix + tags[1];
    }
  }
  return tagname;
}
var attrsRegx = new RegExp(`([^\\s=]+)\\s*(=\\s*(['"])([\\s\\S]*?)\\3)?`, "gm");
function buildAttributesMap(attrStr, jPath) {
  if (this.options.ignoreAttributes !== true && typeof attrStr === "string") {
    const matches = getAllMatches(attrStr, attrsRegx);
    const len = matches.length;
    const attrs = {};
    for (let i = 0; i < len; i++) {
      const attrName = this.resolveNameSpace(matches[i][1]);
      if (this.ignoreAttributesFn(attrName, jPath)) {
        continue;
      }
      let oldVal = matches[i][4];
      let aName = this.options.attributeNamePrefix + attrName;
      if (attrName.length) {
        if (this.options.transformAttributeName) {
          aName = this.options.transformAttributeName(aName);
        }
        if (aName === "__proto__") aName = "#__proto__";
        if (oldVal !== void 0) {
          if (this.options.trimValues) {
            oldVal = oldVal.trim();
          }
          oldVal = this.replaceEntitiesValue(oldVal);
          const newVal = this.options.attributeValueProcessor(attrName, oldVal, jPath);
          if (newVal === null || newVal === void 0) {
            attrs[aName] = oldVal;
          } else if (typeof newVal !== typeof oldVal || newVal !== oldVal) {
            attrs[aName] = newVal;
          } else {
            attrs[aName] = parseValue(
              oldVal,
              this.options.parseAttributeValue,
              this.options.numberParseOptions
            );
          }
        } else if (this.options.allowBooleanAttributes) {
          attrs[aName] = true;
        }
      }
    }
    if (!Object.keys(attrs).length) {
      return;
    }
    if (this.options.attributesGroupName) {
      const attrCollection = {};
      attrCollection[this.options.attributesGroupName] = attrs;
      return attrCollection;
    }
    return attrs;
  }
}
var parseXml = function(xmlData) {
  xmlData = xmlData.replace(/\r\n?/g, "\n");
  const xmlObj = new XmlNode("!xml");
  let currentNode = xmlObj;
  let textData = "";
  let jPath = "";
  const docTypeReader = new DocTypeReader(this.options.processEntities);
  for (let i = 0; i < xmlData.length; i++) {
    const ch = xmlData[i];
    if (ch === "<") {
      if (xmlData[i + 1] === "/") {
        const closeIndex = findClosingIndex(xmlData, ">", i, "Closing Tag is not closed.");
        let tagName = xmlData.substring(i + 2, closeIndex).trim();
        if (this.options.removeNSPrefix) {
          const colonIndex = tagName.indexOf(":");
          if (colonIndex !== -1) {
            tagName = tagName.substr(colonIndex + 1);
          }
        }
        if (this.options.transformTagName) {
          tagName = this.options.transformTagName(tagName);
        }
        if (currentNode) {
          textData = this.saveTextToParentTag(textData, currentNode, jPath);
        }
        const lastTagName = jPath.substring(jPath.lastIndexOf(".") + 1);
        if (tagName && this.options.unpairedTags.indexOf(tagName) !== -1) {
          throw new Error(`Unpaired tag can not be used as closing tag: </${tagName}>`);
        }
        let propIndex = 0;
        if (lastTagName && this.options.unpairedTags.indexOf(lastTagName) !== -1) {
          propIndex = jPath.lastIndexOf(".", jPath.lastIndexOf(".") - 1);
          this.tagsNodeStack.pop();
        } else {
          propIndex = jPath.lastIndexOf(".");
        }
        jPath = jPath.substring(0, propIndex);
        currentNode = this.tagsNodeStack.pop();
        textData = "";
        i = closeIndex;
      } else if (xmlData[i + 1] === "?") {
        let tagData = readTagExp(xmlData, i, false, "?>");
        if (!tagData) throw new Error("Pi Tag is not closed.");
        textData = this.saveTextToParentTag(textData, currentNode, jPath);
        if (this.options.ignoreDeclaration && tagData.tagName === "?xml" || this.options.ignorePiTags) {
        } else {
          const childNode = new XmlNode(tagData.tagName);
          childNode.add(this.options.textNodeName, "");
          if (tagData.tagName !== tagData.tagExp && tagData.attrExpPresent) {
            childNode[":@"] = this.buildAttributesMap(tagData.tagExp, jPath);
          }
          this.addChild(currentNode, childNode, jPath, i);
        }
        i = tagData.closeIndex + 1;
      } else if (xmlData.substr(i + 1, 3) === "!--") {
        const endIndex = findClosingIndex(xmlData, "-->", i + 4, "Comment is not closed.");
        if (this.options.commentPropName) {
          const comment = xmlData.substring(i + 4, endIndex - 2);
          textData = this.saveTextToParentTag(textData, currentNode, jPath);
          currentNode.add(this.options.commentPropName, [{ [this.options.textNodeName]: comment }]);
        }
        i = endIndex;
      } else if (xmlData.substr(i + 1, 2) === "!D") {
        const result = docTypeReader.readDocType(xmlData, i);
        this.docTypeEntities = result.entities;
        i = result.i;
      } else if (xmlData.substr(i + 1, 2) === "![") {
        const closeIndex = findClosingIndex(xmlData, "]]>", i, "CDATA is not closed.") - 2;
        const tagExp = xmlData.substring(i + 9, closeIndex);
        textData = this.saveTextToParentTag(textData, currentNode, jPath);
        let val = this.parseTextData(tagExp, currentNode.tagname, jPath, true, false, true, true);
        if (val == void 0) val = "";
        if (this.options.cdataPropName) {
          currentNode.add(this.options.cdataPropName, [{ [this.options.textNodeName]: tagExp }]);
        } else {
          currentNode.add(this.options.textNodeName, val);
        }
        i = closeIndex + 2;
      } else {
        let result = readTagExp(xmlData, i, this.options.removeNSPrefix);
        let tagName = result.tagName;
        const rawTagName = result.rawTagName;
        let tagExp = result.tagExp;
        let attrExpPresent = result.attrExpPresent;
        let closeIndex = result.closeIndex;
        if (this.options.transformTagName) {
          const newTagName = this.options.transformTagName(tagName);
          if (tagExp === tagName) {
            tagExp = newTagName;
          }
          tagName = newTagName;
        }
        if (currentNode && textData) {
          if (currentNode.tagname !== "!xml") {
            textData = this.saveTextToParentTag(textData, currentNode, jPath, false);
          }
        }
        const lastTag = currentNode;
        if (lastTag && this.options.unpairedTags.indexOf(lastTag.tagname) !== -1) {
          currentNode = this.tagsNodeStack.pop();
          jPath = jPath.substring(0, jPath.lastIndexOf("."));
        }
        if (tagName !== xmlObj.tagname) {
          jPath += jPath ? "." + tagName : tagName;
        }
        const startIndex = i;
        if (this.isItStopNode(this.stopNodesExact, this.stopNodesWildcard, jPath, tagName)) {
          let tagContent = "";
          if (tagExp.length > 0 && tagExp.lastIndexOf("/") === tagExp.length - 1) {
            if (tagName[tagName.length - 1] === "/") {
              tagName = tagName.substr(0, tagName.length - 1);
              jPath = jPath.substr(0, jPath.length - 1);
              tagExp = tagName;
            } else {
              tagExp = tagExp.substr(0, tagExp.length - 1);
            }
            i = result.closeIndex;
          } else if (this.options.unpairedTags.indexOf(tagName) !== -1) {
            i = result.closeIndex;
          } else {
            const result2 = this.readStopNodeData(xmlData, rawTagName, closeIndex + 1);
            if (!result2) throw new Error(`Unexpected end of ${rawTagName}`);
            i = result2.i;
            tagContent = result2.tagContent;
          }
          const childNode = new XmlNode(tagName);
          if (tagName !== tagExp && attrExpPresent) {
            childNode[":@"] = this.buildAttributesMap(
              tagExp,
              jPath
            );
          }
          if (tagContent) {
            tagContent = this.parseTextData(tagContent, tagName, jPath, true, attrExpPresent, true, true);
          }
          jPath = jPath.substr(0, jPath.lastIndexOf("."));
          childNode.add(this.options.textNodeName, tagContent);
          this.addChild(currentNode, childNode, jPath, startIndex);
        } else {
          if (tagExp.length > 0 && tagExp.lastIndexOf("/") === tagExp.length - 1) {
            if (tagName[tagName.length - 1] === "/") {
              tagName = tagName.substr(0, tagName.length - 1);
              jPath = jPath.substr(0, jPath.length - 1);
              tagExp = tagName;
            } else {
              tagExp = tagExp.substr(0, tagExp.length - 1);
            }
            if (this.options.transformTagName) {
              const newTagName = this.options.transformTagName(tagName);
              if (tagExp === tagName) {
                tagExp = newTagName;
              }
              tagName = newTagName;
            }
            const childNode = new XmlNode(tagName);
            if (tagName !== tagExp && attrExpPresent) {
              childNode[":@"] = this.buildAttributesMap(tagExp, jPath);
            }
            this.addChild(currentNode, childNode, jPath, startIndex);
            jPath = jPath.substr(0, jPath.lastIndexOf("."));
          } else {
            const childNode = new XmlNode(tagName);
            this.tagsNodeStack.push(currentNode);
            if (tagName !== tagExp && attrExpPresent) {
              childNode[":@"] = this.buildAttributesMap(tagExp, jPath);
            }
            this.addChild(currentNode, childNode, jPath, startIndex);
            currentNode = childNode;
          }
          textData = "";
          i = closeIndex;
        }
      }
    } else {
      textData += xmlData[i];
    }
  }
  return xmlObj.child;
};
function addChild(currentNode, childNode, jPath, startIndex) {
  if (!this.options.captureMetaData) startIndex = void 0;
  const result = this.options.updateTag(childNode.tagname, jPath, childNode[":@"]);
  if (result === false) {
  } else if (typeof result === "string") {
    childNode.tagname = result;
    currentNode.addChild(childNode, startIndex);
  } else {
    currentNode.addChild(childNode, startIndex);
  }
}
var replaceEntitiesValue = function(val) {
  if (this.options.processEntities) {
    for (let entityName in this.docTypeEntities) {
      const entity = this.docTypeEntities[entityName];
      val = val.replace(entity.regx, entity.val);
    }
    for (let entityName in this.lastEntities) {
      const entity = this.lastEntities[entityName];
      val = val.replace(entity.regex, entity.val);
    }
    if (this.options.htmlEntities) {
      for (let entityName in this.htmlEntities) {
        const entity = this.htmlEntities[entityName];
        val = val.replace(entity.regex, entity.val);
      }
    }
    val = val.replace(this.ampEntity.regex, this.ampEntity.val);
  }
  return val;
};
function saveTextToParentTag(textData, currentNode, jPath, isLeafNode) {
  if (textData) {
    if (isLeafNode === void 0) isLeafNode = currentNode.child.length === 0;
    textData = this.parseTextData(
      textData,
      currentNode.tagname,
      jPath,
      false,
      currentNode[":@"] ? Object.keys(currentNode[":@"]).length !== 0 : false,
      isLeafNode
    );
    if (textData !== void 0 && textData !== "")
      currentNode.add(this.options.textNodeName, textData);
    textData = "";
  }
  return textData;
}
function isItStopNode(stopNodesExact, stopNodesWildcard, jPath, currentTagName) {
  if (stopNodesWildcard && stopNodesWildcard.has(currentTagName)) return true;
  if (stopNodesExact && stopNodesExact.has(jPath)) return true;
  return false;
}
function tagExpWithClosingIndex(xmlData, i, closingChar = ">") {
  let attrBoundary;
  let tagExp = "";
  for (let index = i; index < xmlData.length; index++) {
    let ch = xmlData[index];
    if (attrBoundary) {
      if (ch === attrBoundary) attrBoundary = "";
    } else if (ch === '"' || ch === "'") {
      attrBoundary = ch;
    } else if (ch === closingChar[0]) {
      if (closingChar[1]) {
        if (xmlData[index + 1] === closingChar[1]) {
          return {
            data: tagExp,
            index
          };
        }
      } else {
        return {
          data: tagExp,
          index
        };
      }
    } else if (ch === "	") {
      ch = " ";
    }
    tagExp += ch;
  }
}
function findClosingIndex(xmlData, str, i, errMsg) {
  const closingIndex = xmlData.indexOf(str, i);
  if (closingIndex === -1) {
    throw new Error(errMsg);
  } else {
    return closingIndex + str.length - 1;
  }
}
function readTagExp(xmlData, i, removeNSPrefix, closingChar = ">") {
  const result = tagExpWithClosingIndex(xmlData, i + 1, closingChar);
  if (!result) return;
  let tagExp = result.data;
  const closeIndex = result.index;
  const separatorIndex = tagExp.search(/\s/);
  let tagName = tagExp;
  let attrExpPresent = true;
  if (separatorIndex !== -1) {
    tagName = tagExp.substring(0, separatorIndex);
    tagExp = tagExp.substring(separatorIndex + 1).trimStart();
  }
  const rawTagName = tagName;
  if (removeNSPrefix) {
    const colonIndex = tagName.indexOf(":");
    if (colonIndex !== -1) {
      tagName = tagName.substr(colonIndex + 1);
      attrExpPresent = tagName !== result.data.substr(colonIndex + 1);
    }
  }
  return {
    tagName,
    tagExp,
    closeIndex,
    attrExpPresent,
    rawTagName
  };
}
function readStopNodeData(xmlData, tagName, i) {
  const startIndex = i;
  let openTagCount = 1;
  for (; i < xmlData.length; i++) {
    if (xmlData[i] === "<") {
      if (xmlData[i + 1] === "/") {
        const closeIndex = findClosingIndex(xmlData, ">", i, `${tagName} is not closed`);
        let closeTagName = xmlData.substring(i + 2, closeIndex).trim();
        if (closeTagName === tagName) {
          openTagCount--;
          if (openTagCount === 0) {
            return {
              tagContent: xmlData.substring(startIndex, i),
              i: closeIndex
            };
          }
        }
        i = closeIndex;
      } else if (xmlData[i + 1] === "?") {
        const closeIndex = findClosingIndex(xmlData, "?>", i + 1, "StopNode is not closed.");
        i = closeIndex;
      } else if (xmlData.substr(i + 1, 3) === "!--") {
        const closeIndex = findClosingIndex(xmlData, "-->", i + 3, "StopNode is not closed.");
        i = closeIndex;
      } else if (xmlData.substr(i + 1, 2) === "![") {
        const closeIndex = findClosingIndex(xmlData, "]]>", i, "StopNode is not closed.") - 2;
        i = closeIndex;
      } else {
        const tagData = readTagExp(xmlData, i, ">");
        if (tagData) {
          const openTagName = tagData && tagData.tagName;
          if (openTagName === tagName && tagData.tagExp[tagData.tagExp.length - 1] !== "/") {
            openTagCount++;
          }
          i = tagData.closeIndex;
        }
      }
    }
  }
}
function parseValue(val, shouldParse, options) {
  if (shouldParse && typeof val === "string") {
    const newval = val.trim();
    if (newval === "true") return true;
    else if (newval === "false") return false;
    else return toNumber(val, options);
  } else {
    if (isExist(val)) {
      return val;
    } else {
      return "";
    }
  }
}
function fromCodePoint(str, base, prefix) {
  const codePoint = Number.parseInt(str, base);
  if (codePoint >= 0 && codePoint <= 1114111) {
    return String.fromCodePoint(codePoint);
  } else {
    return prefix + str + ";";
  }
}

// node_modules/fast-xml-parser/src/xmlparser/node2json.js
var METADATA_SYMBOL2 = XmlNode.getMetaDataSymbol();
function prettify(node, options) {
  return compress(node, options);
}
function compress(arr, options, jPath) {
  let text;
  const compressedObj = {};
  for (let i = 0; i < arr.length; i++) {
    const tagObj = arr[i];
    const property = propName(tagObj);
    let newJpath = "";
    if (jPath === void 0) newJpath = property;
    else newJpath = jPath + "." + property;
    if (property === options.textNodeName) {
      if (text === void 0) text = tagObj[property];
      else text += "" + tagObj[property];
    } else if (property === void 0) {
      continue;
    } else if (tagObj[property]) {
      let val = compress(tagObj[property], options, newJpath);
      const isLeaf = isLeafTag(val, options);
      if (tagObj[METADATA_SYMBOL2] !== void 0) {
        val[METADATA_SYMBOL2] = tagObj[METADATA_SYMBOL2];
      }
      if (tagObj[":@"]) {
        assignAttributes(val, tagObj[":@"], newJpath, options);
      } else if (Object.keys(val).length === 1 && val[options.textNodeName] !== void 0 && !options.alwaysCreateTextNode) {
        val = val[options.textNodeName];
      } else if (Object.keys(val).length === 0) {
        if (options.alwaysCreateTextNode) val[options.textNodeName] = "";
        else val = "";
      }
      if (compressedObj[property] !== void 0 && compressedObj.hasOwnProperty(property)) {
        if (!Array.isArray(compressedObj[property])) {
          compressedObj[property] = [compressedObj[property]];
        }
        compressedObj[property].push(val);
      } else {
        if (options.isArray(property, newJpath, isLeaf)) {
          compressedObj[property] = [val];
        } else {
          compressedObj[property] = val;
        }
      }
    }
  }
  if (typeof text === "string") {
    if (text.length > 0) compressedObj[options.textNodeName] = text;
  } else if (text !== void 0) compressedObj[options.textNodeName] = text;
  return compressedObj;
}
function propName(obj) {
  const keys = Object.keys(obj);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    if (key !== ":@") return key;
  }
}
function assignAttributes(obj, attrMap, jpath, options) {
  if (attrMap) {
    const keys = Object.keys(attrMap);
    const len = keys.length;
    for (let i = 0; i < len; i++) {
      const atrrName = keys[i];
      if (options.isArray(atrrName, jpath + "." + atrrName, true, true)) {
        obj[atrrName] = [attrMap[atrrName]];
      } else {
        obj[atrrName] = attrMap[atrrName];
      }
    }
  }
}
function isLeafTag(obj, options) {
  const { textNodeName } = options;
  const propCount = Object.keys(obj).length;
  if (propCount === 0) {
    return true;
  }
  if (propCount === 1 && (obj[textNodeName] || typeof obj[textNodeName] === "boolean" || obj[textNodeName] === 0)) {
    return true;
  }
  return false;
}

// node_modules/fast-xml-parser/src/xmlparser/XMLParser.js
var XMLParser = class {
  constructor(options) {
    this.externalEntities = {};
    this.options = buildOptions(options);
  }
  /**
   * Parse XML dats to JS object 
   * @param {string|Uint8Array} xmlData 
   * @param {boolean|Object} validationOption 
   */
  parse(xmlData, validationOption) {
    if (typeof xmlData !== "string" && xmlData.toString) {
      xmlData = xmlData.toString();
    } else if (typeof xmlData !== "string") {
      throw new Error("XML data is accepted in String or Bytes[] form.");
    }
    if (validationOption) {
      if (validationOption === true) validationOption = {};
      const result = validate(xmlData, validationOption);
      if (result !== true) {
        throw Error(`${result.err.msg}:${result.err.line}:${result.err.col}`);
      }
    }
    const orderedObjParser = new OrderedObjParser(this.options);
    orderedObjParser.addExternalEntities(this.externalEntities);
    const orderedResult = orderedObjParser.parseXml(xmlData);
    if (this.options.preserveOrder || orderedResult === void 0) return orderedResult;
    else return prettify(orderedResult, this.options);
  }
  /**
   * Add Entity which is not by default supported by this library
   * @param {string} key 
   * @param {string} value 
   */
  addEntity(key, value) {
    if (value.indexOf("&") !== -1) {
      throw new Error("Entity value can't have '&'");
    } else if (key.indexOf("&") !== -1 || key.indexOf(";") !== -1) {
      throw new Error("An entity must be set without '&' and ';'. Eg. use '#xD' for '&#xD;'");
    } else if (value === "&") {
      throw new Error("An entity with value '&' is not permitted");
    } else {
      this.externalEntities[key] = value;
    }
  }
  /**
   * Returns a Symbol that can be used to access the metadata
   * property on a node.
   * 
   * If Symbol is not available in the environment, an ordinary property is used
   * and the name of the property is here returned.
   * 
   * The XMLMetaData property is only present when `captureMetaData`
   * is true in the options.
   */
  static getMetaDataSymbol() {
    return XmlNode.getMetaDataSymbol();
  }
};

// index.js
var import_date_fns = __toESM(require_date_fns(), 1);
import crypto from "node:crypto";
var CONFIG = {
  url: process.env.NEXTCLOUD_URL,
  user: process.env.NEXTCLOUD_USER,
  token: process.env.NEXTCLOUD_TOKEN,
  timeZone: process.env.NEXTCLOUD_TIMEZONE || process.env.TZ || "UTC"
};
if (!CONFIG.url || !CONFIG.user || !CONFIG.token) {
  console.error(JSON.stringify({
    status: "error",
    message: "Missing configuration. Set NEXTCLOUD_URL, NEXTCLOUD_USER, and NEXTCLOUD_TOKEN."
  }));
  process.exit(1);
}
var AUTH_HEADER = "Basic " + Buffer2.from(`${CONFIG.user}:${CONFIG.token}`).toString("base64");
var parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: "@_"
});
async function request(endpoint, options = {}) {
  const url = `${CONFIG.url}${endpoint}`;
  const headers = {
    "Authorization": AUTH_HEADER,
    "User-Agent": "OpenClaw-Nextcloud-Skill",
    ...options.headers
  };
  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    } else if (contentType && contentType.includes("xml")) {
      const text = await response.text();
      return parser.parse(text);
    } else {
      return await response.text();
    }
  } catch (error) {
    throw new Error(`Request failed: ${error.message}`);
  }
}
function output(data) {
  console.log(JSON.stringify({
    status: "success",
    data
  }, null, 2));
}
function errorOutput(message) {
  console.error(JSON.stringify({
    status: "error",
    message: message.stack || message
  }, null, 2));
  process.exit(1);
}
function ensureArray(item) {
  if (Array.isArray(item)) return item;
  if (item === void 0 || item === null) return [];
  return [item];
}
function ensureNonEmptyString(value, fieldName) {
  const normalized = String(value ?? "").trim();
  if (!normalized) {
    throw new Error(`${fieldName} is required.`);
  }
  return normalized;
}
function normalizeOptionalString(value) {
  if (value === void 0 || value === null) return null;
  return String(value).trim();
}
function ensureValidTimeZone(timeZone) {
  try {
    new Intl.DateTimeFormat("en-US", { timeZone }).format(new Date());
    return true;
  } catch (_error) {
    return false;
  }
}
function getTimeZoneOffsetMillis(date, timeZone) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).formatToParts(date);
  const map = {};
  for (const part of parts) {
    if (part.type !== "literal") map[part.type] = part.value;
  }
  const asUtc = Date.UTC(
    Number(map.year),
    Number(map.month) - 1,
    Number(map.day),
    Number(map.hour),
    Number(map.minute),
    Number(map.second)
  );
  return asUtc - date.getTime();
}
function zonedDateTimeToUtcMs(year, month, day, hour, minute, second, timeZone) {
  let utcMs = Date.UTC(year, month - 1, day, hour, minute, second);
  for (let i = 0; i < 3; i++) {
    const offset = getTimeZoneOffsetMillis(new Date(utcMs), timeZone);
    const next = Date.UTC(year, month - 1, day, hour, minute, second) - offset;
    if (next === utcMs) break;
    utcMs = next;
  }
  return utcMs;
}
function resolveCalendarTimeZone(timeZoneInput) {
  const selected = normalizeOptionalString(timeZoneInput) || CONFIG.timeZone;
  if (!ensureValidTimeZone(selected)) {
    throw new Error(`Invalid timezone '${selected}'. Set NEXTCLOUD_TIMEZONE to a valid IANA timezone (e.g. America/Los_Angeles).`);
  }
  return selected;
}
function parseDateTimeInput(value, fieldName, timeZoneInput = null) {
  const raw = ensureNonEmptyString(value, fieldName);
  const explicitTzRegex = /(Z|[+\-]\d{2}:?\d{2})$/i;
  if (explicitTzRegex.test(raw)) {
    const d = new Date(raw);
    if (Number.isNaN(d.getTime())) {
      throw new Error(`${fieldName} must be a valid ISO date or datetime.`);
    }
    return d;
  }
  const dateOnlyMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  const dateTimeMatch = raw.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?$/);
  if (!dateOnlyMatch && !dateTimeMatch) {
    throw new Error(`${fieldName} must be ISO-like. Use timezone-aware values (e.g. 2026-03-02T10:00:00-08:00) or set NEXTCLOUD_TIMEZONE for local values.`);
  }
  const tz = resolveCalendarTimeZone(timeZoneInput);
  const year = Number((dateTimeMatch || dateOnlyMatch)[1]);
  const month = Number((dateTimeMatch || dateOnlyMatch)[2]);
  const day = Number((dateTimeMatch || dateOnlyMatch)[3]);
  const hour = dateTimeMatch ? Number(dateTimeMatch[4]) : 0;
  const minute = dateTimeMatch ? Number(dateTimeMatch[5]) : 0;
  const second = dateTimeMatch && dateTimeMatch[6] ? Number(dateTimeMatch[6]) : 0;
  const utcMs = zonedDateTimeToUtcMs(year, month, day, hour, minute, second, tz);
  const d = new Date(utcMs);
  if (Number.isNaN(d.getTime())) {
    throw new Error(`${fieldName} must be a valid ISO date or datetime.`);
  }
  if (d.getUTCFullYear() < 1900 || d.getUTCFullYear() > 9999) {
    throw new Error(`${fieldName} is out of supported range.`);
  }
  return d;
}
function parseDateInputFlexible(value, fieldName, timeZoneInput = null) {
  const raw = ensureNonEmptyString(value, fieldName);
  const yyyyMmDd = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (yyyyMmDd) {
    return { year: Number(yyyyMmDd[1]), month: Number(yyyyMmDd[2]), day: Number(yyyyMmDd[3]) };
  }
  const mmDdYyyy = raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (mmDdYyyy) {
    return { year: Number(mmDdYyyy[3]), month: Number(mmDdYyyy[1]), day: Number(mmDdYyyy[2]) };
  }
  const d = parseDateTimeInput(raw, fieldName, timeZoneInput);
  const tz = resolveCalendarTimeZone(timeZoneInput);
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: tz,
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).formatToParts(d);
  const map = {};
  for (const part of parts) {
    if (part.type !== "literal") map[part.type] = part.value;
  }
  return { year: Number(map.year), month: Number(map.month), day: Number(map.day) };
}
function toCalDavDate(value, fieldName, timeZoneInput = null) {
  const { year, month, day } = parseDateInputFlexible(value, fieldName, timeZoneInput);
  const utcProbe = new Date(Date.UTC(year, month - 1, day));
  if (utcProbe.getUTCFullYear() !== year || utcProbe.getUTCMonth() !== month - 1 || utcProbe.getUTCDate() !== day) {
    throw new Error(`${fieldName} has an invalid date value.`);
  }
  return `${String(year).padStart(4, "0")}${String(month).padStart(2, "0")}${String(day).padStart(2, "0")}`;
}
function addOneDayCalDate(calDate) {
  const year = Number(calDate.slice(0, 4));
  const month = Number(calDate.slice(4, 6));
  const day = Number(calDate.slice(6, 8));
  const d = new Date(Date.UTC(year, month - 1, day));
  d.setUTCDate(d.getUTCDate() + 1);
  return `${d.getUTCFullYear().toString().padStart(4, "0")}${String(d.getUTCMonth() + 1).padStart(2, "0")}${String(d.getUTCDate()).padStart(2, "0")}`;
}
function compareCalDate(a, b) {
  if (a === b) return 0;
  return a < b ? -1 : 1;
}
function isoDateAddDays(isoDate, days) {
  const [year, month, day] = isoDate.split("-").map((v) => Number(v));
  const d = new Date(Date.UTC(year, month - 1, day));
  d.setUTCDate(d.getUTCDate() + days);
  return `${d.getUTCFullYear().toString().padStart(4, "0")}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
}
function parseClockLikeDateTime(rawValue) {
  const raw = String(rawValue ?? "").trim();
  const match = raw.match(/^(\d{4}-\d{2}-\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?$/);
  if (!match) return null;
  return {
    date: match[1],
    hour: Number(match[2]),
    minute: Number(match[3]),
    second: match[4] ? Number(match[4]) : 0
  };
}
function isAllDayLikeTimedRange(startRaw, endRaw) {
  const start = parseClockLikeDateTime(startRaw);
  const end = parseClockLikeDateTime(endRaw);
  if (!start || !end) return false;
  const startsAtMidnight = start.hour === 0 && start.minute === 0 && start.second === 0;
  const endsAtDayEnd = end.hour === 23 && end.minute === 59 && (end.second === 0 || end.second === 59);
  if (startsAtMidnight && endsAtDayEnd && start.date === end.date) return true;
  const endsAtNextMidnight = end.hour === 0 && end.minute === 0 && end.second === 0 && end.date === isoDateAddDays(start.date, 1);
  if (startsAtMidnight && endsAtNextMidnight) return true;
  return false;
}
function toCalDavDateTime(value, fieldName, timeZoneInput = null) {
  const d = parseDateTimeInput(value, fieldName, timeZoneInput);
  return d.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
}
function encodeICalText(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/\r\n/g, "\\n").replace(/\n/g, "\\n").replace(/,/g, "\\,").replace(/;/g, "\\;");
}
function decodeICalText(value) {
  return String(value ?? "").replace(/\\n/gi, "\n").replace(/\\,/g, ",").replace(/\\;/g, ";").replace(/\\\\/g, "\\").trim();
}
function normalizeICalLineEndings(value) {
  return String(value ?? "").replace(/\r?\n/g, "\r\n");
}
var Notes = {
  async list() {
    const data = await request("/index.php/apps/notes/api/v1/notes", {
      headers: { "Accept": "application/json" }
    });
    return data.map((n) => ({
      id: n.id,
      title: n.title,
      modified: n.modified,
      category: n.category
    }));
  },
  async get(id) {
    return await request(`/index.php/apps/notes/api/v1/notes/${id}`, {
      headers: { "Accept": "application/json" }
    });
  },
  async create(title, content, category = "") {
    if (!title || typeof title !== "string" || title.trim() === "") {
      throw new Error("Title is required for creating a note.");
    }
    if (!content || typeof content !== "string") {
      throw new Error("Content is required for creating a note.");
    }
    const payload = { title, content };
    if (category) {
      payload.category = category;
    }
    const data = await request("/index.php/apps/notes/api/v1/notes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });
    return {
      id: data.id,
      title: data.title,
      modified: data.modified,
      category: data.category,
      content: data.content
      // Return content as well for verification
    };
  },
  async update(id, title, content, category) {
    if (!id) throw new Error("Note ID is required for update.");
    const payload = {};
    if (title !== void 0) payload.title = String(title);
    if (content !== void 0) payload.content = String(content);
    if (category !== void 0) payload.category = String(category);
    if (Object.keys(payload).length === 0) {
      throw new Error("Nothing to update. Provide title, content, or category.");
    }
    const data = await request(`/index.php/apps/notes/api/v1/notes/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });
    return data;
  },
  async delete(id) {
    if (!id) throw new Error("Note ID is required for deletion.");
    await request(`/index.php/apps/notes/api/v1/notes/${id}`, {
      method: "DELETE",
      headers: {
        "Accept": "application/json"
      }
    });
    return { success: true, id };
  }
};
var SEARCH_STOP_WORDS = new Set([
  "a",
  "an",
  "and",
  "document",
  "doc",
  "file",
  "files",
  "find",
  "for",
  "in",
  "is",
  "me",
  "my",
  "of",
  "please",
  "show",
  "the",
  "to"
]);
function normalizeSearchText(value) {
  return String(value ?? "").toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, " ").trim();
}
function extractSearchTokens(query) {
  const normalized = normalizeSearchText(query);
  if (!normalized) return [];
  return normalized.split(" ").map((t) => t.trim()).filter((t) => t.length >= 2 && !SEARCH_STOP_WORDS.has(t));
}
function buildSearchQueryVariants(rawQuery) {
  const direct = ensureNonEmptyString(rawQuery, "Search query");
  const normalized = normalizeSearchText(direct);
  const tokens = extractSearchTokens(direct);
  const tokenPhrase = tokens.join(" ");
  const variants = [];
  const seen = /* @__PURE__ */ new Set();
  for (const candidate of [direct, normalized, tokenPhrase]) {
    const cleaned = String(candidate ?? "").trim();
    if (!cleaned) continue;
    const key = cleaned.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    variants.push(cleaned);
  }
  return variants;
}
function parseDavFileResponses(response) {
  if (!response?.["d:multistatus"] || !response["d:multistatus"]["d:response"]) return [];
  const responses = ensureArray(response["d:multistatus"]["d:response"]);
  return responses.map((r) => {
    const href = r["d:href"];
    const propstats = ensureArray(r["d:propstat"]);
    if (!propstats[0] || !propstats[0]["d:prop"]) return null;
    const props = propstats[0]["d:prop"];
    const isDir = props["d:resourcetype"] && props["d:resourcetype"]["d:collection"] !== void 0;
    const fallbackName = decodeURIComponent(String(href || "").split("/").filter((p) => p).pop() || "");
    return {
      name: props["d:displayname"] || fallbackName,
      path: toUserPathFromDavHref(href),
      davHref: href,
      isDir,
      size: props["d:getcontentlength"],
      lastModified: props["d:getlastmodified"]
    };
  }).filter((f) => f);
}
function rankFileSearchResults(items, rawQuery) {
  const queryNorm = normalizeSearchText(rawQuery);
  const tokens = extractSearchTokens(rawQuery);
  const ranked = [];
  const seenPaths = /* @__PURE__ */ new Set();
  for (const item of items) {
    if (!item || !item.path) continue;
    const pathKey = String(item.path).toLowerCase();
    if (seenPaths.has(pathKey)) continue;
    seenPaths.add(pathKey);
    const nameNorm = normalizeSearchText(item.name || "");
    const pathNorm = normalizeSearchText(decodeURIComponent(item.path || ""));
    let score = 0;
    if (queryNorm && nameNorm === queryNorm) score += 120;
    if (queryNorm && nameNorm.includes(queryNorm)) score += 70;
    if (queryNorm && pathNorm.includes(queryNorm)) score += 45;
    if (tokens.length > 0) {
      let matched = 0;
      for (const token of tokens) {
        if (nameNorm.includes(token)) {
          score += 22;
          matched++;
        } else if (pathNorm.includes(token)) {
          score += 10;
          matched++;
        }
      }
      if (matched === tokens.length) score += 25;
    }
    if (score > 0 || items.length === 1) {
      ranked.push({
        ...item,
        relevanceScore: score
      });
    }
  }
  ranked.sort((a, b) => b.relevanceScore - a.relevanceScore || String(a.name || "").localeCompare(String(b.name || "")));
  return ranked;
}
function normalizeDavFilePathInput(filePath, fieldName = "File path") {
  const raw = ensureNonEmptyString(filePath, fieldName);
  let candidate = raw.trim();
  if (/^https?:\/\//i.test(candidate)) {
    try {
      candidate = new URL(candidate).pathname;
    } catch (_error) {
    }
  }
  const expectedPrefix = `/remote.php/dav/files/${CONFIG.user}/`;
  const prefixIndex = candidate.indexOf(expectedPrefix);
  if (prefixIndex !== -1) {
    candidate = candidate.slice(prefixIndex + expectedPrefix.length);
  }
  candidate = candidate.replace(/^\/+/, "");
  if (!candidate) throw new Error(`${fieldName} is required.`);
  return candidate;
}
function toUserPathFromDavHref(href) {
  const expectedPrefix = `/remote.php/dav/files/${CONFIG.user}/`;
  const rawHref = String(href || "");
  const normalized = rawHref.startsWith(expectedPrefix) ? rawHref.slice(expectedPrefix.length) : rawHref.replace(/^\/+/, "");
  const decoded = decodeURIComponent(normalized);
  return decoded.startsWith("/") ? decoded : `/${decoded}`;
}
var Files = {
  async list(dirPath = "/") {
    const cleanPath = dirPath === "/" ? "" : normalizeDavFilePathInput(dirPath, "Directory path");
    const endpoint = `/remote.php/dav/files/${CONFIG.user}/${cleanPath}`;
    const response = await request(endpoint, {
      method: "PROPFIND",
      headers: {
        "Depth": "1",
        "Content-Type": "application/xml"
      }
    });
    if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) {
      return [];
    }
    const responses = ensureArray(response["d:multistatus"]["d:response"]);
    return responses.map((r) => {
      const href = r["d:href"];
      const propstats = ensureArray(r["d:propstat"]);
      if (!propstats[0] || !propstats[0]["d:prop"]) return null;
      const props = propstats[0]["d:prop"];
      const isDir = props["d:resourcetype"] && props["d:resourcetype"]["d:collection"] !== void 0;
      const name = decodeURIComponent(href.split("/").filter((p) => p).pop());
      if (href.endsWith(encodeURIComponent(CONFIG.user) + "/" + cleanPath) || href.endsWith(encodeURIComponent(CONFIG.user) + "/" + cleanPath + "/")) {
        if (cleanPath !== "" && name === cleanPath.split("/").pop()) return null;
      }
      return {
        name,
        path: toUserPathFromDavHref(href),
        davHref: href,
        isDir,
        size: props["d:getcontentlength"],
        lastModified: props["d:getlastmodified"]
      };
    }).filter((f) => f);
  },
  async upload(filePath, content) {
    const cleanPath = normalizeDavFilePathInput(filePath, "File path");
    const endpoint = `/remote.php/dav/files/${CONFIG.user}/${cleanPath}`;
    await request(endpoint, {
      method: "PUT",
      headers: {
        "Content-Type": "application/octet-stream"
      },
      body: content,
      rawBody: true
    });
    return { path: filePath, status: "uploaded", size: content.length };
  },
  async get(filePath) {
    const cleanPath = normalizeDavFilePathInput(filePath, "File path");
    const endpoint = `/remote.php/dav/files/${CONFIG.user}/${cleanPath}`;
    const response = await fetch(`${CONFIG.url}${endpoint}`, {
      method: "GET",
      headers: {
        "Authorization": `Basic ${Buffer2.from(`${CONFIG.user}:${CONFIG.token}`).toString("base64")}`
      }
    });
    if (!response.ok) {
      throw new Error(`Request failed: HTTP ${response.status}: ${response.statusText}`);
    }
    const content = await response.text();
    return { path: filePath, content, size: content.length };
  },
  async delete(filePath) {
    const cleanPath = normalizeDavFilePathInput(filePath, "File path");
    const endpoint = `/remote.php/dav/files/${CONFIG.user}/${cleanPath}`;
    await request(endpoint, {
      method: "DELETE"
    });
    return { path: filePath, status: "deleted" };
  },
  async search(query) {
    const rawQuery = ensureNonEmptyString(query, "Search query");
    const queryVariants = buildSearchQueryVariants(rawQuery);
    const endpoint = `/remote.php/dav/files/${CONFIG.user}/`;
    const buildSearchBody = (term) => {
      const safeTerm = escapeXml(term);
      return `
            <d:searchrequest xmlns:d="DAV:">
                <d:basicsearch>
                    <d:select>
                        <d:prop>
                            <d:getlastmodified/>
                            <d:getcontentlength/>
                            <d:resourcetype/>
                            <d:displayname/>
                        </d:prop>
                    </d:select>
                    <d:from>
                        <d:scope>
                            <d:href>/files/${CONFIG.user}</d:href>
                            <d:depth>infinity</d:depth>
                        </d:scope>
                    </d:from>
                    <d:where>
                        <d:like>
                            <d:prop>
                                <d:displayname/>
                            </d:prop>
                            <d:literal>%${safeTerm}%</d:literal>
                        </d:like>
                    </d:where>
                </d:basicsearch>
            </d:searchrequest>
        `;
    };
    const fallbackBody = `
                <d:propfind xmlns:d="DAV:">
                    <d:prop>
                        <d:getlastmodified/>
                        <d:getcontentlength/>
                        <d:resourcetype/>
                        <d:displayname/>
                    </d:prop>
                </d:propfind>
            `;
    const runFallbackScan = async () => {
      const response = await request(endpoint, {
        method: "PROPFIND",
        headers: {
          "Depth": "infinity",
          "Content-Type": "application/xml"
        },
        body: fallbackBody
      });
      const candidates = parseDavFileResponses(response);
      return rankFileSearchResults(candidates, rawQuery);
    };
    try {
      let serverCandidates = [];
      for (const term of queryVariants) {
        const response = await request(endpoint, {
          method: "SEARCH",
          headers: { "Content-Type": "application/xml" },
          body: buildSearchBody(term)
        });
        serverCandidates = serverCandidates.concat(parseDavFileResponses(response));
      }
      const ranked = rankFileSearchResults(serverCandidates, rawQuery);
      if (ranked.length > 0) return ranked;
      return await runFallbackScan();
    } catch (error) {
      if (!String(error.message || "").includes("HTTP 501")) {
        throw error;
      }
      return await runFallbackScan();
    }
  }
};
var CalDAV = {
  _isLikelyReadOnlyCalendar(calendar) {
    const name = String(calendar?.displayname || "").toLowerCase();
    if (calendar?.readOnly === true) return true;
    return name.includes("birthday") || name.includes("birthdays") || name.includes("holidays") || name.includes("read only") || name.includes("readonly");
  },
  async findCalendars(componentType = null) {
    const endpoint = `/remote.php/dav/calendars/${CONFIG.user}/`;
    const response = await request(endpoint, {
      method: "PROPFIND",
      headers: { "Depth": "1" }
    });
    if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) return [];
    const responses = ensureArray(response["d:multistatus"]["d:response"]);
    return responses.map((r) => {
      const propstats = ensureArray(r["d:propstat"]);
      if (!propstats[0] || !propstats[0]["d:prop"]) return null;
      const props = propstats[0]["d:prop"];
      if (!props["d:resourcetype"] || !("cal:calendar" in props["d:resourcetype"])) return null;
      let compType = null;
      let compTypes = [];
      const compSet = props["cal:supported-calendar-component-set"];
      if (compSet && compSet["cal:comp"]) {
        compTypes = ensureArray(compSet["cal:comp"]).map((comp) => comp?.["@_name"]).filter(Boolean);
        compType = compTypes[0] || null;
      }
      return {
        url: r["d:href"],
        displayname: props["d:displayname"],
        componentType: compType,
        componentTypes: compTypes,
        readOnly: props["oc:read-only"] === "1" || props["oc:read-only"] === 1 || props["oc:read-only"] === true
      };
    }).filter((c) => c && (!componentType || c.componentTypes.includes(componentType)));
  },
  async getEvents(start, end) {
    const calendars = await this.findCalendars("VEVENT");
    const allEvents = [];
    const toCalDavDate = (dateStr) => {
      const d = new Date(dateStr);
      return d.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
    };
    const startStr = toCalDavDate(start);
    const endStr = toCalDavDate(end);
    const body = `
            <c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
                <d:prop>
                    <d:getetag />
                    <c:calendar-data />
                </d:prop>
                <c:filter>
                    <c:comp-filter name="VCALENDAR">
                        <c:comp-filter name="VEVENT">
                            <c:time-range start="${startStr}" end="${endStr}" />
                        </c:comp-filter>
                    </c:comp-filter>
                </c:filter>
            </c:calendar-query>
        `;
    for (const cal of calendars) {
      try {
        const response = await request(cal.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        for (const r of responses) {
          const propstats = ensureArray(r["d:propstat"]);
          if (!propstats[0] || !propstats[0]["d:prop"]) continue;
          const calData = propstats[0]["d:prop"]["cal:calendar-data"];
          const uidMatch = calData.match(/UID:(.*)/);
          const summaryMatch = calData.match(/SUMMARY:(.*)/);
          const dtstartMatch = calData.match(/DTSTART(?:;.*)?:(.*)/);
          const dtendMatch = calData.match(/DTEND(?:;.*)?:(.*)/);
          const locationMatch = calData.match(/LOCATION(?:;.*)?:(.*)/);
          const descriptionMatch = calData.match(/DESCRIPTION(?:;.*)?:(.*)/);
          allEvents.push({
            uid: uidMatch ? uidMatch[1].trim() : "No UID",
            calendar: cal.displayname,
            summary: summaryMatch ? decodeICalText(summaryMatch[1]) : "No Title",
            start: dtstartMatch ? dtstartMatch[1].trim() : "Unknown",
            end: dtendMatch ? dtendMatch[1].trim() : null,
            location: locationMatch ? decodeICalText(locationMatch[1]) : null,
            description: descriptionMatch ? decodeICalText(descriptionMatch[1]) : null
          });
        }
      } catch (e) {
      }
    }
    return allEvents;
  },
  async getTodos(calendarName = null) {
    let calendars = await this.findCalendars("VTODO");
    if (calendarName) {
      calendars = calendars.filter((c) => c.displayname === calendarName);
      if (calendars.length === 0) {
        throw new Error(`Task-enabled calendar '${calendarName}' not found.`);
      }
    }
    const allTodos = [];
    const body = `
            <c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
                <d:prop>
                    <d:getetag />
                    <c:calendar-data />
                    <c:uid />
                </d:prop>
                <c:filter>
                    <c:comp-filter name="VCALENDAR">
                        <c:comp-filter name="VTODO">
                            <c:prop-filter name="STATUS">
                                <c:text-match negate-condition="yes">COMPLETED</c:text-match>
                            </c:prop-filter>
                        </c:comp-filter>
                    </c:comp-filter>
                </c:filter>
            </c:calendar-query>
        `;
    for (const cal of calendars) {
      try {
        const response = await request(cal.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        for (const r of responses) {
          const propstats = ensureArray(r["d:propstat"]);
          if (!propstats[0] || !propstats[0]["d:prop"]) {
            continue;
          }
          const calData = propstats[0]["d:prop"]["cal:calendar-data"];
          const summaryMatch = calData.match(/SUMMARY:(.*)/);
          const statusMatch = calData.match(/STATUS:(.*)/);
          const uidMatch = calData.match(/UID:(.*)/);
          const dueMatch = calData.match(/DUE(?:;.*)?:(.*)/);
          const priorityMatch = calData.match(/PRIORITY:(.*)/);
          const descriptionMatch = calData.match(/DESCRIPTION(?:;.*)?:(.*)/);
          allTodos.push({
            uid: uidMatch ? uidMatch[1].trim() : "No UID",
            calendar: cal.displayname,
            summary: summaryMatch ? decodeICalText(summaryMatch[1]) : "No Title",
            status: statusMatch ? statusMatch[1].trim() : "NEEDS-ACTION",
            due: dueMatch ? dueMatch[1].trim() : null,
            priority: priorityMatch ? parseInt(priorityMatch[1].trim(), 10) : null,
            description: descriptionMatch ? decodeICalText(descriptionMatch[1]) : null
          });
        }
      } catch (e) {
      }
    }
    return allTodos;
  },
  async getCalendar(calendarName, componentType = null) {
    const calendars = await this.findCalendars(componentType);
    let targetCal = null;
    if (calendarName) {
      targetCal = calendars.find((c) => c.displayname === calendarName);
    } else if (calendars.length > 0) {
      targetCal = calendars.find((c) => !this._isLikelyReadOnlyCalendar(c)) || calendars[0];
    }
    if (!targetCal) {
      const typeDesc = componentType === "VTODO" ? "task-enabled " : componentType === "VEVENT" ? "event-enabled " : "";
      throw new Error(calendarName ? `${typeDesc}Calendar '${calendarName}' not found.` : `No ${typeDesc}calendars found.`);
    }
    return targetCal;
  },
  async findTaskPath(uid, calendarName) {
    const calendars = await this.findCalendars("VTODO");
    let searchTargets = calendars;
    if (calendarName) {
      const found = calendars.find((c) => c.displayname === calendarName);
      if (found) searchTargets = [found];
      else throw new Error(`Task-enabled calendar '${calendarName}' not found.`);
    }
    const escapedUid = escapeXml(ensureNonEmptyString(uid, "Task UID"));
    const body = `
            <c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
                <d:prop>
                    <d:getetag />
                    <c:calendar-data />
                </d:prop>
                <c:filter>
                    <c:comp-filter name="VCALENDAR">
                        <c:comp-filter name="VTODO">
                             <c:prop-filter name="UID">
                                <c:text-match collation="i;octet">${escapedUid}</c:text-match>
                             </c:prop-filter>
                        </c:comp-filter>
                    </c:comp-filter>
                </c:filter>
            </c:calendar-query>
        `;
    for (const cal of searchTargets) {
      try {
        const response = await request(cal.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        if (responses.length > 0) {
          const propstats = ensureArray(responses[0]["d:propstat"]);
          return {
            href: responses[0]["d:href"],
            etag: propstats[0]["d:prop"]["d:getetag"],
            data: propstats[0]["d:prop"]["cal:calendar-data"],
            calendarUrl: cal.url
          };
        }
      } catch (e) {
      }
    }
    return null;
  },
  _updateProperty(vcal, prop, value) {
    const regex = new RegExp(`^${prop}(?:;[^:]*)?:.*$`, "m");
    if (value === null || value === void 0 || value === "") {
      return vcal;
    }
    const newLine = `${prop}:${value}`;
    let updated = vcal;
    if (regex.test(vcal)) {
      updated = vcal.replace(regex, newLine);
    } else if (vcal.includes("END:VTODO")) {
      updated = vcal.replace("END:VTODO", `${newLine}\nEND:VTODO`);
    } else if (vcal.includes("END:VEVENT")) {
      updated = vcal.replace("END:VEVENT", `${newLine}\nEND:VEVENT`);
    } else {
      updated = `${vcal}\n${newLine}`;
    }
    return normalizeICalLineEndings(updated);
  },
  _upsertDateProperty(vcal, prop, dateValue) {
    const regex = new RegExp(`^${prop}(?:;[^:]*)?:.*$`, "m");
    const newLine = `${prop};VALUE=DATE:${dateValue}`;
    let updated = vcal;
    if (regex.test(vcal)) {
      updated = vcal.replace(regex, newLine);
    } else if (vcal.includes("END:VEVENT")) {
      updated = vcal.replace("END:VEVENT", `${newLine}\nEND:VEVENT`);
    } else if (vcal.includes("END:VTODO")) {
      updated = vcal.replace("END:VTODO", `${newLine}\nEND:VTODO`);
    } else {
      updated = `${vcal}\n${newLine}`;
    }
    return normalizeICalLineEndings(updated);
  },
  async createTask(title, calendarName, dueDate, priority, description, timeZone = null) {
    const cal = await this.getCalendar(calendarName, "VTODO");
    const uid = crypto.randomUUID();
    const now = /* @__PURE__ */ new Date();
    const dtstamp = (0, import_date_fns.format)(now, "yyyyMMdd'T'HHmmss'Z'");
    const safeTitle = encodeICalText(ensureNonEmptyString(title, "Task title"));
    let vtodo = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OpenClaw//Nextcloud Skill//EN
BEGIN:VTODO
UID:${uid}
DTSTAMP:${dtstamp}
SUMMARY:${safeTitle}
STATUS:NEEDS-ACTION
`;
    if (dueDate) {
      vtodo += `DUE:${toCalDavDateTime(dueDate, "Task due date", timeZone)}
`;
    }
    if (priority !== null && priority !== void 0 && String(priority).trim() !== "") {
      const parsedPriority = Number.parseInt(String(priority), 10);
      if (Number.isNaN(parsedPriority) || parsedPriority < 0 || parsedPriority > 9) {
        throw new Error("Task priority must be an integer between 0 and 9.");
      }
      vtodo += `PRIORITY:${parsedPriority}
`;
    }
    if (description !== null && description !== void 0 && String(description).trim() !== "") vtodo += `DESCRIPTION:${encodeICalText(description)}
`;
    vtodo += `END:VTODO
END:VCALENDAR`;
    const filename = `${uid}.ics`;
    const urlWithSlash = cal.url.endsWith("/") ? cal.url : cal.url + "/";
    const endpoint = `${urlWithSlash}${filename}`;
    await request(endpoint, {
      method: "PUT",
      headers: {
        "Content-Type": "text/calendar; charset=utf-8",
        "If-None-Match": "*"
      },
      body: vtodo
    });
    return { uid, status: "created", calendar: cal.displayname };
  },
  async updateTask(uid, calendarName, updates) {
    const task = await this.findTaskPath(uid, calendarName);
    if (!task) throw new Error(`Task ${uid} not found.`);
    let vtodo = task.data;
    if (updates.title !== void 0) vtodo = this._updateProperty(vtodo, "SUMMARY", encodeICalText(ensureNonEmptyString(updates.title, "Task title")));
    if (updates.priority !== void 0) {
      const parsedPriority = Number.parseInt(String(updates.priority), 10);
      if (Number.isNaN(parsedPriority) || parsedPriority < 0 || parsedPriority > 9) {
        throw new Error("Task priority must be an integer between 0 and 9.");
      }
      vtodo = this._updateProperty(vtodo, "PRIORITY", String(parsedPriority));
    }
    if (updates.description !== void 0) vtodo = this._updateProperty(vtodo, "DESCRIPTION", encodeICalText(updates.description));
    if (updates.dueDate !== void 0) {
      vtodo = this._updateProperty(vtodo, "DUE", toCalDavDateTime(updates.dueDate, "Task due date", updates.timeZone));
    }
    await request(task.href, {
      method: "PUT",
      headers: {
        "Content-Type": "text/calendar; charset=utf-8",
        "If-Match": task.etag
      },
      body: vtodo
    });
    return { uid, status: "updated" };
  },
  async deleteTask(uid, calendarName) {
    const task = await this.findTaskPath(uid, calendarName);
    if (!task) throw new Error(`Task ${uid} not found.`);
    await request(task.href, {
      method: "DELETE"
    });
    return { uid, status: "deleted" };
  },
  async completeTask(uid, calendarName) {
    const task = await this.findTaskPath(uid, calendarName);
    if (!task) throw new Error(`Task ${uid} not found.`);
    let vtodo = task.data;
    const now = /* @__PURE__ */ new Date();
    const completedDate = (0, import_date_fns.format)(now, "yyyyMMdd'T'HHmmss'Z'");
    vtodo = this._updateProperty(vtodo, "STATUS", "COMPLETED");
    vtodo = this._updateProperty(vtodo, "COMPLETED", completedDate);
    vtodo = this._updateProperty(vtodo, "PERCENT-COMPLETE", "100");
    await request(task.href, {
      method: "PUT",
      headers: {
        "Content-Type": "text/calendar; charset=utf-8",
        "If-Match": task.etag
      },
      body: vtodo
    });
    return { uid, status: "completed" };
  },
  // --- Calendar Events ---
  async createEvent(summary, start, end, calendarName, description, timeZone = null, allDay = false) {
    if (!allDay && isAllDayLikeTimedRange(start, end)) {
      throw new Error("Detected all-day-like timed range (00:00-23:59 or 00:00-next midnight). Use --all-day with date values to avoid timezone and DST drift.");
    }
    const cal = await this.getCalendar(calendarName, "VEVENT");
    const uid = crypto.randomUUID();
    const now = /* @__PURE__ */ new Date();
    const dtstamp = (0, import_date_fns.format)(now, "yyyyMMdd'T'HHmmss'Z'");
    let startLine = "";
    let endLine = "";
    if (allDay) {
      const startDateValue = toCalDavDate(start, "Event start", timeZone);
      const endInput = end !== void 0 && end !== null ? end : start;
      const endDateValue = toCalDavDate(endInput, "Event end", timeZone);
      let exclusiveEnd = "";
      if (compareCalDate(endDateValue, startDateValue) < 0) {
        exclusiveEnd = addOneDayCalDate(startDateValue);
      } else if (compareCalDate(endDateValue, startDateValue) === 0) {
        // Inclusive single-day input (start=end) -> convert to exclusive next day.
        exclusiveEnd = addOneDayCalDate(startDateValue);
      } else if (endDateValue === addOneDayCalDate(startDateValue)) {
        // Autofix: treat next-day end as already-exclusive single-day encoding.
        exclusiveEnd = endDateValue;
      } else {
        // Multi-day inclusive input -> convert to exclusive end by adding one day.
        exclusiveEnd = addOneDayCalDate(endDateValue);
      }
      startLine = `DTSTART;VALUE=DATE:${startDateValue}`;
      endLine = `DTEND;VALUE=DATE:${exclusiveEnd}`;
    } else {
      const startDate = parseDateTimeInput(start, "Event start", timeZone);
      const endDate = parseDateTimeInput(end, "Event end", timeZone);
      const startValue = startDate.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
      const endValue = endDate.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
      if (startDate.getTime() >= endDate.getTime()) {
        throw new Error("Event end must be after event start.");
      }
      startLine = `DTSTART:${startValue}`;
      endLine = `DTEND:${endValue}`;
    }
    let vevent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OpenClaw//Nextcloud Skill//EN
BEGIN:VEVENT
UID:${uid}
DTSTAMP:${dtstamp}
SUMMARY:${encodeICalText(ensureNonEmptyString(summary, "Event summary"))}
${startLine}
${endLine}
`;
    if (description !== null && description !== void 0 && String(description).trim() !== "") vevent += `DESCRIPTION:${encodeICalText(description)}
`;
    vevent += `END:VEVENT
END:VCALENDAR`;
    const filename = `${uid}.ics`;
    const urlWithSlash = cal.url.endsWith("/") ? cal.url : cal.url + "/";
    const endpoint = `${urlWithSlash}${filename}`;
    try {
      await request(endpoint, {
        method: "PUT",
        headers: {
          "Content-Type": "text/calendar; charset=utf-8",
          "If-None-Match": "*"
        },
        body: vevent
      });
    } catch (error) {
      if (String(error.message || "").includes("HTTP 403")) {
        throw new Error(`Calendar '${cal.displayname}' appears to be read-only or lacks write permissions.`);
      }
      throw error;
    }
    return { uid, status: "created", calendar: cal.displayname };
  },
  async findEventPath(uid, calendarName) {
    const calendars = await this.findCalendars("VEVENT");
    let searchTargets = calendars;
    if (calendarName) {
      const found = calendars.find((c) => c.displayname === calendarName);
      if (found) searchTargets = [found];
      else throw new Error(`Event-enabled calendar '${calendarName}' not found.`);
    }
    const escapedUid = escapeXml(ensureNonEmptyString(uid, "Event UID"));
    const body = `
            <c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
                <d:prop>
                    <d:getetag />
                    <c:calendar-data />
                </d:prop>
                <c:filter>
                    <c:comp-filter name="VCALENDAR">
                        <c:comp-filter name="VEVENT">
                            <c:prop-filter name="UID">
                                <c:text-match collation="i;octet">${escapedUid}</c:text-match>
                            </c:prop-filter>
                        </c:comp-filter>
                    </c:comp-filter>
                </c:filter>
            </c:calendar-query>
        `;
    for (const cal of searchTargets) {
      try {
        const response = await request(cal.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        if (responses.length > 0) {
          const propstats = ensureArray(responses[0]["d:propstat"]);
          return {
            href: responses[0]["d:href"],
            etag: propstats[0]["d:prop"]["d:getetag"],
            data: propstats[0]["d:prop"]["cal:calendar-data"],
            calendarUrl: cal.url
          };
        }
      } catch (e) {
      }
    }
    return null;
  },
  async updateEvent(uid, calendarName, updates) {
    const event = await this.findEventPath(uid, calendarName);
    if (!event) throw new Error(`Event ${uid} not found.`);
    let vevent = event.data;
    if (updates.summary !== void 0) vevent = this._updateProperty(vevent, "SUMMARY", encodeICalText(ensureNonEmptyString(updates.summary, "Event summary")));
    const allDay = updates.allDay === true || updates.allDay === "true";
    if (!allDay && updates.start !== void 0 && updates.end !== void 0 && isAllDayLikeTimedRange(updates.start, updates.end)) {
      throw new Error("Detected all-day-like timed range in update. Use --all-day with date values to avoid timezone and DST drift.");
    }
    if (allDay && updates.start !== void 0) {
      const startDateValue = toCalDavDate(updates.start, "Event start", updates.timeZone);
      const endSource = updates.end !== void 0 ? updates.end : updates.start;
      const endDateValue = toCalDavDate(endSource, "Event end", updates.timeZone);
      let exclusiveEnd = "";
      if (compareCalDate(endDateValue, startDateValue) < 0) {
        exclusiveEnd = addOneDayCalDate(startDateValue);
      } else if (compareCalDate(endDateValue, startDateValue) === 0) {
        exclusiveEnd = addOneDayCalDate(startDateValue);
      } else if (endDateValue === addOneDayCalDate(startDateValue)) {
        exclusiveEnd = endDateValue;
      } else {
        exclusiveEnd = addOneDayCalDate(endDateValue);
      }
      vevent = this._upsertDateProperty(vevent, "DTSTART", startDateValue);
      vevent = this._upsertDateProperty(vevent, "DTEND", exclusiveEnd);
    } else if (updates.start !== void 0) {
      vevent = this._updateProperty(vevent, "DTSTART", toCalDavDateTime(updates.start, "Event start", updates.timeZone));
    }
    if (!allDay && updates.end !== void 0) {
      vevent = this._updateProperty(vevent, "DTEND", toCalDavDateTime(updates.end, "Event end", updates.timeZone));
    }
    if (updates.description !== void 0) {
      vevent = this._updateProperty(vevent, "DESCRIPTION", encodeICalText(updates.description));
    }
    await request(event.href, {
      method: "PUT",
      headers: {
        "Content-Type": "text/calendar; charset=utf-8",
        "If-Match": event.etag
      },
      body: vevent
    });
    return { uid, status: "updated" };
  },
  async deleteEvent(uid, calendarName) {
    const event = await this.findEventPath(uid, calendarName);
    if (!event) throw new Error(`Event ${uid} not found.`);
    await request(event.href, {
      method: "DELETE"
    });
    return { uid, status: "deleted" };
  }
};
function escapeXml(value) {
  return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}
function splitUnescaped(value, delimiter) {
  const result = [];
  let current = "";
  let escaped = false;
  for (const char of String(value ?? "")) {
    if (escaped) {
      current += char;
      escaped = false;
      continue;
    }
    if (char === "\\") {
      current += char;
      escaped = true;
      continue;
    }
    if (char === delimiter) {
      result.push(current);
      current = "";
      continue;
    }
    current += char;
  }
  result.push(current);
  return result;
}
function decodeVCardText(value) {
  return String(value ?? "").replace(/&#13;?/gi, "").replace(/&#x0d;?/gi, "").replace(/\r/g, "").replace(/\\n/gi, "\n").replace(/\\,/g, ",").replace(/\\;/g, ";").replace(/\\\\/g, "\\");
}
function encodeVCardText(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/;/g, "\\;").replace(/,/g, "\\,");
}
function unfoldVCard(vcard) {
  return String(vcard ?? "").replace(/&#13;?/gi, "").replace(/&#x0d;?/gi, "").replace(/\r\n[ \t]/g, "").replace(/\n[ \t]/g, "");
}
function splitVCardLines(vcard) {
  return unfoldVCard(vcard).split(/\r?\n/).map((line) => line.trimEnd()).filter((line) => line.length > 0);
}
function parseVCardLine(line) {
  const value = String(line ?? "");
  let colonIndex = -1;
  let escaped = false;
  for (let i = 0; i < value.length; i++) {
    const char = value[i];
    if (escaped) {
      escaped = false;
      continue;
    }
    if (char === "\\") {
      escaped = true;
      continue;
    }
    if (char === ":") {
      colonIndex = i;
      break;
    }
  }
  if (colonIndex === -1) return null;
  const left = value.slice(0, colonIndex);
  const right = value.slice(colonIndex + 1);
  const leftParts = splitUnescaped(left, ";");
  const firstPart = leftParts.shift() || "";
  const groupAndName = firstPart.split(".");
  const name = (groupAndName[groupAndName.length - 1] || "").toUpperCase();
  return {
    raw: value,
    name,
    params: leftParts,
    valueRaw: right,
    value: decodeVCardText(right)
  };
}
function parseStructuredName(rawValue) {
  const components = splitUnescaped(rawValue ?? "", ";");
  while (components.length < 5) components.push("");
  return {
    familyName: decodeVCardText(components[0] || ""),
    givenName: decodeVCardText(components[1] || ""),
    additionalNames: decodeVCardText(components[2] || ""),
    honorificPrefixes: decodeVCardText(components[3] || ""),
    honorificSuffixes: decodeVCardText(components[4] || "")
  };
}
function deriveStructuredNameFromFullName(fullName) {
  const cleaned = String(fullName ?? "").trim();
  if (!cleaned) {
    return {
      familyName: "",
      givenName: "",
      additionalNames: "",
      honorificPrefixes: "",
      honorificSuffixes: ""
    };
  }
  const parts = cleaned.split(/\s+/).filter(Boolean);
  if (parts.length === 1) {
    return {
      familyName: "",
      givenName: parts[0],
      additionalNames: "",
      honorificPrefixes: "",
      honorificSuffixes: ""
    };
  }
  const familyName = parts[parts.length - 1];
  const givenName = parts.slice(0, -1).join(" ");
  return {
    familyName,
    givenName,
    additionalNames: "",
    honorificPrefixes: "",
    honorificSuffixes: ""
  };
}
function buildStructuredNameValue(nameParts) {
  return [
    encodeVCardText(nameParts.familyName || ""),
    encodeVCardText(nameParts.givenName || ""),
    encodeVCardText(nameParts.additionalNames || ""),
    encodeVCardText(nameParts.honorificPrefixes || ""),
    encodeVCardText(nameParts.honorificSuffixes || "")
  ].join(";");
}
function buildDisplayName(nameParts, fallback = "") {
  const pieces = [
    nameParts.honorificPrefixes || "",
    nameParts.givenName || "",
    nameParts.additionalNames || "",
    nameParts.familyName || "",
    nameParts.honorificSuffixes || ""
  ].map((piece) => String(piece).trim()).filter(Boolean);
  if (pieces.length > 0) return pieces.join(" ");
  return String(fallback || "").trim();
}
function normalizeVCardLineEndings(vcard) {
  return String(vcard ?? "").replace(/\r?\n/g, "\r\n");
}
function upsertSingleVCardProperty(vcard, propertyName, propertyLine) {
  const targetName = String(propertyName).toUpperCase();
  const lines = splitVCardLines(vcard);
  let hasBegin = false;
  let hasVersion = false;
  const kept = [];
  for (const line of lines) {
    const normalized = line.toUpperCase();
    if (normalized === "BEGIN:VCARD") {
      hasBegin = true;
      kept.push("BEGIN:VCARD");
      continue;
    }
    if (normalized.startsWith("VERSION:")) {
      hasVersion = true;
      kept.push(line);
      continue;
    }
    if (normalized === "END:VCARD") {
      continue;
    }
    const parsed = parseVCardLine(line);
    if (parsed && parsed.name === targetName) {
      continue;
    }
    kept.push(line);
  }
  if (!hasBegin) kept.unshift("BEGIN:VCARD");
  if (!hasVersion) kept.splice(1, 0, "VERSION:3.0");
  if (propertyLine) kept.push(propertyLine);
  kept.push("END:VCARD");
  return normalizeVCardLineEndings(kept.join("\n"));
}
function replaceVCardPropertyList(vcard, propertyName, propertyLines) {
  const targetName = String(propertyName).toUpperCase();
  const lines = splitVCardLines(vcard);
  let hasBegin = false;
  let hasVersion = false;
  const kept = [];
  for (const line of lines) {
    const normalized = line.toUpperCase();
    if (normalized === "BEGIN:VCARD") {
      hasBegin = true;
      kept.push("BEGIN:VCARD");
      continue;
    }
    if (normalized.startsWith("VERSION:")) {
      hasVersion = true;
      kept.push(line);
      continue;
    }
    if (normalized === "END:VCARD") continue;
    const parsed = parseVCardLine(line);
    if (parsed && parsed.name === targetName) continue;
    kept.push(line);
  }
  if (!hasBegin) kept.unshift("BEGIN:VCARD");
  if (!hasVersion) kept.splice(1, 0, "VERSION:3.0");
  for (const line of ensureArray(propertyLines)) {
    if (line) kept.push(line);
  }
  kept.push("END:VCARD");
  return normalizeVCardLineEndings(kept.join("\n"));
}
function readPropertyValues(vcard, propertyName) {
  const target = String(propertyName).toUpperCase();
  const values = [];
  for (const line of splitVCardLines(vcard)) {
    const parsed = parseVCardLine(line);
    if (!parsed || parsed.name !== target) continue;
    values.push(parsed);
  }
  return values;
}
function normalizeBirthdayForStorage(input) {
  const raw = String(input ?? "").trim();
  if (!raw) throw new Error("Birthday cannot be empty.");
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    const compact = raw.replace(/-/g, "");
    const year = Number(compact.slice(0, 4));
    const month = Number(compact.slice(4, 6));
    const day = Number(compact.slice(6, 8));
    const d = new Date(Date.UTC(year, month - 1, day));
    if (d.getUTCFullYear() !== year || d.getUTCMonth() !== month - 1 || d.getUTCDate() !== day) {
      throw new Error("Birthday date is invalid.");
    }
    return compact;
  }
  if (/^\d{8}$/.test(raw)) {
    const year = Number(raw.slice(0, 4));
    const month = Number(raw.slice(4, 6));
    const day = Number(raw.slice(6, 8));
    const d = new Date(Date.UTC(year, month - 1, day));
    if (d.getUTCFullYear() !== year || d.getUTCMonth() !== month - 1 || d.getUTCDate() !== day) {
      throw new Error("Birthday date is invalid.");
    }
    return raw;
  }
  if (/^--\d{2}-\d{2}$/.test(raw)) {
    return `--${raw.slice(2, 4)}${raw.slice(5, 7)}`;
  }
  if (/^--\d{4}$/.test(raw)) {
    return raw;
  }
  throw new Error("Birthday must be YYYY-MM-DD, YYYYMMDD, --MM-DD, or --MMDD.");
}
function normalizeBirthdayForOutput(value) {
  const raw = String(value ?? "").trim();
  if (/^\d{8}$/.test(raw)) {
    return `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`;
  }
  if (/^--\d{4}$/.test(raw)) {
    return `--${raw.slice(2, 4)}-${raw.slice(4, 6)}`;
  }
  return raw || null;
}
function parseMultiValueInput(value) {
  if (value === void 0 || value === null) return [];
  if (Array.isArray(value)) {
    return value.map((v) => String(v).trim()).filter(Boolean);
  }
  return String(value).split(",").map((v) => v.trim()).filter(Boolean);
}
var Contacts = {
  async findAddressBooks() {
    const endpoint = `/remote.php/dav/addressbooks/users/${CONFIG.user}/`;
    const response = await request(endpoint, {
      method: "PROPFIND",
      headers: { "Depth": "1" }
    });
    if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) return [];
    const responses = ensureArray(response["d:multistatus"]["d:response"]);
    return responses.map((r) => {
      const propstats = ensureArray(r["d:propstat"]);
      if (!propstats[0] || !propstats[0]["d:prop"]) return null;
      const props = propstats[0]["d:prop"];
      if (!props["d:resourcetype"] || !("card:addressbook" in props["d:resourcetype"])) return null;
      let name = props["d:displayname"];
      if (!name) {
        const urlParts = r["d:href"].split("/").filter((p) => p);
        name = urlParts[urlParts.length - 1] || "Unnamed";
      }
      return {
        url: r["d:href"],
        displayname: name
      };
    }).filter((a) => a);
  },
  async getAddressBook(addressBookName) {
    const addressBooks = await this.findAddressBooks();
    let target = null;
    if (addressBookName) {
      target = addressBooks.find((a) => a.displayname === addressBookName);
    } else if (addressBooks.length > 0) {
      target = addressBooks[0];
    }
    if (!target) {
      throw new Error(addressBookName ? `Address book '${addressBookName}' not found.` : "No address books found.");
    }
    return target;
  },
  _buildAddressBookQueryBody(filterXml = "") {
    return `
            <card:addressbook-query xmlns:d="DAV:" xmlns:card="urn:ietf:params:xml:ns:carddav">
                <d:prop>
                    <d:getetag />
                    <card:address-data content-type="text/vcard" version="3.0" />
                </d:prop>
                ${filterXml}
            </card:addressbook-query>
        `;
  },
  _buildCardPropertyLine(name, value, params = []) {
    const safeName = String(name || "").toUpperCase();
    const safeParams = ensureArray(params).filter(Boolean).join(";");
    return `${safeName}${safeParams ? `;${safeParams}` : ""}:${value}`;
  },
  _applyNameUpdates(existingName, updates) {
    const next = {
      familyName: updates.familyName !== void 0 ? updates.familyName : existingName.familyName,
      givenName: updates.givenName !== void 0 ? updates.givenName : existingName.givenName,
      additionalNames: updates.additionalNames !== void 0 ? updates.additionalNames : existingName.additionalNames,
      honorificPrefixes: updates.honorificPrefixes !== void 0 ? updates.honorificPrefixes : existingName.honorificPrefixes,
      honorificSuffixes: updates.honorificSuffixes !== void 0 ? updates.honorificSuffixes : existingName.honorificSuffixes
    };
    return {
      familyName: String(next.familyName || "").trim(),
      givenName: String(next.givenName || "").trim(),
      additionalNames: String(next.additionalNames || "").trim(),
      honorificPrefixes: String(next.honorificPrefixes || "").trim(),
      honorificSuffixes: String(next.honorificSuffixes || "").trim()
    };
  },
  _extractNameFromVCard(vcard) {
    const nProps = readPropertyValues(vcard, "N");
    if (nProps.length > 0) return parseStructuredName(nProps[0].valueRaw);
    const fnProps = readPropertyValues(vcard, "FN");
    if (fnProps.length > 0) return deriveStructuredNameFromFullName(fnProps[0].value);
    return deriveStructuredNameFromFullName("");
  },
  async list(addressBookName = null) {
    let addressBooks = await this.findAddressBooks();
    if (addressBookName) {
      addressBooks = addressBooks.filter((a) => a.displayname === addressBookName);
      if (addressBooks.length === 0) {
        throw new Error(`Address book '${addressBookName}' not found.`);
      }
    }
    const allContacts = [];
    const body = this._buildAddressBookQueryBody();
    for (const ab of addressBooks) {
      try {
        const response = await request(ab.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        for (const r of responses) {
          const propstats = ensureArray(r["d:propstat"]);
          if (!propstats[0] || !propstats[0]["d:prop"]) continue;
          const cardData = propstats[0]["d:prop"]["card:address-data"];
          if (!cardData) continue;
          const contact = this._parseVCard(cardData);
          contact.addressBook = ab.displayname;
          contact.href = r["d:href"];
          allContacts.push(contact);
        }
      } catch (e) {
      }
    }
    return allContacts;
  },
  _parseVCard(vcard) {
    const uidProp = readPropertyValues(vcard, "UID")[0] || null;
    const fnProp = readPropertyValues(vcard, "FN")[0] || null;
    const nProp = readPropertyValues(vcard, "N")[0] || null;
    const nameParts = nProp ? parseStructuredName(nProp.valueRaw) : deriveStructuredNameFromFullName(fnProp ? fnProp.value : "");
    const fullName = fnProp ? fnProp.value : buildDisplayName(nameParts, "");
    const phones = readPropertyValues(vcard, "TEL").map((item) => item.value).filter(Boolean);
    const emails = readPropertyValues(vcard, "EMAIL").map((item) => item.value).filter(Boolean);
    const orgProp = readPropertyValues(vcard, "ORG")[0] || null;
    const titleProp = readPropertyValues(vcard, "TITLE")[0] || null;
    const noteProp = readPropertyValues(vcard, "NOTE")[0] || null;
    const bdayProp = readPropertyValues(vcard, "BDAY")[0] || null;
    return {
      uid: uidProp ? uidProp.value : null,
      fullName: fullName || null,
      structuredName: {
        familyName: nameParts.familyName || null,
        givenName: nameParts.givenName || null,
        additionalNames: nameParts.additionalNames || null,
        honorificPrefixes: nameParts.honorificPrefixes || null,
        honorificSuffixes: nameParts.honorificSuffixes || null
      },
      nameRaw: nProp ? decodeVCardText(nProp.valueRaw) : null,
      phones: phones.length > 0 ? phones : null,
      emails: emails.length > 0 ? emails : null,
      organization: orgProp ? orgProp.value : null,
      title: titleProp ? titleProp.value : null,
      note: noteProp ? noteProp.value : null,
      birthday: bdayProp ? normalizeBirthdayForOutput(bdayProp.valueRaw) : null,
      birthdayRaw: bdayProp ? bdayProp.valueRaw : null
    };
  },
  async get(uid, addressBookName = null) {
    const contacts = await this.list(addressBookName);
    const contact = contacts.find((c) => c.uid === uid);
    if (!contact) {
      throw new Error(`Contact with UID '${uid}' not found.`);
    }
    return contact;
  },
  async findContactPath(uid, addressBookName = null) {
    let addressBooks = await this.findAddressBooks();
    if (addressBookName) {
      const found = addressBooks.find((a) => a.displayname === addressBookName);
      if (found) addressBooks = [found];
      else throw new Error(`Address book '${addressBookName}' not found.`);
    }
    const escapedUid = escapeXml(uid);
    const body = this._buildAddressBookQueryBody(`
                <card:filter>
                    <card:prop-filter name="UID">
                        <card:text-match collation="i;octet">${escapedUid}</card:text-match>
                    </card:prop-filter>
                </card:filter>
        `);
    for (const ab of addressBooks) {
      try {
        const response = await request(ab.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        for (const r of responses) {
          const propstats = ensureArray(r["d:propstat"]);
          if (!propstats[0] || !propstats[0]["d:prop"]) continue;
          const props = propstats[0]["d:prop"];
          const href = r["d:href"];
          const etag = props["d:getetag"];
          const data = props["card:address-data"];
          if (!href || !etag || !data) continue;
          return {
            href,
            etag,
            data,
            addressBookUrl: ab.url
          };
        }
      } catch (e) {
      }
    }
    return null;
  },
  async create(fullName, addressBookName, options = {}) {
    const ab = await this.getAddressBook(addressBookName);
    const uid = crypto.randomUUID();
    const namePartsFromInput = {
      familyName: options.familyName,
      givenName: options.givenName,
      additionalNames: options.additionalNames,
      honorificPrefixes: options.honorificPrefixes,
      honorificSuffixes: options.honorificSuffixes
    };
    const hasStructuredName = Object.values(namePartsFromInput).some((value) => value !== void 0);
    const structuredName = hasStructuredName ? this._applyNameUpdates(deriveStructuredNameFromFullName(fullName), namePartsFromInput) : deriveStructuredNameFromFullName(fullName);
    const resolvedFullName = String(fullName || "").trim() || buildDisplayName(structuredName, "");
    if (!resolvedFullName) {
      throw new Error("Contact name is required. Provide --name or structured name fields.");
    }
    const lines = [
      "BEGIN:VCARD",
      "VERSION:3.0",
      this._buildCardPropertyLine("UID", uid),
      this._buildCardPropertyLine("FN", encodeVCardText(resolvedFullName)),
      this._buildCardPropertyLine("N", buildStructuredNameValue(structuredName))
    ];
    const emails = parseMultiValueInput(options.emails ?? options.email);
    const phones = parseMultiValueInput(options.phones ?? options.phone);
    for (const email of emails) {
      lines.push(this._buildCardPropertyLine("EMAIL", encodeVCardText(email), ["TYPE=INTERNET"]));
    }
    for (const phone of phones) {
      lines.push(this._buildCardPropertyLine("TEL", encodeVCardText(phone), ["TYPE=CELL"]));
    }
    if (options.organization) lines.push(this._buildCardPropertyLine("ORG", encodeVCardText(options.organization)));
    if (options.title) lines.push(this._buildCardPropertyLine("TITLE", encodeVCardText(options.title)));
    if (options.note) lines.push(this._buildCardPropertyLine("NOTE", encodeVCardText(options.note)));
    if (options.birthday) lines.push(this._buildCardPropertyLine("BDAY", normalizeBirthdayForStorage(options.birthday)));
    lines.push("END:VCARD");
    let vcard = normalizeVCardLineEndings(lines.join("\n"));
    const filename = `${uid}.vcf`;
    const urlWithSlash = ab.url.endsWith("/") ? ab.url : ab.url + "/";
    const endpoint = `${urlWithSlash}${filename}`;
    await request(endpoint, {
      method: "PUT",
      headers: {
        "Content-Type": "text/vcard; charset=utf-8",
        "If-None-Match": "*"
      },
      body: vcard
    });
    return { uid, status: "created", addressBook: ab.displayname };
  },
  _updateVCardField(vcard, field, value) {
    const safeValue = value === void 0 || value === null ? "" : String(value);
    const line = safeValue === "" ? null : `${field}:${safeValue}`;
    return upsertSingleVCardProperty(vcard, field, line);
  },
  _normalizeVCardLineEndings(vcard) {
    return normalizeVCardLineEndings(vcard);
  },
  _formatBirthdayDate(input) {
    return normalizeBirthdayForStorage(input);
  },
  async update(uid, addressBookName, updates) {
    const contact = await this.findContactPath(uid, addressBookName);
    if (!contact) throw new Error(`Contact ${uid} not found.`);
    let vcard = contact.data;
    const currentName = this._extractNameFromVCard(vcard);
    const nameUpdates = {
      familyName: updates.familyName,
      givenName: updates.givenName,
      additionalNames: updates.additionalNames,
      honorificPrefixes: updates.honorificPrefixes,
      honorificSuffixes: updates.honorificSuffixes
    };
    let nextName = currentName;
    if (updates.fullName !== void 0) {
      nextName = deriveStructuredNameFromFullName(updates.fullName);
    }
    if (Object.values(nameUpdates).some((value) => value !== void 0)) {
      nextName = this._applyNameUpdates(nextName, nameUpdates);
    }
    if (updates.fullName !== void 0 || Object.values(nameUpdates).some((value) => value !== void 0)) {
      const resolvedFullName = updates.fullName !== void 0 ? String(updates.fullName || "").trim() : buildDisplayName(nextName, "");
      if (!resolvedFullName) {
        throw new Error("Updated name is empty. Provide --name or structured name fields.");
      }
      vcard = this._updateVCardField(vcard, "FN", encodeVCardText(resolvedFullName));
      vcard = this._updateVCardField(vcard, "N", buildStructuredNameValue(nextName));
    }
    if (updates.email !== void 0 || updates.emails !== void 0) {
      const emails = parseMultiValueInput(updates.emails ?? updates.email);
      const emailLines = emails.map((email) => this._buildCardPropertyLine("EMAIL", encodeVCardText(email), ["TYPE=INTERNET"]));
      vcard = replaceVCardPropertyList(vcard, "EMAIL", emailLines);
    }
    if (updates.phone !== void 0 || updates.phones !== void 0) {
      const phones = parseMultiValueInput(updates.phones ?? updates.phone);
      const phoneLines = phones.map((phone) => this._buildCardPropertyLine("TEL", encodeVCardText(phone), ["TYPE=CELL"]));
      vcard = replaceVCardPropertyList(vcard, "TEL", phoneLines);
    }
    if (updates.organization !== void 0) vcard = this._updateVCardField(vcard, "ORG", updates.organization ? encodeVCardText(updates.organization) : null);
    if (updates.title !== void 0) vcard = this._updateVCardField(vcard, "TITLE", updates.title ? encodeVCardText(updates.title) : null);
    if (updates.note !== void 0) vcard = this._updateVCardField(vcard, "NOTE", updates.note ? encodeVCardText(updates.note) : null);
    if (updates.birthday !== void 0) {
      if (updates.birthday === null || String(updates.birthday).trim() === "") {
        vcard = this._updateVCardField(vcard, "BDAY", null);
      } else {
        const bday = this._formatBirthdayDate(updates.birthday);
        vcard = this._updateVCardField(vcard, "BDAY", bday);
      }
    }
    vcard = this._normalizeVCardLineEndings(vcard);
    await request(contact.href, {
      method: "PUT",
      headers: {
        "Content-Type": "text/vcard; charset=utf-8",
        "If-Match": contact.etag
      },
      body: vcard
    });
    return { uid, status: "updated" };
  },
  async delete(uid, addressBookName = null) {
    const contact = await this.findContactPath(uid, addressBookName);
    if (!contact) throw new Error(`Contact ${uid} not found.`);
    await request(contact.href, {
      method: "DELETE"
    });
    return { uid, status: "deleted" };
  },
  async search(query, addressBookName = null) {
    let addressBooks = await this.findAddressBooks();
    if (addressBookName) {
      addressBooks = addressBooks.filter((a) => a.displayname === addressBookName);
      if (addressBooks.length === 0) {
        throw new Error(`Address book '${addressBookName}' not found.`);
      }
    }
    const allContacts = [];
    const escapedQuery = escapeXml(query);
    const body = this._buildAddressBookQueryBody(`
                <card:filter test="anyof">
                    <card:prop-filter name="FN">
                        <card:text-match collation="i;unicode-casemap" match-type="contains">${escapedQuery}</card:text-match>
                    </card:prop-filter>
                    <card:prop-filter name="EMAIL">
                        <card:text-match collation="i;unicode-casemap" match-type="contains">${escapedQuery}</card:text-match>
                    </card:prop-filter>
                    <card:prop-filter name="TEL">
                        <card:text-match collation="i;unicode-casemap" match-type="contains">${escapedQuery}</card:text-match>
                    </card:prop-filter>
                    <card:prop-filter name="ORG">
                        <card:text-match collation="i;unicode-casemap" match-type="contains">${escapedQuery}</card:text-match>
                    </card:prop-filter>
                </card:filter>
        `);
    for (const ab of addressBooks) {
      try {
        const response = await request(ab.url, {
          method: "REPORT",
          headers: { "Depth": "1", "Content-Type": "application/xml" },
          body
        });
        if (!response["d:multistatus"] || !response["d:multistatus"]["d:response"]) continue;
        const responses = ensureArray(response["d:multistatus"]["d:response"]);
        for (const r of responses) {
          const propstats = ensureArray(r["d:propstat"]);
          if (!propstats[0] || !propstats[0]["d:prop"]) continue;
          const cardData = propstats[0]["d:prop"]["card:address-data"];
          if (!cardData) continue;
          const contact = this._parseVCard(cardData);
          contact.addressBook = ab.displayname;
          contact.href = r["d:href"];
          allContacts.push(contact);
        }
      } catch (e) {
      }
    }
    return allContacts;
  }
};
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const subCommand = args[1];
  try {
    if (command === "notes") {
      if (subCommand === "list") {
        const result = await Notes.list();
        output(result);
      } else if (subCommand === "get") {
        const idIndex = args.indexOf("--id");
        if (idIndex === -1) throw new Error("Missing --id");
        const result = await Notes.get(args[idIndex + 1]);
        output(result);
      } else if (subCommand === "create") {
        const titleIndex = args.indexOf("--title");
        const contentIndex = args.indexOf("--content");
        const categoryIndex = args.indexOf("--category");
        if (titleIndex === -1 || contentIndex === -1) {
          throw new Error("Missing --title or --content arguments");
        }
        const title = args[titleIndex + 1];
        const content = args[contentIndex + 1];
        const category = categoryIndex !== -1 ? args[categoryIndex + 1] : "";
        if (!title || title.startsWith("--")) throw new Error("Invalid title provided");
        if (!content || content.startsWith("--")) throw new Error("Invalid content provided");
        if (category && category.startsWith("--")) throw new Error("Invalid category provided");
        const result = await Notes.create(title, content, category);
        output(result);
      } else if (subCommand === "edit") {
        const idIndex = args.indexOf("--id");
        const titleIndex = args.indexOf("--title");
        const contentIndex = args.indexOf("--content");
        const categoryIndex = args.indexOf("--category");
        if (idIndex === -1) throw new Error("Missing --id");
        const id = args[idIndex + 1];
        const title = titleIndex !== -1 ? args[titleIndex + 1] : void 0;
        const content = contentIndex !== -1 ? args[contentIndex + 1] : void 0;
        const category = categoryIndex !== -1 ? args[categoryIndex + 1] : void 0;
        const result = await Notes.update(id, title, content, category);
        output(result);
      } else if (subCommand === "delete") {
        const idIndex = args.indexOf("--id");
        if (idIndex === -1) throw new Error("Missing --id");
        const result = await Notes.delete(args[idIndex + 1]);
        output(result);
      } else {
        throw new Error("Unknown notes command");
      }
    } else if (command === "files") {
      if (subCommand === "list") {
        const pathIndex = args.indexOf("--path");
        const path = pathIndex !== -1 ? args[pathIndex + 1] : "/";
        const result = await Files.list(path);
        output(result);
      } else if (subCommand === "search") {
        const queryIndex = args.indexOf("--query");
        if (queryIndex === -1) throw new Error("Missing --query");
        const result = await Files.search(args[queryIndex + 1]);
        output(result);
      } else if (subCommand === "upload") {
        const pathIndex = args.indexOf("--path");
        if (pathIndex === -1) throw new Error("Missing --path");
        const filePath = args[pathIndex + 1];
        const contentIndex = args.indexOf("--content");
        if (contentIndex === -1) throw new Error("Missing --content");
        const content = args[contentIndex + 1];
        output(await Files.upload(filePath, content));
      } else if (subCommand === "get") {
        const pathIndex = args.indexOf("--path");
        if (pathIndex === -1) throw new Error("Missing --path");
        output(await Files.get(args[pathIndex + 1]));
      } else if (subCommand === "delete") {
        const pathIndex = args.indexOf("--path");
        if (pathIndex === -1) throw new Error("Missing --path");
        output(await Files.delete(args[pathIndex + 1]));
      } else {
        throw new Error("Unknown files command");
      }
    } else if (command === "calendar") {
      if (subCommand === "list") {
        const fromIndex = args.indexOf("--from");
        const toIndex = args.indexOf("--to");
        const start = fromIndex !== -1 ? args[fromIndex + 1] : (0, import_date_fns.formatISO)(/* @__PURE__ */ new Date());
        const end = toIndex !== -1 ? args[toIndex + 1] : (0, import_date_fns.formatISO)((0, import_date_fns.addDays)(/* @__PURE__ */ new Date(), 7));
        const result = await CalDAV.getEvents(start, end);
        output(result);
      } else if (subCommand === "create") {
        const summaryIndex = args.indexOf("--summary");
        if (summaryIndex === -1) throw new Error("Missing --summary");
        const summary = args[summaryIndex + 1];
        const startIndex = args.indexOf("--start");
        if (startIndex === -1) throw new Error("Missing --start");
        const start = args[startIndex + 1];
        const endIndex = args.indexOf("--end");
        if (endIndex === -1) throw new Error("Missing --end");
        const end = args[endIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        const descIndex = args.indexOf("--description");
        const description = descIndex !== -1 ? args[descIndex + 1] : null;
        const tzIndex = args.indexOf("--timezone");
        const timeZone = tzIndex !== -1 ? args[tzIndex + 1] : null;
        const allDay = args.includes("--all-day");
        output(await CalDAV.createEvent(summary, start, end, calendar, description, timeZone, allDay));
      } else if (subCommand === "edit") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        const updates = {};
        const summaryIndex = args.indexOf("--summary");
        if (summaryIndex !== -1) updates.summary = args[summaryIndex + 1];
        const startIndex = args.indexOf("--start");
        if (startIndex !== -1) updates.start = args[startIndex + 1];
        const endIndex = args.indexOf("--end");
        if (endIndex !== -1) updates.end = args[endIndex + 1];
        const descIndex = args.indexOf("--description");
        if (descIndex !== -1) updates.description = args[descIndex + 1];
        const tzIndex = args.indexOf("--timezone");
        if (tzIndex !== -1) updates.timeZone = args[tzIndex + 1];
        if (args.includes("--all-day")) updates.allDay = true;
        output(await CalDAV.updateEvent(uid, calendar, updates));
      } else if (subCommand === "delete") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        output(await CalDAV.deleteEvent(uid, calendar));
      } else {
        throw new Error("Unknown calendar command");
      }
    } else if (command === "tasks") {
      if (subCommand === "list") {
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        const result = await CalDAV.getTodos(calendar);
        output(result);
      } else if (subCommand === "create") {
        const titleIndex = args.indexOf("--title");
        if (titleIndex === -1) throw new Error("Missing --title");
        const title = args[titleIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        const dueIndex = args.indexOf("--due");
        const dueDate = dueIndex !== -1 ? args[dueIndex + 1] : null;
        const prioIndex = args.indexOf("--priority");
        const priority = prioIndex !== -1 ? args[prioIndex + 1] : null;
        const descIndex = args.indexOf("--description");
        const description = descIndex !== -1 ? args[descIndex + 1] : null;
        const tzIndex = args.indexOf("--timezone");
        const timeZone = tzIndex !== -1 ? args[tzIndex + 1] : null;
        output(await CalDAV.createTask(title, calendar, dueDate, priority, description, timeZone));
      } else if (subCommand === "edit") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        const updates = {};
        const titleIndex = args.indexOf("--title");
        if (titleIndex !== -1) updates.title = args[titleIndex + 1];
        const dueIndex = args.indexOf("--due");
        if (dueIndex !== -1) updates.dueDate = args[dueIndex + 1];
        const prioIndex = args.indexOf("--priority");
        if (prioIndex !== -1) updates.priority = args[prioIndex + 1];
        const descIndex = args.indexOf("--description");
        if (descIndex !== -1) updates.description = args[descIndex + 1];
        const tzIndex = args.indexOf("--timezone");
        if (tzIndex !== -1) updates.timeZone = args[tzIndex + 1];
        output(await CalDAV.updateTask(uid, calendar, updates));
      } else if (subCommand === "delete") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        output(await CalDAV.deleteTask(uid, calendar));
      } else if (subCommand === "complete") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const calIndex = args.indexOf("--calendar");
        const calendar = calIndex !== -1 ? args[calIndex + 1] : null;
        output(await CalDAV.completeTask(uid, calendar));
      } else {
        throw new Error("Unknown tasks command");
      }
    } else if (command === "calendars") {
      if (subCommand === "list") {
        const typeIndex = args.indexOf("--type");
        const type = typeIndex !== -1 ? args[typeIndex + 1] : null;
        let componentType = null;
        if (type === "tasks") componentType = "VTODO";
        else if (type === "events") componentType = "VEVENT";
        const calendars = await CalDAV.findCalendars(componentType);
        output(calendars.map((c) => ({ name: c.displayname, type: c.componentType === "VTODO" ? "tasks" : "events" })));
      } else {
        throw new Error("Unknown calendars command");
      }
    } else if (command === "addressbooks") {
      if (subCommand === "list") {
        const addressBooks = await Contacts.findAddressBooks();
        output(addressBooks.map((a) => ({ name: a.displayname })));
      } else {
        throw new Error("Unknown addressbooks command");
      }
    } else if (command === "contacts") {
      if (subCommand === "list") {
        const abIndex = args.indexOf("--addressbook");
        const addressBook = abIndex !== -1 ? args[abIndex + 1] : null;
        const result = await Contacts.list(addressBook);
        output(result);
      } else if (subCommand === "get") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const abIndex = args.indexOf("--addressbook");
        const addressBook = abIndex !== -1 ? args[abIndex + 1] : null;
        output(await Contacts.get(uid, addressBook));
      } else if (subCommand === "search") {
        const queryIndex = args.indexOf("--query");
        if (queryIndex === -1) throw new Error("Missing --query");
        const query = args[queryIndex + 1];
        const abIndex = args.indexOf("--addressbook");
        const addressBook = abIndex !== -1 ? args[abIndex + 1] : null;
        output(await Contacts.search(query, addressBook));
      } else if (subCommand === "create") {
        const nameIndex = args.indexOf("--name");
        const fullName = nameIndex !== -1 ? args[nameIndex + 1] : "";
        const abIndex = args.indexOf("--addressbook");
        const addressBook = abIndex !== -1 ? args[abIndex + 1] : null;
        const options = {};
        const emailIndex = args.indexOf("--email");
        if (emailIndex !== -1) options.email = args[emailIndex + 1];
        const emailsIndex = args.indexOf("--emails");
        if (emailsIndex !== -1) options.emails = args[emailsIndex + 1];
        const phoneIndex = args.indexOf("--phone");
        if (phoneIndex !== -1) options.phone = args[phoneIndex + 1];
        const phonesIndex = args.indexOf("--phones");
        if (phonesIndex !== -1) options.phones = args[phonesIndex + 1];
        const orgIndex = args.indexOf("--organization");
        if (orgIndex !== -1) options.organization = args[orgIndex + 1];
        const titleIndex = args.indexOf("--title");
        if (titleIndex !== -1) options.title = args[titleIndex + 1];
        const noteIndex = args.indexOf("--note");
        if (noteIndex !== -1) options.note = args[noteIndex + 1];
        const birthdayIndex = args.indexOf("--birthday");
        if (birthdayIndex !== -1) options.birthday = args[birthdayIndex + 1];
        const firstNameIndex = args.indexOf("--first-name");
        if (firstNameIndex !== -1) options.givenName = args[firstNameIndex + 1];
        const lastNameIndex = args.indexOf("--last-name");
        if (lastNameIndex !== -1) options.familyName = args[lastNameIndex + 1];
        const middleNameIndex = args.indexOf("--middle-name");
        if (middleNameIndex !== -1) options.additionalNames = args[middleNameIndex + 1];
        const prefixIndex = args.indexOf("--prefix");
        if (prefixIndex !== -1) options.honorificPrefixes = args[prefixIndex + 1];
        const suffixIndex = args.indexOf("--suffix");
        if (suffixIndex !== -1) options.honorificSuffixes = args[suffixIndex + 1];
        output(await Contacts.create(fullName, addressBook, options));
      } else if (subCommand === "edit") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const abIndex = args.indexOf("--addressbook");
        const addressBook = abIndex !== -1 ? args[abIndex + 1] : null;
        const updates = {};
        const nameIndex = args.indexOf("--name");
        if (nameIndex !== -1) updates.fullName = args[nameIndex + 1];
        const emailIndex = args.indexOf("--email");
        if (emailIndex !== -1) updates.email = args[emailIndex + 1];
        const emailsIndex = args.indexOf("--emails");
        if (emailsIndex !== -1) updates.emails = args[emailsIndex + 1];
        const phoneIndex = args.indexOf("--phone");
        if (phoneIndex !== -1) updates.phone = args[phoneIndex + 1];
        const phonesIndex = args.indexOf("--phones");
        if (phonesIndex !== -1) updates.phones = args[phonesIndex + 1];
        const orgIndex = args.indexOf("--organization");
        if (orgIndex !== -1) updates.organization = args[orgIndex + 1];
        const titleIndex = args.indexOf("--title");
        if (titleIndex !== -1) updates.title = args[titleIndex + 1];
        const noteIndex = args.indexOf("--note");
        if (noteIndex !== -1) updates.note = args[noteIndex + 1];
        const birthdayIndex = args.indexOf("--birthday");
        if (birthdayIndex !== -1) updates.birthday = args[birthdayIndex + 1];
        const firstNameIndex = args.indexOf("--first-name");
        if (firstNameIndex !== -1) updates.givenName = args[firstNameIndex + 1];
        const lastNameIndex = args.indexOf("--last-name");
        if (lastNameIndex !== -1) updates.familyName = args[lastNameIndex + 1];
        const middleNameIndex = args.indexOf("--middle-name");
        if (middleNameIndex !== -1) updates.additionalNames = args[middleNameIndex + 1];
        const prefixIndex = args.indexOf("--prefix");
        if (prefixIndex !== -1) updates.honorificPrefixes = args[prefixIndex + 1];
        const suffixIndex = args.indexOf("--suffix");
        if (suffixIndex !== -1) updates.honorificSuffixes = args[suffixIndex + 1];
        output(await Contacts.update(uid, addressBook, updates));
      } else if (subCommand === "delete") {
        const uidIndex = args.indexOf("--uid");
        if (uidIndex === -1) throw new Error("Missing --uid");
        const uid = args[uidIndex + 1];
        const abIndex = args.indexOf("--addressbook");
        const addressBook = abIndex !== -1 ? args[abIndex + 1] : null;
        output(await Contacts.delete(uid, addressBook));
      } else {
        throw new Error("Unknown contacts command");
      }
    } else {
      console.log("Usage: node index.js <notes|files|calendar|calendars|tasks|contacts|addressbooks> <list|get|create|search|edit|delete> [options]");
    }
  } catch (err) {
    errorOutput(err);
  }
}
main();
