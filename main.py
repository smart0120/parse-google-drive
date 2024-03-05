#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for loading a list of files on google drive and store info to ms sql db
"""

import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pyodbc
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
    # Get Connection to Google Drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    gdrive = GoogleDrive(gauth)

    # Get Connection to MS SQL Server
    server_name = os.getenv("SERVER_NAME")
    driver = 'SQL Server'
    db_name = os.getenv("DB_NAME")
    table_name = os.getenv("TABLE_NAME")
    db_conn = pyodbc.connect(f'Driver={{SQL Server}};Server={server_name};Database={db_name};Trusted_Connection=yes;')
    cursor = db_conn.cursor()
    print ("SQL Server Connected")

    # Check if Table exist on Database
    query = f"IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' \
                AND TABLE_NAME=?) SELECT 1 AS res ELSE SELECT 0 AS res"
    result = cursor.execute(query, (table_name, ))
    if (result.fetchall()[0][0] == 0):
        query = f"CREATE TABLE {table_name} (\
            id nvarchar(100) NOT NULL,\
            directory varchar(255) NOT NULL,\
            title varchar(255) NOT NULL,\
            mime_type varchar(100) NOT NULL,\
            created_date datetime2 NOT NULL,\
            updated_date datetime2 NOT NULL,\
            file_size int DEFAULT 0 NOT NULL,\
            link varchar(255) NOT NULL,\
            PRIMARY KEY CLUSTERED (id)\
            WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)\
        )"
        # table doesn't exist, so create it
        result = cursor.execute(query)
        db_conn.commit()
    print ("SQL Server Table Configured")

    # Working with records
    updated_records = 0
    added_records = 0
    target_folders = list(filter(lambda x: x['title'] in os.getenv('FOLDERS').split(','), get_root_folders(gdrive)))
    if len(target_folders) > 0:
        for folder in target_folders:
            for file in get_files_in_folder(gdrive, folder['id']):
                # check if record already exist
                query = f"""SELECT count(*) FROM {table_name} WHERE id='{file["id"]}'"""
                if cursor.execute(query).fetchall()[0][0] == 0:
                    # create new record
                    query = f"""INSERT INTO {table_name} \
                        (id, directory, title, mime_type, created_date, updated_date, file_size, link) \
                        VALUES ('{file["id"]}', '{folder["title"]}', '{file["title"]}', '{file["mimeType"]}', '{file["createdDate"]}', \
                        CURRENT_TIMESTAMP, {file['fileSize']}, '{file["alternateLink"]}')"""
                    cursor.execute(query)
                    added_records += 1
                else:
                    # update record
                    query = f"""UPDATE {table_name} SET \
                        directory='{folder["title"]}', \
                        title='{file["title"]}', \
                        mime_type='{file["mimeType"]}', \
                        created_date='{file["createdDate"]}', \
                        updated_date=CURRENT_TIMESTAMP, \
                        file_size={file['fileSize']}, \
                        link='{file["alternateLink"]}' \
                        WHERE id='{file["id"]}'"""
                    cursor.execute(query)
                    updated_records += 1
            db_conn.commit()
    print (f"Records added: {added_records}")
    print (f"Records updated: {updated_records}")

if __name__ == '__main__':
    main()
