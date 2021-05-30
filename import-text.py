#! /usr/bin/env python3
#
#    PBS Text to SQLite importer
#    Copyright 2021 David Adam <david.adam.au@gmail.com>
#
#    Licensed under the MIT license - see LICENSE.txt for more

import argparse
import io
import re
import sqlite3
from zipfile import ZipFile


def stripfields(fields):
    return tuple(map(str.strip, fields))


def generic_import(table, delimiter="\t", header_delimiter=None, num_fields=None):
    # Returns an import function which splits on the given delimiter

    # Some tables have different delimiters in the header and the body
    if not header_delimiter:
        header_delimiter = delimiter

    def import_function(conn, inputlines):
        # Pop the header row from the generator, and use this to count the number of fields
        header = inputlines.__next__()
        # Some files have different delimiters in the header and the body 🤯
        header = header.split(header_delimiter)
        # Some files have the wrong number of fields in the header 🤯
        if not num_fields:
            fieldcount = len(header)
        else:
            fieldcount = num_fields

        # Do not strip lines before splitting; there may be empty fields
        lines = (line.split(delimiter) for line in inputlines)
        # Do strip each field once it's broken up - some are padded with spaces
        fields = (stripfields(line) for line in lines)

        valuestring = ", ".join(("?",) * fieldcount)
        conn.executemany(f"INSERT INTO {table} VALUES ({valuestring});", fields)
        conn.commit()

    return import_function


def import_authorities_items(table_base):
    delimiter = "\t"
    # Table for core information
    authorities_items_table = f"{table_base}_items"
    # Table for many-to-many relationship for notes
    authorities_notes_table = f"{table_base}_notes"
    # Table for many-to-many relationship for cautions
    authorities_cautions_table = f"{table_base}_cautions"

    def import_function(conn, inputlines):
        header = inputlines.__next__()
        lines = (line.split(delimiter) for line in inputlines)
        records = (stripfields(line) for line in lines)
        cursor = conn.cursor()
        for record in records:
            # There are a bunch of blank fields in each record which are not in the header
            # but were in old versions of this table. Strip the fields we are interested in out:
            assert len(record) == 28, "Authorities record length incorrect"
            item_columns = record[0:2] + record[6:8]
            cursor.execute(
                f"INSERT INTO {authorities_items_table} VALUES (?, ?, ?, ?)",
                item_columns,
            )
            rowid = cursor.lastrowid
            notes_columns = record[8:23]
            cautions_columns = record[23:29]
            cursor.executemany(
                f"INSERT INTO {authorities_notes_table} VALUES (:rowid, :note_code);",
                ({"rowid": rowid, "note_code": x} for x in notes_columns if x != "0"),
            )
            cursor.executemany(
                f"INSERT INTO {authorities_cautions_table} VALUES (:rowid, :caution_code);",
                (
                    {"rowid": rowid, "caution_code": x}
                    for x in cautions_columns
                    if x != "0"
                ),
            )
        conn.commit()

    return import_function


def import_racf_charts(table, type):
    delimiter = "\t"
    column_name = f"med_chart_{type}"

    def import_function(conn, inputlines):
        header = inputlines.__next__()
        lines = (line.split(delimiter) for line in inputlines)
        fields = (stripfields(line) for line in lines)
        # To support the UPSERT statement that allows for inserting the two different values,
        # use the dictionary argument to executemany instead of the sequence used for other tables
        # (this allows repeating the same value multiple times)
        fieldsdict = (
            dict(
                (
                    ("pbs_code", x),
                    ("column_value", y),
                )
            )
            for x, y in fields
        )
        conn.executemany(
            f"INSERT INTO {table} (pbs_code, {column_name}) VALUES (:pbs_code, :column_value) \
                           ON CONFLICT DO UPDATE SET {column_name} = :column_value;",
            fieldsdict,
        )

    return import_function


# Tuple of (nametemplate, table, parser_function)
INTERESTING_FILES = (
    ("amt_{}.txt", generic_import("amt", "!")),
    ("atc_{}.txt", generic_import("atc", "!")),
    ("CautionExtract_{}.txt", generic_import("cautions")),
    ("cd_{}.txt", generic_import("continued_dispensing")),
    ("DI_{}.txt", generic_import("dispensing_incentive")),
    ("drug_{}.txt", generic_import("drugs", "!")),
    ("LinkExtract_{}.txt", generic_import("links")),
    (
        "med-chart-electronic.txt",
        import_racf_charts(table="racf_med_chart", type="electronic"),
    ),
    ("med-chart-paper.txt", import_racf_charts(table="racf_med_chart", type="paper")),
    ("mnfr_{}.txt", generic_import("manufacturers", "!")),
    ("NoteExtract_{}.txt", generic_import("notes")),
    ("Pharmacy_PBS_Item_Table_{}.txt", import_authorities_items("authorities")),
    (
        "Prescriber_type_{}.txt",
        generic_import("prescriber_types", delimiter="\t", header_delimiter=","),
    ),
    ("RestrictionExtractDelimited_{}.txt", generic_import("restrictions")),
    ("sn20dr_{}.txt", generic_import("safety_net_20_day_rule", num_fields=3)),
    ("streamlined_{}.txt", generic_import("streamlined_authorities")),
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PBS Text to SQLite importer")
    parser.add_argument("input_file", type=argparse.FileType("rb"))
    args = parser.parse_args()

    date_suffix_pattern = re.compile("^[A-Za-z_]+_([0-9]{8})\.txt$")

    with ZipFile(args.input_file) as z:
        testresult = z.testzip()
        if testresult:
            print(
                f"Error: zip file {args.input_file.name} corrupt - bad entry for {testresult}"
            )
            exit(1)

        names = z.namelist()

        # Work out date suffix
        suffixes = {
            date_suffix_pattern.match(name).group(1)
            for name in names
            if date_suffix_pattern.match(name)
        }

        if len(suffixes) != 1:
            print(f"Error: date suffix not detected in zipfile {args.input_file.name}")
            exit(1)
        else:
            date_suffix = suffixes.pop()

        with sqlite3.connect("pbs-{}.sqlite3".format(date_suffix)) as db:

            with open("schema-text.sql") as f:
                db.executescript(f.read())

            for filename, import_function in INTERESTING_FILES:
                with z.open(filename.format(date_suffix)) as f:
                    import_function(db, io.TextIOWrapper(f))
            db.execute("ANALYZE;")

        db.close()
