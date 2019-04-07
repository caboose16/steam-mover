
class Game:
    def __init__(self, app_manifest, steam_folder_path):
        self.app_manifest = app_manifest
        self.install_dir = ''
        self.name = ''
        self.size = ''
        
        # automatically obtain appid
        self.appid = ''
        for char in self.app_manifest:
            if char.isdigit():
                self.appid += char