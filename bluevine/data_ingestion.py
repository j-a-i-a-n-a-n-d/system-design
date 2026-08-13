import json
import os
import requests
import pandas as pd

#constants
ISBN_FILE = "books-isbns.txt"
OUTPUT_CSV = "books_preprocessed.csv"
API_TIMEOUT = 1
API_BASE = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
LIMIT_COUNT = 1001

#load the txt file
def load_isbns(filepath, limit=None):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(dir_path, filepath)
    with open(fp, "r") as f:
        isbns = [line.strip() for line in f if line.strip()]
    if limit:
        return isbns[:limit]
    return isbns

#api call to endpoint
def fetch_book_data(isbn):
    url = API_BASE.format(isbn=isbn)
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get(f"ISBN:{isbn}")
    except Exception:
        return None


#fetch data
def fetch_data(isbns):
    """Fetch data for each ISBN and preprocess on the fly."""    
    rows = []
    for idx, isbn in enumerate(isbns, 1):
        book = fetch_book_data(isbn)

        if book is None:
            rows.append({
                "isbn": isbn,
                "title": None,
                "authors": None,
                "publishers": None,
                "publish_date": None,
                "number_of_pages": None,
                "identifiers_goodreads": None,
                "description": None,
                "first_sentence": None,
                "last_modified": None
            })
            continue

        title = book.get("title", None)
        
        # Serialize list fields to strings or JSON arrays to make CSV representation clean
        authors = [a["name"] for a in book.get("authors", []) if "name" in a]
        publishers = [p["name"] for p in book.get("publishers", []) if "name" in p]
        goodreads = book.get("identifiers", {}).get("goodreads", [])
        
        pages = book.get("number_of_pages", None)
        if pages is not None:
            try:
                pages = int(pages)
            except (ValueError, TypeError):
                pages = None

        desc = book.get("description", None)
        if isinstance(desc, dict):
            desc = desc.get("value", None)

        first_sent = book.get("first_sentence", None)
        if isinstance(first_sent, dict):
            first_sent = first_sent.get("value", None)

        last_mod = book.get("last_modified", {})
        if isinstance(last_mod, dict):
            last_mod = last_mod.get("value", None)

        rows.append({
            "isbn": isbn,
            "title": title,
            "authors": json.dumps(authors) if authors else None,
            "publishers": json.dumps(publishers) if publishers else None,
            "publish_date": book.get("publish_date", None),
            "number_of_pages": pages,
            "identifiers_goodreads": json.dumps(goodreads) if goodreads else None,
            "description": desc,
            "first_sentence": first_sent,
            "last_modified": last_mod
        })
        
    return pd.DataFrame(rows)

def main():
    isbns = load_isbns(ISBN_FILE, limit=LIMIT_COUNT)
    df = fetch_data(isbns)
    df.to_csv(OUTPUT_CSV, index=False)    
    found = df["title"].notna().sum()
    print(f"valid books found: {found}/{len(df)}")


if __name__ == "__main__":
    main()
