#!/usr/bin/env python3
"""
Secoda Update column Script:
Creates a new tag 'Return Data' in Secoda and optionally tags all columns in tables with 'returns' in their title.

Requirements:
    SECODA_API_KEY
    pip install -r requirments.txt
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
SECODA_API_KEY = os.getenv("SECODA_API_KEY")

def create_return_data_tag():
 
    # Prepare the tag request payload
    payload = {
        'name': 'Return Data',
        'description': "Custom Return Data tag",
        'color': "#4299E1"
    }
    # Make the API request
    response = requests.post(
        "https://app.secoda.co/api/v1/tag",
        headers={
            "Authorization": f"Bearer {SECODA_API_KEY}"  
        },
        json=payload
    )
    
def get_columns_for_table(table_id):
    
    
    response = requests.get(
        f"https://app.secoda.co/api/v1/column/columns?table_id={table_id}",
        headers={
             "Authorization": f"Bearer {SECODA_API_KEY}" 
        }
    )
    data = response.json()
    columns = data['results']
    return columns

def add_tag(column_id,tag_id):

    response = requests.patch(
        f"https://app.secoda.co/api/v1/column/{column_id}",
        headers={
            "Authorization": f"Bearer {SECODA_API_KEY}"
        },
        payload = {
            'tags': tag_id
        }
    )
    response.raise_for_status()

    return True

if __name__ == "__main__":
    
    # Get all tags
    #SECODA_API_KEY = os.getenv("SECODA_API_KEY")
    response = requests.get(
        "https://app.secoda.co/api/v1/tag",
        headers={
            "Authorization": f"Bearer {SECODA_API_KEY}"  
        },
    )
    data = response.json()
    tags = data['results']
    
    for tag in tags:  
        print(f"Tag Name: {tag.get('name')}, ID: {tag.get('id')}")

    # Check if 'Return Data' tag exists
    tag_exists = any(tag.get('name', '') == 'Return Data' for tag in tags)
    
    if not tag_exists:
        print("Creating 'Return Data' tag")
        create_return_data_tag()
    else:
        print("'Return Data' tag already exists")

    return_data_tag_id = next((tag.get('id') for tag in tags if tag.get('name') == 'Return Data'), None)

    # Filter tables that have 'returns' in their title
    response = requests.get(
        "https://app.secoda.co/api/v1/table/tables",
        headers={
            "Authorization": f"Bearer {SECODA_API_KEY}"  
        },
    )
    data = response.json()
    all_tables = data["results"]
    matching_tables = []
    for table in all_tables:
        table_title = table.get('title')
        if 'Returns' in table_title or 'returns' in table_title:
            matching_tables.append(table)

    #
    if not matching_tables:
        print("No tables found with 'returns' in their title, exiting.")
        exit(0)
    
    print(f"Found {len(matching_tables)} tables with 'returns' in their title.")

    proceed = (
        input(f"\nDo you want to proceed with updating above tables? (y/n): ")
        .lower()
        .strip()
    )

    if proceed in ["y", "yes"]:
        for i, table in enumerate(matching_tables, 1):
            table_id = table.get('id')
        
            # Get columns for this table
            columns = get_columns_for_table(table_id)
        
            # Tag each column
            column_tagged = 0
            for column in columns:
                column_name = column.get('title')
                column_id = column.get('id')

                #    Add tag to column
                success = add_tag(column_id,return_data_tag_id)
                if success:
                    column_tagged += 1
    else:
        print("Operation cancelled by user.")