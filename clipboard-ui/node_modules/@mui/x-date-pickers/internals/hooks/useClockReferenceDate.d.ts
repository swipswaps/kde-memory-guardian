import { MuiPickersAdapter, PickersTimezone, PickerValidDate } from "../../models/index.js";
import { PickerValue } from "../models/index.js";
export declare const useClockReferenceDate: <TProps extends {}>({
  value,
  referenceDate: referenceDateProp,
  utils,
  props,
  timezone
}: {
  value: PickerValue;
  referenceDate: PickerValidDate | undefined;
  utils: MuiPickersAdapter;
  props: TProps;
  timezone: PickersTimezone;
}) => PickerValidDate;