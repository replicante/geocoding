#  #!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  geo_adress_coord.py
#
#  Tannhausser <lamiradadelreplicante.com>
#
#
#  Simple script to obtain address or coordinates using module geopy

from geopy.geocoders import Nominatim

def geo():
    geolocator = Nominatim()
    while True:
        try:
            choice = 0
            choice = int(input("To get the coordinates type '1':\n"\
            "To get the address choose '2':\n"\
            "If you want to exit press '3': \n"))
        except ValueError:
            print("Oops! That value is not valid, try again.")

        if choice == 1:
            inputAddress = input("Which is the address?")
            coordenadas = geolocator.geocode(inputAddress)
            print(coordenadas.latitude, coordenadas.longitude)
            decision = input("Do you wish to continue? Y/n: ")
            if decision == "Y":
                continue
            elif decision == "n":
                break
            else:
                print("I don't understand your answer")

        elif choice == 2:
            inputLatitude = input("¿Which is the latitude? ")
            inputLongitude = input("Which is the longitude? ")
            location = geolocator.reverse([inputLatitude, inputLongitude])
            print(location.address)
            decision = input("Do you wish to continue? Y/n: ")
            if decision == "Y":
                continue
            elif decision == "n":
                break
            else:
                print("I don't understand your answer")
    
        elif choice == 3:
            break

if __name__ == "__main__":
    geo()
