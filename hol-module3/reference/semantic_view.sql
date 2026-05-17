CREATE OR REPLACE SEMANTIC VIEW EPOWER_DEMO.EPOWER_GOLD.CUSTOMER_HEALTH_SEMANTIC_VIEW
  TABLES (
    CHURN AS EPOWER_DEMO.EPOWER_GOLD.MART_CUSTOMER_CHURN
      PRIMARY KEY (CATEGORY_NAME, REGION_NAME, CANCELLATION_MONTH, REASON)
      WITH SYNONYMS = ('Kuendigung', 'cancellation', 'churn', 'Abwanderung'),
    NPS AS EPOWER_DEMO.EPOWER_GOLD.MART_NPS_ANALYSIS
      PRIMARY KEY (REGION_NAME, CUSTOMER_TYPE, CATEGORY, SURVEY_MONTH)
      WITH SYNONYMS = ('Zufriedenheit', 'satisfaction', 'NPS', 'survey')
  )
  FACTS (
    CHURN.CANCELLATIONS AS CANCELLATIONS
      WITH SYNONYMS = ('Kuendigungen', 'churn count')
      COMMENT = 'Number of contract cancellations',
    CHURN.RETENTION_OFFERED_COUNT AS RETENTION_OFFERED_COUNT
      COMMENT = 'Number of retention offers made',
    CHURN.RETENTION_ACCEPTED_COUNT AS RETENTION_ACCEPTED_COUNT
      COMMENT = 'Number of retention offers accepted',
    NPS.TOTAL_RESPONSES AS TOTAL_RESPONSES
      COMMENT = 'Total NPS survey responses',
    NPS.AVG_NPS AS AVG_NPS
      WITH SYNONYMS = ('average NPS', 'Durchschnitt NPS')
      COMMENT = 'Average NPS score (0-10)',
    NPS.PROMOTERS AS PROMOTERS
      COMMENT = 'Count of promoters (NPS 9-10)',
    NPS.DETRACTORS AS DETRACTORS
      COMMENT = 'Count of detractors (NPS 0-6)'
  )
  DIMENSIONS (
    CHURN.CATEGORY_NAME AS CHURN_CATEGORY
      WITH SYNONYMS = ('Produktkategorie', 'product category')
      COMMENT = 'Product category of cancelled contract',
    CHURN.REGION_NAME AS CHURN_REGION
      WITH SYNONYMS = ('Region', 'Gebiet')
      COMMENT = 'Region where cancellation occurred',
    CHURN.CANCELLATION_MONTH AS CANCELLATION_MONTH
      WITH SYNONYMS = ('Monat', 'month')
      COMMENT = 'Month of cancellation',
    CHURN.REASON AS CANCELLATION_REASON
      WITH SYNONYMS = ('Kuendigungsgrund', 'reason', 'Grund')
      COMMENT = 'Reason for cancellation (Umzug, Preiserhoehung, Wettbewerber, ...)',
    NPS.REGION_NAME AS NPS_REGION
      COMMENT = 'Region of survey respondent',
    NPS.CUSTOMER_TYPE AS NPS_CUSTOMER_TYPE
      WITH SYNONYMS = ('Kundentyp', 'segment')
      COMMENT = 'Customer type (Privatkunde, Kleingewerbe, Gewerbekunde)',
    NPS.CATEGORY AS NPS_CATEGORY
      WITH SYNONYMS = ('Umfragekategorie', 'survey topic')
      COMMENT = 'Survey category (Gesamtzufriedenheit, Kundenservice, ...)',
    NPS.SURVEY_MONTH AS SURVEY_MONTH
      COMMENT = 'Month of survey response'
  )
  METRICS (
    CHURN.TOTAL_CANCELLATIONS AS SUM(CHURN.CANCELLATIONS)
      WITH SYNONYMS = ('Gesamtkuendigungen', 'total churn')
      COMMENT = 'Total contract cancellations',
    NPS.OVERALL_AVG_NPS AS AVG(NPS.AVG_NPS)
      WITH SYNONYMS = ('Gesamt-NPS', 'overall satisfaction')
      COMMENT = 'Overall average NPS score'
  )
  COMMENT = 'Customer health analytics — churn analysis and NPS satisfaction scores';
