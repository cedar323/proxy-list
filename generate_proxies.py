import requests
import yaml
import re
import os
import sys
from collections import defaultdict
from datetime import datetime

# --- 配置区 ---
SOURCE_URL = "https://raw.githubusercontent.com/TopChina/proxy-list/main/README.md"
OUTPUT_FILE = "proxies.yaml"
LAST_UPDATE_FILE = "last_update_time.txt"
# 默认密码
DEFAULT_PASSWORD = "1"

COUNTRY_FLAG_MAP = {
    # 亚洲
        "中国": "🇨🇳", "香港": "🇭🇰", "澳门": "🇲🇴", "台湾": "🇹🇼",
        "日本": "🇯🇵", "韩国": "🇰🇷", "朝鲜": "🇰🇵", "蒙古": "🇲🇳",
        "新加坡": "🇸🇬", "马来西亚": "🇲🇾", "泰国": "🇹🇭", "越南": "🇻🇳",
        "菲律宾": "🇵🇭", "印度尼西亚": "🇮🇩", "文莱": "🇧🇳", "柬埔寨": "🇰🇭",
        "老挝": "🇱🇦", "缅甸": "🇲🇲", "东帝汶": "🇹🇱",
        "印度": "🇮🇳", "巴基斯坦": "🇵🇰", "孟加拉国": "🇧🇩", "尼泊尔": "🇳🇵", # 修正了拼写
        "不丹": "🇧🇹", "斯里兰卡": "🇱🇰", "马尔代夫": "🇲🇻",
        "哈萨克斯坦": "🇰🇿", "乌兹别克斯坦": "🇺🇿", "吉尔吉斯斯坦": "🇰🇬", "塔吉克斯坦": "🇹🇯", "土库曼斯坦": "🇹🇲",
        "阿富汗": "🇦🇫", "伊朗": "🇮🇷", "伊拉克": "🇮🇶", "叙利亚": "🇸🇾",
        "约旦": "🇯🇴", "黎巴嫩": "🇱🇧", "巴勒斯坦": "🇵🇸", "以色列": "🇮🇱",
        "沙特阿拉伯": "🇸🇦", "阿拉伯联合酋长国": "🇦🇪", "阿联酋": "🇦🇪", "卡塔尔": "🇶🇦",
        "科威特": "🇰🇼", "巴林": "🇧🇭", "阿曼": "🇴🇲", "也门": "🇾🇪",
        "土耳其": "🇹🇷", "塞浦路斯": "🇨🇾", "格鲁吉亚": "🇬🇪", "亚美尼亚": "🇦🇲", "阿塞拜疆": "🇦🇿",
        # 欧洲
        "俄罗斯": "🇷🇺", "乌克兰": "🇺🇦", "白俄罗斯": "🇧🇾", "摩尔多瓦": "🇲🇩",
        "英国": "🇬🇧", "爱尔兰": "🇮🇪", "法国": "🇫🇷", "德国": "🇩🇪",
        "荷兰": "🇳🇱", "比利时": "🇧🇪", "卢森堡": "🇱🇺", "瑞士": "🇨🇭",
        "奥地利": "🇦🇹", "列支敦士登": "🇱🇮",
        "西班牙": "🇪🇸", "葡萄牙": "🇵🇹", "意大利": "🇮🇹", "希腊": "🇬🇷",
        "梵蒂冈": "🇻🇦", "圣马力诺": "🇸🇲", "马耳他": "🇲🇹", "安道尔": "🇦🇩",
        "挪威": "🇳🇴", "瑞典": "🇸🇪", "芬兰": "🇫🇮", "丹麦": "🇩🇰", "冰岛": "🇮🇸",
        "波兰": "🇵🇱", "捷克": "🇨🇿", "斯洛伐克": "🇸🇰", "匈牙利": "🇭🇺",
        "罗马尼亚": "🇷🇴", "保加利亚": "🇧🇬", "塞尔维亚": "🇷🇸", "克罗地亚": "🇭🇷",
        "斯洛文尼亚": "🇸🇮", "波斯尼亚和黑塞哥维那": "🇧🇦", "波黑": "🇧🇦", "黑山": "🇲🇪",
        "北马其顿": "🇲🇰", "阿尔巴尼亚": "🇦🇱", "科索沃": "🇽🇰",
        "立陶宛": "🇱🇹", "拉脱维亚": "🇱🇻", "爱沙尼亚": "🇪🇪",
        # 北美洲
        "美国": "🇺🇸", "加拿大": "🇨🇦", "墨西哥": "🇲🇽",
        "格陵兰": "🇬🇱", "百慕大": "🇧🇲",
        "危地马拉": "🇬🇹", "伯利兹": "🇧🇿", "萨尔瓦多": "🇸🇻", "洪都拉斯": "🇭🇳",
        "尼加拉瓜": "🇳🇮", "哥斯达黎加": "🇨🇷", "巴拿马": "🇵🇦",
        "古巴": "🇨🇺", "牙买加": "🇯🇲", "海地": "🇭🇹", "多米尼加": "🇩🇴",
        "波多黎各": "🇵🇷",
        # 南美洲
        "巴西": "🇧🇷", "阿根廷": "🇦🇷", "智利": "🇨🇱", "哥伦比亚": "🇨🇴",
        "秘鲁": "🇵🇪", "委内瑞拉": "🇻🇪", "厄瓜多尔": "🇪🇨", "玻利维亚": "🇧🇴",
        "巴拉圭": "🇵🇾", "乌拉圭": "🇺🇾", "圭亚那": "🇬🇾", "苏里南": "🇸🇷",
        # 非洲
        "埃及": "🇪🇬", "利比亚": "🇱🇾", "苏丹": "🇸🇩", "突尼斯": "🇹🇳",
        "阿尔及利亚": "🇩🇿", "摩洛哥": "🇲🇦",
        "埃塞俄比亚": "🇪🇹", "索马里": "🇸🇴", "肯尼亚": "🇰🇪", "坦桑尼亚": "🇹🇿",
        "乌干达": "🇺🇬", "卢旺达": "🇷🇼",
        "尼日利亚": "🇳🇬", "加纳": "🇬🇭", "科特迪瓦": "🇨🇮", "塞内加尔": "🇸🇳",
        "南非": "🇿🇦", "津巴布韦": "🇿🇼", "赞比亚": "🇿🇲", "纳米比亚": "🇳🇦", "博茨瓦纳": "🇧🇼",
        # 大洋洲
        "澳大利亚": "🇦🇺", "新西兰": "🇳🇿", "斐济": "🇫🇯", "巴布亚新几内亚": "🇵🇬",
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

def extract_update_time(content):
    """从README内容中提取更新时间"""
    # 匹配格式：2025年08月18日 07:20, 本次发布有效代理309个
    patterns = [
        r'(\d{4}年\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2}),\s*本次发布有效代理\d+个',
        r'(\d{4}年\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2})',  # 备用匹配
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            update_time = match.group(1).strip()
            print(f"[+] Found update time: {update_time}")
            return update_time
    
    print("[!] Could not find update time in content")
    # 调试：打印一些内容帮助定位问题
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '更新' in line or '代理' in line:
            print(f"[DEBUG] Line {i}: {line}")
    return None

def read_last_update_time():
    """读取上次记录的更新时间"""
    try:
        if os.path.exists(LAST_UPDATE_FILE):
            with open(LAST_UPDATE_FILE, 'r', encoding='utf-8') as f:
                last_time = f.read().strip()
                print(f"[*] Last recorded update time: {last_time}")
                return last_time
        else:
            print("[*] No previous update time record found")
            return None
    except Exception as e:
        print(f"[!] Error reading last update time: {e}")
        return None

def save_update_time(update_time):
    """保存当前的更新时间"""
    try:
        with open(LAST_UPDATE_FILE, 'w', encoding='utf-8') as f:
            f.write(update_time)
        print(f"[+] Saved new update time: {update_time}")
    except Exception as e:
        print(f"[!] Error saving update time: {e}")

def check_for_updates(content):
    """检查是否有更新"""
    current_update_time = extract_update_time(content)
    if not current_update_time:
        print("[!] Cannot determine current update time, forcing update")
        return True, current_update_time
    
    last_update_time = read_last_update_time()
    if not last_update_time:
        print("[*] No previous update time, proceeding with update")
        return True, current_update_time
    
    if current_update_time == last_update_time:
        print(f"[=] No update needed. Current time: {current_update_time} matches last time: {last_update_time}")
        return False, current_update_time
    else:
        print(f"[+] Update detected! Current: {current_update_time}, Last: {last_update_time}")
        return True, current_update_time
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

    # 检查是否需要更新
    needs_update, current_time = check_for_updates(content)
    if not needs_update:
        print("[=] No update needed, exiting.")
        sys.exit(0)

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
        
        # 保存当前更新时间
        if current_time:
            save_update_time(current_time)
            
    except Exception as e:
        print(f"[!] Error writing to file: {e}")

if __name__ == "__main__":
    main()
