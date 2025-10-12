"""
Módulo de gestión de videos
Contiene las clases especializadas para el manejo de videos largos y cortos
"""

from .video_downloader import VideoDownloader
from .video_forwarder import VideoForwarder

__all__ = ['VideoDownloader', 'VideoForwarder']