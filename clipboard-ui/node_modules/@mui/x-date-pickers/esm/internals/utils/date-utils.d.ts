import { DateView, MuiPickersAdapter, PickersTimezone, PickerValidDate, PickerValueType } from "../../models/index.js";
import { DateOrTimeViewWithMeridiem } from "../models/index.js";
export declare const mergeDateAndTime: (utils: MuiPickersAdapter, dateParam: PickerValidDate, timeParam: PickerValidDate) => PickerValidDate;
interface FindClosestDateParams {
  date: PickerValidDate;
  disableFuture?: boolean;
  disablePast?: boolean;
  maxDate: PickerValidDate;
  minDate: PickerValidDate;
  isDateDisabled: (date: PickerValidDate) => boolean;
  utils: MuiPickersAdapter;
  timezone: PickersTimezone;
}
export declare const findClosestEnabledDate: ({
  date,
  disableFuture,
  disablePast,
  maxDate,
  minDate,
  isDateDisabled,
  utils,
  timezone
}: FindClosestDateParams) => PickerValidDate | null;
export declare const replaceInvalidDateByNull: (utils: MuiPickersAdapter, value: PickerValidDate | null) => PickerValidDate | null;
export declare const applyDefaultDate: (utils: MuiPickersAdapter, value: PickerValidDate | null | undefined, defaultValue: PickerValidDate) => PickerValidDate;
export declare const areDatesEqual: (utils: MuiPickersAdapter, a: PickerValidDate | null, b: PickerValidDate | null) => boolean;
export declare const getMonthsInYear: (utils: MuiPickersAdapter, year: PickerValidDate) => PickerValidDate[];
export declare const getTodayDate: (utils: MuiPickersAdapter, timezone: PickersTimezone, valueType?: PickerValueType) => PickerValidDate;
export declare const formatMeridiem: (utils: MuiPickersAdapter, meridiem: "am" | "pm") => string;
export declare const DATE_VIEWS: readonly ["year", "month", "day"];
export declare const isDatePickerView: (view: DateOrTimeViewWithMeridiem) => view is DateView;
export declare const resolveDateFormat: (utils: MuiPickersAdapter, {
  format,
  views
}: {
  format?: string;
  views: readonly DateView[];
}, isInToolbar: boolean) => string;
export declare const getWeekdays: (utils: MuiPickersAdapter, date: PickerValidDate) => PickerValidDate[];
export {};