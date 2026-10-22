import { test } from 'node:test'
import assert from 'node:assert/strict'
import { toCsv, fixedNumber } from './csv.js'

// Single-row helper: returns the data line (header is fixed and plain).
const cell = value => toCsv(['h'], [[value]]).split('\r\n')[1]

test('plain text is untouched', () => {
  assert.equal(cell('Widget'), 'Widget')
  assert.equal(cell(''), '')
  assert.equal(cell(null), '')
  assert.equal(cell(undefined), '')
})

test('quotes fields containing comma, quote, CR or LF', () => {
  assert.equal(cell('a,b'), '"a,b"')
  assert.equal(cell('say "hi"'), '"say ""hi"""')
  assert.equal(cell('line1\nline2'), '"line1\nline2"')
  // A cell starting with CR is also formula-guarded, then quoted
  assert.equal(cell('x\ry'), '"x\ry"')
})

test('neutralizes formula triggers with a leading single quote', () => {
  for (const v of ['=1+1', '+1', '-1+2', '@SUM(A1)', '-cmd']) {
    assert.equal(cell(v), "'" + v, v)
  }
})

test('neutralizes triggers after leading whitespace', () => {
  for (const v of [' =1+1', '   +1', '  @x', ' -1']) {
    assert.equal(cell(v), "'" + v, JSON.stringify(v))
  }
})

test('neutralizes values starting with tab or CR (then quotes CR)', () => {
  assert.equal(cell('\tfoo'), "'\tfoo")
  assert.equal(cell('\rfoo'), '"\'\rfoo"')
})

test('does not touch text where the trigger is not first', () => {
  assert.equal(cell('a=b'), 'a=b')
  assert.equal(cell('x-1'), 'x-1')
  assert.equal(cell('  hello'), '  hello')
})

test('guarded value that also needs quoting', () => {
  assert.equal(cell('=A1,B1'), '"\'=A1,B1"')
  assert.equal(cell('@say "x"'), '"\'@say ""x"""')
})

test('numbers are never guarded, including negatives', () => {
  assert.equal(cell(-5), '-5')
  assert.equal(cell(-0.25), '-0.25')
  assert.equal(cell(42), '42')
  assert.equal(cell(0), '0')
})

test('fixedNumber keeps decimals and stays numeric', () => {
  assert.equal(cell(fixedNumber(1234.5)), '1234.50')
  assert.equal(cell(fixedNumber(-3)), '-3.00')
  assert.equal(cell(fixedNumber(2, 0)), '2')
  assert.equal(cell(fixedNumber(1.005, 3)), '1.005')
  assert.equal(cell(fixedNumber('7.1', 2)), '7.10')
})

test('non-ASCII text passes through', () => {
  assert.equal(cell('回路基板'), '回路基板')
  assert.equal(cell('café, ¥1,000'), '"café, ¥1,000"')
  assert.equal(cell('=回路'), "'=回路")
})

test('rows are joined with CRLF and have no trailing separator', () => {
  const out = toCsv(['a', 'b'], [[1, 'x'], [2, 'y']])
  assert.equal(out, 'a,b\r\n1,x\r\n2,y')
  assert.ok(!out.endsWith('\r\n'))
  assert.equal(out.split('\r\n').length, 3)
})

test('headers go through the same escaping', () => {
  assert.equal(toCsv(['a,b', '=x'], []), '"a,b",\'=x')
})
