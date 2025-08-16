# Cron Job Configuration

The jobs-agent system now supports configurable cron job scheduling through environment variables. This allows you to easily adjust the frequency and timing of all automated tasks without modifying code.

## Configuration Variables

### Environment Variables

All cron jobs can be configured using the following environment variables:

| Variable | Description | Default | Format |
|----------|-------------|---------|---------|
| `CRON_JOB_SEEKER_INTERVAL_HOURS` | How often to search for new jobs | `6` | Hours (integer) |
| `CRON_JOB_SEEKER_START_TIME` | When to start the first job seeker run | `00:00` | HH:MM (24-hour) |
| `CRON_JOB_ENRICHMENT_INTERVAL_HOURS` | How often to enrich job postings | `12` | Hours (integer) |
| `CRON_JOB_ENRICHMENT_START_TIME` | When to start the first enrichment run | `02:00` | HH:MM (24-hour) |
| `CRON_NOTIFICATION_INTERVAL_HOURS` | How often to send general notifications | `6` | Hours (integer) |
| `CRON_NOTIFICATION_START_TIME` | When to start the first notification run | `08:00` | HH:MM (24-hour) |
| `CRON_MATCH_NOTIFICATION_INTERVAL_HOURS` | How often to send match notifications | `24` | Hours (integer) |
| `CRON_MATCH_NOTIFICATION_START_TIME` | When to start the first match notification run | `09:00` | HH:MM (24-hour) |

## Job Descriptions

### 1. Job Seeker Cron (`job_seeker_agent_cron`)
- **Purpose**: Searches for new job postings using AI agents
- **Default**: Every 6 hours starting at midnight
- **Use Case**: Keep job database fresh with new opportunities

### 2. Job Enrichment Cron (`job_enrichment_workflow_cron`)
- **Purpose**: Enriches job postings with detailed analysis and generates matches
- **Default**: Every 12 hours starting at 2 AM
- **Use Case**: Process new jobs and create candidate matches

### 3. Notification Cron (`notification_cron`)
- **Purpose**: Sends general notifications about system updates
- **Default**: Every 6 hours starting at 8 AM
- **Use Case**: Keep users informed about system status

### 4. Match Notification Cron (`match_notification_cron`)
- **Purpose**: Sends personalized job matches to candidates
- **Default**: Every 24 hours starting at 9 AM
- **Use Case**: Daily digest of relevant job opportunities

## Configuration Examples

### Example 1: High-Frequency Job Search
```bash
# Search for jobs every 2 hours, starting at midnight
CRON_JOB_SEEKER_INTERVAL_HOURS=2
CRON_JOB_SEEKER_START_TIME=00:00

# Enrich jobs every 4 hours, starting at 1 AM
CRON_JOB_ENRICHMENT_INTERVAL_HOURS=4
CRON_JOB_ENRICHMENT_START_TIME=01:00
```

### Example 2: Business Hours Focus
```bash
# Run enrichment during business hours only
CRON_JOB_ENRICHMENT_INTERVAL_HOURS=8
CRON_JOB_ENRICHMENT_START_TIME=09:00

# Send match notifications at lunch time
CRON_MATCH_NOTIFICATION_INTERVAL_HOURS=24
CRON_MATCH_NOTIFICATION_START_TIME=12:00
```

### Example 3: Weekend Optimization
```bash
# Less frequent during weekends
CRON_JOB_SEEKER_INTERVAL_HOURS=12
CRON_JOB_SEEKER_START_TIME=08:00

# More frequent during weekdays
CRON_JOB_ENRICHMENT_INTERVAL_HOURS=6
CRON_JOB_ENRICHMENT_START_TIME=06:00
```

## Time Format

All start times use 24-hour format:
- `00:00` = Midnight
- `09:00` = 9:00 AM
- `13:30` = 1:30 PM
- `23:59` = 11:59 PM

## Best Practices

1. **Stagger Start Times**: Avoid having all jobs start at the same time
2. **Consider Time Zones**: Configure start times based on your target audience's time zone
3. **Resource Management**: Balance frequency with system resources
4. **User Experience**: Schedule match notifications when users are most likely to check

## Environment File Setup

Copy the `env.example` file to `.env` and customize the values:

```bash
cp env.example .env
# Edit .env with your preferred values
```

## Monitoring

The system logs all cron job scheduling and execution. Check logs for:
- Job scheduling confirmation
- Start time calculations
- Execution success/failure
- Performance metrics

## Troubleshooting

### Common Issues

1. **Invalid Time Format**: Ensure times are in HH:MM format
2. **Invalid Interval**: Intervals must be positive integers
3. **Start Time in Past**: System automatically adjusts to next occurrence
4. **Timezone Issues**: All times are processed in system timezone

### Debug Mode

Enable debug logging to see detailed scheduling information:

```bash
export LOG_LEVEL=DEBUG
```

## Migration from Hardcoded Values

If you're upgrading from the previous version:
1. The system will use default values if environment variables are not set
2. All existing functionality remains unchanged
3. You can gradually adjust values to find optimal settings
