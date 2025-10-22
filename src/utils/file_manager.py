import os
import shutil
from src.config.logger import setup_logger

class FileManager:
    def __init__(self):
        self.logger = setup_logger('FileManager')
        self.persist_dir = os.path.join('downloads', 'persist')
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Asegura que los directorios necesarios existan."""
        os.makedirs('downloads', exist_ok=True)
        os.makedirs(self.persist_dir, exist_ok=True)

    def persist_file(self, filepath):
        """Mueve el archivo a la carpeta persist."""
        try:
            if not os.path.exists(filepath):
                self.logger.error(f"Archivo no encontrado: {filepath}")
                return False
            
            filename = os.path.basename(filepath)
            persist_path = os.path.join(self.persist_dir, filename)
            
            shutil.move(filepath, persist_path)
            self.logger.info(f"Archivo persistido: {filepath} -> {persist_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error persistiendo archivo {filepath}: {e}")
            return False

    def delete_file(self, filepath):
        """Elimina el archivo del filesystem."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"Archivo eliminado: {filepath}")
                return True
            else:
                self.logger.warning(f"Archivo no encontrado para eliminar: {filepath}")
                return False
        except Exception as e:
            self.logger.error(f"Error eliminando archivo {filepath}: {e}")
            return False