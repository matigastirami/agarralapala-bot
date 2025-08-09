# Database Seeder

This document describes how to use the database seeder functionality for the jobs-agent application.

## Overview

The database seeder allows you to populate the database with sample candidates for testing and development purposes. It creates 10 candidates with current market technologies, roles, and locations across Latin America.

## Available Commands

### Seed Candidates

To seed the database with sample candidates:

```bash
make seed
```

This command will:
- Create 10 candidates with diverse tech stacks (NestJS, React, Python, etc.)
- Assign roles (backend, frontend, data)
- Set locations across Latin America (Argentina, Chile, Colombia, etc.)
- Skip candidates that already exist (based on tech_stack and role combination)

### Clear Seeded Candidates

To clear all seeded candidates from the database:

```bash
make seed-clear
```

This command will remove all candidates from the database.

## Candidate Data

The seeder creates candidates with the following characteristics:

### Tech Stacks
- **Backend**: NestJS, TypeScript, Node.js, PostgreSQL, Docker
- **Frontend**: React, TypeScript, Next.js, Tailwind CSS, Redux
- **Data**: Python, Pandas, NumPy, Scikit-learn, Jupyter

### Roles
- Backend Developer
- Frontend Developer
- Data Scientist/Engineer

### Locations
- Buenos Aires, Argentina
- Santiago, Chile
- Bogotá, Colombia
- Lima, Peru
- Montevideo, Uruguay
- São Paulo, Brazil
- Mexico City, Mexico

### Languages
- Spanish (es) - for most Latin American countries
- Portuguese (pt) - for Brazil

## Implementation Details

The seeder is implemented in the following files:

- `common/database/seeders/__init__.py` - Package initialization
- `common/database/seeders/candidate_seeder.py` - Main seeder logic
- `common/database/seeders/__main__.py` - Command-line interface

### Usage Examples

```bash
# Seed candidates
make seed

# Clear candidates
make seed-clear

# Run seeder directly with Python
source venv/bin/activate
python -m common.database.seeders

# Run seeder with clear option
python -m common.database.seeders --clear

# Run seeder with clear-only option
python -m common.database.seeders --clear-only
```

## Error Handling

The seeder includes error handling for:
- Database connection issues
- Duplicate candidate detection
- Transaction rollback on errors

## Notes

- The seeder checks for existing candidates before creating new ones to avoid duplicates
- All candidates are created with realistic tech stacks and locations
- The seeder is designed to be idempotent - running it multiple times won't create duplicates
