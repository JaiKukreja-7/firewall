import unittest
from model import Firewall, PUBLIC, WEB, DNS, JUMP, SCADA, run_demo

class PolicyTests(unittest.TestCase):
    def test_scenarios(self):
        _, results = run_demo()
        for r in results:
            with self.subTest(r['name']):
                self.assertTrue(r['passed'])

    def test_pat_collision_and_reuse(self):
        f = Firewall()
        a = f.evaluate('192.168.10.50', WEB)
        b = f.evaluate('192.168.10.51', WEB)
        self.assertNotEqual(a['nat'], b['nat'])
        self.assertEqual(a['nat'], f.evaluate('192.168.10.50', WEB)['nat'])
        self.assertEqual(len(f.translations), 2)

    def test_wan_reply_only_matching_session(self):
        f = Firewall()
        self.assertEqual(f.reply(WEB, PUBLIC, 'TCP', 443, 10001)['action'], 'DENY')
        f.evaluate('192.168.10.50', WEB)
        self.assertEqual(f.reply(WEB, PUBLIC, 'TCP', 443, 10001)['delivered_to'], '192.168.10.50:51234')
        self.assertEqual(f.reply('198.51.100.11', PUBLIC, 'TCP', 443, 10001)['action'], 'DENY')
        self.assertEqual(f.reply(WEB, PUBLIC, 'TCP', 4444, 10001)['action'], 'DENY')

    def test_admin_ot_reply_and_no_ot_pat(self):
        f = Firewall()
        f.evaluate(JUMP, SCADA, 'TCP', 3389)
        self.assertEqual(f.reply(SCADA, JUMP, 'TCP', 3389, 51234)['action'], 'PERMIT')
        self.assertEqual(f.evaluate(SCADA, WEB)['action'], 'DENY')
        self.assertEqual(f.translations, [])

    def test_dns_reply(self):
        f = Firewall()
        f.evaluate('192.168.10.50', DNS, 'UDP', 53)
        self.assertEqual(f.reply(DNS, PUBLIC, 'UDP', 53, 10001)['action'], 'PERMIT')

    def test_invalid_input(self):
        for kwargs in [dict(source='bad', destination=WEB), dict(source=JUMP, destination=WEB, port=0), dict(source=JUMP, destination=WEB, protocol='FTP')]:
            with self.assertRaises(ValueError):
                Firewall().evaluate(**kwargs)

if __name__ == '__main__':
    unittest.main()
