import logging
from datetime import datetime
from pathlib import Path

class BOELogger:
    def __init__(self, log_file="logs/boe_monitor.log"):
        # Crear directorio de logs si no existe
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar el logger
        self.logger = logging.getLogger('BOEMonitor')
        self.logger.setLevel(logging.INFO)
        
        # Formato más detallado para los logs
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s\n'
            '           {Process ID: %(process)d - Thread: %(threadName)s}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Añadir handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def success(self, message):
        """Método específico para registrar operaciones exitosas"""
        self.logger.info(f"✅ SUCCESS: {message}")
    
    def start_operation(self, operation_name):
        """Registra el inicio de una operación importante"""
        self.logger.info(f"▶️ INICIANDO: {operation_name}")
    
    def end_operation(self, operation_name):
        """Registra el fin de una operación importante"""
        self.logger.info(f"⏹️ FINALIZADO: {operation_name}") 