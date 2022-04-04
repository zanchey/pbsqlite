-- PBS schema for text extracts (from 1 December 2020)
-- Copyright 2021 David Adam <david.adam.au@gmail.com>

PRAGMA journal_mode = WAL;

DROP TABLE IF EXISTS amt;
CREATE TABLE amt (
    program_code,
    pbs_code,
    manufacturer_code,
    brand_name,
    unit_of_measure,
    mp_id,
    mp_pt,
    mpuu_id,
    mpuu_pt,
    mpp_id,
    mpp_pt,
    tpuu_id,
    tpuu_pt,
    tpp_id,
    tpp_pt,
    vial_content,
    mq_pack,
    mq_uu,
    cemp_tpp,
    cemp_tpuu,
    memp_tpp,
    memp_tpuu,
    pfdi,
    FOREIGN KEY (manufacturer_code) REFERENCES manufacturers(code)
);

DROP TABLE IF EXISTS atc;
CREATE TABLE atc (
    atc_level,
    atc_description
);

DROP TABLE IF EXISTS cautions;
CREATE TABLE cautions (
    code PRIMARY KEY,
    caution_text
);

DROP TABLE IF EXISTS continued_dispensing;
CREATE TABLE continued_dispensing (
    pbs_code,
    continued_dispensing
);

DROP TABLE IF EXISTS dispensing_incentive;
CREATE TABLE dispensing_incentive (
    mp_pt,
    pbs_code,
    manufacturer_code,
    pfdi
);

DROP TABLE IF EXISTS drugs;
CREATE TABLE drugs (
    program,
    atc_code,
    atc_type,
    atc_print,
    pbs_code,
    restriction,
    caution,
    note,
    max_quantity INTEGER,
    max_repeats INTEGER,
    manufacturer,
    pack_size,
    markup,
    dispense_fee,
    dangerous_drug_fee,
    brand_premium,
    group_premium,
    comm_pharmacist_price,
    comm_dpmq,
    tg_manu_pharmacist price,
    tg_manu_dpmq,
    manu_pharmacist_price,
    manu_dpmq,
    max_safety_net,
    bioequivalence,
    brand,
    drug,
    amt_term,
    FOREIGN KEY (caution) REFERENCES cautions(code),
    FOREIGN KEY (note) REFERENCES notes(code),
    FOREIGN KEY (manufacturer) REFERENCES manufacturers(code)
);

DROP TABLE IF EXISTS links;
CREATE TABLE links (
    pbs_code,
    treatment_code,
    increase_code,
    start_date INTEGER,
    end_date INTEGER
);

DROP TABLE IF EXISTS racf_med_chart;
CREATE TABLE racf_med_chart (
    pbs_code PRIMARY KEY,
    med_chart_electronic,
    med_chart_paper
);

DROP TABLE IF EXISTS manufacturers;
CREATE TABLE manufacturers (
    code PRIMARY KEY,
    name,
    address,
    telephone,
    fax
);

DROP TABLE IF EXISTS notes;
CREATE TABLE notes (
    code PRIMARY KEY,
    note_text
);

-- from the oddly-named Pharmacy_PBS_Item_Table.txt
-- normalise this data in import scripts into a many-to-many relationship
DROP TABLE IF EXISTS authorities_items;
CREATE TABLE authorities_items (
    pbs_code,
    restriction,
    start_date,
    end_date
);

DROP TABLE IF EXISTS authorities_notes;
CREATE TABLE authorities_notes (
    authorities_rowid,
    note_code,
    FOREIGN KEY (authorities_rowid) REFERENCES authorities_items(ROWID) ON DELETE CASCADE,
    FOREIGN KEY (note_code) REFERENCES notes(code)
);

DROP TABLE IF EXISTS authorities_cautions;
CREATE TABLE authorities_cautions (
    authorities_rowid,
    caution_code,
    FOREIGN KEY (authorities_rowid) REFERENCES authorities_items(ROWID) ON DELETE CASCADE,
    FOREIGN KEY (caution_code) REFERENCES cautions(code)
);

DROP TABLE IF EXISTS prescriber_types;
CREATE TABLE prescriber_types (
    drug,
    pbs_code,
    prescriber_type
);

DROP TABLE IF EXISTS restrictions;
CREATE TABLE restrictions (
    treatment_code INTEGER,
    text,
    misc INTEGER,
    date_required,
    text_required
);

DROP TABLE IF EXISTS safety_net_20_day_rule;
CREATE TABLE safety_net_20_day_rule (
    pbs_code,
    days,
    safety_net_counted
);

DROP TABLE IF EXISTS streamlined_authorities;
CREATE TABLE streamlined_authorities (
    drug,
    pbs_code,
    treatment_code INTEGER,
    FOREIGN KEY (treatment_code) REFERENCES restrictions(treatment_code)
);

DROP TABLE IF EXISTS pbsqlite;
CREATE TABLE pbsqlite (
    schedule_date,
    generator
);
