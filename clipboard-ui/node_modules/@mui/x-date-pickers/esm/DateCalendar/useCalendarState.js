'use client';

import _extends from "@babel/runtime/helpers/esm/extends";
import * as React from 'react';
import useEventCallback from '@mui/utils/useEventCallback';
import { useIsDateDisabled } from "./useIsDateDisabled.js";
import { useUtils } from "../internals/hooks/useUtils.js";
import { singleItemValueManager } from "../internals/utils/valueManagers.js";
import { SECTION_TYPE_GRANULARITY } from "../internals/utils/getDefaultReferenceDate.js";
import { findClosestEnabledDate } from "../internals/utils/date-utils.js";
const createCalendarStateReducer = (reduceAnimations, utils) => (state, action) => {
  switch (action.type) {
    case 'setVisibleDate':
      return _extends({}, state, {
        slideDirection: action.direction,
        currentMonth: action.month,
        isMonthSwitchingAnimating: !utils.isSameMonth(action.month, state.currentMonth) && !reduceAnimations && !action.skipAnimation,
        focusedDay: action.focusedDay
      });
    case 'changeMonthTimezone':
      {
        const newTimezone = action.newTimezone;
        if (utils.getTimezone(state.currentMonth) === newTimezone) {
          return state;
        }
        let newCurrentMonth = utils.setTimezone(state.currentMonth, newTimezone);
        if (utils.getMonth(newCurrentMonth) !== utils.getMonth(state.currentMonth)) {
          newCurrentMonth = utils.setMonth(newCurrentMonth, utils.getMonth(state.currentMonth));
        }
        return _extends({}, state, {
          currentMonth: newCurrentMonth
        });
      }
    case 'finishMonthSwitchingAnimation':
      return _extends({}, state, {
        isMonthSwitchingAnimating: false
      });
    default:
      throw new Error('missing support');
  }
};
export const useCalendarState = params => {
  const {
    value,
    referenceDate: referenceDateProp,
    disableFuture,
    disablePast,
    maxDate,
    minDate,
    onMonthChange,
    onYearChange,
    reduceAnimations,
    shouldDisableDate,
    timezone,
    getCurrentMonthFromVisibleDate
  } = params;
  const utils = useUtils();
  const reducerFn = React.useRef(createCalendarStateReducer(Boolean(reduceAnimations), utils)).current;
  const referenceDate = React.useMemo(() => {
    return singleItemValueManager.getInitialReferenceValue({
      value,
      utils,
      timezone,
      props: params,
      referenceDate: referenceDateProp,
      granularity: SECTION_TYPE_GRANULARITY.day
    });
  },
  // We want the `referenceDate` to update on prop and `timezone` change (https://github.com/mui/mui-x/issues/10804)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  [referenceDateProp, timezone]);
  const [calendarState, dispatch] = React.useReducer(reducerFn, {
    isMonthSwitchingAnimating: false,
    focusedDay: referenceDate,
    currentMonth: utils.startOfMonth(referenceDate),
    slideDirection: 'left'
  });
  const isDateDisabled = useIsDateDisabled({
    shouldDisableDate,
    minDate,
    maxDate,
    disableFuture,
    disablePast,
    timezone
  });

  // Ensure that `calendarState.currentMonth` timezone is updated when `referenceDate` (or timezone changes)
  // https://github.com/mui/mui-x/issues/10804
  React.useEffect(() => {
    dispatch({
      type: 'changeMonthTimezone',
      newTimezone: utils.getTimezone(referenceDate)
    });
  }, [referenceDate, utils]);
  const setVisibleDate = useEventCallback(({
    target,
    reason
  }) => {
    if (reason === 'cell-interaction' && calendarState.focusedDay != null && utils.isSameDay(target, calendarState.focusedDay)) {
      return;
    }
    const skipAnimation = reason === 'cell-interaction';
    let month;
    let focusedDay;
    if (reason === 'cell-interaction') {
      month = getCurrentMonthFromVisibleDate(target, calendarState.currentMonth);
      focusedDay = target;
    } else {
      month = utils.isSameMonth(target, calendarState.currentMonth) ? calendarState.currentMonth : utils.startOfMonth(target);
      focusedDay = target;

      // If the date is disabled, we try to find a non-disabled date inside the same month.
      if (isDateDisabled(focusedDay)) {
        const startOfMonth = utils.startOfMonth(target);
        const endOfMonth = utils.endOfMonth(target);
        focusedDay = findClosestEnabledDate({
          utils,
          date: focusedDay,
          minDate: utils.isBefore(minDate, startOfMonth) ? startOfMonth : minDate,
          maxDate: utils.isAfter(maxDate, endOfMonth) ? endOfMonth : maxDate,
          disablePast,
          disableFuture,
          isDateDisabled,
          timezone
        });
      }
    }
    const hasChangedMonth = !utils.isSameMonth(calendarState.currentMonth, month);
    const hasChangedYear = !utils.isSameYear(calendarState.currentMonth, month);
    if (hasChangedMonth) {
      onMonthChange?.(month);
    }
    if (hasChangedYear) {
      onYearChange?.(utils.startOfYear(month));
    }
    dispatch({
      type: 'setVisibleDate',
      month,
      direction: utils.isAfterDay(month, calendarState.currentMonth) ? 'left' : 'right',
      focusedDay: calendarState.focusedDay != null && focusedDay != null && utils.isSameDay(focusedDay, calendarState.focusedDay) ? calendarState.focusedDay : focusedDay,
      skipAnimation
    });
  });
  const onMonthSwitchingAnimationEnd = React.useCallback(() => {
    dispatch({
      type: 'finishMonthSwitchingAnimation'
    });
  }, []);
  return {
    referenceDate,
    calendarState,
    setVisibleDate,
    isDateDisabled,
    onMonthSwitchingAnimationEnd
  };
};