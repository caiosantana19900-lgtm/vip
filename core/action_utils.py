import win32api
import win32con
import time
import win32gui
import random
from settings.config import config_manager
from core.stealth_manager import stealth_manager


def handle_action(action, step_delay=1, hwnd=None, move_mouse_away=False):
    """
    Handle action execution with optional mouse movement away from center.
    
    Args:
        action: Action dictionary with type, key, mouse, etc.
        step_delay: Delay between key and mouse actions
        hwnd: Window handle for mouse operations
        move_mouse_away: Whether to move mouse away from center
    """
    action_type = action.get('type')
    anti_detection_delay = stealth_manager.generate_random_delay(30, 150)
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
        
        if vk_code:
            win32api.keybd_event(vk_code, 0, 0, 0)
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
    elif action_type == 'key':
        key = action.get('key')
        vk_code = key_to_vk(key) if key else None
        if vk_code:
            win32api.keybd_event(vk_code, 0, 0, 0)
            hold_duration = action.get('hold_duration', 0.1)
            try:
                hold_duration = float(hold_duration)
            except Exception:
                hold_duration = 0.1
            time.sleep(hold_duration)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def key_to_vk(key):
    """Convert key string to Virtual Key code"""
    if not key:
        return None
    key = key.upper()
    return vk_map.get(key)


# Virtual Key Code Mapping
vk_map = {
    '0': win32con.VK_0, '1': win32con.VK_1, '2': win32con.VK_2, '3': win32con.VK_3, '4': win32con.VK_4,
    '5': win32con.VK_5, '6': win32con.VK_6, '7': win32con.VK_7, '8': win32con.VK_8, '9': win32con.VK_9,
    'A': win32con.VK_A, 'B': win32con.VK_B, 'C': win32con.VK_C, 'D': win32con.VK_D, 'E': win32con.VK_E,
    'F': win32con.VK_F, 'G': win32con.VK_G, 'H': win32con.VK_H, 'I': win32con.VK_I, 'J': win32con.VK_J,
    'K': win32con.VK_K, 'L': win32con.VK_L, 'M': win32con.VK_M, 'N': win32con.VK_N, 'O': win32con.VK_O,
    'P': win32con.VK_P, 'Q': win32con.VK_Q, 'R': win32con.VK_R, 'S': win32con.VK_S, 'T': win32con.VK_T,
    'U': win32con.VK_U, 'V': win32con.VK_V, 'W': win32con.VK_W, 'X': win32con.VK_X, 'Y': win32con.VK_Y,
    'Z': win32con.VK_Z,
    'F1': win32con.VK_F1, 'F2': win32con.VK_F2, 'F3': win32con.VK_F3, 'F4': win32con.VK_F4,
    'F5': win32con.VK_F5, 'F6': win32con.VK_F6, 'F7': win32con.VK_F7, 'F8': win32con.VK_F8,
    'F9': win32con.VK_F9, 'F10': win32con.VK_F10, 'F11': win32con.VK_F11, 'F12': win32con.VK_F12,
    'SPACE': win32con.VK_SPACE, 'RETURN': win32con.VK_RETURN, 'ESCAPE': win32con.VK_ESCAPE,
    'BACKSPACE': win32con.VK_BACK, 'TAB': win32con.VK_TAB, 'SHIFT': win32con.VK_SHIFT,
    'CTRL': win32con.VK_CONTROL, 'ALT': win32con.VK_MENU, 'DELETE': win32con.VK_DELETE,
    'LEFT': win32con.VK_LEFT, 'RIGHT': win32con.VK_RIGHT, 'UP': win32con.VK_UP, 'DOWN': win32con.VK_DOWN,
}


class ActionManager:
    """Handles actions such as mouse movement and clicking on windows, using config settings."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or globals()['config_manager']
    
    def move_mouse_away_from_center(self, hwnd, avoid_center_ratio=0.3, target_edge_ratio=0.15):
        """
        Move the mouse away from the center of the window to avoid clicking on mobs.
        """
        try:
            if hwnd is None:
                from core.logger import logger
                logger.log('[ActionManager] No window handle provided for mouse movement', level=30)
                return False
            
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
            
            # Define safe zones (edges, corners)
            safe_zones = [
                (edge_margin_w, center_x - center_avoid_w // 2, edge_margin_h, center_y - center_avoid_h // 2),
                (center_x + center_avoid_w // 2, client_width - edge_margin_w, edge_margin_h, center_y - center_avoid_h // 2),
                (edge_margin_w, center_x - center_avoid_w // 2, center_y + center_avoid_h // 2, client_height - edge_margin_h),
                (center_x + center_avoid_w // 2, client_width - edge_margin_w, center_y + center_avoid_h // 2, client_height - edge_margin_h),
            ]
            
            valid_zones = []
            for zone in safe_zones:
                x1, x2, y1, y2 = zone
                if x1 < x2 and y1 < y2:
                    valid_zones.append(zone)
            
            if not valid_zones:
                corner_margin = min(edge_margin_w, edge_margin_h)
                valid_zones = [
                    (corner_margin, corner_margin + 50, corner_margin, corner_margin + 50),
                    (client_width - corner_margin - 50, client_width - corner_margin, corner_margin, corner_margin + 50),
                ]
            
            selected_zone = random.choice(valid_zones)
            x1, x2, y1, y2 = selected_zone
            target_x = random.randint(int(x1), int(x2))
            target_y = random.randint(int(y1), int(y2))
            
            # Move mouse with smooth interpolation if enabled
            if enable_human_mouse:
                cur_x, cur_y = win32api.GetCursorPos()
                steps = int(((target_x - cur_x) ** 2 + (target_y - cur_y) ** 2) ** 0.5 / mouse_speed)
                steps = max(1, steps)
                
                for i in range(1, steps + 1):
                    t = i / steps
                    jitter_x = random.randint(-1, 1)
                    jitter_y = random.randint(-1, 1)
                    interp_x = int(cur_x + (target_x - cur_x) * (3 * t ** 2 - 2 * t ** 3)) + jitter_x
                    interp_y = int(cur_y + (target_y - cur_y) * (3 * t ** 2 - 2 * t ** 3)) + jitter_y
                    win32api.SetCursorPos((interp_x, interp_y))
                    time.sleep(0.01)
            else:
                win32api.SetCursorPos((target_x, target_y))
            
            from core.logger import logger
            logger.log(f'[ActionManager] Mouse moved away from center to client position ({target_x}, {target_y})', level=10)
            return True
            
        except Exception as e:
            from core.logger import logger
            logger.log(f'[ActionManager] Error moving mouse away from center: {e}', level=40)
            return False
