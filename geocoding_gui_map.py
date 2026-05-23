#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geo Tool - Con mapa interactivo (corregido error L is not defined)
"""

import sys
import tempfile
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QTextEdit, QStatusBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium

# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------
USER_AGENT = "mi_app_geo_map/1.0"
TIMEOUT = 10

STYLESHEET = """
QMainWindow { background-color: #f5f7fa; }
QTabWidget::pane { border: 1px solid #cbd5e0; border-radius: 8px; background-color: white; margin-top: -1px; }
QTabBar::tab { background-color: #e2e8f0; color: #2d3748; font-weight: bold; padding: 8px 16px; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
QTabBar::tab:selected { background-color: white; color: #2c5282; border-bottom: 2px solid #2c5282; }
QLineEdit { border: 1px solid #cbd5e0; border-radius: 6px; padding: 8px; }
QPushButton { background-color: #2c5282; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background-color: #1a365d; }
QTextEdit { border: 1px solid #cbd5e0; border-radius: 6px; padding: 8px; background-color: #f7fafc; font-family: monospace; }
QStatusBar { background-color: #edf2f7; }
"""

# ------------------------------------------------------------
# Función para generar mapa con CDN alternativo
# ------------------------------------------------------------
def crear_mapa_html(coord1, coord2):
    centro_lat = (coord1[0] + coord2[0]) / 2
    centro_lon = (coord1[1] + coord2[1]) / 2
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=5,
        control_scale=True,
        tiles='OpenStreetMap'
    )
    folium.Marker(coord1, popup="📍 Origen", icon=folium.Icon(color='green', icon='play', prefix='fa')).add_to(mapa)
    folium.Marker(coord2, popup="🎯 Destino", icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(mapa)
    folium.PolyLine([coord1, coord2], color='blue', weight=5, opacity=0.8, tooltip='Ruta directa').add_to(mapa)
    archivo = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    mapa.save(archivo.name)
    return archivo.name

# ------------------------------------------------------------
# Hilos (igual que antes, sin cambios)
# ------------------------------------------------------------
class GeocodeThread(QThread):
    resultado = pyqtSignal(tuple)
    error = pyqtSignal(str)
    def __init__(self, direccion):
        super().__init__()
        self.direccion = direccion
    def run(self):
        try:
            geolocator = Nominatim(user_agent=USER_AGENT, timeout=TIMEOUT)
            loc = geolocator.geocode(self.direccion)
            if loc:
                self.resultado.emit((loc.latitude, loc.longitude))
            else:
                self.resultado.emit(None)
        except Exception as e:
            self.error.emit(str(e))

class ReverseGeocodeThread(QThread):
    resultado = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, lat, lon):
        super().__init__()
        self.lat = lat
        self.lon = lon
    def run(self):
        try:
            geolocator = Nominatim(user_agent=USER_AGENT, timeout=TIMEOUT)
            loc = geolocator.reverse((self.lat, self.lon))
            if loc:
                self.resultado.emit(loc.address)
            else:
                self.resultado.emit(None)
        except Exception as e:
            self.error.emit(str(e))

class DistanceAddressesThread(QThread):
    resultado = pyqtSignal(float, tuple, tuple)
    error = pyqtSignal(str)
    def __init__(self, dir1, dir2):
        super().__init__()
        self.dir1 = dir1
        self.dir2 = dir2
    def run(self):
        try:
            geolocator = Nominatim(user_agent=USER_AGENT, timeout=TIMEOUT)
            loc1 = geolocator.geocode(self.dir1)
            loc2 = geolocator.geocode(self.dir2)
            if not loc1:
                self.error.emit(f"No se encontró: {self.dir1}")
                return
            if not loc2:
                self.error.emit(f"No se encontró: {self.dir2}")
                return
            coord1 = (loc1.latitude, loc1.longitude)
            coord2 = (loc2.latitude, loc2.longitude)
            dist = geodesic(coord1, coord2).kilometers
            self.resultado.emit(dist, coord1, coord2)
        except Exception as e:
            self.error.emit(str(e))

class DistanceCoordsThread(QThread):
    resultado = pyqtSignal(float, tuple, tuple)
    error = pyqtSignal(str)
    def __init__(self, lat1, lon1, lat2, lon2):
        super().__init__()
        self.lat1 = lat1
        self.lon1 = lon1
        self.lat2 = lat2
        self.lon2 = lon2
    def run(self):
        try:
            coord1 = (self.lat1, self.lon1)
            coord2 = (self.lat2, self.lon2)
            dist = geodesic(coord1, coord2).kilometers
            self.resultado.emit(dist, coord1, coord2)
        except Exception as e:
            self.error.emit(str(e))

# ------------------------------------------------------------
# Pestañas (simplificadas por brevedad, pero completas)
# ------------------------------------------------------------
class TabAddressToCoords(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.setup_ui()
        self.thread = None
    def setup_ui(self):
        layout = QVBoxLayout()
        self.address_edit = QLineEdit()
        self.btn_convert = QPushButton("🔍 Obtener coordenadas")
        self.btn_convert.clicked.connect(self.on_convert)
        self.result_text = QTextEdit()
        layout.addWidget(QLabel("📍 Convertir dirección a coordenadas"))
        layout.addWidget(self.address_edit)
        layout.addWidget(self.btn_convert)
        layout.addWidget(self.result_text)
        self.setLayout(layout)
    def on_convert(self):
        direccion = self.address_edit.text().strip()
        if not direccion:
            self.result_text.setText("❌ Ingrese dirección")
            return
        self.btn_convert.setEnabled(False)
        self.result_text.setText("🌐 Buscando...")
        self.thread = GeocodeThread(direccion)
        self.thread.resultado.connect(self.on_result)
        self.thread.error.connect(self.on_error)
        self.thread.finished.connect(lambda: self.btn_convert.setEnabled(True))
        self.thread.start()
    def on_result(self, coords):
        if coords:
            self.result_text.setText(f"✅ Lat: {coords[0]:.6f}\nLon: {coords[1]:.6f}")
        else:
            self.result_text.setText("❌ No encontrado")
    def on_error(self, err):
        self.result_text.setText(f"⚠️ {err}")

class TabCoordsToAddress(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.setup_ui()
        self.thread = None
    def setup_ui(self):
        layout = QVBoxLayout()
        self.lat_edit = QLineEdit()
        self.lon_edit = QLineEdit()
        self.btn_reverse = QPushButton("🔁 Obtener dirección")
        self.btn_reverse.clicked.connect(self.on_reverse)
        self.result_text = QTextEdit()
        layout.addWidget(QLabel("🗺️ Coordenadas a dirección"))
        layout.addWidget(self.lat_edit)
        layout.addWidget(self.lon_edit)
        layout.addWidget(self.btn_reverse)
        layout.addWidget(self.result_text)
        self.setLayout(layout)
    def on_reverse(self):
        try:
            lat = float(self.lat_edit.text().strip())
            lon = float(self.lon_edit.text().strip())
        except:
            self.result_text.setText("❌ Números válidos")
            return
        self.btn_reverse.setEnabled(False)
        self.result_text.setText("🌐 Consultando...")
        self.thread = ReverseGeocodeThread(lat, lon)
        self.thread.resultado.connect(self.on_result)
        self.thread.error.connect(self.on_error)
        self.thread.finished.connect(lambda: self.btn_reverse.setEnabled(True))
        self.thread.start()
    def on_result(self, address):
        self.result_text.setText(f"✅ {address}" if address else "❌ No encontrado")
    def on_error(self, err):
        self.result_text.setText(f"⚠️ {err}")

class TabDistanceAddresses(QWidget):
    def __init__(self, status_bar, update_map_callback):
        super().__init__()
        self.status_bar = status_bar
        self.update_map_callback = update_map_callback
        self.setup_ui()
        self.thread = None
    def setup_ui(self):
        layout = QVBoxLayout()
        self.addr1_edit = QLineEdit()
        self.addr2_edit = QLineEdit()
        self.btn_dist = QPushButton("🚀 Calcular distancia")
        self.btn_dist.clicked.connect(self.on_distance)
        self.result_text = QTextEdit()
        layout.addWidget(QLabel("📏 Distancia entre direcciones"))
        layout.addWidget(self.addr1_edit)
        layout.addWidget(self.addr2_edit)
        layout.addWidget(self.btn_dist)
        layout.addWidget(self.result_text)
        self.setLayout(layout)
    def on_distance(self):
        d1 = self.addr1_edit.text().strip()
        d2 = self.addr2_edit.text().strip()
        if not d1 or not d2:
            self.result_text.setText("❌ Complete ambas")
            return
        self.btn_dist.setEnabled(False)
        self.result_text.setText("🔄 Calculando...")
        self.thread = DistanceAddressesThread(d1, d2)
        self.thread.resultado.connect(self.on_result)
        self.thread.error.connect(self.on_error)
        self.thread.finished.connect(lambda: self.btn_dist.setEnabled(True))
        self.thread.start()
    def on_result(self, km, coord1, coord2):
        self.result_text.setText(f"✅ {km:.2f} km / {km*0.621371:.2f} millas")
        self.update_map_callback(coord1, coord2)
    def on_error(self, err):
        self.result_text.setText(f"⚠️ {err}")

class TabDistanceCoords(QWidget):
    def __init__(self, status_bar, update_map_callback):
        super().__init__()
        self.status_bar = status_bar
        self.update_map_callback = update_map_callback
        self.setup_ui()
        self.thread = None
    def setup_ui(self):
        layout = QVBoxLayout()
        self.lat1_edit = QLineEdit()
        self.lon1_edit = QLineEdit()
        self.lat2_edit = QLineEdit()
        self.lon2_edit = QLineEdit()
        self.btn_dist = QPushButton("📐 Calcular distancia")
        self.btn_dist.clicked.connect(self.on_distance)
        self.result_text = QTextEdit()
        layout.addWidget(QLabel("📍 Distancia entre coordenadas"))
        layout.addWidget(QLabel("Punto A"))
        layout.addWidget(self.lat1_edit)
        layout.addWidget(self.lon1_edit)
        layout.addWidget(QLabel("Punto B"))
        layout.addWidget(self.lat2_edit)
        layout.addWidget(self.lon2_edit)
        layout.addWidget(self.btn_dist)
        layout.addWidget(self.result_text)
        self.setLayout(layout)
    def on_distance(self):
        try:
            lat1 = float(self.lat1_edit.text())
            lon1 = float(self.lon1_edit.text())
            lat2 = float(self.lat2_edit.text())
            lon2 = float(self.lon2_edit.text())
        except:
            self.result_text.setText("❌ Números válidos")
            return
        self.btn_dist.setEnabled(False)
        self.result_text.setText("🔄 Calculando...")
        self.thread = DistanceCoordsThread(lat1, lon1, lat2, lon2)
        self.thread.resultado.connect(self.on_result)
        self.thread.error.connect(self.on_error)
        self.thread.finished.connect(lambda: self.btn_dist.setEnabled(True))
        self.thread.start()
    def on_result(self, km, coord1, coord2):
        self.result_text.setText(f"✅ {km:.2f} km / {km*0.621371:.2f} millas")
        self.update_map_callback(coord1, coord2)
    def on_error(self, err):
        self.result_text.setText(f"⚠️ {err}")

# ------------------------------------------------------------
# Pestaña Mapa con configuración mejorada
# ------------------------------------------------------------
class TabMapVisual(QWidget):
    def __init__(self, status_bar):
        super().__init__()
        self.status_bar = status_bar
        self.web_view = QWebEngineView()
        # Configuración para permitir contenido remoto
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.current_html_path = None
        self.mostrar_mapa_inicial()

    def mostrar_mapa_inicial(self):
        # Mapa con un solo punto para inicio
        mapa = folium.Map(location=[40.4167, -3.7038], zoom_start=6)
        folium.Marker([40.4167, -3.7038], popup="Madrid", icon=folium.Icon(color='blue')).add_to(mapa)
        archivo = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        mapa.save(archivo.name)
        self.cargar_mapa(archivo.name)

    def cargar_mapa(self, ruta_html):
        self.web_view.setUrl(QUrl.fromLocalFile(ruta_html))
        if self.current_html_path and os.path.exists(self.current_html_path):
            try:
                os.unlink(self.current_html_path)
            except:
                pass
        self.current_html_path = ruta_html

    def actualizar_mapa(self, coord1, coord2):
        try:
            ruta_html = crear_mapa_html(coord1, coord2)
            self.cargar_mapa(ruta_html)
            self.status_bar.showMessage("Mapa actualizado", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error al generar mapa: {e}", 5000)

    def closeEvent(self, event):
        if self.current_html_path and os.path.exists(self.current_html_path):
            try:
                os.unlink(self.current_html_path)
            except:
                pass
        event.accept()

# ------------------------------------------------------------
# Ventana principal
# ------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌐 Geo Tool - Mapas y distancias")
        self.setMinimumSize(800, 650)
        self.setStyleSheet(STYLESHEET)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Listo")

        self.tab_map = TabMapVisual(self.status_bar)
        self.tabs = QTabWidget()
        self.tabs.addTab(TabAddressToCoords(self.status_bar), "📍 Dirección → Coordenadas")
        self.tabs.addTab(TabCoordsToAddress(self.status_bar), "🗺️ Coordenadas → Dirección")
        self.tabs.addTab(TabDistanceAddresses(self.status_bar, self.actualizar_mapa), "🚗 Distancia (direcciones)")
        self.tabs.addTab(TabDistanceCoords(self.status_bar, self.actualizar_mapa), "📐 Distancia (coordenadas)")
        self.tabs.addTab(self.tab_map, "🗺️ Ver Mapa")
        self.setCentralWidget(self.tabs)

    def actualizar_mapa(self, coord1, coord2):
        self.tab_map.actualizar_mapa(coord1, coord2)
        self.tabs.setCurrentWidget(self.tab_map)

# ------------------------------------------------------------
# Ejecución
# ------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
