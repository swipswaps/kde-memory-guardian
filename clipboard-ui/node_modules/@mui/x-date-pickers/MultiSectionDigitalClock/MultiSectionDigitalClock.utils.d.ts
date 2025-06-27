import { MuiPickersAdapter, PickerValidDate } from "../models/index.js";
import { MultiSectionDigitalClockOption } from "./MultiSectionDigitalClock.types.js";
interface GetHoursSectionOptionsParameters {
  now: PickerValidDate;
  value: PickerValidDate | null;
  utils: MuiPickersAdapter;
  ampm: boolean;
  isDisabled: (value: number) => boolean;
  timeStep: number;
  resolveAriaLabel: (value: string) => string;
  valueOrReferenceDate: PickerValidDate;
}
export declare const getHourSectionOptions: ({
  now,
  value,
  utils,
  ampm,
  isDisabled,
  resolveAriaLabel,
  timeStep,
  valueOrReferenceDate
}: GetHoursSectionOptionsParameters) => MultiSectionDigitalClockOption<number>[];
interface GetTimeSectionOptionsParameters {
  value: number | null;
  utils: MuiPickersAdapter;
  isDisabled: (value: number) => boolean;
  timeStep: number;
  resolveLabel: (value: number) => string;
  hasValue?: boolean;
  resolveAriaLabel: (value: string) => string;
}
export declare const getTimeSectionOptions: ({
  value,
  utils,
  isDisabled,
  timeStep,
  resolveLabel,
  resolveAriaLabel,
  hasValue
}: GetTimeSectionOptionsParameters) => MultiSectionDigitalClockOption<number>[];
export {};