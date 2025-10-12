"""
Módulo de gestión de videos
Contiene las clases especializadas para el manejo de videos largos y cortos
"""

from .video_downloader import VideoDownloader
from .video_forwarder import VideoForwarder
from .video_processor_advanced import AdvancedVideoProcessor

__all__ = ['VideoDownloader', 'VideoForwarder', 'AdvancedVideoProcessor']