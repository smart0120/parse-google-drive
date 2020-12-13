#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for loading a list of files on google drive and store info to ms sql db
"""

import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv

__author__ = "bursno22"
__license__ = "MIT"
__version__ = "0.0.1"

load_dotenv()


def get_root_folders(drive):
    folder_list = []
    for file in drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList():
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            folder_list.append({
                'title': file['title'],
                'id': file['id']
            })
    return folder_list

def get_files_in_folder(drive, parent):
    files =[]
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        files.append({
            "id": f["id"],
            "title": f['title'],
            "mimeType": f["mimeType"],
            "createdDate": f["createdDate"],
            "fileSize": f["fileSize"],
            "alternateLink": f['alternateLink']
        })
    return files

def main():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    gdrive = GoogleDrive(gauth)
    target_folders = list(filter(lambda x: x['title'] in os.getenv('FOLDERS').split(','), get_root_folders(gdrive)))
    if len(target_folders) > 0:
        for folder in target_folders:
            files = get_files_in_folder(gdrive, folder['id'])
            print (files)

if __name__ == '__main__':
    main()
