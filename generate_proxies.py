import requests
import re
import base64
import json
import yaml
from urllib.parse import urlparse, unquote

README_URL = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
OUTPUT_FILE = "proxies.yaml"

def fetch_readme_content(url):
    print(f"[*] Fetching content from {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        print("[+] Content downloaded successfully.")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[!] Download failed: {e}")
        return None

def extract_proxy_links(content):
    pattern = r'(vmess|ss|trojan)://[^\s`\'"]+'
    links = re.findall(pattern, content)
    print(f"[*] Found {len(links)} potential proxy links.")
    return links

def parse_link(link):
    try:
        if link.startswith('vmess://'):
            return parse_vmess(link)
        elif link.startswith('ss://'):
            return parse_ss(link)
        elif link.startswith('trojan://'):
            return parse_trojan(link)
    except Exception:
        return None
    return None

def parse_vmess(link):
    try:
        decoded_part = base64.b64decode(link[8:]).decode('utf-8')
        data = json.loads(decoded_part)
        proxy = {
            'name': data.get('ps', data.get('add', 'vmess_node')),
            'type': 'vmess', 'server': data.get('add'), 'port': int(data.get('port')),
            'uuid': data.get('id'), 'alterId': int(data.get('aid')), 'cipher': data.get('scy', 'auto'),
            'tls': data.get('tls') == 'tls', 'network': data.get('net', 'tcp'),
        }
        if proxy['tls']:
            proxy['sni'] = data.get('sni', data.get('host', ''))
            proxy['skip-cert-verify'] = True
        if proxy['network'] == 'ws':
            proxy['ws-opts'] = {'path': data.get('path', '/'), 'headers': {'Host': data.get('host', proxy['server'])}}
        return proxy
    except: return None

def parse_ss(link):
    try:
        main_part, name_part = link[5:].split('#', 1)
        name = unquote(name_part)
        if '@' in main_part:
            decoded_part = base64.b64decode(main_part).decode('utf-8')
            method, password_server = decoded_part.split(':', 1)
            password, server_port = password_server.split('@', 1)
            server, port = server_port.split(':')
        else: # ss://method:pass@server:port#name
            user_info, server_info = main_part.split('@')
            method, password = user_info.split(':')
            server, port = server_info.split(':')

        return {'name': name, 'type': 'ss', 'server': server, 'port': int(port), 'cipher': method, 'password': password}
    except: return None

def parse_trojan(link):
    try:
        parsed_url = urlparse(link)
        password = parsed_url.username
        server = parsed_url.hostname
        port = parsed_url.port
        name = unquote(parsed_url.fragment) if parsed_url.fragment else f"trojan_{server}"
        query_params = dict(p.split('=') for p in parsed_url.query.split('&') if '=' in p)
        sni = query_params.get('sni', server)
        return {'name': name, 'type': 'trojan', 'server': server, 'port': port, 'password': password, 'sni': sni, 'skip-cert-verify': True}
    except: return None

def main():
    content = fetch_readme_content(README_URL)
    if not content: return

    links = extract_proxy_links(content)
    proxies = [p for p in (parse_link(link) for link in links) if p]
    
    print(f"[+] Successfully parsed {len(proxies)} nodes.")

    # Create a dictionary with a single 'proxies' key
    clash_config_part = {'proxies': proxies}

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(clash_config_part, f, allow_unicode=True, sort_keys=False, indent=2)

    print(f"\n[✓] Success! Proxy list has been saved to: {OUTPUT_FILE}")
    
if __name__ == "__main__":
    main()
