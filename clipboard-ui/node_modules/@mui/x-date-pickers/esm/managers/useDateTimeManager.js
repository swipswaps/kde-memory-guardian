'use client';

import _extends from "@babel/runtime/helpers/esm/extends";
import * as React from 'react';
import { applyDefaultDate } from "../internals/utils/date-utils.js";
import { singleItemFieldValueManager, singleItemValueManager } from "../internals/utils/valueManagers.js";
import { validateDateTime } from "../validation/index.js";
import { useDefaultDates, useUtils } from "../internals/hooks/useUtils.js";
import { usePickerTranslations } from "../hooks/usePickerTranslations.js";
export function useDateTimeManager(parameters = {}) {
  const {
    enableAccessibleFieldDOMStructure = true
  } = parameters;
  return React.useMemo(() => ({
    valueType: 'date-time',
    validator: validateDateTime,
    internal_valueManager: singleItemValueManager,
    internal_fieldValueManager: singleItemFieldValueManager,
    internal_enableAccessibleFieldDOMStructure: enableAccessibleFieldDOMStructure,
    internal_useApplyDefaultValuesToFieldInternalProps: useApplyDefaultValuesToDateTimeFieldInternalProps,
    internal_useOpenPickerButtonAriaLabel: useOpenPickerButtonAriaLabel
  }), [enableAccessibleFieldDOMStructure]);
}
function useOpenPickerButtonAriaLabel(value) {
  const utils = useUtils();
  const translations = usePickerTranslations();
  return React.useMemo(() => {
    const formattedValue = utils.isValid(value) ? utils.format(value, 'fullDate') : null;
    return translations.openDatePickerDialogue(formattedValue);
  }, [value, translations, utils]);
}
function useApplyDefaultValuesToDateTimeFieldInternalProps(internalProps) {
  const utils = useUtils();
  const validationProps = useApplyDefaultValuesToDateTimeValidationProps(internalProps);
  const ampm = React.useMemo(() => internalProps.ampm ?? utils.is12HourCycleInCurrentLocale(), [internalProps.ampm, utils]);
  return React.useMemo(() => _extends({}, internalProps, validationProps, {
    format: internalProps.format ?? (ampm ? utils.formats.keyboardDateTime12h : utils.formats.keyboardDateTime24h)
  }), [internalProps, validationProps, ampm, utils]);
}
export function useApplyDefaultValuesToDateTimeValidationProps(props) {
  const utils = useUtils();
  const defaultDates = useDefaultDates();
  return React.useMemo(() => ({
    disablePast: props.disablePast ?? false,
    disableFuture: props.disableFuture ?? false,
    // TODO: Explore if we can remove it from the public API
    disableIgnoringDatePartForTimeValidation: !!props.minDateTime || !!props.maxDateTime || !!props.disableFuture || !!props.disablePast,
    minDate: applyDefaultDate(utils, props.minDateTime ?? props.minDate, defaultDates.minDate),
    maxDate: applyDefaultDate(utils, props.maxDateTime ?? props.maxDate, defaultDates.maxDate),
    minTime: props.minDateTime ?? props.minTime,
    maxTime: props.maxDateTime ?? props.maxTime
  }), [props.minDateTime, props.maxDateTime, props.minTime, props.maxTime, props.minDate, props.maxDate, props.disableFuture, props.disablePast, utils, defaultDates]);
}