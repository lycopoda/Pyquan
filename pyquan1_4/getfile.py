import sys, os

def get_file_name(dir_path, file_name, always="false"):
    file_list = os.listdir(dir_path)
    for item in file_list:
        if item.lower() == file_name.lower():
	    return os.path.join(dir_path, item)
    if always == "true":
        return os.path.join(dir_path, file_name)
    return None


    
