"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.useApplyDefaultValuesToDateTimeValidationProps = useApplyDefaultValuesToDateTimeValidationProps;
exports.useDateTimeManager = useDateTimeManager;
var _extends2 = _interopRequireDefault(require("@babel/runtime/helpers/extends"));
var React = _interopRequireWildcard(require("react"));
var _dateUtils = require("../internals/utils/date-utils");
var _valueManagers = require("../internals/utils/valueManagers");
var _validation = require("../validation");
var _useUtils = require("../internals/hooks/useUtils");
var _usePickerTranslations = require("../hooks/usePickerTranslations");
function useDateTimeManager(parameters = {}) {
  const {
    enableAccessibleFieldDOMStructure = true
  } = parameters;
  return React.useMemo(() => ({
    valueType: 'date-time',
    validator: _validation.validateDateTime,
    internal_valueManager: _valueManagers.singleItemValueManager,
    internal_fieldValueManager: _valueManagers.singleItemFieldValueManager,
    internal_enableAccessibleFieldDOMStructure: enableAccessibleFieldDOMStructure,
    internal_useApplyDefaultValuesToFieldInternalProps: useApplyDefaultValuesToDateTimeFieldInternalProps,
    internal_useOpenPickerButtonAriaLabel: useOpenPickerButtonAriaLabel
  }), [enableAccessibleFieldDOMStructure]);
}
function useOpenPickerButtonAriaLabel(value) {
  const utils = (0, _useUtils.useUtils)();
  const translations = (0, _usePickerTranslations.usePickerTranslations)();
  return React.useMemo(() => {
    const formattedValue = utils.isValid(value) ? utils.format(value, 'fullDate') : null;
    return translations.openDatePickerDialogue(formattedValue);
  }, [value, translations, utils]);
}
function useApplyDefaultValuesToDateTimeFieldInternalProps(internalProps) {
  const utils = (0, _useUtils.useUtils)();
  const validationProps = useApplyDefaultValuesToDateTimeValidationProps(internalProps);
  const ampm = React.useMemo(() => internalProps.ampm ?? utils.is12HourCycleInCurrentLocale(), [internalProps.ampm, utils]);
  return React.useMemo(() => (0, _extends2.default)({}, internalProps, validationProps, {
    format: internalProps.format ?? (ampm ? utils.formats.keyboardDateTime12h : utils.formats.keyboardDateTime24h)
  }), [internalProps, validationProps, ampm, utils]);
}
function useApplyDefaultValuesToDateTimeValidationProps(props) {
  const utils = (0, _useUtils.useUtils)();
  const defaultDates = (0, _useUtils.useDefaultDates)();
  return React.useMemo(() => ({
    disablePast: props.disablePast ?? false,
    disableFuture: props.disableFuture ?? false,
    // TODO: Explore if we can remove it from the public API
    disableIgnoringDatePartForTimeValidation: !!props.minDateTime || !!props.maxDateTime || !!props.disableFuture || !!props.disablePast,
    minDate: (0, _dateUtils.applyDefaultDate)(utils, props.minDateTime ?? props.minDate, defaultDates.minDate),
    maxDate: (0, _dateUtils.applyDefaultDate)(utils, props.maxDateTime ?? props.maxDate, defaultDates.maxDate),
    minTime: props.minDateTime ?? props.minTime,
    maxTime: props.maxDateTime ?? props.maxTime
  }), [props.minDateTime, props.maxDateTime, props.minTime, props.maxTime, props.minDate, props.maxDate, props.disableFuture, props.disablePast, utils, defaultDates]);
}