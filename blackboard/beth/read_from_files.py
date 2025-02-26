import extract_from_pdf as efp
import os
import updated_db as udb

client = udb.db("MAIN")
internal_collection = client._create_collection("INTERNAL")
external_collection = client._create_collection("EXTERNAL")

internal_folder_path = "./INTERNAL/"
external_folder_path = "./EXTERNAL/"

num_results = 10000000000000000

# NOTE: You need an ID to upload documents, so I am currently autogenerating it with uuid4()

def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

def add_to_internal_db(document, id=None, metadata=None):
    print(document)
    return client.add_to_internal_collection(id, document, metadata=metadata)

def add_to_external_db(document, id=None, metadata=None):
    print(document)
    return client.add_to_external_collection(id, document, metadata=metadata)
    
def query_internal_db(query, num_results=num_results):
    return client.filter_results(internal_collection.query(query_texts=[query], n_results=num_results))

def query_external_db(query, num_results=num_results):
    return client.filter_results(external_collection.query(query_texts=[query], n_results=num_results))

def folder_insert_in_db_and_delete(collection_name): #chosen type affects the database the function will add files to

    # Get a list of all files in the folder
    folder_path = internal_folder_path if collection_name == "INTERNAL" else external_folder_path
    files = os.listdir(folder_path)
    if not folder_path or not files:
        return "Error: No folder path provided."
    # Iterate over the files and remove each one
    for file in files:
        file_path = os.path.join(folder_path, file)
        words = efp.extract_text_from_pdf(file_path)

        #INSERT INTO DB
        if collection_name == "INTERNAL":
            add_to_internal_db(words, id=None, metadata=None)
        elif collection_name == "EXTERNAL":
            add_to_external_db(words, id=None, metadata=None)
        else:
            return "Error: Invalid collection name."    

        # REMOVE FILE
        remove_file(file_path)
        
    return True

print(query_external_db("international legal trends"))

