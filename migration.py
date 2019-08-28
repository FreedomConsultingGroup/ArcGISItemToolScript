# -*- coding: utf-8 -*-

"""
Created as a transfer tool script for one item at a time by id
"""
from arcgis import GIS
from pathlib import Path
import re


#creates GIS object
origin_url = input("Enter url of portal: ")
origin_user= input("Enter username: ")
origin_pass = input("Enter password: ")

my_gis = GIS(origin_url,origin_user,origin_pass )

#stores username
user = my_gis.properties.user.username

print("Successfully logged in as: " + user)

#boolean that will be used for conditional for the while loop running the migration
migration_finish = False

while (not migration_finish):
    
    
    #prompts user for item id
    feature_prompt = input("Enter Item ID or type 'exit' to finish : ")
    try:
            
        #ends loop
        if(feature_prompt =="exit"):
            print("Migration complete")
            migration_finish = True
            
        else:
            #gets Item at the ID inputted
            feature_item = my_gis.content.get(feature_prompt)
            
            print("\n")
            print(feature_item)
            
            #sets conditional boolean variables for the loop
            is_valid = True
            status_finished = False
            
            while(is_valid and not status_finished):
                # checks if user logged in is the owner of the item
                if(feature_item.owner == user):
                    print("This user owns this item")
                    
                    # checks if item is a hosted feature service
                    if(feature_item.type == "Feature Service"):   
                        print("Item is a hosted feature service")
                        
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
                        
                        
                        # prompts to asks for information regarding where to send the downloaded File Geodatabase to
                        migrant_url = input( "Enter url of the portal to send data to: ")
                        rec_user = input("Enter username to deliver to: ")
                        rec_pass = input("Enter password of user: ")
                        receiver_gis = GIS(migrant_url, rec_user, rec_pass)
                        
                        
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
                        print(item_name + " file has succesfully been added to the " + rec_user + " account at url: " + migrant_url  )
                        
                        #publishes url
                        pub_migrate = rec_adder.publish()
                        
                        print("Item has successfully become a hosted feature layer")
                        
                        
                        
                    else:
                        print("Not a hosted feature service")
                        is_valid = False
                        
            
                else:
                    print("User does not own this item")
                    is_valid = False
                    
    except:
            print("invalid ID")
                
    


 
