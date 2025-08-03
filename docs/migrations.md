# Migrations
This is a guide on how to generate and run database migrations

## Creating migrations
1. Create new models, modify existing ones, or anything under folder `common/database/models`
2. Exec `make migrate name=YOUR_MIGRATION_NAME`
3. A new file will be created under folder `common/database/migrations/versions`

## Applying migrations
Run `make upgrade [target=(HEAD|MIGRATION_ID)]`
>NOTE: Target is optional, by default it'll be head

## Rolling back
Run `make downgrade [steps=TOTAL_STEPS]`
>NOTE: Total steps by default is -1 if not informed