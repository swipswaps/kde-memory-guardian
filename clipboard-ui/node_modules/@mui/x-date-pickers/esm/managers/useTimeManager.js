'use client';

import _extends from "@babel/runtime/helpers/esm/extends";
import * as React from 'react';
import { singleItemFieldValueManager, singleItemValueManager } from "../internals/utils/valueManagers.js";
import { validateTime } from "../validation/index.js";
import { useUtils } from "../internals/hooks/useUtils.js";
import { usePickerTranslations } from "../hooks/usePickerTranslations.js";
export function useTimeManager(parameters = {}) {
  const {
    enableAccessibleFieldDOMStructure = true,
    ampm
  } = parameters;
  return React.useMemo(() => ({
    valueType: 'time',
    validator: validateTime,
    internal_valueManager: singleItemValueManager,
    internal_fieldValueManager: singleItemFieldValueManager,
    internal_enableAccessibleFieldDOMStructure: enableAccessibleFieldDOMStructure,
    internal_useApplyDefaultValuesToFieldInternalProps: useApplyDefaultValuesToTimeFieldInternalProps,
    internal_useOpenPickerButtonAriaLabel: createUseOpenPickerButtonAriaLabel(ampm)
  }), [ampm, enableAccessibleFieldDOMStructure]);
}
function createUseOpenPickerButtonAriaLabel(ampm) {
  return function useOpenPickerButtonAriaLabel(value) {
    const utils = useUtils();
    const translations = usePickerTranslations();
    return React.useMemo(() => {
      const formatKey = ampm ?? utils.is12HourCycleInCurrentLocale() ? 'fullTime12h' : 'fullTime24h';
      const formattedValue = utils.isValid(value) ? utils.format(value, formatKey) : null;
      return translations.openTimePickerDialogue(formattedValue);
    }, [value, translations, utils]);
  };
}
function useApplyDefaultValuesToTimeFieldInternalProps(internalProps) {
  const utils = useUtils();
  const validationProps = useApplyDefaultValuesToTimeValidationProps(internalProps);
  const ampm = React.useMemo(() => internalProps.ampm ?? utils.is12HourCycleInCurrentLocale(), [internalProps.ampm, utils]);
  return React.useMemo(() => _extends({}, internalProps, validationProps, {
    format: internalProps.format ?? (ampm ? utils.formats.fullTime12h : utils.formats.fullTime24h)
  }), [internalProps, validationProps, ampm, utils]);
}
export function useApplyDefaultValuesToTimeValidationProps(props) {
  return React.useMemo(() => ({
    disablePast: props.disablePast ?? false,
    disableFuture: props.disableFuture ?? false
  }), [props.disablePast, props.disableFuture]);
}