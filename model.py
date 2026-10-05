"""Educational L3/L4 policy simulator; does not transmit network packets."""
from ipaddress import ip_address, ip_network

PUBLIC = '203.0.113.2'
DNS = '8.8.8.8'
WEB = '198.51.100.10'
JUMP = '192.168.30.10'
SCADA = '192.168.20.10'

def zone(address):
    ip = ip_address(address)
    for name, net in [('Corporate', '192.168.10.0/24'), ('Factory OT', '192.168.20.0/24'), ('Admin', '192.168.30.0/24')]:
        if ip in ip_network(net):
            return name
    if ip.is_global or ip in ip_network('198.51.100.0/24') or ip in ip_network('203.0.113.0/24'):
        return 'Internet'
    return 'Unknown'

class Firewall:
    def __init__(self):
        self.sessions = {}
        self.translations = []
        self.events = []
        self.next_port = 10001

    def evaluate(self, source, destination, protocol='TCP', port=443, source_port=51234):
        if not isinstance(protocol, str):
            raise ValueError('Protocol must be TCP, UDP, or ICMP')
        protocol = protocol.upper()
        ip_address(source)
        ip_address(destination)
        if protocol not in ('TCP', 'UDP', 'ICMP'):
            raise ValueError('Protocol must be TCP, UDP, or ICMP')
        if type(port) is not int or type(source_port) is not int or not 1 <= port <= 65535 or not 1 <= source_port <= 65535:
            raise ValueError('Ports must be integers from 1 to 65535')
        src, dst = zone(source), zone(destination)
        allow, rule = False, 'Default deny'
        if destination in ('192.168.10.1', '192.168.20.1', '192.168.30.1'):
            allow = source == JUMP and protocol == 'TCP' and port == 22
            rule = 'Gateway VTY restricted to jump host SSH' if allow else 'Block gateway management'
        elif src == dst and src in ('Corporate', 'Factory OT', 'Admin'):
            allow, rule = True, 'Same VLAN: gateway is bypassed (no firewall isolation within a zone)'
        elif protocol == 'TCP' and port == 23:
            rule = 'Block Telnet'
        elif src == 'Corporate' and dst in ('Factory OT', 'Admin'):
            rule = 'Block Corporate lateral movement'
        elif src == 'Factory OT':
            rule = 'Block OT-initiated traffic across zones'
        elif src == 'Internet':
            rule = 'Block unsolicited Internet traffic'
        elif source == JUMP and dst in ('Corporate', 'Factory OT', 'Admin') and protocol == 'TCP' and port == 22:
            allow, rule = True, 'Jump host SSH management'
        elif source == JUMP and destination == SCADA and protocol == 'TCP' and port == 3389:
            allow, rule = True, 'Jump host SCADA RDP'
        elif src in ('Corporate', 'Admin') and dst == 'Internet':
            if protocol == 'TCP' and port == 443:
                allow, rule = True, 'Outbound HTTPS'
            elif protocol == 'UDP' and port == 53 and destination == DNS:
                allow, rule = True, 'DNS to approved resolver'
            elif protocol == 'ICMP' and destination == WEB:
                allow, rule = True, 'Lab-only external ping'
        result = dict(source=source, destination=destination, protocol=protocol, port=port,
                      source_port=source_port, source_zone=src, destination_zone=dst,
                      action='PERMIT' if allow else 'DENY', rule=rule, nat=None)
        if allow and src != dst:
            key = (source, source_port, destination, port, protocol)
            if key not in self.sessions:
                self.sessions[key] = None
                if dst == 'Internet':
                    self.sessions[key] = self.next_port
                    self.next_port += 1
                    self.translations.append(dict(inside_local=f'{source}:{source_port}', inside_global=f'{PUBLIC}:{self.sessions[key]}', outside=f'{destination}:{port}', protocol=protocol))
            if self.sessions[key] is not None:
                result['nat'] = f'{PUBLIC}:{self.sessions[key]}'
        self.events.append(result)
        return result

    def reply(self, source, destination, protocol, source_port, destination_port):
        """Reverse flow lookup illustrates state tracking, not Cisco stateless ACLs."""
        protocol = protocol.upper()
        for (client, client_port, server, server_port, proto), mapped_port in self.sessions.items():
            expected_destination = PUBLIC if mapped_port is not None else client
            expected_port = mapped_port if mapped_port is not None else client_port
            if (source, destination, protocol, source_port, destination_port) == (server, expected_destination, proto, server_port, expected_port):
                return dict(action='PERMIT', rule='Matching simulated session', delivered_to=f'{client}:{client_port}')
        return dict(action='DENY', rule='No matching simulated session')

SCENARIOS = [
    ('Corporate HTTPS + PAT', '192.168.10.50', WEB, 'TCP', 443, 'PERMIT'),
    ('Second workstation HTTPS + PAT', '192.168.10.51', WEB, 'TCP', 443, 'PERMIT'),
    ('Approved DNS', '192.168.10.50', DNS, 'UDP', 53, 'PERMIT'),
    ('Corporate to SCADA', '192.168.10.50', SCADA, 'TCP', 3389, 'DENY'),
    ('Corporate to PLC', '192.168.10.50', '192.168.20.50', 'TCP', 502, 'DENY'),
    ('Corporate to Admin', '192.168.10.50', JUMP, 'TCP', 22, 'DENY'),
    ('Jump host gateway SSH', JUMP, '192.168.30.1', 'TCP', 22, 'PERMIT'),
    ('Jump host OT SSH', JUMP, SCADA, 'TCP', 22, 'PERMIT'),
    ('Jump host SCADA RDP', JUMP, SCADA, 'TCP', 3389, 'PERMIT'),
    ('Other admin cannot manage OT', '192.168.30.11', SCADA, 'TCP', 3389, 'DENY'),
    ('Telnet across zones', JUMP, SCADA, 'TCP', 23, 'DENY'),
    ('OT Internet access', SCADA, WEB, 'TCP', 443, 'DENY'),
    ('Unsolicited Internet', WEB, PUBLIC, 'TCP', 22, 'DENY'),
    ('Unauthorized egress', '192.168.10.50', WEB, 'TCP', 4444, 'DENY'),
    ('Unapproved DNS', '192.168.10.50', '1.1.1.1', 'UDP', 53, 'DENY'),
    ('Lab external ping', '192.168.10.50', WEB, 'ICMP', 1, 'PERMIT'),
]

def run_demo():
    fw = Firewall()
    results = []
    for name, source, destination, protocol, port, expected in SCENARIOS:
        result = fw.evaluate(source, destination, protocol, port)
        results.append(dict(name=name, expected=expected, passed=result['action'] == expected, **result))
    return fw, results
