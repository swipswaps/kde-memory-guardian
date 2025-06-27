"use strict";
'use client';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.usePickerTranslations = void 0;
var _useUtils = require("../internals/hooks/useUtils");
const usePickerTranslations = () => (0, _useUtils.useLocalizationContext)().localeText;
exports.usePickerTranslations = usePickerTranslations;