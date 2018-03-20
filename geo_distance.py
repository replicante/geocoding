#  #!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   geo_adress_coord.py
#
#   Tannhausser <lamiradadelreplicante.com>
#
# Simple script to calculate distances between address or coordinates 
# using module geopy.
# 
# We use Great-circle distance to obtain the shortest distance 
# between two points.


from geopy.geocoders import Nominatim
from geopy.distance import great_circle

geolocator = Nominatim()

def distance():
    while True:
        try:
            choice = 0
            choice = int(input("To calculate the distance between cities type '1':\n"
            "To calculate the distance between coordinates type '2':\n"\
            "If you want to exit press '3': \n"))
        except ValueError:
            print("Oops! That value is not valid, try again.")
        
        
        if choice == 1:
            try:
                inputAddress = input("¿Which is the address 1? ")
                coord1 = geolocator.geocode(inputAddress)
                address_1 = (coord1.latitude, coord1.longitude)
            except AttributeError:
                print("There is a problem with data")
                
            try:
                inputAddress = input("¿Which is the address 2? ")
                coord2 = geolocator.geocode(inputAddress)
                address_2 = (coord2.latitude, coord2.longitude)
            except AttributeError:
                print("There is a problem with data")

            def distance_cities():
                print(great_circle(address_1, address_2))
            distance_cities()
            decision = input("Do you wish to continue? Y/n: ")
            if decision == "Y":
                continue
            elif decision == "n":
                break
            
        
        elif choice == 2:
            latitude1 = input ('origin latitude: ')
            longitude1 = input ('origin longitude: ')
            latitude2 = input('destination latitude: ')
            longitude2 = input ('destination longitude: ')
            def distance_coord():
                address_1 = (latitude1, longitude1)
                address_2 = (latitude2, longitude2)
                print(great_circle(address_1, address_2))


            distance_coord()
            decision = input("Do you wish to continue? Y/n: ")
            if decision == "Y":
                continue
            elif decision == "N":
                break
            else:
                print("I do not understand your answer")
        
        elif choice== 3:
            break

if __name__ == "__main__":
    distance()



