import subprocess
import webbrowser
import psutil
import os
import shutil
from typing import Dict, Optional

class ComputerController:
    def __init__(self):
        self.processes = {}
        self.app_paths = {
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'edge': 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
            'firefox': 'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
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
            'settings': 'ms-settings:',
            'browser': 'browser'
        }
        self.search_engines = {
            'google': 'https://www.google.com/search?q=',
            'baidu': 'https://www.baidu.com/s?wd=',
            'bing': 'https://www.bing.com/search?q=',
            'default': 'https://www.bing.com/search?q='
        }
        self._system_commands = ['notepad.exe', 'calc.exe', 'explorer.exe', 'mspaint.exe', 
                               'taskmgr.exe', 'control.exe', 'powershell.exe', 'cmd.exe']

    def _resolve_path(self, name: str, base_path: Optional[str] = None) -> str:
        if base_path:
            return os.path.join(base_path, name)
        return name

    def _check_exists(self, path: str, check_type: str = 'any') -> tuple[bool, str]:
        if not os.path.exists(path):
            return False, '不存在'
        if check_type == 'file' and not os.path.isfile(path):
            return False, '不是文件'
        if check_type == 'dir' and not os.path.isdir(path):
            return False, '不是文件夹'
        return True, ''

    def open_application(self, app_name: str) -> Dict[str, any]:
        try:
            app_key = app_name.lower()
            path = self.app_paths.get(app_key, app_name)
            return self._run_application(path, app_key)
        except Exception as e:
            return {'success': False, 'message': f'打开应用失败: {str(e)}'}

    def _run_application(self, path: str, app_key: str) -> Dict[str, any]:
        try:
            if app_key in ['browser', 'chrome']:
                browser_path = self.app_paths.get('chrome')
                if not os.path.exists(browser_path):
                    browser_path = self.app_paths.get('edge')
                if not os.path.exists(browser_path):
                    webbrowser.get().open('about:blank')
                    return {'success': True, 'message': '已打开默认浏览器'}
                path = browser_path
            
            if app_key == 'settings':
                subprocess.Popen(path, shell=True)
                return {'success': True, 'message': '已打开系统设置'}
            
            if os.path.exists(path) or path in self._system_commands or any(cmd in path.lower() for cmd in self._system_commands):
                process = subprocess.Popen(path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes[app_key] = process
                return {'success': True, 'message': f'已启动 {app_key}', 'pid': process.pid}
            
            return {'success': False, 'message': f'找不到应用: {path}'}
        except Exception as e:
            return {'success': False, 'message': f'启动失败: {str(e)}'}

    def search_web(self, query: str, engine: str = 'default') -> Dict[str, any]:
        try:
            import urllib.parse
            search_url = self.search_engines.get(engine, self.search_engines['default'])
            webbrowser.open(f'{search_url}{urllib.parse.quote(query)}')
            return {'success': True, 'message': f'正在搜索: {query}'}
        except Exception as e:
            return {'success': False, 'message': f'搜索失败: {str(e)}'}

    def close_application(self, app_name: str) -> Dict[str, any]:
        try:
            app_key = app_name.lower()
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_key in proc_name:
                        proc.terminate()
                        proc.wait(timeout=3)
                        return {'success': True, 'message': f'已关闭 {app_name}'}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return {'success': False, 'message': f'未找到运行中的应用: {app_name}'}
        except Exception as e:
            return {'success': False, 'message': f'关闭应用失败: {str(e)}'}

    def take_screenshot(self, save_path: Optional[str] = None) -> Dict[str, any]:
        try:
            import pyautogui
            if save_path is None:
                import datetime
                save_path = f'screenshot_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return {'success': True, 'message': f'截图已保存: {save_path}', 'path': save_path}
        except Exception as e:
            return {'success': False, 'message': f'截图失败: {str(e)}'}

    def system_control(self, action: str) -> Dict[str, any]:
        try:
            if '截图' in action or '截屏' in action:
                return self.take_screenshot()
            elif '锁屏' in action:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                return {'success': True, 'message': '屏幕已锁定'}
            elif '关机' in action:
                os.system('shutdown /s /t 60')
                return {'success': True, 'message': '系统将在60秒后关机'}
            elif '取消关机' in action:
                os.system('shutdown /a')
                return {'success': True, 'message': '已取消关机'}
            elif '重启' in action:
                os.system('shutdown /r /t 60')
                return {'success': True, 'message': '系统将在60秒后重启'}
            elif '睡眠' in action:
                os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                return {'success': True, 'message': '系统已进入睡眠模式'}
            return {'success': False, 'message': f'未知的系统命令: {action}'}
        except Exception as e:
            return {'success': False, 'message': f'系统命令执行失败: {str(e)}'}

    def volume_control(self, action: str) -> Dict[str, any]:
        try:
            import ctypes
            action_lower = action.lower()
            if '调大' in action or '增加' in action or 'up' in action_lower:
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
                    ctypes.windll.user32.Sleep(50)
                return {'success': True, 'message': '音量已增加'}
            elif '调小' in action or '降低' in action or 'down' in action_lower:
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                    ctypes.windll.user32.Sleep(50)
                return {'success': True, 'message': '音量已减小'}
            elif '静音' in action or 'mute' in action_lower:
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return {'success': True, 'message': '已静音'}
            elif '取消静音' in action or 'unmute' in action_lower:
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return {'success': True, 'message': '已取消静音'}
            return {'success': True, 'message': f'音量命令已执行: {action}'}
        except Exception as e:
            return {'success': False, 'message': f'音量控制失败: {str(e)}'}

    def open_file(self, file_path: str) -> Dict[str, any]:
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
                return {'success': True, 'message': f'已打开: {file_path}'}
            return {'success': False, 'message': f'文件不存在: {file_path}'}
        except Exception as e:
            return {'success': False, 'message': f'打开文件失败: {str(e)}'}

    def create_file(self, file_name: str, file_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not file_name:
                return {'success': False, 'message': '文件名不能为空'}
            full_path = self._resolve_path(file_name, file_path)
            exists, msg = self._check_exists(full_path, 'any')
            if exists:
                return {'success': False, 'message': f'文件已存在: {full_path}'}
            os.makedirs(os.path.dirname(full_path) or '.', exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                pass
            return {'success': True, 'message': f'已创建文件: {full_path}', 'path': full_path}
        except Exception as e:
            return {'success': False, 'message': f'创建文件失败: {str(e)}'}

    def create_folder(self, folder_name: str, folder_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not folder_name:
                return {'success': False, 'message': '文件夹名不能为空'}
            full_path = self._resolve_path(folder_name, folder_path)
            exists, msg = self._check_exists(full_path, 'any')
            if exists:
                return {'success': False, 'message': f'文件夹已存在: {full_path}'}
            os.makedirs(full_path, exist_ok=False)
            return {'success': True, 'message': f'已创建文件夹: {full_path}', 'path': full_path}
        except Exception as e:
            return {'success': False, 'message': f'创建文件夹失败: {str(e)}'}

    def delete_file(self, file_name: str, file_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not file_name:
                return {'success': False, 'message': '文件名不能为空'}
            full_path = self._resolve_path(file_name, file_path)
            exists, msg = self._check_exists(full_path, 'file')
            if not exists:
                return {'success': False, 'message': f'文件{msg}: {full_path}'}
            os.remove(full_path)
            return {'success': True, 'message': f'已删除文件: {full_path}', 'path': full_path}
        except Exception as e:
            return {'success': False, 'message': f'删除文件失败: {str(e)}'}

    def delete_folder(self, folder_name: str, folder_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not folder_name:
                return {'success': False, 'message': '文件夹名不能为空'}
            full_path = self._resolve_path(folder_name, folder_path)
            exists, msg = self._check_exists(full_path, 'dir')
            if not exists:
                return {'success': False, 'message': f'文件夹{msg}: {full_path}'}
            shutil.rmtree(full_path)
            return {'success': True, 'message': f'已删除文件夹: {full_path}', 'path': full_path}
        except Exception as e:
            return {'success': False, 'message': f'删除文件夹失败: {str(e)}'}

    def execute_command(self, parsed_command: Dict) -> Dict[str, any]:
        intent = parsed_command.get('intent')
        params = parsed_command.get('params', {})
        if intent == '打开应用':
            return self.open_application(params.get('app_name', ''))
        elif intent == '搜索':
            return self.search_web(params.get('query', ''), params.get('engine', 'default'))
        elif intent == '关闭应用':
            app_name = params.get('app_name', '')
            return self.close_application(app_name) if app_name else {'success': False, 'message': '未指定要关闭的应用'}
        elif intent == '系统控制':
            return self.system_control(params.get('action', ''))
        elif intent == '音量控制':
            return self.volume_control(params.get('action', ''))
        elif intent == '文件操作':
            return self.open_file(params.get('path', ''))
        elif intent == '创建文件':
            return self.create_file(params.get('name', ''))
        elif intent == '创建文件夹':
            return self.create_folder(params.get('name', ''))
        elif intent == '删除文件':
            return self.delete_file(params.get('name', ''))
        elif intent == '删除文件夹':
            return self.delete_folder(params.get('name', ''))
        else:
            raw_text = params.get('raw_text', '')
            return self.search_web(raw_text, 'default') if raw_text else {'success': False, 'message': f'无法处理命令: {intent}'}
