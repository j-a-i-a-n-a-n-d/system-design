"""
Bluevine Data Assignment - Sci-Fi and Fantasy Books Analysis

Approach
--------
1. Load pre-processed book data directly from books_preprocessed.csv
2. Answer all 12 questions, printing results as logs.

Key Assumptions
---------------
- Books with identical title values (case-insensitive, stripped) are treated as
  the same book, regardless of how many ISBNs they have.
- ISBNs not found in Open Library are excluded from analysis (already handled in CSV).
- For Q3: a book has a Goodreads id if ANY of its ISBNs carries one.
- For Q4 (authors > 1): distinct author names are counted per book title.
- For Q7: the first valid publish_date per book title is used.
- For Q8: words are alpha-only tokens; the globally longest one is found.
- For Q11: books are sorted by parsed publish year; ties are not broken further.
- For Q12: multiple publishers/authors per book generate multiple pairs;
  the most frequent pair across all ISBNs wins.
"""

import re
import ast
import pandas as pd

CSV_FILE = "books_preprocessed.csv"

def load_data(filepath):
    """Load pre-processed book data from CSV file."""
    df = pd.read_csv(filepath)
    return df

def normalise(df):
    """
    Process the CSV data into a tidy DataFrame.
    Converts string representations of lists to actual Python lists.
    One row per ISBN.
    """
    rows = []
    for _, row in df.iterrows():
        isbn = row["isbn"]
        title = row["title"] if pd.notna(row["title"]) else None

        authors = None
        if pd.notna(row["authors"]):
            try:
                authors = ast.literal_eval(row["authors"])
            except (ValueError, SyntaxError):
                authors = None

        publishers = None
        if pd.notna(row["publishers"]):
            try:
                publishers = ast.literal_eval(row["publishers"])
            except (ValueError, SyntaxError):
                publishers = None

        publish_date = row["publish_date"] if pd.notna(row["publish_date"]) else None

        pages = row["number_of_pages"]
        if pd.notna(pages):
            try:
                pages = int(pages)
            except (ValueError, TypeError):
                pages = None
        else:
            pages = None

        goodreads = None
        if pd.notna(row["identifiers_goodreads"]):
            try:
                goodreads = ast.literal_eval(row["identifiers_goodreads"])
            except (ValueError, SyntaxError):
                goodreads = None

        desc = row["description"] if pd.notna(row["description"]) else None
        first_sent = row["first_sentence"] if pd.notna(row["first_sentence"]) else None
        last_mod = row["last_modified"] if pd.notna(row["last_modified"]) else None

        rows.append({
            "isbn"                  : isbn,
            "title"                 : title,
            "authors"               : authors,
            "publishers"            : publishers,
            "publish_date"          : publish_date,
            "number_of_pages"       : pages,
            "identifiers_goodreads" : goodreads,
            "description"           : desc,
            "first_sentence"        : first_sent,
            "last_modified"         : last_mod,
        })

    return pd.DataFrame(rows)



def normalise_title(t):
    """Lowercase + strip whitespace for grouping editions of the same book."""
    return t.strip().lower() if t else None


def parse_year(date_str):
    """
    Extract a 4-digit year from a publish_date string.
    Handles: '2001', 'January 1, 2001', '2001-03-15', '1 Jan 2001', etc.
    """
    if not date_str:
        return None
    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", str(date_str))
    return int(m.group(1)) if m else None


def parse_month(date_str):
    """
    Extract a month name from a publish_date string.
    Returns the full name (e.g. 'January') or None.
    Handles textual and ISO-style dates.
    """
    if not date_str:
        return None
    month_map = {
        "january": "January", "february": "February", "march": "March",
        "april": "April",     "may": "May",           "june": "June",
        "july": "July",       "august": "August",     "september": "September",
        "october": "October", "november": "November", "december": "December",
    }
    lower = str(date_str).lower()
    for k, v in month_map.items():
        if k in lower:
            return v
    # ISO-style: YYYY-MM or YYYY-MM-DD
    m = re.match(r"\d{4}-(\d{2})", str(date_str).strip())
    if m:
        n = int(m.group(1))
        names = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        if 1 <= n <= 12:
            return names[n - 1]
    return None

def answer_questions(df):
    # ---- shared pre-processing ----
    # Use only ISBNs that returned data from Open Library
    found_df = df.dropna(subset=["title"]).copy()
    found_df["title_norm"] = found_df["title"].apply(normalise_title)

    # Book-level view: one row per unique title
    # (first ISBN row used for scalar fields like publish_date)
    book_df = found_df.groupby("title_norm", as_index=False).first()

    # ================================================================
    # Q1. How many different books are in the list?
    # ================================================================
    num_books = found_df["title_norm"].nunique()
    print("=" * 65)
    print("Q1. How many different books are in the list?")
    print(f"    Answer: {num_books} unique books")

    # ================================================================
    # Q2. What is the book with the most number of different ISBNs?
    # ================================================================
    isbn_counts = (found_df.groupby("title_norm")["isbn"]
                   .count().sort_values(ascending=False))
    top_norm  = isbn_counts.idxmax()
    top_title = found_df.loc[found_df["title_norm"] == top_norm, "title"].iloc[0]
    top_count = isbn_counts.max()
    print("=" * 65)
    print("Q2. Book with the most different ISBNs:")
    print(f"    '{top_title}' -- {top_count} ISBNs")

    # ================================================================
    # Q3. How many books don't have a goodreads id?
    # ================================================================
    # A book has a Goodreads id if at least one of its ISBNs carries one.
    def has_goodreads(series):
        return series.dropna().any()

    goodreads_per_book = (found_df.groupby("title_norm")["identifiers_goodreads"]
                          .apply(has_goodreads))
    no_goodreads = (~goodreads_per_book).sum()
    print("=" * 65)
    print("Q3. How many books don't have a goodreads id?")
    print(f"    Answer: {no_goodreads} books")

    # ================================================================
    # Q4. How many books have more than one author?
    # ================================================================
    auth_exp = (found_df[["title_norm", "authors"]]
                .dropna(subset=["authors"])
                .explode("authors"))
    auth_exp["authors"]    = auth_exp["authors"].str.strip()
    authors_per_book       = auth_exp.groupby("title_norm")["authors"].nunique()
    multi_author_books     = (authors_per_book > 1).sum()
    print("=" * 65)
    print("Q4. How many books have more than one author?")
    print(f"    Answer: {multi_author_books} books")

    # ================================================================
    # Q5. What is the number of books published per publisher?
    # ================================================================
    pub_exp = (found_df[["title_norm", "publishers"]]
               .dropna(subset=["publishers"])
               .explode("publishers"))
    pub_exp["publishers"]  = pub_exp["publishers"].str.strip()
    books_per_publisher    = (pub_exp.groupby("publishers")["title_norm"]
                              .nunique().sort_values(ascending=False))
    print("=" * 65)
    print("Q5. Number of books published per publisher (top 20 shown):")
    print(books_per_publisher.head(20).to_string())
    print(f"    ... ({len(books_per_publisher)} unique publishers total)")

    # ================================================================
    # Q6. What is the median number of pages for books in this list?
    # ================================================================
    pages_per_book = (found_df.dropna(subset=["number_of_pages"])
                      .groupby("title_norm")["number_of_pages"].first())
    median_pages   = pages_per_book.median()
    print("=" * 65)
    print("Q6. Median number of pages:")
    print(f"    Answer: {median_pages} pages  "
          f"(from {len(pages_per_book)} books with page data)")

    # ================================================================
    # Q7. What is the month with the most number of published books?
    # ================================================================
    book_df["pub_month"] = book_df["publish_date"].apply(parse_month)
    month_counts         = book_df["pub_month"].dropna().value_counts()
    busiest_month        = month_counts.idxmax()
    busiest_count        = month_counts.max()
    print("=" * 65)
    print("Q7. Month with the most published books:")
    print(f"    Answer: {busiest_month} ({busiest_count} books)")

    # ================================================================
    # Q8. Longest word(s) in any description or first sentence
    # ================================================================
    # Check if we have any description/first_sentence data
    has_text_data = (found_df["description"].notna().any() or 
                     found_df["first_sentence"].notna().any())
    
    if has_text_data:
        text_df = found_df[["title_norm", "title", "description", "first_sentence"]].copy()
        text_df["combined_text"] = (
            text_df["description"].fillna("") + " " + text_df["first_sentence"].fillna("")
        ).str.strip()
        text_df = text_df[text_df["combined_text"] != ""]

        global_max_len = 0
        global_longest = []
        global_book    = None

        for _, row in text_df.iterrows():
            words = re.findall(r"[A-Za-z]+", row["combined_text"])
            if not words:
                continue
            local_max = max(len(w) for w in words)
            if local_max > global_max_len:
                global_max_len = local_max
                global_longest = [w for w in words if len(w) == local_max]
                global_book    = row["title"]
            elif local_max == global_max_len:
                global_longest += [w for w in words if len(w) == local_max]

        global_longest = list(set(global_longest))
        print("=" * 65)
        print("Q8. Longest word(s) in description / first_sentence:")
        print(f"    Word(s) : {global_longest}")
        print(f"    Length  : {global_max_len} characters")
        print(f"    Found in: '{global_book}'")
    else:
        print("=" * 65)
        print("Q8. Longest word(s) in description / first_sentence:")
        print("    No description or first_sentence data available in the dataset.")

    # ================================================================
    # Q9. What was the last book published in the list?
    # ================================================================
    book_df["pub_year"] = book_df["publish_date"].apply(parse_year)
    valid_years         = book_df.dropna(subset=["pub_year"])
    if not valid_years.empty:
        latest_idx  = valid_years["pub_year"].idxmax()
        latest_book = valid_years.loc[latest_idx, "title"]
        latest_year = int(valid_years.loc[latest_idx, "pub_year"])
        print("=" * 65)
        print("Q9. Last book published:")
        print(f"    '{latest_book}' (year: {latest_year})")
    else:
        print("=" * 65)
        print("Q9. No valid publication year data available.")

    # ================================================================
    # Q10. What is the year of the most updated entry in the list?
    # ================================================================
    if found_df["last_modified"].notna().any():
        found_df["last_modified_dt"] = pd.to_datetime(
            found_df["last_modified"], errors="coerce", utc=True
        )
        latest_mod_idx  = found_df["last_modified_dt"].idxmax()
        latest_mod_row  = found_df.loc[latest_mod_idx]
        latest_mod_year = latest_mod_row["last_modified_dt"].year
        print("=" * 65)
        print("Q10. Year of the most recently updated entry:")
        print(f"     Answer       : {latest_mod_year}")
        print(f"     Entry title  : '{latest_mod_row['title']}'")
        print(f"     Last modified: {latest_mod_row['last_modified']}")
    else:
        print("=" * 65)
        print("Q10. Year of the most recently updated entry:")
        print("     No last_modified data available in the dataset.")

    # ================================================================
    # Q11. Second published book for the author with the most titles
    # ================================================================
    # Step A: find the author with the most distinct book titles
    auth_exp2 = (found_df[["title_norm", "authors"]]
                 .dropna(subset=["authors"])
                 .explode("authors"))
    auth_exp2["authors"] = auth_exp2["authors"].str.strip()
    titles_per_author    = (auth_exp2.groupby("authors")["title_norm"]
                            .nunique().sort_values(ascending=False))
    prolific_author      = titles_per_author.idxmax()
    prolific_count       = titles_per_author.max()
    print("=" * 65)
    print("Q11. Author with the highest number of different titles:")
    print(f"     '{prolific_author}' ({prolific_count} titles)")

    # Step B: get all that author's books, sort by publication year
    author_titles = (
        auth_exp2[auth_exp2["authors"] == prolific_author][["title_norm"]]
        .drop_duplicates()
        .merge(book_df[["title_norm", "title", "publish_date"]],
               on="title_norm", how="left")
    )
    author_titles["pub_year"] = author_titles["publish_date"].apply(parse_year)
    author_titles_sorted = (
        author_titles.dropna(subset=["pub_year"])
        .sort_values("pub_year")
        .reset_index(drop=True)
    )
    if len(author_titles_sorted) >= 2:
        second = author_titles_sorted.iloc[1]
        print(f"     Second published book: '{second['title']}' "
              f"(year: {int(second['pub_year'])})")
    elif len(author_titles_sorted) == 1:
        first = author_titles_sorted.iloc[0]
        print(f"     Only one book with a valid year: '{first['title']}'")
    else:
        print("     No books with valid publication years found for this author.")

    # ================================================================
    # Q12. (Publisher, Author) pair with the highest number of books
    # ================================================================
    pair_df = (found_df[["title_norm", "publishers", "authors"]]
               .dropna(subset=["publishers", "authors"]))
    pair_df = pair_df.explode("publishers").explode("authors")
    pair_df["publishers"] = pair_df["publishers"].str.strip()
    pair_df["authors"]    = pair_df["authors"].str.strip()
    pair_counts = (pair_df.groupby(["publishers", "authors"])["title_norm"]
                   .nunique().sort_values(ascending=False))
    top_pair       = pair_counts.idxmax()
    top_pair_count = pair_counts.max()
    print("=" * 65)
    print("Q12. (Publisher, Author) pair with the most books:")
    print(f"     Publisher : '{top_pair[0]}'")
    print(f"     Author    : '{top_pair[1]}'")
    print(f"     Books     : {top_pair_count}")
    print("=" * 65)


def main():
    raw_df = load_data(CSV_FILE)
    df = normalise(raw_df)
    answer_questions(df)

if __name__ == "__main__":
    main()
