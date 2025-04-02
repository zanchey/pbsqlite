#! /usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "sqlite-utils",
# ]
# ///
#
#    PBS API to SQLite importer
#    Copyright 2024 David Adam <david.adam.au@gmail.com>
#
#    Licensed under the MIT license - see LICENSE.txt for more

import argparse
import urllib.request
import gzip
import json
from time import sleep
from sqlite_utils import Database

# The PBS API will spit out both CSV and JSON. The JSON is much bigger, but when compressed
# transfers faster (thanks to Azure API gateway funkiness, presumably)


def progress(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def make_request(table, schedule_code=None):
    # The API returns 10 records by default. An empty limit parameter appears to return everything.
    request = urllib.request.Request(
        f"https://data-api.health.gov.au/pbs/api/v3/{table}?limit={f'&schedule_code={schedule_code}' if schedule_code else ''}",
        headers={
            # Public subscription key, subject to significant rate-limiting
            "Subscription-Key": "2384af7c667342ceb5a736fe29f1dc6b",
            "Accept-Encoding": "gzip",
        },
    )
    progress(f"Retrieving {request.full_url}...", end=" ")
    response = urllib.request.urlopen(request)
    progress(response.status, response.reason, end=", ")
    # Empty queries return 204 No Content, which is not a valid response for a GET request per MDN
    if response.status == 200:
        data = gzip.decompress(response.read()).decode(
            response.headers.get_content_charset()
        )
        j = json.loads(data)
        progress(f"{j['_meta']['total_records']} records returned")
        return j["data"]
    else:
        progress("no records returned")
        return {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PBS API to SQLite importer")

    progress("Getting list of active schedules...")
    schedules = make_request("schedules")
    schedules.sort(key=lambda d: d["effective_date"])
    latest_schedule = schedules[-1]
    latest_schedule_code = latest_schedule["schedule_code"]
    progress(
        f"Latest schedule is {latest_schedule_code}, effective {latest_schedule['effective_date']}"
    )

    progress("Downloading tables:")
    tables = (
        # (endpoint, (tuple of compound primary keys), (tuple of foreign key tuples))
        (
            "programs",
            ("program_code", "schedule_code"),
            (("schedule_code", "schedules"),),
        ),
        (
            "organisations",
            ("organisation_id", "schedule_code"),
            (("schedule_code", "schedules"),),
        ),
        (
            "items",
            ("li_item_id", "schedule_code"),
            (
                ("schedule_code", "schedules"),
                (("program_code", "schedule_code"), "programs"),
                (("organisation_id", "schedule_code"), "organisations"),
            ),
        ),
        (
            "amt-items",
            ("pbs_concept_id", "li_item_id", "schedule_code"),
            ((("li_item_id", "schedule_code"), "items")),
        ),
        (
            "atc-codes",
            ("atc_code", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "containers",
            ("container_code", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "container-organisation-relationships",
            None,
            (
                (("container_code", "schedule_code"), "containers"),
                (("organisation_id", "schedule_code"), "organisations"),
            ),
        ),
        (
            "copayments",
            None,
            (("schedule_code", "schedules")),
        ),
        (
            "criteria",
            ("criteria_prescribing_txt_id", "schedule_code"),
            (
                ("schedule_code", "schedules"),
                (
                    ("criteria_prescribing_txt_id", "schedule_code"),
                    "criteria-parameter-relationships",
                ),
            ),
        ),
        (
            "criteria-parameter-relationships",
            (
                "criteria_prescribing_txt_id",
                "parameter_prescribing_txt_id",
                "schedule_code",
            ),
            (
                ("schedule_code", "schedules"),
                (("parameter_prescribing_txt_id", "schedule_code"), "parameters"),
            ),
        ),
        (
            "dispensing-rules",
            ("dispensing_rule_reference", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "extemporaneous-ingredients",
            ("pbs_code", "schedule_code"),
            (
                ("schedule_code", "schedules"),
                (("pbs_code", "schedule_code"), "items"),
            ),
        ),
        (
            "extemporaneous-preparations",
            ("pbs_code", "schedule_code"),
            (
                ("schedule_code", "schedules"),
                (("pbs_code", "schedule_code"), "items"),
            ),
        ),
        (
            "extemporaneous-prep-sfp-relationships",
            ("ex_prep_pbs_code", "sfp_pbs_code", "schedule_code"),
            (
                ("schedule_code", "schedules"),
                (("sfp_pbs_code", "schedule_code"), "standard-formula-preparations"),
            ),
        ),
        (
            "extemporaneous-tariffs",
            ("pbs_code", "schedule_code"),
            (
                ("schedule_code", "schedules"),
                (("pbs_code", "schedule_code"), "items"),
            ),
        ),
        (
            "fees",
            ("program_code", "schedule_code"),
            (("schedule_code", "schedules"), ("programs", "program_code")),
        ),
        (
            "indications",
            ("indication_prescribing_txt_id", "schedule_code"),
            (
                (
                    ("indication_prescribing_txt_id", "schedule_code"),
                    "prescribing-texts",
                    ("prescribing_txt_id", "schedule_code"),
                )
            ),
        ),
        (
            "item-atc-relationships",
            ("atc_code", "pbs_code", "schedule_code"),
            (
                (("atc_code", "schedule_code"), "atc_codes"),
                (("pbs_code", "schedule_code"), "items"),
            ),
        ),
        (
            "item-dispensing-rule-relationships",
            ("li_item_id", "dispensing_rule_reference", "schedule_code"),
            (
                (("li_item_id", "schedule_code"), "items"),
                (("dispensing_rule_reference", "schedule_code"), "dispensing_rules"),
            ),
        ),
        (
            # It's not clear to me why this table exists, if there's an organisation_id in the items table
            "item-organisation-relationships",
            ("pbs_code", "schedule_code", "organisation_id"),
            (
                (("organisation_id", "schedule_code"), "organisations"),
                (("pbs_code", "schedule_code", "organisation_id"), "items"),
            ),
        ),
        (
            "item-prescribing-text-relationships",
            ("pbs_code", "schedule_code", "prescribing_txt_id"),
            (
                (("pbs_code", "schedule_code"), "items"),
                (
                    ("pbs_code", "prescribing_txt_id", "schedule_code"),
                    "prescribing_texts",
                ),
            ),
        ),
        (
            "item-pricing-events",
            # The schema (see v3.2 data dictionary) says that the primary key for this table is a compound key of
            # ("li_item_id", "schedule_code"), but this is not a unique combination as of schedule 4429
            None,
            ((("li_item_id", "schedule_code"), "items"),),
        ),
        (
            "item-restriction-relationships",
            ("res_code", "pbs_code", "schedule_code"),
            (
                (("pbs_code", "schedule_code"), "items"),
                (
                    ("pbs_code", "prescribing_txt_id", "schedule_code"),
                    "prescribing_texts",
                ),
            ),
        ),
        (
            "markup-bands",
            # The schema says that the primary key is
            # ("program_code", "dispensing_rule_mnem", "schedule_code")
            # but this violates the UNIQUE constraint as there are multiple
            # rows with the same combination
            (None),
            (
                (("program_code", "schedule_code"), "programs"),
                (("dispensing_rule_mnem", "schedule_code"), "dispensing_rules"),
            ),
        ),
        (
            "parameters",
            ("parameter_prescribing_txt_id", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "prescribers",
            ("pbs_code", "prescriber_code", "schedule_code"),
            (("pbs_code", "schedule_code"), "items"),
        ),
        (
            "prescribing-texts",
            ("prescribing_txt_id", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "program-dispensing-rules",
            ("program_code", "dispensing_rule_mnem", "schedule_code"),
            (
                (("program_code", "schedule_code"), "programs"),
                (("dispensing_rule_mnem", "schedule_code"), "dispensing_rules"),
            ),
        ),
        (
            "programs",
            ("program_code", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "restriction-prescribing-text-relationships",
            ("res_code", "prescribing_text_id", "schedule_code"),
            (
                (("res_code", "schedule_code"), "restrictions"),
                (
                    ("prescribing_text_id", "schedule_code"),
                    "prescribing_texts",
                    ("prescribing_txt_id", "schedule_code"),
                ),
            ),
        ),
        (
            "restrictions",
            ("res_code", "schedule_code"),
            (("schedule_code", "schedules")),
        ),
        (
            "standard-formula-preparations",
            ("pbs_code", "schedule_code"),
            (("pbs_code", "schedule_code"), "items"),
        ),
    )

    db_filename = f"pbs-{latest_schedule['effective_date']}.sqlite3"

    db = Database(db_filename)

    db["schedules"].drop(ignore=True)
    db["schedules"].insert_all(schedules, pk="schedule_code")

    for table, pks, fks in tables:
        # Table names with hyphens in them require escaping in SQL, use underscores instead
        table_name = table.replace("-", "_")
        db[table_name].drop(ignore=True)
        db[table_name].insert_all(
            make_request(table, schedule_code=latest_schedule_code),
            pk=pks,
            # sqlite-utils doesn't yet support compound foreign keys
            # see https://github.com/simonw/sqlite-utils/issues/117
            # drop them for now
            foreign_keys=(fk for fk in fks if isinstance(fk[0], str)),
        )

        # Sleep for 20 seconds between requests to avoid hitting the rate limits, which are documented as
        # one request every 20 seconds although in practice seem to be configured at one every ten seconds
        sleep(20)

    db.analyze()

    progress(f"Successfully generated database: {db_filename}")
