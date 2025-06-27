'use client';

import _extends from "@babel/runtime/helpers/esm/extends";
import * as React from 'react';
import { applyDefaultDate } from "../internals/utils/date-utils.js";
import { singleItemFieldValueManager, singleItemValueManager } from "../internals/utils/valueManagers.js";
import { validateDate } from "../validation/index.js";
import { useDefaultDates, useUtils } from "../internals/hooks/useUtils.js";
import { usePickerTranslations } from "../hooks/usePickerTranslations.js";
export function useDateManager(parameters = {}) {
  const {
    enableAccessibleFieldDOMStructure = true
  } = parameters;
  return React.useMemo(() => ({
    valueType: 'date',
    validator: validateDate,
    internal_valueManager: singleItemValueManager,
    internal_fieldValueManager: singleItemFieldValueManager,
    internal_enableAccessibleFieldDOMStructure: enableAccessibleFieldDOMStructure,
    internal_useApplyDefaultValuesToFieldInternalProps: useApplyDefaultValuesToDateFieldInternalProps,
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
function useApplyDefaultValuesToDateFieldInternalProps(internalProps) {
  const utils = useUtils();
  const validationProps = useApplyDefaultValuesToDateValidationProps(internalProps);
  return React.useMemo(() => _extends({}, internalProps, validationProps, {
    format: internalProps.format ?? utils.formats.keyboardDate
  }), [internalProps, validationProps, utils]);
}
export function useApplyDefaultValuesToDateValidationProps(props) {
  const utils = useUtils();
  const defaultDates = useDefaultDates();
  return React.useMemo(() => ({
    disablePast: props.disablePast ?? false,
    disableFuture: props.disableFuture ?? false,
    minDate: applyDefaultDate(utils, props.minDate, defaultDates.minDate),
    maxDate: applyDefaultDate(utils, props.maxDate, defaultDates.maxDate)
  }), [props.minDate, props.maxDate, props.disableFuture, props.disablePast, utils, defaultDates]);
}