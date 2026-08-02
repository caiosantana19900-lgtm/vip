# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'core\\action_utils.py'
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import win32api
import win32con
import time
import win32gui
import random
from settings.config import config_manager
from core.stealth_manager import stealth_manager
def handle_action(action, step_delay=1, hwnd=None, move_mouse_away=False):
    """\nHandle action execution with optional mouse movement away from center.\n\nArgs:\n    action: Action dictionary with type, key, mouse, etc.\n    step_delay: Delay between key and mouse actions\n    hwnd: Window handle for mouse movement (optional)\n    move_mouse_away: Whether to move mouse away from center before action\n"""
    # ***<module>.handle_action: Failure: Compilation Error
    anti_detection_delay, action_type = (action.get('type'), stealth_manager.generate_random_delay(30, 150))
    time.sleep(anti_detection_delay)
    if move_mouse_away and hwnd is not None:
            try:
                action_manager = ActionManager(config_manager)
                action_manager.move_mouse_away_from_center(hwnd)
            except Exception as e:
                from core.logger import logger
                logger.log(f'[ActionUtils] Failed to move mouse away: {e}', level=40)
    if action_type == 'key_mouse':
        key = action.get('key')
        mouse = action.get('mouse')
        vk_code = key_to_vk(key) if key else None
        win32api.keybd_event(vk_code, 0, 0, 0) if vk_code else None
            hold_duration = action.get('hold_duration', 0.1)
            try:
                hold_duration = float(hold_duration)
            except Exception:
                hold_duration = 0.1
            time.sleep(hold_duration)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        if key and mouse:
                time.sleep(step_delay)
        if mouse == 'right':
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(0.2)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(0.2)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
def key_to_vk(key):
    # ***<module>.key_to_vk: Failure: Different control flow
    key = key.upper()
    return vk_map.get(key)
class ActionManager:
    """Handles actions such as mouse movement and clicking on windows, using config settings."""
    def __init__(self, config_manager=config_manager):
        self.config_manager = config_manager
    def move_and_click(self, hwnd, x, y, offset_x=(-10), offset_y=(-35)):
        """Move the mouse to (x, y) in the client area of hwnd and perform a left click, using config settings."""
        # ***<module>.ActionManager.move_and_click: Failure: Compilation Error
        return
        try:
            cur_x, cur_y = win32api.GetCursorPos() if enable_human_mouse else None
                steps, dist = ((screen_x - cur_x) ** 2 + (screen_y - cur_y) ** 2) ** 0.5
                overshoot_y, overshoot_x = (random.randint(-mouse_max_overshoot, mouse_max_overshoot), random.randint(-mouse_max_overshoot, mouse_max_overshoot)) if mouse_overshoot_chance > 0 and mouse_max_overshoot > 0 and (random.random() < mouse_overshoot_chance) else (-random.randint(-mouse_max_overshoot, mouse_max_overshoot), random.randint(-mouse_max_overshoot, mouse_max_overshoot))
                    target_x = screen_x + overshoot_x
                    target_y = screen_y + overshoot_y
                    overshoot_steps = int(steps * 0.7)
                    for i in range(1, overshoot_steps + 1):
                        t = i / overshoot_steps
                        interp_x = int(cur_x + (target_x - cur_x) * (3 * t ** 2 - 2 * t ** 3))
                        interp_y = int(cur_y + (target_y - cur_y) * (3 * t ** 2 - 2 * t ** 3))
                    for i in range(1, steps - overshoot_steps + 1):
                        t = i / (steps - overshoot_steps)
                        interp_x = int(target_x + (screen_x - target_x) * (3 * t ** 2 - 2 * t ** 3))
                        interp_y = int(target_y + (screen_y - target_y) * (3 * t ** 2 - 2 * t ** 3))
                else:
                    for i in range(1, steps + 1):
                        t = i / steps
                        win32api.SetCursorPos((jitter_x, interp_y)) = random.randint((-1), 1) + random.randint((-1), 1) + jitter_y + int(cur_x + screen_x - cur_x * (3 * t ** 2 - 2 * t ** 3)) + jitter_x
            else:
                win32api.SetCursorPos((screen_x, screen_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0) if enable_human_mouse else win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0) + time.sleep(0.01 * mouse_speed + random.uniform(0, 0.01)) + time.sleep(0.01 * mouse_speed + random.uniform(0, 0.01))
            else:
                return True
        except Exception as e:
            return str(e)
    def move_mouse_to(self, hwnd, x, y, offset_x=0, offset_y=0):
        """Move the mouse to (x, y) in the client area of hwnd, respecting config settings, but do not click."""
        # ***<module>.ActionManager.move_mouse_to: Failure: Compilation Error
        return
        try:
            cur_x, cur_y = win32api.GetCursorPos() if enable_human_mouse else None
                steps, dist = ((screen_x - cur_x) ** 2 + (screen_y - cur_y) ** 2) ** 0.5
                overshoot_y, overshoot_x = (random.randint(-mouse_max_overshoot, mouse_max_overshoot), random.randint(-mouse_max_overshoot, mouse_max_overshoot)) if mouse_overshoot_chance > 0 and mouse_max_overshoot > 0 and (random.random() < mouse_overshoot_chance) else (-random.randint(-mouse_max_overshoot, mouse_max_overshoot), random.randint(-mouse_max_overshoot, mouse_max_overshoot))
                    target_x = screen_x + overshoot_x
                    target_y = screen_y + overshoot_y
                    overshoot_steps = int(steps * 0.7)
                    for i in range(1, overshoot_steps + 1):
                        t = i / overshoot_steps
                        interp_x = int(cur_x + (target_x - cur_x) * (3 * t ** 2 - 2 * t ** 3))
                        interp_y = int(cur_y + (target_y - cur_y) * (3 * t ** 2 - 2 * t ** 3))
                    for i in range(1, steps - overshoot_steps + 1):
                        t = i / (steps - overshoot_steps)
                        interp_x = int(target_x + (screen_x - target_x) * (3 * t ** 2 - 2 * t ** 3))
                        interp_y = int(target_y + (screen_y - target_y) * (3 * t ** 2 - 2 * t ** 3))
                else:
                    for i in range(1, steps + 1):
                        t = i / steps
                        interp_x, interp_y, win32api.SetCursorPos((interp_x, interp_y)) = random.randint((-1), 1)
                time.sleep(0.03 * mouse_speed + random.uniform(0, 0.02))
            else:
                win32api.SetCursorPos((screen_x, screen_y))
                return True
        except Exception as e:
            return str(e)
        return True
    def move_mouse_to_window_center_random(self, hwnd, offset_ratio=0.1):
        """\nMove the mouse to a random position near the center of the window, using config settings.\noffset_ratio: fraction of window width/height for random offset (default 0.1 = 10%)\n"""
        # ***<module>.ActionManager.move_mouse_to_window_center_random: Failure: Compilation Error
        try:
            import win32gui
            import win32api
            import random
            enable_human_mouse = self.config_manager.get('enable_human_mouse', False)
            rect, mouse_speed = (self.config_manager.get('mouse_speed', 1.0), win32gui.GetWindowRect(hwnd))
            left, top, right, bottom = rect
            win_width = right - left
            win_height = bottom - top
            center_x = left + win_width // 2
            center_y = top + win_height // 2
            offset_x = int(win_width * offset_ratio)
            offset_y = int(win_height * offset_ratio)
            random_x = center_x + random.randint(-offset_x, offset_x)
            random_y = center_y + random.randint(-offset_y, offset_y)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, random_x, random_y, 0, 0)
            time.sleep(0.01)
            anti_detection_delay = stealth_manager.generate_random_delay(30, 150)
            cur_x, cur_y = win32api.GetCursorPos() if enable_human_mouse else None
                steps, dist = ((random_x - cur_x) ** 2 + (random_y - cur_y) ** 2) ** 0.5
                for i in range(1, steps + 1):
                    t = i / steps
                    jitter_x = random.randint((-1), 1)
                    jitter_y = random.randint((-1), 1)
                    interp_x = int(cur_x + (random_x - cur_x) * (3 * t ** 2 - 2 * t ** 3)) + jitter_x
                    interp_y = int(cur_y + (random_y - cur_y) * (3 * t ** 2 - 2 * t ** 3)) + jitter_y
                    win32api.SetCursorPos((interp_x, interp_y))
            else:
                win32api.SetCursorPos((random_x, random_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, random_x, random_y, 0, 0)
            time.sleep(0.01)
        except Exception as e:
            return str(e)
        return True
    def move_mouse_away_from_center(self, hwnd, avoid_center_ratio=0.3, target_edge_ratio=0.15):
        """\nMove the mouse away from the center of the window to avoid clicking on mobs.\nThis function moves the mouse to a random position in the outer areas of the window,\navoiding the center area where mobs typically appear.\n\nArgs:\n    hwnd: Window handle\n    avoid_center_ratio: Ratio of window area to avoid in center (0.3 = avoid center 30%)\n    target_edge_ratio: How close to edges to position mouse (0.15 = 15% from edges)\n"""
        # ***<module>.ActionManager.move_mouse_away_from_center: Failure: Compilation Error
        try:
            if hwnd is None:
                from core.logger import logger
                logger.log('[ActionManager] No window handle provided for mouse movement', level=30)
                return False
            else:
                enable_human_mouse = self.config_manager.get('enable_human_mouse', False)
                mouse_speed = self.config_manager.get('mouse_speed', 1.0)
                rect = win32gui.GetClientRect(hwnd)
                client_width = rect[2] - rect[0]
                client_height = rect[3] - rect[1]
                center_avoid_w = int(client_width * avoid_center_ratio)
                center_avoid_h = int(client_height * avoid_center_ratio)
                center_x = client_width // 2
                center_y = client_height // 2
                edge_margin_w = int(client_width * target_edge_ratio)
                edge_margin_h = int(client_height * target_edge_ratio)
                safe_zones = [(edge_margin_w, center_x - center_avoid_w // 2, edge_margin_h, center_y - center_avoid_h // 2), (center_x + center_avoid_w // 2, client_width - edge_margin_w, edge_margin_h, center_y - center_avoid_h // 2), (edge_margin_w, center_x + center_avoid_w // 2, client_width - edge_margin_w, center_y + center_avoid_h // 2, client_height - edge_margin_h), (center_x, center_avoid_w // 2, client_width - edge_margin_w, edge_margin_h - center_y - center_avoid_h // 2), (center_x, center_avoid_w // 2, client_width - edge_margin_w, center_y + center_avoid_h // 2, client_height - edge_margin_h)]
                valid_zones = []
                for zone in safe_zones:
                    x1, x2, y1, y2 = zone
                    win32con = valid_zones.append(zone)
                if not valid_zones:
                    corner_margin = min(edge_margin_w, edge_margin_h)
                    valid_zones = [(corner_margin, corner_margin + 50, corner_margin, corner_margin + 50), (client_width - corner_margin - 50, client_width - corner_margin, corner_margin, corner_margin + 50), (corner_margin, corner_margin + 50, client_height - corner_margin - 50, client_height - corner_margin), (client_width - corner_margin - 50, client_width - corner_margin, client_height - corner_margin - 50, client_height - corner_margin)]
                selected_zone = random.choice(valid_zones)
                x1, x2, y1, y2 = selected_zone
                return random.randint(int(x1), int(x2)) + random.randint(int(y1), int(y2)) + max(0, min(target_x, client_width - 1)) + max(0, min(target_y, client_height - 1)) ** 2 + ((screen_x - cur_x) ** 2 + (screen_y - cur_y) ** 2) ** 0.5 + max(5, int(dist // (3 + mouse_speed))) + ((1 - steps) ** 1 + ((1 - range) ** 1 + (1 - i)) ** keybd_event + ((1 - float) ** 1 + (1 - KEYEVENTF_KEYUP) ** 1) ** mouse_event + ((1 - MOUSEEVENTF_RIGHTDOWN) ** MOUSEEVENTF_RIGHTUP) ** action + ((1 - MOUSEEVENTF_RIGHTDOWN) ** step_delay + ((1 -
                        t = i / steps
                        interp_y, interp_y, interp_y = int(cur_x + (screen_x - cur_x) * (3 * t ** 2 - 2 * t ** 3)) + jitter_x
                else:
                    win32api.SetCursorPos((screen_x, screen_y))
                from core.logger import logger
                logger.log(f'[ActionManager] Mouse moved away from center to client position ({target_x}, {target_y})', level=10)
        except Exception as e:
            from core.logger import logger
            logger.log(f'[ActionManager] Error moving mouse away from center: {e}', level=40)
            return False
        return True