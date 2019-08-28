# -*- coding: utf-8 -*-
"""
Created as a version of the item transfer tool script that does bulk transfers
"""

from arcgis import GIS
from pathlib import Path
import re


# creates GIS object for user that contains the data for migration
origin_url = input("Enter url of portal: ")
origin_user= input("Enter username: ")
origin_pass = input("Enter password: ")
my_gis = GIS(origin_url,origin_user,origin_pass )

# Creates the GIS object for the user that will be recieving the data from the migration
migrant_url = input( "Enter url of the portal to send data to: ")
rec_user = input("Enter username to deliver to: ")
rec_pass = input("Enter password of user: ")
receiver_gis = GIS(migrant_url, rec_user, rec_pass)

#stores username
user = my_gis.properties.user.username

print("Successfully logged in as: " + user)
    
#searches for Hosted Feature Layer items and begins migration process
feature_search = my_gis.content.search(query="owner: " +user, max_items = 100, item_type = "Feature Layer Collection")
for item in feature_search:
    
    # try and except case to cover any issues with the id's from the user
    try:
                   
            #gets Item ID at the ID 
            feature_item = my_gis.content.get(item.id)
            
            print("\n")
                
            # starts the export of the hosted feature layer to File Geodatabase 'FGDB' format
            item_name = feature_item.title
            feature_item.export(item_name,"File Geodatabase",parameters = None, wait = True)
            status_finished = True
            print("File '" + item_name + "' converted to a File Geodatabase format successfully")
            
            # Searches for created File Geodatabase version of Hosted Feature Layer
            geodata_result = my_gis.content.search(query = "owner: " + user and "title:" + item_name ,item_type = "File Geodatabase")
            geo_item = my_gis.content.get(geodata_result[0].id)
            
            #creates a path to store the data where the current file is being run
            data_path = Path('./data')
            
            # checks if 'data' path exits. If not, it creates the path
            if not data_path.exists():
                data_path.mkdir()
                
            geo_item.download(data_path)
            print("Item succefully downloaded to temporary folder in current directory")
            
            
            # Stores name of file location
            data_name = re.sub('[\W_]+', '',item_name)
            data_location =  "./data/" + data_name  + ".zip"
            
            # Creates a disctionary that stores the properties of the File Geodatabase
            geo_properties = {
                    'title': item_name,
                    'type' : 'File Geodatabase',
                    'typeKeywords': feature_item.typeKeywords,
                    'tags': feature_item.tags,
                    'description': feature_item.description,
                    'snippet': feature_item.snippet
                    }
            
            # uses add() from ContententManager portion of python api to the new profile
            rec_adder = receiver_gis.content.add(geo_properties, data = data_location)
            print("\n")
            
            
            #publishes url
            pub_migrate = rec_adder.publish()
            print(item_name + " file has succesfully been added to the " + rec_user + " account at url: " + migrant_url  )
            print("Item has successfully become a hosted feature layer")
                    
                        
                    
    except:
            print("invalid ID")
                    
    
print("migration complete")

 


