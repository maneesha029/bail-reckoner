"""
Downloads and cleans NCRB Prison Statistics data from data.gov.in.
Search "Prison Statistics India" on data.gov.in for the dataset catalog.
This is a stub - fill in the actual dataset ID/API endpoint once located.
"""
import json


def fetch_and_clean():
    # TODO: replace with real data.gov.in API call using the dataset's
    # resource ID (search the portal for "Prison Statistics India")
    placeholder = {"source": "NCRB Prison Statistics India", "note": "populate real data here"}
    with open("ncrb_cleaned.json", "w") as f:
        json.dump(placeholder, f, indent=2)
    print("Wrote ncrb_cleaned.json (placeholder - replace with real data)")


if __name__ == "__main__":
    fetch_and_clean()
