INSERT INTO cases (case_id, prisoner_id, custody_start_date, is_first_time_offender, state, district, case_stage, has_legal_aid, charges, created_at, updated_at)
VALUES
  ('demo-case-1', 'prisoner-1', '2024-06-01', false, 'Karnataka', 'Bengaluru Urban', 'under_trial', true,
   '[{"act": "IPC", "section": "379", "offense_category": "general", "is_compoundable": true, "max_sentence_months": 36}]',
   NOW(), NOW()),
  ('demo-case-2', 'prisoner-2', '2023-01-01', true, 'Maharashtra', 'Mumbai', 'under_trial', true,
   '[{"act": "PMLA", "section": "4", "offense_category": "economic_offences", "is_compoundable": false, "max_sentence_months": 84}]',
   NOW(), NOW());
