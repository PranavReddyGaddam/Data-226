
  create or replace   view STOCK_DB.analytics.session_timestamp
  
   as (
    WITH session_data AS (
    SELECT sessionId, starttime as ts
    FROM stock_db.raw_data.session_timestamp
    WHERE sessionId IS NOT NULL
)
SELECT * FROM session_data
  );

