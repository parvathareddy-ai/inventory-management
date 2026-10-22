// Small, dependency-free CSV helpers (RFC 4180) reusable across views.

// Characters that make Excel/Sheets interpret a text cell as a formula.
const FORMULA_TRIGGER = /^[=+\-@\t\r]/

// Wraps a number formatted to fixed decimals so it is treated as numeric, not text.
class NumericCell {
  constructor(text) {
    this.text = text
  }
}

/** Format a number with fixed decimals as a numeric CSV cell (no symbols or separators). */
export function fixedNumber(n, decimals = 2) {
  return new NumericCell(Number(n).toFixed(decimals))
}

// Convert one cell to its CSV text form.
function formatCell(value) {
  if (value === null || value === undefined) return ''

  let text
  if (value instanceof NumericCell) {
    // Pre-formatted number (e.g. fixed decimals): also exempt from the guard.
    text = value.text
  } else if (typeof value === 'number') {
    // Numeric cells are never altered: a negative number must stay a number.
    text = String(value)
  } else {
    text = String(value)
    // Formula-injection guard: prefix a single quote so spreadsheets treat
    // the cell as text. Applied to STRING cells only.
    if (FORMULA_TRIGGER.test(text)) text = "'" + text
  }

  // RFC 4180: quote fields containing comma, quote, CR or LF; double quotes.
  if (/[",\r\n]/.test(text)) text = '"' + text.replace(/"/g, '""') + '"'
  return text
}

/**
 * Build CSV text (without BOM) from a header array and an array of row arrays.
 * Rows are joined with CRLF as RFC 4180 requires.
 */
export function toCsv(headers, rows) {
  return [headers, ...rows].map(row => row.map(formatCell).join(',')).join('\r\n')
}

/** Local-date stamp (YYYY-MM-DD). toISOString() is UTC and can be off by a day. */
export function localDateStamp(date = new Date()) {
  const pad = n => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

/** Trigger a browser download of csvText as filename. */
export function downloadCsv(filename, csvText) {
  // UTF-8 BOM so Excel detects the encoding and shows Japanese text correctly.
  const blob = new Blob(['﻿', csvText], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  // Release the blob; deferred so the browser has started the download.
  setTimeout(() => URL.revokeObjectURL(url), 0)
}
