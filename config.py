# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia

import os
from pathlib import Path

class Config:
    """
    Classe de configuração principal do sistema
    """

    # ========================================================================
    # INFORMAÇÕES DO SISTEMA
    # ========================================================================
    DESENVOLVEDOR = 'Márcio Fernando Maia'
    VERSAO_SISTEMA = '2.0.0'

    # ========================================================================
    # DIRETÓRIOS DO SISTEMA
    # ========================================================================
    BASE_DIR = Path(__file__).resolve().parent
    RELATORIOS_DIR = os.path.join(BASE_DIR, 'relatorios')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    # Criar diretórios se não existirem
    for directory in [RELATORIOS_DIR, STATIC_DIR, TEMPLATES_DIR, UPLOAD_FOLDER]:
        os.makedirs(directory, exist_ok=True)

    # ========================================================================
    # BANCO DE DADOS
    # ========================================================================
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "analise_por_posicao.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 30,
        'pool_recycle': -1,
        'pool_pre_ping': True,
        'echo': False,
        'connect_args': {
            'timeout': 15,
            'check_same_thread': False
        }
    }

    # Alias para compatibilidade
    DATABASE_URL = SQLALCHEMY_DATABASE_URI

    # ========================================================================
    # FLASK CONFIGURATION
    # ========================================================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production-mfm-2024')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # ========================================================================
    # CORES E TEMAS
    # ========================================================================
    COR_PRIMARIA = '#4A90E2'  # Azul principal
    COR_SECUNDARIA = '#50E3C2'  # Verde água
    COR_SUCESSO = '#7ED321'  # Verde sucesso
    COR_ALERTA = '#F5A623'  # Laranja alerta
    COR_ERRO = '#D0021B'  # Vermelho erro

    # ========================================================================
    # PERFORMANCE SETTINGS (Alto Volume)
    # ========================================================================
    CHUNK_SIZE = 10000  # Apostas por chunk
    MAX_WORKERS = 8     # Threads paralelas
    CACHE_SIZE = 1000   # Cache LRU
    BATCH_SIZE = 500    # Operações em lote

    # ========================================================================
    # LIMITS
    # ========================================================================
    MAX_APOSTAS = 2629575
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_EXECUTION_TIME = 3600  # 1 hora

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')

    # ========================================================================
    # MONITORING
    # ========================================================================
    ENABLE_MONITORING = True
    LOG_LEVEL = 'INFO'

    # ========================================================================
    # CORS
    # ========================================================================
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5000',
        'http://localhost:5050'
    ]

    # ========================================================================
    # FILE UPLOAD
    # ========================================================================
    ALLOWED_EXTENSIONS = {'csv', 'json', 'txt', 'xlsx', 'xls', 'pdf'}
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE

    # ========================================================================
    # REDIS (Opcional - para cache distribuído)
    # ========================================================================
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # ========================================================================
    # 🆕 ANÁLISE DE COLUNAS - CONFIGURAÇÕES
    # ========================================================================
    
    # Mapeamento: Número → Coluna (1 a 10)
    NUMERO_PARA_COLUNA = {
        1: 1, 11: 1, 21: 1, 31: 1,
        2: 2, 12: 2, 22: 2,
        3: 3, 13: 3, 23: 3,
        4: 4, 14: 4, 24: 4,
        5: 5, 15: 5, 25: 5,
        6: 6, 16: 6, 26: 6,
        7: 7, 17: 7, 27: 7,
        8: 8, 18: 8, 28: 8,
        9: 9, 19: 9, 29: 9,
        10: 10, 20: 10, 30: 10
    }

    # Mapeamento reverso: Coluna → Números
    COLUNA_PARA_NUMEROS = {
        1: [1, 11, 21, 31],
        2: [2, 12, 22],
        3: [3, 13, 23],
        4: [4, 14, 24],
        5: [5, 15, 25],
        6: [6, 16, 26],
        7: [7, 17, 27],
        8: [8, 18, 28],
        9: [9, 19, 29],
        10: [10, 20, 30]
    }

    # Cores oficiais do Dia de Sorte
    CORES_DIA_DE_SORTE = {
        'principal': '#FF6B35',      # Laranja vibrante
        'secundaria': '#FFB84D',     # Laranja claro
        'destaque': '#FF8C42',       # Laranja médio
        'fundo': '#FFF5EB',          # Bege claro
        'texto': '#2C3E50',          # Azul escuro
        'sucesso': '#27AE60',        # Verde
        'info': '#3498DB',           # Azul
        'alerta': '#F39C12'          # Amarelo
    }

    # Escala de cores para heatmap (do menos frequente ao mais frequente)
    HEATMAP_CORES = [
        '#FFF5EB',  # 0-10% - Muito claro
        '#FFE5CC',  # 10-20%
        '#FFD6AD',  # 20-30%
        '#FFC78E',  # 30-40%
        '#FFB84D',  # 40-50% - Laranja claro
        '#FFA93D',  # 50-60%
        '#FF9A2D',  # 60-70%
        '#FF8C42',  # 70-80% - Laranja médio
        '#FF7D38',  # 80-90%
        '#FF6B35'   # 90-100% - Laranja vibrante (mais frequente)
    ]

    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    @staticmethod
    def get_performance_config(volume):
        """
        Ajusta configuração baseado no volume de apostas

        Args:
            volume (int): Número de apostas

        Returns:
            dict: Configurações de performance ajustadas
        """
        if volume < 10000:
            return {
                'CHUNK_SIZE': 1000,
                'MAX_WORKERS': 4,
                'CACHE_SIZE': 500
            }
        elif volume < 100000:
            return {
                'CHUNK_SIZE': 5000,
                'MAX_WORKERS': 6,
                'CACHE_SIZE': 1000
            }
        else:
            return {
                'CHUNK_SIZE': 10000,
                'MAX_WORKERS': 8,
                'CACHE_SIZE': 1000
            }

    @staticmethod
    def init_directories():
        """Inicializa todos os diretórios necessários"""
        directories = [
            Config.RELATORIOS_DIR,
            Config.STATIC_DIR,
            Config.TEMPLATES_DIR,
            Config.UPLOAD_FOLDER
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Diretório verificado/criado: {directory}")

    # 🆕 Métodos para Análise de Colunas
    @staticmethod
    def obter_coluna(numero):
        """Retorna a coluna (1-10) de um número (1-31)"""
        return Config.NUMERO_PARA_COLUNA.get(numero)

    @staticmethod
    def obter_numeros_da_coluna(coluna):
        """Retorna os números que pertencem a uma coluna"""
        return Config.COLUNA_PARA_NUMEROS.get(coluna, [])

    @staticmethod
    def obter_cor_heatmap(percentual):
        """Retorna a cor do heatmap baseada no percentual (0-100)"""
        if percentual < 0:
            percentual = 0
        if percentual > 100:
            percentual = 100
        
        # Mapear percentual para índice (0-9)
        indice = min(int(percentual / 10), 9)
        return Config.HEATMAP_CORES[indice]


# ========================================================================
# COMPATIBILIDADE COM VERSÕES ANTIGAS
# ========================================================================
class HighVolumeConfig:
    """Mantém compatibilidade com código antigo que usa HighVolumeConfig"""

    # Performance Settings
    CHUNK_SIZE = Config.CHUNK_SIZE
    MAX_WORKERS = Config.MAX_WORKERS
    CACHE_SIZE = Config.CACHE_SIZE
    BATCH_SIZE = Config.BATCH_SIZE

    # Limits
    MAX_APOSTAS = Config.MAX_APOSTAS
    MAX_FILE_SIZE = Config.MAX_FILE_SIZE
    MAX_EXECUTION_TIME = Config.MAX_EXECUTION_TIME

    # Database
    DATABASE_URL = Config.DATABASE_URL

    # Redis
    REDIS_URL = Config.REDIS_URL

    # Rate Limiting
    RATELIMIT_STORAGE_URL = Config.RATELIMIT_STORAGE_URL

    # Monitoring
    ENABLE_MONITORING = Config.ENABLE_MONITORING
    LOG_LEVEL = Config.LOG_LEVEL
    DEBUG = Config.DEBUG

    # CORS
    CORS_ORIGINS = Config.CORS_ORIGINS

    # File Upload
    UPLOAD_FOLDER = Config.UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS

    @staticmethod
    def get_performance_config(volume):
        """Wrapper para Config.get_performance_config"""
        return Config.get_performance_config(volume)
