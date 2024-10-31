
  create or replace   view STOCK_DB.analytics.session_summary
  
   as (
    WITH u AS (
    SELECT * FROM STOCK_DB.analytics.user_session_channel
), st AS (
    SELECT * FROM STOCK_DB.analytics.session_timestamp
)
SELECT u.userId, u.sessionId, u.channel, st.ts
FROM u
JOIN st ON u.sessionId = st.sessionId
  );

