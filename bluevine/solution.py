import re
import ast
import pandas as pd
import os

def normalise(df):
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
    return t.strip().lower() if t else None


def parse_year(date_str):
    if not date_str:
        return None
    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", str(date_str))
    return int(m.group(1)) if m else None


def parse_month(date_str):
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
    # drop nulls
    found_df = df.dropna(subset=["title"]).copy()
    found_df["title_norm"] = found_df["title"].apply(normalise_title)
    book_df = found_df.groupby("title_norm", as_index=False).first()

    #q1
    num_books = found_df["title_norm"].nunique()
    print(f"Q1: {num_books} unique books")

    #q2
    isbn_counts = (found_df.groupby("title_norm")["isbn"]
                   .count().sort_values(ascending=False))
    top_norm  = isbn_counts.idxmax()
    top_title = found_df.loc[found_df["title_norm"] == top_norm, "title"].iloc[0]
    top_count = isbn_counts.max()
    print(f"Q2: {top_title} -- {top_count} ISBNs")

    #q3
    def has_goodreads(series):
        return series.dropna().any()
    goodreads_per_book = (found_df.groupby("title_norm")["identifiers_goodreads"]
                          .apply(has_goodreads))
    no_goodreads = (~goodreads_per_book).sum()
    print(f"Q3: {no_goodreads} books")

    #q4
    auth_exp = (found_df[["title_norm", "authors"]]
                .dropna(subset=["authors"])
                .explode("authors"))
    auth_exp["authors"]    = auth_exp["authors"].str.strip()
    authors_per_book       = auth_exp.groupby("title_norm")["authors"].nunique()
    multi_author_books     = (authors_per_book > 1).sum()
    print(f"Q4: {multi_author_books} books")

    #q5
    pub_exp = (found_df[["title_norm", "publishers"]]
               .dropna(subset=["publishers"])
               .explode("publishers"))
    pub_exp["publishers"]  = pub_exp["publishers"].str.strip()
    books_per_publisher    = (pub_exp.groupby("publishers")["title_norm"]
                              .nunique().sort_values(ascending=False))
    print(f"Q5: {books_per_publisher.head(20).to_string()}")

    #q6
    pages_per_book = (found_df.dropna(subset=["number_of_pages"])
                      .groupby("title_norm")["number_of_pages"].first())
    median_pages   = pages_per_book.median()
    print(f"Q6: {median_pages}")

    #q7
    book_df["pub_month"] = book_df["publish_date"].apply(parse_month)
    month_counts         = book_df["pub_month"].dropna().value_counts()
    busiest_month        = month_counts.idxmax()
    busiest_count        = month_counts.max()
    print(f"Q7: {busiest_month} ({busiest_count})")

    #q8
    print("Question 8 was pretty hard :(")

    #q9
    book_df["pub_year"] = book_df["publish_date"].apply(parse_year)
    valid_years         = book_df.dropna(subset=["pub_year"])
    if not valid_years.empty:
        latest_idx  = valid_years["pub_year"].idxmax()
        latest_book = valid_years.loc[latest_idx, "title"]
        latest_year = int(valid_years.loc[latest_idx, "pub_year"])
        print(f"Q9: '{latest_book}' ({latest_year})")
    else:
        print("Q9 No valid publication ")

    #q10
    if found_df["last_modified"].notna().any():
        found_df["last_modified_dt"] = pd.to_datetime(
            found_df["last_modified"], errors="coerce", utc=True
        )
        latest_mod_idx  = found_df["last_modified_dt"].idxmax()
        latest_mod_row  = found_df.loc[latest_mod_idx]
        latest_mod_year = latest_mod_row["last_modified_dt"].year
        print(f"Q10: {latest_mod_year}")
    else:
        print("Q10 No last_modified data available in the dataset.")

    #q11
    auth_exp2 = (found_df[["title_norm", "authors"]]
                 .dropna(subset=["authors"])
                 .explode("authors"))
    auth_exp2["authors"] = auth_exp2["authors"].str.strip()
    titles_per_author    = (auth_exp2.groupby("authors")["title_norm"]
                            .nunique().sort_values(ascending=False))
    prolific_author      = titles_per_author.idxmax()
    prolific_count       = titles_per_author.max()
    print(f"Q11: {prolific_author} - {prolific_count} titles")

    #q12
    print("Q12 was pretty hard :(")

CSV_FILE = "books_preprocessed.csv"

dir_path = os.path.dirname(os.path.abspath(__file__))
fp = os.path.join(dir_path, CSV_FILE)
df = pd.read_csv(fp)
df = normalise(df)
answer_questions(df)


