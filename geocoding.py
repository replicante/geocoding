#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geo_tool.py - Geocodificación y distancias (direcciones o coordenadas)
Requiere: pip install geopy
"""

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Configuración obligatoria: user_agent personalizado
geolocator = Nominatim(user_agent="mi_aplicacion_geo/1.0", timeout=10)

# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------
def coord_desde_direccion(direccion):
    try:
        loc = geolocator.geocode(direccion)
        if loc:
            return (loc.latitude, loc.longitude)
        else:
            print(f"❌ No se encontró: '{direccion}'")
            return None
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None

def direccion_desde_coord(lat, lon):
    try:
        loc = geolocator.reverse((lat, lon))
        return loc.address if loc else None
    except Exception as e:
        print(f"⚠️ Error reverso: {e}")
        return None

def distancia_entre_coords(coord1, coord2):
    try:
        return geodesic(coord1, coord2).kilometers
    except:
        return None

# ------------------------------------------------------------
# Menús
# ------------------------------------------------------------
def menu_coordenadas():
    while True:
        direc = input("\n📍 Dirección: ").strip()
        if not direc:
            continue
        coords = coord_desde_direccion(direc)
        if coords:
            print(f"✅ Lat: {coords[0]:.6f}, Lon: {coords[1]:.6f}")
        if input("¿Otra dirección? (s/n): ").lower() != 's':
            break

def menu_direccion():
    while True:
        try:
            lat = float(input("🌐 Latitud: "))
            lon = float(input("🌐 Longitud: "))
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                print("❌ Fuera de rango")
                continue
            direc = direccion_desde_coord(lat, lon)
            if direc:
                print(f"✅ Dirección:\n{direc}")
        except ValueError:
            print("❌ Número inválido")
        if input("¿Otra coordenada? (s/n): ").lower() != 's':
            break

def menu_distancia_direcciones():
    while True:
        d1 = input("🏙️ Primera dirección: ").strip()
        d2 = input("🏙️ Segunda dirección: ").strip()
        c1 = coord_desde_direccion(d1)
        c2 = coord_desde_direccion(d2)
        if c1 and c2:
            km = distancia_entre_coords(c1, c2)
            if km:
                print(f"✅ {km:.2f} km / {km*0.621371:.2f} millas")
        if input("¿Otra distancia? (s/n): ").lower() != 's':
            break

def menu_distancia_coordenadas():
    while True:
        try:
            print("📍 Punto A:")
            lat1 = float(input("  Lat: "))
            lon1 = float(input("  Lon: "))
            print("📍 Punto B:")
            lat2 = float(input("  Lat: "))
            lon2 = float(input("  Lon: "))
            km = distancia_entre_coords((lat1, lon1), (lat2, lon2))
            if km:
                print(f"✅ {km:.2f} km / {km*0.621371:.2f} millas")
        except ValueError:
            print("❌ Números válidos")
        if input("¿Otro cálculo? (s/n): ").lower() != 's':
            break

# ------------------------------------------------------------
# Principal
# ------------------------------------------------------------
def main():
    while True:
        print("\n" + "="*50)
        print("  GEO TOOL - Elige una opción")
        print("="*50)
        print("1️⃣  Dirección → coordenadas")
        print("2️⃣  Coordenadas → dirección")
        print("3️⃣  Distancia entre dos direcciones")
        print("4️⃣  Distancia entre dos coordenadas")
        print("5️⃣  Salir")
        op = input("Opción (1-5): ").strip()
        if op == '1':
            menu_coordenadas()
        elif op == '2':
            menu_direccion()
        elif op == '3':
            menu_distancia_direcciones()
        elif op == '4':
            menu_distancia_coordenadas()
        elif op == '5':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupción. Saliendo...")
