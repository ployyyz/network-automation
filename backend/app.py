from flask import Flask, request, jsonify
from flask_cors import CORS
import paramiko
import time

app = Flask(__name__)
CORS(app)

ROUTER_USERNAME = "admin"
ROUTER_PASSWORD = "cisco"
ROUTER_PORT = 22

def translate_cisco_command(cmd):
    cmd_lower = cmd.strip().lower()
    mapping = {
        'show ip interface brief': 'ip -br addr show',
        'show ip int br': 'ip -br addr show',
        'show ip interface': 'ip addr show',
        'show interfaces': 'ip addr show',
        'show ip route': 'ip route show',
        'show version': 'cat /etc/os-release',
    }
    return mapping.get(cmd_lower, cmd)

def format_cisco_output(command, raw_output):
    cmd_lower = command.strip().lower()
    if cmd_lower in ['show ip interface brief', 'show ip int br']:
        result = f"{command}\n"
        result += f"{'Interface':<16}{'IP-Address':<18}{'OK?':<6}{'Method':<8}{'Status':<8}{'Protocol':<8}\n"
        for line in raw_output.split('\n'):
            line = line.strip()
            if not line or ('lo' not in line and 'eth' not in line):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            iface_raw = parts[0].split('@')[0]
            if iface_raw == 'lo':
                iface = 'Loopback0'
            elif iface_raw.startswith('eth'):
                iface = 'FastEthernet0/0'
            else:
                iface = iface_raw
            ip = parts[2].split('/')[0] if len(parts) > 2 else 'unassigned'
            status = 'up' if 'UP' in line.upper() else 'down'
            result += f"{iface:<16}{ip:<18}{'YES':<6}{'manual':<8}{status:<8}{status:<8}\n"
        result += f"\nR1#"
        return result
    return f"{command}\n{raw_output}\nR1#"

def ssh_to_router(router_ip, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        host = router_ip
        port = ROUTER_PORT
        if ':' in router_ip:
            host, port_str = router_ip.split(':')
            port = int(port_str)
        if host in ('localhost', '127.0.0.1'):
            host = 'ploy-router'
            port = 22
        client.connect(
            hostname=host, port=port,
            username=ROUTER_USERNAME, password=ROUTER_PASSWORD,
            look_for_keys=False, allow_agent=False, timeout=10
        )
        shell = client.invoke_shell()
        time.sleep(1)
        if shell.recv_ready():
            shell.recv(65535)
        actual_cmd = translate_cisco_command(command)
        shell.send(actual_cmd + "\n")
        time.sleep(2)
        output = ""
        while shell.recv_ready():
            output += shell.recv(65535).decode('utf-8', errors='ignore')
            time.sleep(0.5)
        client.close()
        return format_cisco_output(command, output)
    except Exception as e:
        client.close()
        raise Exception(f"SSH connection failed: {str(e)}")

@app.route('/api/execute', methods=['POST'])
def execute():
    data = request.get_json()
    if not data or 'router_ip' not in data or 'command' not in data:
        return jsonify({"status": "error", "error": "Missing router_ip or command"}), 400
    try:
        output = ssh_to_router(data['router_ip'], data['command'])
        return jsonify({"status": "success", "output": output})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
