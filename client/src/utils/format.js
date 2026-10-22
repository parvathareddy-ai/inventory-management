// Shared display formatters. Variants that used to be copy-pasted per view are named options.
import { formatCurrency } from './currency'

/** Map the app locale ('en' | 'ja') to a BCP 47 tag for Intl. */
export const localeTag = (appLocale) => (appLocale === 'ja' ? 'ja-JP' : 'en-US')

/**
 * Format a date string for display.
 *
 * @param {string|null|undefined} value  ISO date or datetime
 * @param {object} [options]
 * @param {string} [options.locale='en']      app locale ('en' | 'ja')
 * @param {'short'|'long'} [options.month='short']  month text style
 * @param {boolean} [options.year=true]       include the year
 * @param {string} [options.empty='-']        returned for empty input
 * @param {boolean} [options.rawOnInvalid=true]  return the input unchanged when unparseable
 */
export function formatDate(
  value,
  { locale = 'en', month = 'short', year = true, empty = '-', rawOnInvalid = true } = {},
) {
  if (!value) return empty
  // A bare YYYY-MM-DD is parsed as UTC midnight, which displays a day early in timezones
  // behind UTC; building it from parts keeps it on the intended local day.
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  const date = dateOnly ? new Date(+dateOnly[1], +dateOnly[2] - 1, +dateOnly[3]) : new Date(value)
  if (isNaN(date.getTime())) return rawOnInvalid ? value : 'Invalid Date'
  const opts = { month, day: 'numeric' }
  if (year) opts.year = 'numeric'
  return date.toLocaleDateString(localeTag(locale), opts)
}

/** Currency formatter bound to a (reactive) currency ref: amounts are USD, converted for display. */
export const currencyFormatter = (currencyRef) => (value) =>
  formatCurrency(value, currencyRef.value)
