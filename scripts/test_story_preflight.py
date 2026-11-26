"""Focus on distinctions that influence the resulting editorial cut."""
import copy
import json
import unittest
from pathlib import Path

from story_preflight import ROUTES, validate


EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'


def example(name):
    return json.loads((EXAMPLES / f'artemis-{name}.json').read_text(encoding='utf-8'))


class Preflight(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(validate(example('event-intro'))['structure'], 'event_intro')
        self.assertEqual(validate(example('reverse'))['structure'], 'reverse_chronology')

    def test_wrong_reverse_order(self):
        m = example('reverse')
        m['beats'][1]['event_date'] = '2022-11-15'
        m['beats'][1]['detail'] = '2022-11-15'
        with self.assertRaisesRegex(ValueError, 'descending'):
            validate(m)

    def test_false_source_attribution(self):
        m = example('event-intro')
        del m['editorial']['facts']['quote']['attribution']
        with self.assertRaisesRegex(ValueError, 'attribute'):
            validate(m)

    def test_failed_label(self):
        m = example('reverse')
        m['beats'][1]['detail'] = '日期不详'
        with self.assertRaisesRegex(ValueError, 'display the date'):
            validate(m)

    def test_quotes_demand_exact_original(self):
        m = example('event-intro')
        m['beats'][3]['quote_mode'] = 'direct'
        with self.assertRaisesRegex(ValueError, 'original wording'):
            validate(m)

    def test_future_source_not_in_archive(self):
        m = example('event-intro')
        m['editorial']['facts']['next']['available_on'] = '2024-12-11'
        with self.assertRaisesRegex(ValueError, 'was not available'):
            validate(m)

    def test_each_role_defined(self):
        for route, options in ROUTES.items():
            if route in ('event_intro','reverse_chronology'):
                continue
            with self.subTest(route=route):
                m = example('event-intro')
                m['editorial']['structure'] = route
                template = m['beats'][2]
                m['beats'] = []
                order = list(options[0])
                if route == 'explainer':
                    order.insert(1, 'mechanism')
                dates = {'news':'2022-12-11','turn':'2022-11-16',
                         'origin':'2022-11-16','development':'2022-12-05',
                         'return':'2022-12-11','outcome':'2022-12-11'}
                for role in order:
                    b = copy.deepcopy(template)
                    b.update(role=role,event_date=dates.get(role,'2022-12-11'))
                    b['detail'] = b['event_date']
                    m['beats'].append(b)
                self.assertEqual(validate(m)['structure'], route)


if __name__ == '__main__':
    unittest.main()
