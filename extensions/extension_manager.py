import os
import sys
import subprocess

class ExtensionManager:
    def __init__(self, folder="extensions"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def list_extensions(self):
        return [f for f in os.listdir(self.folder) if f.endswith(".py")]

    def run_extension(self, script_name):
        script_path = os.path.join(self.folder, script_name)
        if not os.path.exists(script_path):
            raise FileNotFoundError(script_name)
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["cmd", "/c", f'start cmd /k "python "{script_path}" & pause"'])
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["osascript", "-e", f'tell app "Terminal" to do script "python3 {script_path}"'])
            else:
                subprocess.Popen(f'gnome-terminal -- bash -c "python3 {script_path}; read -p \'Appuyez sur Entrée\'"', shell=True)
        except Exception as e:
            print(f"Erreur extension: {e}")
