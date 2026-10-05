"""Evaluate this lab's ACL subset. This is not an IOS emulator."""
import ipaddress
import unittest
from pathlib import Path

CONFIG = (Path(__file__).resolve().parents[1] / 'configs/gateway.cfg').read_text()

def address(tokens, position, ip):
    token = tokens[position]
    if token == 'any':
        return True, position + 1
    if token == 'host':
        return ip == tokens[position + 1], position + 2
    base, wildcard = map(ipaddress.IPv4Address, tokens[position:position+2])
    mask = 0xffffffff ^ int(wildcard)
    return int(ipaddress.IPv4Address(ip)) & mask == int(base) & mask, position + 2

def port(tokens, position, value):
    if position < len(tokens) and tokens[position] in ('eq', 'gt'):
        op, number = tokens[position:position+2]
        return (value == int(number) if op == 'eq' else value > int(number)), position + 2
    return True, position

def acl(name, src, dst, proto='tcp', sport=51234, dport=443, ack=False, icmp='echo'):
    active = False
    for line in CONFIG.splitlines():
        if line.startswith('ip access-list'):
            active = line.split()[-1] == name
            continue
        if not active or not line.startswith(' '):
            continue
        t = line.split()
        if not t or t[0] == 'remark':
            continue
        if t[1] not in ('ip', proto):
            continue
        match, i = address(t, 2, src)
        m, i = port(t, i, sport)
        match &= m
        m, i = address(t, i, dst)
        match &= m
        m, i = port(t, i, dport)
        match &= m
        for option in t[i:]:
            if option == 'established':
                match &= ack
            elif option in ('echo', 'echo-reply'):
                match &= option == icmp
            elif option != 'log':
                raise ValueError('Unsupported ACL option: ' + option)
        if match:
            return t[0]
    return 'deny'

class CiscoPolicyTests(unittest.TestCase):
    def test_corporate_web_and_dns(self):
        self.assertEqual(acl('CORP-INBOUND-ACL', '192.168.10.50', '198.51.100.10'), 'permit')
        self.assertEqual(acl('CORP-INBOUND-ACL', '192.168.10.50', '8.8.8.8', 'udp', dport=53), 'permit')
        self.assertEqual(acl('CORP-INBOUND-ACL', '192.168.10.50', '1.1.1.1', 'udp', dport=53), 'deny')

    def test_corporate_boundary_matrix(self):
        for host in range(1, 255):
            for dst in ['192.168.20.10', '192.168.20.50', '192.168.30.10']:
                for proto, p in [('tcp', 22), ('tcp', 23), ('tcp', 443), ('tcp', 3389), ('tcp', 502), ('udp', 53), ('icmp', 1)]:
                    self.assertEqual(acl('CORP-INBOUND-ACL', f'192.168.10.{host}', dst, proto, dport=p), 'deny')

    def test_corporate_admin_ssh_return_not_shadowed(self):
        self.assertEqual(acl('CORP-INBOUND-ACL', '192.168.10.50', '192.168.30.10', sport=22, dport=51234, ack=True), 'permit')
        self.assertEqual(acl('CORP-INBOUND-ACL', '192.168.10.50', '192.168.30.10', sport=22, dport=51234), 'deny')

    def test_ot_replies_and_egress(self):
        self.assertEqual(acl('OT-INBOUND-ACL', '192.168.20.10', '192.168.30.10', sport=3389, dport=51234, ack=True), 'permit')
        self.assertEqual(acl('OT-INBOUND-ACL', '192.168.20.50', '192.168.30.10', sport=3389, dport=51234, ack=True), 'deny')
        for proto, p in [('tcp', 443), ('udp', 53), ('icmp', 1)]:
            self.assertEqual(acl('OT-INBOUND-ACL', '192.168.20.10', '198.51.100.10', proto, dport=p), 'deny')

    def test_jump_host_restriction(self):
        for host in range(2, 255):
            action = 'permit' if host == 10 else 'deny'
            self.assertEqual(acl('ADMIN-INBOUND-ACL', f'192.168.30.{host}', '192.168.20.10', dport=3389), action)
        self.assertEqual(acl('ADMIN-INBOUND-ACL', '192.168.30.10', '192.168.20.50', dport=3389), 'deny')
        self.assertEqual(acl('ADMIN-INBOUND-ACL', '192.168.30.10', '192.168.20.50', dport=22), 'permit')

    def test_wan_pre_nat_and_stateless_limit(self):
        self.assertEqual(acl('WAN-INBOUND-ACL', '198.51.100.10', '203.0.113.2', sport=443, dport=10001, ack=True), 'permit')
        self.assertEqual(acl('WAN-INBOUND-ACL', '198.51.100.10', '192.168.10.50', sport=443, dport=51234, ack=True), 'deny')
        self.assertEqual(acl('WAN-INBOUND-ACL', '198.51.100.10', '203.0.113.2', sport=443, dport=10001), 'deny')
        # ACK permit without any prior session demonstrates why ACLs aren't SPI.
        self.assertEqual(acl('WAN-INBOUND-ACL', '198.51.100.99', '203.0.113.2', sport=443, dport=55555, ack=True), 'permit')

    def test_interfaces_and_nat_scope(self):
        self.assertIn('ip access-group OT-INBOUND-ACL in', CONFIG)
        ot_interface = CONFIG.split('interface GigabitEthernet0/1.20')[1].split('interface ')[0]
        self.assertNotIn('ip nat inside', ot_interface)
        nat_acl = CONFIG.split('ip access-list standard NAT-PERMIT-ACL')[1].split('\nip nat inside')[0]
        self.assertNotIn('192.168.20.0', nat_acl)
        self.assertIn('transport input ssh', CONFIG)
        self.assertIn('access-class VTY-ADMIN in', CONFIG)
