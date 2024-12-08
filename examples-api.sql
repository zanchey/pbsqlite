-- Produce the restriction text for each item

WITH restriction_texts AS (SELECT
    restrictions.res_code,
    treatment_of_code,
    string_agg(prescribing_txt, CHAR(10) ORDER BY pt_position) AS restriction_text
FROM restrictions
LEFT JOIN restriction_prescribing_text_relationships USING (res_code)
LEFT JOIN prescribing_texts
    ON
        restriction_prescribing_text_relationships.prescribing_text_id
        = prescribing_texts.prescribing_txt_id
GROUP BY res_code)
SELECT pbs_code, treatment_of_code, restriction_text
FROM item_restriction_relationships
LEFT JOIN restriction_texts USING (res_code);

-- Show manufacturer contact details for all the brands of amoxicillin

SELECT
    brand_name,
    name,
    street_address,
    city,
    state,
    postcode,
    telephone_number
FROM items
INNER JOIN
    organisations
    USING (organisation_id)
WHERE drug_name = 'amoxicillin';