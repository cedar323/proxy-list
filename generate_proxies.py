# generate_proxies.py
import requests
import yaml
import re
from urllib.parse import urlparse, unquote, quote

# README.md 的 Raw 链接，数据源现在是这里
README_URL = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
OUTPUT_FILE = "proxies.yaml"

def fetch_content(url):
    print(f"[*] Fetching content from {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        print("[+] Content downloaded successfully.")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[!] Download failed: {e}")
        return None

def reconstruct_and_parse_from_readme(content):
    """
    从 README.md 的 Markdown 表格中提取信息，
    重构为 vless 链接，然后解析。
    """
    # 正则表达式匹配 Markdown 表格行
    # | 144.48.39.114:8081 | 澳大利亚 | afY491o7...== |
    pattern = re.compile(r'\|\s*([\d\.:]+)\s*\|\s*([^|]+)\s*\|\s*([a-zA-Z0-9+/=_-]+)\s*\|')
    
    matches = pattern.findall(content)
    print(f"[*] Found {len(matches)} potential nodes in the README table.")
    
    proxies = []
    for match in matches:
        ip_port, location, uuid = match
        # 清理提取出的字符串
        ip_port = ip_port.strip()
        location = location.strip()
        uuid = uuid.strip()

        # 分离 IP 和端口
        if ':' not in ip_port:
            continue
        server, port_str = ip_port.split(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            continue
            
        # 构造节点名称
        name = f"VLESS_{location}_{server}"

        # 这是一个基于 VLESS + TCP 的基础配置，因为源信息有限
        # 这是最常见和基础的非 TLS 配置
        proxy_node = {
            'name': name,
            'type': 'vless',
            'server': server,
            'port': port,
            'uuid': uuid,
            'network': 'tcp',
            'tls': False,
            'udp': True, # 普遍开启 UDP 转发
            'cipher': 'auto',
            'client-fingerprint': 'chrome' # 添加指纹以提高连接成功率
        }
        proxies.append(proxy_node)
        
    return proxies

# --- 旧的解析函数不再需要，因为我们直接构造字典 ---
# 我们保留一个通用的主函数结构

def main():
    readme_content = fetch_content(README_URL)
    if not readme_content:
        return

    # 直接从 README 内容构造并解析节点
    proxies = reconstruct_and_parse_from_readme(readme_content)
    
    if not proxies:
        print("[!] No proxy nodes were parsed. The output file will be empty.")
    else:
        print(f"[+] Successfully parsed {len(proxies)} nodes.")

    clash_config_part = {'proxies': proxies}

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(clash_config_part, f, allow_unicode=True, sort_keys=False, indent=2)
        print(f"\n[✓] Success! Proxy list has been saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"[!] Failed to write to {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    main()

