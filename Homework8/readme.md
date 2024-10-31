# dbt Project: Snowflake Analytics

This project is a demonstration of an ELT (Extract, Load, Transform) pipeline using [dbt (Data Build Tool)](https://www.getdbt.com/) with Snowflake as the data warehouse. The project includes setting up input and output models, configuring snapshots for historical data tracking, and adding data quality tests.

## Project Structure

```
build_mau/
├── models/
│   ├── input/
│   │   ├── user_session_channel.sql
│   │   └── session_timestamp.sql
│   ├── output/
│   │   └── session_summary.sql
│   └── schema.yml
├── snapshots/
│   └── snapshot_session_summary.sql
└── dbt_project.yml
```

## Setup Instructions

1. **Install dbt**:
   Make sure you have dbt installed with the Snowflake connector:
   ```bash
   pip install dbt-snowflake
   ```

2. **Initialize dbt Project**:
   Run the following command in your terminal to initialize a new dbt project:
   ```bash
   dbt init build_mau
   ```

3. **Configure Connection to Snowflake**:
   Update `profiles.yml` with your Snowflake account details. The `profiles.yml` file typically goes in the `~/.dbt` directory (for Unix-based systems) or `%USERPROFILE%\.dbt` (for Windows).

   Example configuration:
   ```yaml
   build_mau:
     outputs:
       dev:
         type: snowflake
         account: your_snowflake_account
         user: your_username
         password: your_password
         role: your_role
         database: your_database
         warehouse: your_warehouse
         schema: raw_data
     target: dev
   ```

4. **Run dbt Commands**:
   - **Build Input Models**:
     ```bash
     dbt run
     ```
   - **Run Snapshot**:
     ```bash
     dbt snapshot
     ```
   - **Run Tests**:
     ```bash
     dbt test
     ```

## Project Components

### 1. Models

- **Input Models** (`models/input`):
  - `user_session_channel.sql`: Cleans and stages data from the `raw_data.user_session_channel` table.
  - `session_timestamp.sql`: Cleans and stages data from the `raw_data.session_timestamp` table.

- **Output Model** (`models/output`):
  - `session_summary.sql`: Joins the data from the staged `user_session_channel` and `session_timestamp` models into a summary table.

### 2. Snapshots

- **Snapshot File** (`snapshots/snapshot_session_summary.sql`): Tracks historical changes to the `session_summary` table, allowing rollback to previous data states. Uses the timestamp-based strategy to detect changes.

### 3. Tests

- **Data Quality Tests**:
  - Configured in `schema.yml`, these tests ensure the `sessionId` field in `session_summary` is unique and not null.

## Example SQL Files

### `user_session_channel.sql`
```sql
WITH user_channel_data AS (
    SELECT sessionId, userId, channel
    FROM {{ source('raw_data', 'user_session_channel') }}
    WHERE sessionId IS NOT NULL
)
SELECT * FROM user_channel_data;
```

### `session_timestamp.sql`
```sql
WITH session_data AS (
    SELECT sessionId, ts
    FROM {{ source('raw_data', 'session_timestamp') }}
    WHERE sessionId IS NOT NULL
)
SELECT * FROM session_data;
```

### `session_summary.sql`
```sql
WITH u AS (
    SELECT * FROM {{ ref("user_session_channel") }}
), st AS (
    SELECT * FROM {{ ref("session_timestamp") }}
)
SELECT u.userId, u.sessionId, u.channel, st.ts
FROM u
JOIN st ON u.sessionId = st.sessionId;
```

### `snapshot_session_summary.sql`
```sql
{% snapshot snapshot_session_summary %}
{{
    config(
        target_schema='snapshot',
        unique_key='sessionId',
        strategy='timestamp',
        updated_at='ts',
        invalidate_hard_deletes=True
    )
}}
SELECT * FROM {{ ref('session_summary') }}
{% endsnapshot %}
```

### `schema.yml`
```yaml
version: 2

sources:
  - name: raw_data
    database: your_database
    schema: raw_data
    tables:
      - name: user_session_channel
      - name: session_timestamp

models:
  - name: session_summary
    description: "Analytics model for session data"
    columns:
      - name: sessionId
        description: "Unique identifier for each session"
        tests:
          - unique
          - not_null
```

## Running dbt Commands

- **Run Models**:
  ```bash
  dbt run
  ```

- **Run Snapshots**:
  ```bash
  dbt snapshot
  ```

- **Run Tests**:
  ```bash
  dbt test
  ```
## Notes

- Ensure that your Snowflake credentials are securely managed in `profiles.yml`.
- Update `database` and `schema` names in `schema.yml` to match your Snowflake environment.
- Use `dbt docs generate` and `dbt docs serve` to view the documentation and lineage graph locally.
