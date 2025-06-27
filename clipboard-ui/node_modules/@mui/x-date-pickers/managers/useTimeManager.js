"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
var _interopRequireDefault = require("@babel/runtime/helpers/interopRequireDefault").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.useApplyDefaultValuesToTimeValidationProps = useApplyDefaultValuesToTimeValidationProps;
exports.useTimeManager = useTimeManager;
var _extends2 = _interopRequireDefault(require("@babel/runtime/helpers/extends"));
var React = _interopRequireWildcard(require("react"));
var _valueManagers = require("../internals/utils/valueManagers");
var _validation = require("../validation");
var _useUtils = require("../internals/hooks/useUtils");
var _usePickerTranslations = require("../hooks/usePickerTranslations");
function useTimeManager(parameters = {}) {
  const {
    enableAccessibleFieldDOMStructure = true,
    ampm
  } = parameters;
  return React.useMemo(() => ({
    valueType: 'time',
    validator: _validation.validateTime,
    internal_valueManager: _valueManagers.singleItemValueManager,
    internal_fieldValueManager: _valueManagers.singleItemFieldValueManager,
    internal_enableAccessibleFieldDOMStructure: enableAccessibleFieldDOMStructure,
    internal_useApplyDefaultValuesToFieldInternalProps: useApplyDefaultValuesToTimeFieldInternalProps,
    internal_useOpenPickerButtonAriaLabel: createUseOpenPickerButtonAriaLabel(ampm)
  }), [ampm, enableAccessibleFieldDOMStructure]);
}
function createUseOpenPickerButtonAriaLabel(ampm) {
  return function useOpenPickerButtonAriaLabel(value) {
    const utils = (0, _useUtils.useUtils)();
    const translations = (0, _usePickerTranslations.usePickerTranslations)();
    return React.useMemo(() => {
      const formatKey = ampm ?? utils.is12HourCycleInCurrentLocale() ? 'fullTime12h' : 'fullTime24h';
      const formattedValue = utils.isValid(value) ? utils.format(value, formatKey) : null;
      return translations.openTimePickerDialogue(formattedValue);
    }, [value, translations, utils]);
  };
}
function useApplyDefaultValuesToTimeFieldInternalProps(internalProps) {
  const utils = (0, _useUtils.useUtils)();
  const validationProps = useApplyDefaultValuesToTimeValidationProps(internalProps);
  const ampm = React.useMemo(() => internalProps.ampm ?? utils.is12HourCycleInCurrentLocale(), [internalProps.ampm, utils]);
  return React.useMemo(() => (0, _extends2.default)({}, internalProps, validationProps, {
    format: internalProps.format ?? (ampm ? utils.formats.fullTime12h : utils.formats.fullTime24h)
  }), [internalProps, validationProps, ampm, utils]);
}
function useApplyDefaultValuesToTimeValidationProps(props) {
  return React.useMemo(() => ({
    disablePast: props.disablePast ?? false,
    disableFuture: props.disableFuture ?? false
  }), [props.disablePast, props.disableFuture]);
}