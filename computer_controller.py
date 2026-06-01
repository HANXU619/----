import subprocess
import webbrowser
import psutil
import os
import time
from typing import Dict, Optional

class ComputerController:
    def __init__(self):
        self.processes = {}
        self.app_paths = {
            'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'edge': 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
            'firefox': 'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
            'wechat': 'C:\\Program Files\\Tencent\\Weixin\\Weixin.exe',
            '微信': 'C:\\Program Files\\Tencent\\Weixin\\Weixin.exe',
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

    def open_application(self, app_name: str) -> Dict[str, any]:
        try:
            app_key = app_name.lower()

            if app_key in self.app_paths:
                path = self.app_paths[app_key]
                return self._run_application(path, app_key)

            try:
                result = subprocess.run(
                    ['where', app_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    path = result.stdout.strip().split('\n')[0]
                    return self._run_application(path, app_name)

            except:
                pass

            return self._run_application(app_name, app_name)

        except Exception as e:
            return {
                'success': False,
                'message': f"打开应用失败: {str(e)}"
            }

    def _run_application(self, path: str, app_key: str) -> Dict[str, any]:
        try:
            if app_key == 'browser' or app_key == 'chrome':
                browser_path = self.app_paths.get('chrome')
                if not os.path.exists(browser_path):
                    browser_path = self.app_paths.get('edge')
                if not os.path.exists(browser_path):
                    webbrowser.get().open('about:blank')
                    return {
                        'success': True,
                        'message': '已打开默认浏览器'
                    }
                path = browser_path

            if app_key == 'settings':
                subprocess.Popen(path, shell=True)
                return {
                    'success': True,
                    'message': '已打开系统设置'
                }

            if os.path.exists(path) or self._is_system_command(path):
                process = subprocess.Popen(
                    path,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes[app_key] = process
                return {
                    'success': True,
                    'message': f'已启动 {app_key}',
                    'pid': process.pid
                }
            else:
                return {
                    'success': False,
                    'message': f'找不到应用: {path}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'启动失败: {str(e)}'
            }

    def _is_system_command(self, command: str) -> bool:
        system_commands = [
            'notepad.exe', 'calc.exe', 'explorer.exe', 'mspaint.exe',
            'taskmgr.exe', 'control.exe', 'powershell.exe', 'cmd.exe'
        ]
        return any(cmd in command.lower() for cmd in system_commands)

    def search_web(self, query: str, engine: str = 'default') -> Dict[str, any]:
        try:
            search_url = self.search_engines.get(engine, self.search_engines['default'])

            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"{search_url}{encoded_query}"

            webbrowser.open(url)

            return {
                'success': True,
                'message': f'正在搜索: {query}',
                'url': url
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'搜索失败: {str(e)}'
            }

    def close_application(self, app_name: str) -> Dict[str, any]:
        try:
            app_key = app_name.lower()

            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_key in proc_name or app_key in str(proc.info['name']).lower():
                        proc.terminate()
                        proc.wait(timeout=3)
                        return {
                            'success': True,
                            'message': f'已关闭 {app_name}'
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                'success': False,
                'message': f'未找到运行中的应用: {app_name}'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'关闭应用失败: {str(e)}'
            }

    def take_screenshot(self, save_path: Optional[str] = None) -> Dict[str, any]:
        try:
            import pyautogui

            if save_path is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"screenshot_{timestamp}.png"

            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)

            return {
                'success': True,
                'message': f'截图已保存: {save_path}',
                'path': save_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'截图失败: {str(e)}'
            }

    def system_control(self, action: str) -> Dict[str, any]:
        try:
            if '截图' in action or '截屏' in action:
                return self.take_screenshot()

            elif '锁屏' in action:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                return {
                    'success': True,
                    'message': '屏幕已锁定'
                }

            elif '关机' in action:
                os.system('shutdown /s /t 60')
                return {
                    'success': True,
                    'message': '系统将在60秒后关机'
                }

            elif '取消关机' in action:
                os.system('shutdown /a')
                return {
                    'success': True,
                    'message': '已取消关机'
                }

            elif '重启' in action:
                os.system('shutdown /r /t 60')
                return {
                    'success': True,
                    'message': '系统将在60秒后重启'
                }

            elif '睡眠' in action:
                os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
                return {
                    'success': True,
                    'message': '系统已进入睡眠模式'
                }

            else:
                return {
                    'success': False,
                    'message': f'未知的系统命令: {action}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'系统命令执行失败: {str(e)}'
            }

    def volume_control(self, action: str) -> Dict[str, any]:
        try:
            import ctypes

            action_lower = action.lower()

            if '调大' in action or '增加' in action or 'up' in action_lower:
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
                    ctypes.windll.user32.Sleep(50)
                return {
                    'success': True,
                    'message': '音量已增加'
                }

            elif '调小' in action or '降低' in action or 'down' in action_lower:
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                    ctypes.windll.user32.Sleep(50)
                return {
                    'success': True,
                    'message': '音量已减小'
                }

            elif '静音' in action or 'mute' in action_lower:
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return {
                    'success': True,
                    'message': '已静音'
                }

            elif '取消静音' in action or 'unmute' in action_lower:
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return {
                    'success': True,
                    'message': '已取消静音'
                }

            return {
                'success': True,
                'message': f'音量命令已执行: {action}'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'音量控制失败: {str(e)}'
            }

    def get_running_apps(self) -> list:
        apps = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                apps.append({
                    'name': proc.info['name'],
                    'pid': proc.info['pid']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return apps

    def open_file(self, file_path: str) -> Dict[str, any]:
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
                return {
                    'success': True,
                    'message': f'已打开: {file_path}'
                }
            else:
                return {
                    'success': False,
                    'message': f'文件不存在: {file_path}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'打开文件失败: {str(e)}'
            }

    def create_file(self, file_name: str, file_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not file_name:
                return {
                    'success': False,
                    'message': '文件名不能为空'
                }

            if not file_name.endswith('.txt'):
                full_path = os.path.join(file_path or '', file_name)
            else:
                if file_path:
                    full_path = os.path.join(file_path, file_name)
                else:
                    full_path = file_name

            if os.path.exists(full_path):
                return {
                    'success': False,
                    'message': f'文件已存在: {full_path}'
                }

            os.makedirs(os.path.dirname(full_path) or '.', exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                pass

            return {
                'success': True,
                'message': f'已创建文件: {full_path}',
                'path': full_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'创建文件失败: {str(e)}'
            }

    def create_folder(self, folder_name: str, folder_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not folder_name:
                return {
                    'success': False,
                    'message': '文件夹名不能为空'
                }

            if folder_path:
                full_path = os.path.join(folder_path, folder_name)
            else:
                full_path = folder_name

            if os.path.exists(full_path):
                return {
                    'success': False,
                    'message': f'文件夹已存在: {full_path}'
                }

            os.makedirs(full_path, exist_ok=False)

            return {
                'success': True,
                'message': f'已创建文件夹: {full_path}',
                'path': full_path
            }

        except FileExistsError:
            return {
                'success': False,
                'message': f'文件夹已存在: {folder_name}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'创建文件夹失败: {str(e)}'
            }

    def delete_file(self, file_name: str, file_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not file_name:
                return {
                    'success': False,
                    'message': '文件名不能为空'
                }

            if file_path:
                full_path = os.path.join(file_path, file_name)
            else:
                full_path = file_name

            if not os.path.exists(full_path):
                return {
                    'success': False,
                    'message': f'文件不存在: {full_path}'
                }

            if not os.path.isfile(full_path):
                return {
                    'success': False,
                    'message': f'路径不是文件: {full_path}'
                }

            os.remove(full_path)

            return {
                'success': True,
                'message': f'已删除文件: {full_path}',
                'path': full_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'删除文件失败: {str(e)}'
            }

    def delete_folder(self, folder_name: str, folder_path: Optional[str] = None) -> Dict[str, any]:
        try:
            if not folder_name:
                return {
                    'success': False,
                    'message': '文件夹名不能为空'
                }

            if folder_path:
                full_path = os.path.join(folder_path, folder_name)
            else:
                full_path = folder_name

            if not os.path.exists(full_path):
                return {
                    'success': False,
                    'message': f'文件夹不存在: {full_path}'
                }

            if not os.path.isdir(full_path):
                return {
                    'success': False,
                    'message': f'路径不是文件夹: {full_path}'
                }

            import shutil
            shutil.rmtree(full_path)

            return {
                'success': True,
                'message': f'已删除文件夹: {full_path}',
                'path': full_path
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'删除文件夹失败: {str(e)}'
            }

    def execute_command(self, parsed_command: Dict) -> Dict[str, any]:
        intent = parsed_command.get('intent')
        params = parsed_command.get('params', {})

        if intent == '打开应用':
            app_name = params.get('app_name', '')
            return self.open_application(app_name)

        elif intent == '搜索':
            query = params.get('query', '')
            engine = params.get('engine', 'default')
            return self.search_web(query, engine)

        elif intent == '关闭应用':
            app_name = params.get('app_name', '')
            if app_name:
                return self.close_application(app_name)
            return {
                'success': False,
                'message': '未指定要关闭的应用'
            }

        elif intent == '系统控制':
            action = params.get('action', '')
            return self.system_control(action)

        elif intent == '音量控制':
            action = params.get('action', '')
            return self.volume_control(action)

        elif intent == '文件操作':
            path = params.get('path', '')
            return self.open_file(path)

        elif intent == '创建文件':
            name = params.get('name', '')
            return self.create_file(name)

        elif intent == '创建文件夹':
            name = params.get('name', '')
            return self.create_folder(name)

        elif intent == '删除文件':
            name = params.get('name', '')
            return self.delete_file(name)

        elif intent == '删除文件夹':
            name = params.get('name', '')
            return self.delete_folder(name)

        else:
            raw_text = params.get('raw_text', '')
            if raw_text:
                return self.search_web(raw_text, 'default')
            return {
                'success': False,
                'message': f'无法处理命令: {intent}'
            }
