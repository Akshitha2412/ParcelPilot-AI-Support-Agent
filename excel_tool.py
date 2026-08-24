import re
import pandas as pd
from pathlib import Path


EXCEL_FILE = Path("ParcelPilot_Assessment_Data.xlsx")

ALLOWED_READ_ROLES = {"support", "manager"}


def lookup_data(
    query: str,
    user_role: str = "support"
) -> str:

    
    # ACCESS CONTROL - DATA LAYER
   
    if user_role not in ALLOWED_READ_ROLES:
        return (
            "ACCESS_DENIED: You do not have permission "
            "to access ParcelPilot operational data."
        )

    query = str(query).strip()

    excel_file = pd.ExcelFile(EXCEL_FILE)

    results = []

   
    # EXTRACT IDENTIFIERS
   

    order_ids = re.findall(
        r"\bORD-\d+\b",
        query.upper()
    )

    account_ids = re.findall(
        r"\bACCT-\d+\b",
        query.upper()
    )

    ticket_ids = re.findall(
        r"\bTKT-\d+\b",
        query.upper()
    )

    
    # EXACT ID SEARCH
   

    for sheet_name in excel_file.sheet_names:

        df = pd.read_excel(
            EXCEL_FILE,
            sheet_name=sheet_name
        )

        matching_rows = []

        for index, row in df.iterrows():

            # Safely convert every value to string
            row_text = " | ".join(
                str(value)
                for value in row.values
            ).upper()

            matched = False

            for order_id in order_ids:
                if order_id in row_text:
                    matched = True

            for account_id in account_ids:
                if account_id in row_text:
                    matched = True

            for ticket_id in ticket_ids:
                if ticket_id in row_text:
                    matched = True

            if matched:
                matching_rows.append(index)

        if matching_rows:

            matches = df.loc[matching_rows]

            results.append(
                f"SHEET: {sheet_name}\n"
                f"{matches.to_string(index=False)}"
            )


   
    # NORMAL TEXT SEARCH
  

    if not results:

        search_terms = query.lower().split()

        meaningful_terms = [
            term
            for term in search_terms
            if len(term) > 2
        ]

        for sheet_name in excel_file.sheet_names:

            df = pd.read_excel(
                EXCEL_FILE,
                sheet_name=sheet_name
            )

            matching_rows = []

            for index, row in df.iterrows():

                row_text = " ".join(
                    str(value)
                    for value in row.values
                ).lower()

                if any(
                    term in row_text
                    for term in meaningful_terms
                ):
                    matching_rows.append(index)

            if matching_rows:

                matches = df.loc[matching_rows]

                results.append(
                    f"SHEET: {sheet_name}\n"
                    f"{matches.to_string(index=False)}"
                )

  # NO RESULTS
  

    if not results:

        return "No matching records found."

    return "\n\n".join(results)
