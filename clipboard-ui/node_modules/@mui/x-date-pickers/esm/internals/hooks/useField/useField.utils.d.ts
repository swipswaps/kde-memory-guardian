import { FieldSectionsValueBoundaries, SectionOrdering, FieldSectionValueBoundaries, FieldParsedSelectedSections } from "./useField.types.js";
import { FieldSectionType, FieldSection, MuiPickersAdapter, FieldSectionContentType, PickersTimezone, PickerValidDate, FieldSelectedSections, PickerValueType, InferFieldSection } from "../../../models/index.js";
import { PickerValidValue } from "../../models/index.js";
export declare const getDateSectionConfigFromFormatToken: (utils: MuiPickersAdapter, formatToken: string) => Pick<FieldSection, "type" | "contentType"> & {
  maxLength: number | undefined;
};
export declare const getDaysInWeekStr: (utils: MuiPickersAdapter, format: string) => string[];
export declare const getLetterEditingOptions: (utils: MuiPickersAdapter, timezone: PickersTimezone, sectionType: FieldSectionType, format: string) => string[];
export declare const FORMAT_SECONDS_NO_LEADING_ZEROS = "s";
export declare const getLocalizedDigits: (utils: MuiPickersAdapter) => string[];
export declare const removeLocalizedDigits: (valueStr: string, localizedDigits: string[]) => string;
export declare const applyLocalizedDigits: (valueStr: string, localizedDigits: string[]) => string;
export declare const isStringNumber: (valueStr: string, localizedDigits: string[]) => boolean;
/**
 * Make sure the value of a digit section have the right amount of leading zeros.
 * E.g.: `03` => `3`
 * Warning: Should only be called with non-localized digits. Call `removeLocalizedDigits` with your value if needed.
 */
export declare const cleanLeadingZeros: (valueStr: string, size: number) => string;
export declare const cleanDigitSectionValue: (utils: MuiPickersAdapter, value: number, sectionBoundaries: FieldSectionValueBoundaries<any>, localizedDigits: string[], section: Pick<FieldSection, "format" | "type" | "contentType" | "hasLeadingZerosInFormat" | "hasLeadingZerosInInput" | "maxLength">) => string;
export declare const getSectionVisibleValue: (section: FieldSection, target: "input-rtl" | "input-ltr" | "non-input", localizedDigits: string[]) => string;
export declare const changeSectionValueFormat: (utils: MuiPickersAdapter, valueStr: string, currentFormat: string, newFormat: string) => string;
export declare const doesSectionFormatHaveLeadingZeros: (utils: MuiPickersAdapter, contentType: FieldSectionContentType, sectionType: FieldSectionType, format: string) => boolean;
/**
 * Some date libraries like `dayjs` don't support parsing from date with escaped characters.
 * To make sure that the parsing works, we are building a format and a date without any separator.
 */
export declare const getDateFromDateSections: (utils: MuiPickersAdapter, sections: FieldSection[], localizedDigits: string[]) => PickerValidDate;
export declare const createDateStrForV7HiddenInputFromSections: (sections: FieldSection[]) => string;
export declare const createDateStrForV6InputFromSections: (sections: FieldSection[], localizedDigits: string[], isRtl: boolean) => string;
export declare const getSectionsBoundaries: (utils: MuiPickersAdapter, localizedDigits: string[], timezone: PickersTimezone) => FieldSectionsValueBoundaries;
export declare const validateSections: <TValue extends PickerValidValue>(sections: InferFieldSection<TValue>[], valueType: PickerValueType) => void;
export declare const mergeDateIntoReferenceDate: (utils: MuiPickersAdapter, dateToTransferFrom: PickerValidDate, sections: FieldSection[], referenceDate: PickerValidDate, shouldLimitToEditedSections: boolean) => PickerValidDate;
export declare const isAndroid: () => boolean;
export declare const getSectionOrder: (sections: FieldSection[], shouldApplyRTL: boolean) => SectionOrdering;
export declare const parseSelectedSections: (selectedSections: FieldSelectedSections, sections: FieldSection[]) => FieldParsedSelectedSections;