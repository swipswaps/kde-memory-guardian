import * as React from 'react';
import { useUtils } from "./useUtils.js";
import { getMeridiem, convertToMeridiem } from "../utils/time-utils.js";
export function useNextMonthDisabled(month, {
  disableFuture,
  maxDate,
  timezone
}) {
  const utils = useUtils();
  return React.useMemo(() => {
    const now = utils.date(undefined, timezone);
    const lastEnabledMonth = utils.startOfMonth(disableFuture && utils.isBefore(now, maxDate) ? now : maxDate);
    return !utils.isAfter(lastEnabledMonth, month);
  }, [disableFuture, maxDate, month, utils, timezone]);
}
export function usePreviousMonthDisabled(month, {
  disablePast,
  minDate,
  timezone
}) {
  const utils = useUtils();
  return React.useMemo(() => {
    const now = utils.date(undefined, timezone);
    const firstEnabledMonth = utils.startOfMonth(disablePast && utils.isAfter(now, minDate) ? now : minDate);
    return !utils.isBefore(firstEnabledMonth, month);
  }, [disablePast, minDate, month, utils, timezone]);
}
export function useMeridiemMode(date, ampm, onChange, selectionState) {
  const utils = useUtils();
  const cleanDate = React.useMemo(() => !utils.isValid(date) ? null : date, [utils, date]);
  const meridiemMode = getMeridiem(cleanDate, utils);
  const handleMeridiemChange = React.useCallback(mode => {
    const timeWithMeridiem = cleanDate == null ? null : convertToMeridiem(cleanDate, mode, Boolean(ampm), utils);
    onChange(timeWithMeridiem, selectionState ?? 'partial');
  }, [ampm, cleanDate, onChange, selectionState, utils]);
  return {
    meridiemMode,
    handleMeridiemChange
  };
}