"use strict";
'use client';

var _interopRequireWildcard = require("@babel/runtime/helpers/interopRequireWildcard").default;
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.useParsedFormat = void 0;
var React = _interopRequireWildcard(require("react"));
var _RtlProvider = require("@mui/system/RtlProvider");
var _useUtils = require("../internals/hooks/useUtils");
var _buildSectionsFromFormat = require("../internals/hooks/useField/buildSectionsFromFormat");
var _useField = require("../internals/hooks/useField/useField.utils");
var _usePickerTranslations = require("./usePickerTranslations");
var _useNullablePickerContext = require("../internals/hooks/useNullablePickerContext");
/**
 * Returns the parsed format to be rendered in the field when there is no value or in other parts of the Picker.
 * This format is localized (for example `AAAA` for the year with the French locale) and cannot be parsed by your date library.
 * @param {object} The parameters needed to build the placeholder.
 * @param {string} params.format Format to parse.
 * @returns
 */
const useParsedFormat = (parameters = {}) => {
  const pickerContext = (0, _useNullablePickerContext.useNullablePickerContext)();
  const utils = (0, _useUtils.useUtils)();
  const isRtl = (0, _RtlProvider.useRtl)();
  const translations = (0, _usePickerTranslations.usePickerTranslations)();
  const localizedDigits = React.useMemo(() => (0, _useField.getLocalizedDigits)(utils), [utils]);
  const {
    format = pickerContext?.fieldFormat ?? utils.formats.fullDate
  } = parameters;
  return React.useMemo(() => {
    const sections = (0, _buildSectionsFromFormat.buildSectionsFromFormat)({
      utils,
      format,
      formatDensity: 'dense',
      isRtl,
      shouldRespectLeadingZeros: true,
      localeText: translations,
      localizedDigits,
      date: null,
      // TODO v9: Make sure we still don't reverse in `buildSectionsFromFormat` when using `useParsedFormat`.
      enableAccessibleFieldDOMStructure: false
    });
    return sections.map(section => `${section.startSeparator}${section.placeholder}${section.endSeparator}`).join('');
  }, [utils, isRtl, translations, localizedDigits, format]);
};
exports.useParsedFormat = useParsedFormat;