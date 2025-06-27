import { MuiPickersAdapterContextValue } from "../../LocalizationProvider/LocalizationProvider.js";
import { PickersLocaleText } from "../../locales/utils/pickersLocaleTextApi.js";
import { PickersTimezone, PickerValidDate } from "../../models/index.js";
export declare const useLocalizationContext: () => UseLocalizationContextReturnValue;
export declare const useUtils: () => import("@mui/x-date-pickers/models").MuiPickersAdapter<any>;
export declare const useDefaultDates: () => {
  minDate: PickerValidDate;
  maxDate: PickerValidDate;
};
export declare const useNow: (timezone: PickersTimezone) => PickerValidDate;
export interface UseLocalizationContextReturnValue extends Omit<MuiPickersAdapterContextValue, 'localeText'> {
  localeText: PickersLocaleText;
}