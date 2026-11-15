"""The documented format and arithmetic, without filesystem dependencies."""
from datetime import date
import unittest

from sow_ledger import report


HEADER = ('| variety | harvest_year | quantity | germination | sow_by | shelf_life_years |\n'
          '| --- | --- | --- | --- | --- | --- |\n')
AS_OF = date(2026, 11, 15)


def ledger(*rows):
    return '# Seed drawer\n\n' + HEADER + '\n'.join(rows) + '\n'


class LedgerTests(unittest.TestCase):
    def test_calendar_age_counts_and_rounding(self):
        entries = report(ledger('| Pea | 2024 | 42 | 2/3 | 2026-03-15 | - |'), AS_OF)['entries']
        self.assertEqual(entries[0], {
            'variety': 'Pea', 'harvest_year': 2024, 'age_calendar_years': 2,
            'quantity': 42, 'germination': {'germinated': 2, 'tested': 3, 'percent': '66.67'},
            'sow_by': '2026-03-15', 'sow_by_source': 'explicit_date', 'shelf_life_years': None})

    def test_unknowns_are_distinct_from_measured_zero(self):
        entries = report(ledger('| A | - | - | - | - | - |',
                                '| B | 2026 | 0 | 0/8 | | |'), AS_OF)['entries']
        self.assertIsNone(entries[0]['age_calendar_years'])
        self.assertIsNone(entries[0]['quantity'])
        self.assertIsNone(entries[0]['germination'])
        self.assertIsNone(entries[0]['sow_by'])
        self.assertEqual(entries[1]['quantity'], 0)
        self.assertEqual(entries[1]['germination']['percent'], '0.00')
        self.assertEqual(entries[1]['age_calendar_years'], 0)

    def test_explicit_and_assumed_ordering_unknowns_last(self):
        result = report(ledger('| Unknown | 2020 | 1 | - | - | - |',
                               '| Assumed | 2024 | 2 | - | - | 2 |',
                               '| Early | - | 3 | - | 2026-01-01 | - |',
                               '| alpha | - | 4 | - | 2026-12-31 | - |'), AS_OF)
        self.assertEqual([r['variety'] for r in result['entries']],
                         ['Early', 'alpha', 'Assumed', 'Unknown'])
        self.assertEqual(result['entries'][2]['sow_by'], '2026-12-31')
        self.assertEqual(result['entries'][2]['shelf_life_years'], 2)
        self.assertEqual(result['entries'][2]['sow_by_source'], 'user_shelf_life_assumption')

    def test_explicit_date_need_not_match_a_harvest_or_the_as_of_year(self):
        entry = report(ledger('| Pea | - | - | - | 2020-02-29 | - |'), AS_OF)['entries'][0]
        self.assertEqual(entry['sow_by'], '2020-02-29')

    def test_fixed_date_and_row_order_are_deterministic(self):
        a, b = '| Z | 2025 | 1 | - | - | 0 |', '| A | 2023 | 1 | - | - | - |'
        self.assertEqual(report(ledger(a, b), AS_OF), report(ledger(b, a), AS_OF))
        self.assertEqual(report(ledger(a), date(2027, 1, 1))['entries'][0]['age_calendar_years'], 2)

    def test_rejects_duplicates_including_unicode_and_case(self):
        for a, b in [('Pea', 'pea'), ('Café', 'Cafe\u0301')]:
            with self.subTest(a=a), self.assertRaisesRegex(ValueError, 'duplicate variety'):
                report(ledger(f'| {a} | - | - | - | - | - |',
                              f'| {b} | - | - | - | - | - |'), AS_OF)

    def test_rejects_invalid_cells(self):
        rows = [
            '| | 2024 | 1 | - | - | - |',
            '| Pea | 24 | 1 | - | - | - |',
            '| Pea | 0000 | 1 | - | - | - |',
            '| Pea | 2027 | 1 | - | - | - |',
            '| Pea | - | -1 | - | - | - |',
            '| Pea | - | 1.5 | - | - | - |',
            '| Pea | - | 1 | 1/0 | - | - |',
            '| Pea | - | 1 | 3/2 | - | - |',
            '| Pea | - | 1 | 1/2/3 | - | - |',
            '| Pea | - | 1 | 1 /2 | - | - |',
            '| Pea | - | 1 | - | 2026-02-29 | - |',
            '| Pea | - | 1 | - | 20261115 | - |',
            '| Pea | 2024 | 1 | - | 2026-01-01 | 2 |',
            '| Pea | - | 1 | - | - | 2 |',
            '| Pea | 2024 | 1 | - | - | 9999999999 |',
            '| Pea | 2024 | 10000000000 | - | - | - |',
        ]
        for row in rows:
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, 'line 5:'):
                report(ledger(row), AS_OF)

    def test_rejects_malformed_tables_instead_of_partial_results(self):
        valid = '| Pea | 2024 | 1 | - | - | - |'
        invalid = ['', HEADER, ledger(valid) + 'a stray paragraph',
                   ledger(valid, '| broken |'), ledger(valid).replace('quantity', 'packets'),
                   ledger(valid).replace('| --- |', '| -- |', 1),
                   ledger(valid).replace('Pea', 'P\tea')]
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ValueError):
                report(text, AS_OF)


if __name__ == '__main__':
    unittest.main()
