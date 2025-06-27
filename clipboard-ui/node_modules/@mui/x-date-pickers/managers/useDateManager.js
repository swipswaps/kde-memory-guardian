"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.useApplyDefaultValuesToDateValidationProps = useApplyDefaultValuesToDateValidationProps;
exports.useDateManager = useDateManager;
var _extends2 = _interopRequireDefault(require("@babel/runtime/helpers/extends"));
var React = _interopRequireWildcard(require("react"));
var _dateUtils = require("../internals/utils/date-utils");
var _valueManagers = require("../internals/utils/valueManagers");
var _validation = require("../validation");
var _useUtils = require("../internals/hooks/useUtils");
var _usePickerTranslations = require("../hooks/usePickerTranslations");
function useDateManager(parameters = {}) {
  const {
    enableAccessibleFieldDOMStructure = true
  } = parameters;
  return React.useMemo(() => ({
    valueType: 'date',
    validator: _validation.validateDate,
    internal_valueManager: _valueManagers.singleItemValueManager,
    internal_fieldValueManager: _valueManagers.singleItemFieldValueManager,
    internal_enableAccessibleFieldDOMStructure: enableAccessibleFieldDOMStructure,
    internal_useApplyDefaultValuesToFieldInternalProps: useApplyDefaultValuesToDateFieldInternalProps,
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
function useApplyDefaultValuesToDateFieldInternalProps(internalProps) {
  const utils = (0, _useUtils.useUtils)();
  const validationProps = useApplyDefaultValuesToDateValidationProps(internalProps);
  return React.useMemo(() => (0, _extends2.default)({}, internalProps, validationProps, {
    format: internalProps.format ?? utils.formats.keyboardDate
  }), [internalProps, validationProps, utils]);
}
function useApplyDefaultValuesToDateValidationProps(props) {
  const utils = (0, _useUtils.useUtils)();
  const defaultDates = (0, _useUtils.useDefaultDates)();
  return React.useMemo(() => ({
    disablePast: props.disablePast ?? false,
    disableFuture: props.disableFuture ?? false,
    minDate: (0, _dateUtils.applyDefaultDate)(utils, props.minDate, defaultDates.minDate),
    maxDate: (0, _dateUtils.applyDefaultDate)(utils, props.maxDate, defaultDates.maxDate)
  }), [props.minDate, props.maxDate, props.disableFuture, props.disablePast, utils, defaultDates]);
}