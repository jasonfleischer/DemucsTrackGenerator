#!/usr/bin/python3

import shutil
import os

def getFileName(url):
	file_name = url[url.rindex("/")+1:]
	file_name = file_name[:file_name.index(".")]
	return file_name

def get_file_contents(source_path):
	result = None
	if os.path.isfile(source_path):
		with open(source_path, 'r') as file:
			result = file.read()
	return result

def remove_file(path):
	try:
		os.remove(path)
	except FileNotFoundError:
		print(f"{path} not found.")
	except Exception as e:
		print(f"An error occurred: {e}")

def file_exists(path):
    return os.path.exists(path)

def remove_folder(folder_path):
    try:
        if os.path.exists(folder_path):
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
            else:
                os.remove(folder_path)
        else:
            print(f"Error: {folder_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied to remove {folder_path}.")
    except Exception as e:
        print(f"Error: {e}")

def copy_folder(source_folder, destination_folder):
    try:
        if not os.path.exists(source_folder):
            print(f"Source folder '{source_folder}' does not exist.")
            return
        shutil.copytree(source_folder, destination_folder)
        print(f"Folder copied from '{source_folder}' to '{destination_folder}'.")
    except FileExistsError:
        print(f"Destination folder '{destination_folder}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

def copy_file_to_folder(source_path, destination_folder):
    ext = source_path[source_path.index(".")+1:]
    copy_file(source_path, f"{destination_folder}/{getFileName(source_path)}.{ext}")

def copy_file(source_path, destination_path):
    try:
        with open(source_path, 'rb') as source_file:
            with open(destination_path, 'wb') as destination_file:
                destination_file.write(source_file.read())
    except FileNotFoundError:
        print(f"Error: {source_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied to copy {source_path}.")
    except Exception as e:
        print(f"Error: {e}")