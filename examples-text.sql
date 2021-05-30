-- Produce the notes text for each item

SELECT DISTINCT n.note_text,
                an.note_code,
                ai.pbs_code,
                d.drug
FROM notes AS n
JOIN authorities_notes an ON an.note_code = n.code
JOIN authorities_items ai ON ai.ROWID = an.authorities_rowid
JOIN drugs d ON ai.pbs_code = d.pbs_code;

-- Show manufacturer contact details for all the brands of amoxicillin

SELECT drugs.drug,
       name,
       address,
       telephone
FROM manufacturers
JOIN drugs ON drugs.manufacturer = manufacturers.code
WHERE drugs.drug = "amoxicillin";