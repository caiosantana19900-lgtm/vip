"""
Settings/configuration manager. All config data is stored/loaded here.
"""
import copy
import json
import os


class ConfigManager:
    CONFIG_FILE = 'config.json'

    def __init__(self):
        self.config = {}
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}

        if 'auto_buff' not in self.config:
            self.config['auto_buff'] = {'buffs': {}, 'capture_interval': 2.0, 'detection_delay': 3.0}
            self.save()

    def save(self):
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    # --- Atalhos e Combos de Auto Attack ---
    def get_auto_attack_shortcut(self):
        ctrl = self.get('shortcut_auto_attack_ctrl', True)
        alt = self.get('shortcut_auto_attack_alt', False)
        shift = self.get('shortcut_auto_attack_shift', False)
        key = self.get('shortcut_auto_attack_key', 'F8')
        return (ctrl, alt, shift, key)

    def set_auto_attack_shortcut(self, ctrl, alt, shift, key):
        self.set('shortcut_auto_attack_ctrl', ctrl)
        self.set('shortcut_auto_attack_alt', alt)
        self.set('shortcut_auto_attack_shift', shift)
        self.set('shortcut_auto_attack_key', key)

    def get_auto_attack_combo(self):
        key = self.get('auto_attack_combo_key', '')
        interval = self.get('auto_attack_combo_interval', 5.0)
        return (key, interval)

    def set_auto_attack_combo(self, key, interval):
        self.set('auto_attack_combo_key', key)
        self.set('auto_attack_combo_interval', interval)

    # --- Perfis de Auto Skill ---
    def migrate_auto_skill_to_profiles(self):
        """If profiles are not present, migrate old auto_skill config to a default profile."""
        if 'auto_skill_profiles' not in self.config and self.config.get('auto_skill_skills', []):
            skills = self.config.get('auto_skill_skills', [])
            start_delay = self.config.get('auto_skill_start_delay', 0.0)
            move_mouse_away = self.config.get('auto_skill_move_mouse_away', False)
            self.config['auto_skill_profiles'] = {
                'Default': {
                    'skills': skills,
                    'start_delay': start_delay,
                    'move_mouse_away': move_mouse_away
                }
            }
            self.config['auto_skill_active_profile'] = 'Default'
            self.config.pop('auto_skill_skills', None)
            self.config.pop('auto_skill_start_delay', None)
            self.config.pop('auto_skill_move_mouse_away', None)
            self.save()

    def get_skill_profiles(self):
        """Return the dict of all auto skill profiles."""
        return self.config.get('auto_skill_profiles', {})

    def get_active_skill_profile(self):
        """Return the name of the currently active auto skill profile."""
        return self.config.get('auto_skill_active_profile', None)

    def set_active_skill_profile(self, profile_name):
        self.config['auto_skill_active_profile'] = profile_name
        self.save()

    def add_skill_profile(self, profile_name, data=None):
        profiles = self.config.setdefault('auto_skill_profiles', {})
        if profile_name in profiles:
            raise ValueError(f"Profile '{profile_name}' already exists.")
        
        profiles[profile_name] = data or {'skills': [], 'start_delay': 0.0, 'move_mouse_away': False}
        self.save()

    def delete_skill_profile(self, profile_name):
        profiles = self.config.get('auto_skill_profiles', {})
        if profile_name not in profiles:
            return
        
        if len(profiles) <= 1:
            raise ValueError('At least one profile must exist.')
        
        del profiles[profile_name]
        if self.config.get('auto_skill_active_profile') == profile_name:
            remaining = list(profiles.keys())
            self.config['auto_skill_active_profile'] = remaining[0] if remaining else None
        self.save()

    def rename_skill_profile(self, old_name, new_name):
        profiles = self.config.get('auto_skill_profiles', {})
        if old_name not in profiles:
            raise ValueError(f"Profile '{old_name}' does not exist.")
        if new_name in profiles:
            raise ValueError(f"Profile '{new_name}' already exists.")
            
        profiles[new_name] = profiles.pop(old_name)
        if self.config.get('auto_skill_active_profile') == old_name:
            self.config['auto_skill_active_profile'] = new_name
        self.save()

    def update_skill_profile(self, profile_name, data):
        profiles = self.config.setdefault('auto_skill_profiles', {})
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' does not exist.")
        
        profiles[profile_name] = data
        self.save()

    # --- Perfis de Auto Buff ---
    def migrate_auto_buff_to_profiles(self):
        """Migrate old auto_buff config to profiles if profiles don't exist."""
        if 'auto_buff_profiles' not in self.config:
            old_auto_buff = self.config.get('auto_buff', {})
            buffs = old_auto_buff.get('buffs', {})
            capture_interval = old_auto_buff.get('capture_interval', 2.0)
            detection_delay = old_auto_buff.get('detection_delay', 3.0)
            default_profile = {
                'buffs': buffs, 
                'settings': {
                    'capture_interval': capture_interval, 
                    'detection_delay': detection_delay, 
                    'blinking_detection_enabled': True, 
                    'watch_area_enabled': True, 
                    'watch_area_width_percent': 50, 
                    'watch_area_height_percent': 10, 
                    'move_mouse_away': True
                }, 
                'metadata': {
                    'created_date': '2025-06-17', 
                    'last_modified': '2025-06-17', 
                    'description': 'Default buff profile'
                }
            }
            self.config['auto_buff_profiles'] = {'Default': default_profile}
            self.config['auto_buff_active_profile'] = 'Default'
            self.save()

    def get_buff_profiles(self):
        """Return the dict of all auto buff profiles."""
        return self.config.get('auto_buff_profiles', {})

    def get_active_buff_profile(self):
        """Return the name of the currently active auto buff profile."""
        return self.config.get('auto_buff_active_profile', 'Default')

    def set_active_buff_profile(self, profile_name):
        """Set the active buff profile."""
        profiles = self.get_buff_profiles()
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' does not exist.")
        
        self.config['auto_buff_active_profile'] = profile_name
        self.save()

    def add_buff_profile(self, profile_name, description='', copy_from=None):
        """Add a new buff profile."""
        profiles = self.config.setdefault('auto_buff_profiles', {})
        if profile_name in profiles:
            raise ValueError(f"Profile '{profile_name}' already exists.")
        
        if copy_from and copy_from in profiles:
            new_profile = copy.deepcopy(profiles[copy_from])
            new_profile['metadata']['description'] = description
            new_profile['metadata']['created_date'] = '2025-06-17'
            new_profile['metadata']['last_modified'] = '2025-06-17'
        else:
            new_profile = {
                'buffs': {}, 
                'settings': {
                    'capture_interval': 2.0, 
                    'detection_delay': 3.0, 
                    'blinking_detection_enabled': True, 
                    'watch_area_enabled': True, 
                    'watch_area_width_percent': 50, 
                    'watch_area_height_percent': 10, 
                    'move_mouse_away': True
                }, 
                'metadata': {
                    'created_date': '2025-06-17', 
                    'last_modified': '2025-06-17', 
                    'description': description
                }
            }
        profiles[profile_name] = new_profile
        self.save()

    def delete_buff_profile(self, profile_name):
        """Delete a buff profile."""
        profiles = self.config.get('auto_buff_profiles', {})
        if profile_name not in profiles:
            return
        
        if len(profiles) <= 1:
            raise ValueError('At least one profile must exist.')
            
        del profiles[profile_name]
        if self.config.get('auto_buff_active_profile') == profile_name:
            remaining = list(profiles.keys())
            self.config['auto_buff_active_profile'] = remaining[0] if remaining else 'Default'
        self.save()

    def rename_buff_profile(self, old_name, new_name):
        """Rename a buff profile."""
        profiles = self.config.get('auto_buff_profiles', {})
        if old_name not in profiles:
            raise ValueError(f"Profile '{old_name}' does not exist.")
        if new_name in profiles:
            raise ValueError(f"Profile '{new_name}' already exists.")
            
        profiles[new_name] = profiles.pop(old_name)
        profiles[new_name]['metadata']['last_modified'] = '2025-06-17'
        if self.config.get('auto_buff_active_profile') == old_name:
            self.config['auto_buff_active_profile'] = new_name
        self.save()

    def update_buff_profile(self, profile_name, data):
        """Update a buff profile."""
        profiles = self.config.setdefault('auto_buff_profiles', {})
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' does not exist.")
        
        profiles[profile_name].update(data)
        profiles[profile_name]['metadata']['last_modified'] = '2025-06-17'
        self.save()

    def get_active_buff_profile_data(self):
        """Get the data for the currently active buff profile."""
        profiles = self.get_buff_profiles()
        active_name = self.get_active_buff_profile()
        return profiles.get(active_name, {})

    def export_buff_profile(self, profile_name, file_path):
        """Export a buff profile to a JSON file."""
        profiles = self.get_buff_profiles()
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' does not exist.")
        
        export_data = {
            'profile_name': profile_name, 
            'profile_data': profiles[profile_name], 
            'export_date': '2025-06-17', 
            'version': '2.0'
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=4)

    def import_buff_profile(self, file_path, new_name=None):
        """Import a buff profile from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
            
        profile_name = new_name or import_data.get('profile_name', 'Imported Profile')
        profile_data = import_data.get('profile_data', {})
        
        if 'buffs' not in profile_data:
            profile_data['buffs'] = {}
        if 'settings' not in profile_data:
            profile_data['settings'] = {
                'capture_interval': 2.0, 
                'detection_delay': 3.0, 
                'blinking_detection_enabled': True, 
                'watch_area_enabled': True, 
                'watch_area_width_percent': 50, 
                'watch_area_height_percent': 10, 
                'move_mouse_away': True
            }
        if 'metadata' not in profile_data:
            profile_data['metadata'] = {}
            
        profile_data['metadata']['last_modified'] = '2025-06-17'
        if 'created_date' not in profile_data['metadata']:
            profile_data['metadata']['created_date'] = '2025-06-17'
            
        self.add_buff_profile(profile_name, profile_data['metadata'].get('description', 'Imported profile'), copy_from=None)
        profiles = self.config['auto_buff_profiles']
        profiles[profile_name] = profile_data
        self.save()
        return profile_name

    def validate_buff_profile(self, profile_name):
        """Validate a buff profile for conflicts and issues."""
        profiles = self.get_buff_profiles()
        if profile_name not in profiles:
            return {'valid': False, 'errors': [f"Profile '{profile_name}' does not exist."]}
        
        profile = profiles[profile_name]
        buffs = profile.get('buffs', {})
        errors = []
        warnings = []
        used_keys = {}
        
        for buff_id, buff_data in buffs.items():
            key = buff_data.get('key')
            if key:
                buff_name = buff_data.get('name', buff_id)
                if key in used_keys:
                    errors.append(f"Key '{key}' is used by multiple buffs: {used_keys[key]} and {buff_name}")
                else:
                    used_keys[key] = buff_name
                    
        for buff_id, buff_data in buffs.items():
            if not buff_data.get('template_image') and not buff_data.get('template_path'):
                warnings.append(f"Buff '{buff_data.get('name', buff_id)}' has no template image")
                
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}


config_manager = ConfigManager()