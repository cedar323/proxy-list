import requests
import yaml
import re
from collections import defaultdict

# --- 配置区 ---
SOURCE_URL = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
OUTPUT_FILE = "proxies.yaml"
# 默认密码
DEFAULT_PASSWORD = "1"

COUNTRY_FLAG_MAP = {
    '阿尔及利亚': '🇩🇿', '阿拉伯联合酋长国': '🇦🇪', '阿根廷': '🇦🇷', '爱尔兰': '🇮🇪',
    '爱沙尼亚': '🇪🇪', '奥地利': '🇦🇹', '澳大利亚': '🇦🇺', '巴基斯坦': '🇵🇰',
    '巴拉圭': '🇵🇾', '巴拿马': '🇵🇦', '巴西': '🇧🇷', '白俄罗斯': '🇧🇾',
    '保加利亚': '🇧🇬', '比利时': '🇧🇪', '冰岛': '🇮🇸', '波多黎各': '🇵🇷',
    '波兰': '🇵🇱', '玻利维亚': '🇧🇴', '丹麦': '🇩🇰', '德国': '🇩🇪',
    '厄瓜多尔': '🇪🇨', '俄罗斯': '🇷🇺', '法国': '🇫🇷', '菲律宾': '🇵🇭',
    '芬兰': '🇫🇮', '格鲁吉亚': '🇬🇪', '哥伦比亚': '🇨🇴', '哥斯达黎加': '🇨🇷',
    '哈萨克斯坦': '🇰🇿', '荷兰': '🇳🇱', '洪都拉斯': '🇭🇳', '加拿大': '🇨🇦',
    '捷克': '🇨🇿', '吉尔吉斯斯坦': '🇰🇬', '肯尼亚': '🇰🇪', '克罗地亚': '🇭🇷',
    '科特迪瓦': '🇨🇮', '科威特': '🇰🇼', '拉脱维亚': '🇱🇻', '立陶宛': '🇱🇹',
    '罗马尼亚': '🇷🇴', '卢森堡': '🇱🇺', '马来西亚': '🇲🇾', '马耳他': '🇲🇹',
    '美国': '🇺🇸', '蒙古': '🇲🇳', '孟加拉国': '🇧🇩', '秘鲁': '🇵🇪',
    '摩尔多瓦': '🇲🇩', '摩洛哥': '🇲🇦', '墨西哥': '🇲🇽', '南非': '🇿🇦',
    '尼加拉瓜': '🇳🇮', '尼日利亚': '🇳🇬', '挪威': '🇳🇴', '葡萄牙': '🇵🇹',
    '日本': '🇯🇵', '瑞典': '🇸🇪', '瑞士': '🇨🇭', '塞尔维亚': '🇷🇸',
    '塞浦路斯': '🇨🇾', '沙特阿拉伯': '🇸🇦', '斯洛伐克': '🇸🇰', '斯洛文尼亚': '🇸🇮',
    '泰国': '🇹🇭', '台湾': '🇹🇼', '土耳其': '🇹🇷', '危地马拉': '🇬🇹',
    '乌克兰': '🇺🇦', '乌拉圭': '🇺🇾', '西班牙': '🇪🇸', '希腊': '🇬🇷',
    '香港': '🇭🇰', '新加坡': '🇸🇬', '新西兰': '🇳🇿', '匈牙利': '🇭🇺',
    '叙利亚': '🇸🇾', '以色列': '🇮🇱', '意大利': '🇮🇹', '印度': '🇮🇳',
    '印度尼西亚': '🇮🇩', '英国': '🇬🇧', '约旦': '🇯🇴', '越南': '🇻🇳',
    '智利': '🇨🇱', '中国': '🇨🇳', '埃及': '🇪🇬', '伊拉克': '🇮🇶'
}

def get_flag_emoji(country_name):
    """根据国家中文名返回对应的旗帜Emoji"""
    return COUNTRY_FLAG_MAP.get(country_name, '🌍')

def get_js_based_config():

    proxyName = "代理模式"

    rule_providers = {
        'reject': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt', 'path': './ruleset/reject.yaml', 'interval': 86400},
        'icloud': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt', 'path': './ruleset/icloud.yaml', 'interval': 86400},
        'apple': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt', 'path': './ruleset/apple.yaml', 'interval': 86400},
        'google': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt', 'path': './ruleset/google.yaml', 'interval': 86400},
        'proxy': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt', 'path': './ruleset/proxy.yaml', 'interval': 86400},
        'openai': {'type': 'http', 'behavior': 'classical', 'url': 'https://fastly.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/Clash/OpenAI/OpenAI.yaml', 'path': './ruleset/custom/openai.yaml'},
        'claude': {'type': 'http', 'behavior': 'classical', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.yaml', 'path': './ruleset/custom/Claude.yaml'},
        'gemini': {'type': 'http', 'behavior': 'classical', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Gemini/Gemini.yaml', 'path': './ruleset/custom/Gemini.yaml'},
        'spotify': {'type': 'http', 'behavior': 'classical', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Spotify/Spotify.yaml', 'path': './ruleset/custom/Spotify.yaml'},
        'telegramcidr': {'type': 'http', 'behavior': 'ipcidr', 'url': 'https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt', 'path': './ruleset/custom/telegramcidr.yaml'},
        'direct': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt', 'path': './ruleset/direct.yaml', 'interval': 86400},
        'private': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt', 'path': './ruleset/private.yaml', 'interval': 86400},
        'gfw': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt', 'path': './ruleset/gfw.yaml', 'interval': 86400},
        'greatfire': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/greatfire.txt', 'path': './ruleset/greatfire.yaml', 'interval': 86400},
        'tld-not-cn': {'type': 'http', 'behavior': 'domain', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt', 'path': './ruleset/tld-not-cn.yaml', 'interval': 86400},
        'cncidr': {'type': 'http', 'behavior': 'ipcidr', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt', 'path': './ruleset/cncidr.yaml', 'interval': 86400},
        'lancidr': {'type': 'http', 'behavior': 'ipcidr', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt', 'path': './ruleset/lancidr.yaml', 'interval': 86400},
        'applications': {'type': 'http', 'behavior': 'classical', 'url': 'https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt', 'path': './ruleset/applications.yaml', 'interval': 86400},
        'AWAvenue_Ads_Rule': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'interval': 86400, 'path': './ruleset/AWAvenue_Ads_Rule_Clash.yaml', 'url': 'https://raw.githubusercontent.com/TG-Twilight/AWAvenue-Ads-Rule/main//Filters/AWAvenue-Ads-Rule-Clash.yaml'},
        'blackmatrix7_ad': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'interval': 86400, 'path': './ruleset/blackmatrix7_ad.yaml', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Advertising/Advertising.yaml'},
        'blackmatrix7_direct': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'interval': 86400, 'path': './ruleset/blackmatrix7_direct.yaml', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Direct/Direct.yaml'},
        'private_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/private_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/private.mrs'},
        'cn_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/cn_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/cn.mrs'},
        'cn_ip': {'type': 'http', 'behavior': 'ipcidr', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/cn_ip.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/cn.mrs'},
        'trackerslist': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/trackerslist.mrs', 'url': 'https://github.com/DustinWin/ruleset_geodata/raw/refs/heads/mihomo-ruleset/trackerslist.mrs'},
        'proxy_from_DustinWin': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/proxy.mrs', 'url': 'https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/proxy.mrs'},
        'gfw_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/gfw_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/gfw.mrs'},
        'geolocation-!cn': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/geolocation-!cn.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/geolocation-!cn.mrs'},
        'ai': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/ai.mrs', 'url': 'https://github.com/DustinWin/ruleset_geodata/releases/download/mihomo-ruleset/ai.mrs'},
        'cloudflare': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/cloudflare.mrs', 'url': 'https://github.com/MetaCubeX/meta-rules-dat/raw/refs/heads/meta/geo/geosite/cloudflare.mrs'},
        'geoip_cloudflare': {'type': 'http', 'behavior': 'ipcidr', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/geoip_cloudflare.mrs', 'url': 'https://github.com/MetaCubeX/meta-rules-dat/raw/refs/heads/meta/geo/geoip/cloudflare.mrs'},
        'youtube_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/youtube_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/youtube.mrs'},
        'tiktok_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/tiktok_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/tiktok.mrs'},
        'netflix_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/netflix_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/netflix.mrs'},
        'disney_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/disney_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/disney.mrs'},
        'geoip_netflix': {'type': 'http', 'behavior': 'ipcidr', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/geoip_netflix.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/netflix.mrs'},
        'telegram_domain': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'interval': 86400, 'path': './ruleset/telegram_domain.yaml', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Telegram/Telegram.yaml'},
        'telegram_ip': {'type': 'http', 'behavior': 'ipcidr', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/telegram_ip.mrs', 'url': 'https://github.com/DustinWin/ruleset_geodata/raw/refs/heads/mihomo-ruleset/telegramip.mrs'},
        'Telegram_No_Resolve': {'type': 'http', 'behavior': 'classical', 'format': 'yaml', 'interval': 86400, 'path': './ruleset/Telegram_No_Resolve.yaml', 'url': 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Telegram/Telegram_No_Resolve.yaml'},
        'apple_cn_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/apple_cn_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/apple-cn.mrs'},
        'onedrive_domain': {'type': 'http', 'behavior': 'domain', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/onedrive_domain.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/onedrive.mrs'},
        'geoip_cloudfront': {'type': 'http', 'behavior': 'ipcidr', 'format': 'mrs', 'interval': 86400, 'path': './ruleset/geoip_cloudfront.mrs', 'url': 'https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/cloudfront.mrs'},
    }
    
    rules = [
        f"DOMAIN-SUFFIX,copilot.microsoft.com,{proxyName}", "DOMAIN-SUFFIX,linux.do,DIRECT", "DOMAIN-SUFFIX,oaifree.com,DIRECT", "DOMAIN-SUFFIX,bing.com,DIRECT", "DOMAIN-SUFFIX,live.com,DIRECT", "DOMAIN-SUFFIX,microsoft.com,DIRECT", "DOMAIN-SUFFIX,oracle.com,DIRECT", f"DOMAIN-KEYWORD,browserleaks,{proxyName}", "RULE-SET,AWAvenue_Ads_Rule,广告拦截", "RULE-SET,reject, 广告拦截", "RULE-SET,direct,DIRECT", "RULE-SET,cncidr,DIRECT", "RULE-SET,cn_ip,DIRECT,no-resolve", "RULE-SET,geoip_cloudfront,DIRECT,no-resolve", "RULE-SET,private,DIRECT", "RULE-SET,lancidr,DIRECT", "GEOIP,LAN,DIRECT,no-resolve", "GEOIP,CN,DIRECT,no-resolve", "RULE-SET,applications,DIRECT", "DOMAIN-SUFFIX,julebu.co,DIRECT", "RULE-SET,blackmatrix7_direct,DIRECT", "RULE-SET,private_domain,DIRECT", "RULE-SET,cn_domain,DIRECT", "DOMAIN-SUFFIX,apple.com,DIRECT", "DOMAIN-SUFFIX,icloud.com,DIRECT", "DOMAIN-SUFFIX,cdn-apple.com,DIRECT", "RULE-SET,apple_cn_domain,DIRECT", "DOMAIN-SUFFIX,ls.apple.com,DIRECT", f"RULE-SET,telegram_ip,{proxyName},no-resolve", f"RULE-SET,Telegram_No_Resolve,{proxyName},no-resolve", f"RULE-SET,geoip_cloudflare,{proxyName},no-resolve", f"RULE-SET,geoip_netflix,{proxyName},no-resolve", f"RULE-SET,ai,{proxyName}", f"RULE-SET,openai,{proxyName}", f"RULE-SET,claude,{proxyName}", f"RULE-SET,gemini,{proxyName}", f"RULE-SET,telegramcidr,{proxyName},no-resolve", f"RULE-SET,telegram_domain,{proxyName}", f"RULE-SET,youtube_domain,{proxyName}", f"RULE-SET,tiktok_domain,{proxyName}", f"RULE-SET,netflix_domain,{proxyName}", f"RULE-SET,disney_domain,{proxyName}", f"RULE-SET,spotify,{proxyName}", f"RULE-SET,google,{proxyName}", f"RULE-SET,icloud,{proxyName}", f"RULE-SET,apple,{proxyName}", f"RULE-SET,gfw_domain,{proxyName}", f"RULE-SET,geolocation-!cn,{proxyName}", f"RULE-SET,tld-not-cn,{proxyName}", f"RULE-SET,gfw,{proxyName}", f"RULE-SET,greatfire,{proxyName}", f"RULE-SET,proxy_from_DustinWin,{proxyName}", f"RULE-SET,proxy,{proxyName}", "MATCH, 漏网之鱼",
    ]
    
    predefined_groups = [
        {'name': proxyName, 'type': 'select', 'url': 'http://www.gstatic.com/generate_204', 'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/adjust.svg', 'proxies': ['自动选择', '手动选择', 'DIRECT']},
        {'name': '手动选择', 'type': 'select', 'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/link.svg', 'proxies': []},
        {'name': '自动选择', 'type': 'select', 'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/speed.svg', 'proxies': []},
        {'name': '漏网之鱼', 'type': 'select', 'proxies': ['DIRECT', proxyName], 'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/fish.svg'},
        {'name': '广告拦截', 'type': 'select', 'proxies': ['REJECT', 'DIRECT', proxyName], 'icon': 'https://fastly.jsdelivr.net/gh/clash-verge-rev/clash-verge-rev.github.io@main/docs/assets/icons/block.svg'},
    ]
    
    return {
        "rule-providers": rule_providers,
        "rules": rules,
        "predefined-groups": predefined_groups
    }

def main():
    """主函数"""
    print(f"[*] Fetching proxy data from {SOURCE_URL}...")
    try:
        response = requests.get(SOURCE_URL)
        response.raise_for_status()
        content = response.text
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching data: {e}")
        return

    pattern = re.compile(r"\|\s*([\d\.:]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|")

    proxies = []
    country_proxies = defaultdict(list)
    
    country_node_counts = defaultdict(int)

    for line in content.splitlines():
        match = pattern.match(line)
        if match:
            try:
                server_port = match.group(1).strip()
                country = match.group(2).strip()
                username = match.group(3).strip()
                
                if ':' not in server_port or not username:
                    continue
                    
                server, port = server_port.split(':', 1)
                port = int(port)

                flag = get_flag_emoji(country)
                
                # 生成带序号的节点名
                country_node_counts[country] += 1
                node_index = country_node_counts[country]
                proxy_name = f"{flag} {country} {node_index:02d}"

                proxy_config = {
                    'name': proxy_name,
                    'type': 'http',
                    'server': server,
                    'port': port,
                    'username': username,
                    'password': DEFAULT_PASSWORD
                }
                
                proxies.append(proxy_config)
                country_proxies[country].append(proxy_name)

            except (ValueError, IndexError) as e:
                print(f"[-] Skipping invalid line: {line} -> {e}")
                continue

    if not proxies:
        print("[!] No proxies found. Exiting.")
        return

    print(f"[+] Found and processed {len(proxies)} proxies with username authentication.")

    base_config = get_js_based_config()
    
    proxy_groups = []
    all_proxy_names = [p['name'] for p in proxies]

    # 按国家/地区名称排序，确保分组顺序一致
    for country in sorted(country_proxies.keys()):
        flag = get_flag_emoji(country)
        group = {
            'name': f"{flag} {country}",
            'type': 'url-test',
            'proxies': sorted(country_proxies[country]),
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300,
            'lazy': True
        }
        proxy_groups.append(group)
    
    print(f"[+] Automatically generated {len(proxy_groups)} country groups (as url-test).")
    
    country_group_names = [g['name'] for g in proxy_groups]
    for group in base_config['predefined-groups']:
        if group['name'] == '自动选择':
            group['proxies'].extend(country_group_names)

    for group in base_config['predefined-groups']:
        if group['name'] == '手动选择':
            group['proxies'] = all_proxy_names

    predefined_groups = base_config['predefined-groups']
    final_proxy_groups = []
    try:
        insert_index = next(i for i, group in enumerate(predefined_groups) if group['name'] == '漏网之鱼')
        final_proxy_groups = predefined_groups[:insert_index] + proxy_groups + predefined_groups[insert_index:]
        print("[+] Successfully inserted country groups before '漏网之鱼'.")
    except StopIteration:
        print("[!] Warning: '漏网之鱼' group not found. Appending country groups to the end.")
        final_proxy_groups = predefined_groups + proxy_groups

    clash_config = {
        'proxies': proxies,
        'proxy-groups': final_proxy_groups,
        'rules': base_config['rules'],
        'rule-providers': base_config['rule-providers'],
    }

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
        print(f"[✔] Successfully generated Clash config at: {OUTPUT_FILE}")
    except Exception as e:
        print(f"[!] Error writing to file: {e}")

if __name__ == "__main__":
    main()
