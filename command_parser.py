import re
import json
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

class CommandParser:
    def __init__(self):
        self.intent_patterns = {
            '打开应用': [
                r'打开(.+)',
                r'启动(.+)',
                r'运行(.+)',
                r'开启(.+)',
                r'打開(.+)',
                r'啟動(.+)',
            ],
            '搜索': [
                r'搜索(.+)',
                r'查找(.+)',
                r'找一下(.+)',
                r'搜一下(.+)',
                r'帮我搜索(.+)',
                r'帮我查一下(.+)',
                r'查一下(.+)',
                r'查(.+)',
                r'搜(.+)',
                r'google(.+)',
                r'百度(.+)',
                r'上网查(.+)',
                r'网上搜(.+)',
                r'网上查找(.+)',
                r'请搜索(.+)',
                r'帮我找(.+)',
                r'帮我查(.+)',
                r'请问(.+)',
                r'什么(.+)',
                r'介绍(.+)',
                r'了解(.+)',
                r'查看(.+)'
            ],
            '关闭应用': [
                r'关闭(.+)',
                r'退出(.+)',
                r'停止(.+)',
                r'關閉(.+)',
                r'关机'
            ],
            '系统控制': [
                r'截图',
                r'截屏',
                r'锁屏',
                r'重启',
                r'睡眠'
            ],
            '音乐控制': [
                r'播放(.+)',
                r'暂停',
                r'停止播放',
                r'下一首',
                r'上一首',
                r'上一曲',
                r'下一曲'
            ],
            '音量控制': [
                r'音量(.+)',
                r'声音(.+)',
                r'调大音量',
                r'调小音量',
                r'静音'
            ],
            '文件操作': [
                r'打开文件(.+)',
                r'显示(.+)文件夹',
                r'打开(.+)目录'
            ]
        }

        self.app_aliases = {
            '微信': 'wechat',
            'QQ': 'qq',
            '钉钉': 'dingtalk',
            '淘宝': 'taobao',
            '支付宝': 'alipay',
            '抖音': 'douyin',
            '哔哩哔哩': 'bilibili',
            '网易云': 'cloudmusic',
            '音乐': 'cloudmusic',
            '计算器': 'calc',
            '记事本': 'notepad',
            '画图': 'mspaint',
            '浏览器': 'browser',
            '设置': 'settings',
            '文件管理器': 'explorer',
            '我的电脑': 'explorer',
            '控制面板': 'control',
            '瀏覽器': 'browser',
            '計算器': 'calc',
            '記事本': 'notepad',
            '畫圖': 'mspaint',
            '設置': 'settings',
            '檔案管理器': 'explorer',
            '我的電腦': 'explorer',
            '刘览器': 'browser',
            '流览器': 'browser',
            '流暖器': 'browser',
            '刘暖器': 'browser',
            '计萛器': 'calc',
            '计筫器': 'calc',
        }

        self.command_corrections = {
            '打開': '打开',
            '啟動': '启动',
            '關閉': '关闭',
            '瀏覽': '浏览',
            '劉览': '浏览',
            '流览': '浏览',
            '流暖': '浏览',
            '刘暖': '浏览',
            '计萛': '计算',
            '计筫': '计算',
            '記事': '记事',
            '畫圖': '画图',
            '設置': '设置',
            '電腦': '电脑',
        }

        self.common_apps = {
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'wechat': 'C:\\Program Files\\Tencent\\Weixin\\Weixin.exe',
            'qq': 'C:\\Program Files\\Tencent\\QQNT\\QQ.exe',
            'notepad': 'notepad.exe',
            'calc': 'calc.exe',
            'explorer': 'explorer.exe',
            'mspaint': 'mspaint.exe',
            'word': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE',
            'excel': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE',
            'powershell': 'powershell.exe',
            'cmd': 'cmd.exe',
            'taskmgr': 'taskmgr.exe',
            'control': 'control.exe',
            'settings': 'ms-settings:'
        }

        self.search_engines = {
            'google': 'https://www.google.com/search?q=',
            'baidu': 'https://www.baidu.com/s?wd=',
            'bing': 'https://www.bing.com/search?q=',
            'default': 'https://www.bing.com/search?q='
        }

    def correct_text(self, text: str) -> str:
        corrected = text
        for wrong, right in self.command_corrections.items():
            corrected = corrected.replace(wrong, right)
        return corrected

    def parse(self, text: str) -> Optional[Dict]:
        text = text.strip()

        if not text:
            return None

        original_text = text
        text = self.correct_text(text)
        
        if text != original_text:
            print(f"  文本纠错: '{original_text}' -> '{text}'")

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    params = self._extract_params(text, intent, match)
                    return {
                        'intent': intent,
                        'params': params,
                        'original_text': original_text,
                        'corrected_text': text,
                        'confidence': 0.9
                    }

        return {
            'intent': 'unknown',
            'params': {'raw_text': text},
            'original_text': original_text,
            'corrected_text': text,
            'confidence': 0.5
        }

    def _extract_params(self, text: str, intent: str, match) -> Dict:
        params = {}

        if intent == '打开应用':
            app_name = match.group(1).strip()
            params['app_name'] = self._normalize_app_name(app_name)
            params['original_name'] = app_name

        elif intent == '搜索':
            if match.lastindex and match.group(1):
                params['query'] = match.group(1).strip()
            else:
                query_text = text
                for pattern in self.intent_patterns['搜索']:
                    query_text = re.sub(pattern, '', query_text).strip()
                    if query_text:
                        break
                params['query'] = query_text if query_text else text

            if 'google' in text.lower():
                params['engine'] = 'google'
            elif '百度' in text:
                params['engine'] = 'baidu'
            elif '必应' in text or 'bing' in text.lower():
                params['engine'] = 'bing'
            else:
                params['engine'] = 'default'

        elif intent == '关闭应用':
            if match.lastindex:
                params['app_name'] = match.group(1).strip()
            else:
                params['close_system'] = True

        elif intent == '系统控制':
            params['action'] = text

        elif intent == '音乐控制':
            if '播放' in text and match.lastindex:
                params['song'] = match.group(1).strip()
                params['action'] = 'play'
            else:
                params['action'] = text

        elif intent == '音量控制':
            if '调大' in text or '增加' in text:
                params['action'] = 'increase'
            elif '调小' in text or '降低' in text:
                params['action'] = 'decrease'
            elif '静音' in text:
                params['action'] = 'mute'
            else:
                params['action'] = 'set'

        elif intent == '文件操作':
            params['path'] = match.group(1).strip()

        return params

    def _normalize_app_name(self, app_name: str) -> str:
        for alias, normalized in self.app_aliases.items():
            if alias in app_name:
                return normalized

        app_lower = app_name.lower()
        for common_name, path in self.common_apps.items():
            if common_name in app_lower:
                return common_name

        return app_name

    def extract_keywords(self, text: str) -> List[str]:
        stop_words = {'的', '了', '一下', '帮我', '请', '打开', '搜索', '查找', '请问', '什么', '介绍', '了解', '查看'}
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text)
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        return keywords

    def is_question(self, text: str) -> bool:
        question_patterns = [
            r'[吗?]',
            r'是不是',
            r'能不能',
            r'会不会',
            r'可以帮我',
            r'请问'
        ]
        return any(re.search(p, text) for p in question_patterns)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {
            'apps': [],
            'files': [],
            'keywords': [],
            'urls': []
        }

        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        entities['urls'].extend(urls)

        for alias, normalized in self.app_aliases.items():
            if alias in text:
                entities['apps'].append(alias)

        entities['keywords'] = self.extract_keywords(text)

        return entities

    def validate_command(self, parsed_command: Dict) -> Tuple[bool, str]:
        intent = parsed_command.get('intent')
        params = parsed_command.get('params', {})

        if intent == '打开应用':
            if 'app_name' not in params:
                return False, "未指定要打开的应用程序"

        elif intent == '搜索':
            if 'query' not in params or not params['query']:
                return False, "未指定搜索关键词"
            if len(params['query']) < 2:
                return False, "搜索关键词太短"

        elif intent == '关闭应用':
            if 'app_name' not in params and not params.get('close_system'):
                return False, "未指定要关闭的应用程序"

        return True, "命令有效"

    def generate_response(self, parsed_command: Dict, success: bool = True) -> str:
        intent = parsed_command.get('intent')
        original_text = parsed_command.get('original_text', '')

        if not success:
            return f"抱歉，我无法执行 '{original_text}'"

        if intent == '打开应用':
            app_name = parsed_command['params'].get('original_name', '')
            return f"正在打开 {app_name}..."

        elif intent == '搜索':
            query = parsed_command['params'].get('query', '')
            return f"正在搜索: {query}"

        elif intent == '关闭应用':
            app_name = parsed_command['params'].get('app_name', '系统')
            return f"正在关闭 {app_name}..."

        elif intent == '系统控制':
            return "正在执行系统命令..."

        elif intent == '音乐控制':
            action = parsed_command['params'].get('action', '')
            return f"正在{action}..."

        elif intent == '音量控制':
            action = parsed_command['params'].get('action', '')
            return f"正在{action}音量..."

        elif intent == '文件操作':
            return "正在打开文件..."

        elif intent == 'unknown':
            keywords = self.extract_keywords(original_text)
            if keywords:
                return f"正在搜索: {' '.join(keywords)}"
            return f"我理解了 '{original_text}'，将进行网络搜索"

        return "命令已执行"
