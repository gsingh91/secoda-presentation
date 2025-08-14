#!/usr/bin/env python3
"""
Secoda Table Description Updater

This script:
1. Gets all tables with missing descriptions from Secoda API
2. Reads table descriptions from Google Sheets (table_id, table_name, table_desc)
3. Updates missing descriptions by matching table_id

Requirements:
    SECODA_API_KEY
    pip install -r requirments.txt
"""
import os
import gspread
import requests
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SECODA_API_KEY = os.getenv("SECODA_API_KEY")


def tables_without_desc():

    # Get all tables from the workspace
    response = requests.get(
        "https://app.secoda.co/api/v1/table/tables",
        headers={"Authorization": f"Bearer {SECODA_API_KEY}"},
    )

    data = response.json()
    all_tables = data["results"]

    # Filter tables without descriptions
    tables_without_desc = []
    for table in all_tables:
        description = table.get("description")
        if not description or description.strip() == "":
            tables_without_desc.append(table)

    return tables_without_desc


def read_google_sheet():

    # Read table descriptions from Google Sheets
    sheet_url = os.getenv("GOOGLE_SHEET_URL")
    google_sheets_api_key = os.getenv("GOOGLE_API_KEY")

    gc = gspread.api_key(google_sheets_api_key)
    sheet_id = sheet_url.split("/spreadsheets/d/")[1].split("/")[0]
    sh = gc.open_by_key(sheet_id)

    df = pd.DataFrame(sh.sheet1.get_all_records())

    # Create mapping from table_id to description
    description_map = {}

    for _, row in df.iterrows():
        table_id = row.get("id").strip()
        table_desc = row.get("description").strip()

        if table_id and table_desc:
            description_map[table_id] = table_desc

    return description_map


def update_table_description(table_id, description):

    # Update table description
    url = f"https://app.secoda.co/api/v1/table/tables/{table_id}"

    payload = {"description": description}
    print(description)
    headers = {"Authorization": f"Bearer {SECODA_API_KEY}"}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Successfully updated table {table_id} with new description.")
    else:
        print(
            f"Failed to update table {table_id}. Status code: {response.status_code}, Response: {response.text}"
        )


if __name__ == "__main__":

    # Get tables without descriptions
    print("Fetching tables without descriptions...")
    tables_without_desc = tables_without_desc()

    if not tables_without_desc:
        print("All tables have descriptions. No updates needed.")
        exit(0)

    print(f"Found {len(tables_without_desc)} tables without descriptions:\n")
    for table in tables_without_desc:
        table_id = table.get("id")
        table_name = table.get("title")
        print(f"{table_id} : {table['title']}")

    # Read descriptions from Google Sheet
    print("\nReading table descriptions from Google Sheet...")
    description_map = read_google_sheet()
    print(
        f"\nRead {len(description_map)} tables with descriptions from Google Sheet \n"
    )

    # Check if descriptions are available for tables without descriptions
    print("\nChecking for tables with available descriptions...\n")
    tables_to_update = []
    for table in tables_without_desc:
        table_id = table.get("id")
        table_name = table.get("title")
        if table_id in description_map:
            print(f"description available for {table_id} : {table_name}")
            tables_to_update.append(table)

    if not tables_to_update:
        print("\nNo tables found with available descriptions in Google Sheet, exiting.")
        exit(0)

    # Ask user confirmation
    proceed = (
        input(f"\nDo you want to proceed with updating above tables? (y/n): ")
        .lower()
        .strip()
    )

    if proceed in ["y", "yes"]:
        print("\nUpdating tables with descriptions...")
        for table in tables_without_desc:
            table_id = table.get("id")
            if table_id in description_map:
                description = description_map[table_id]
                update_table_description(table_id, description)
    else:
        print("Update cancelled by user.")
