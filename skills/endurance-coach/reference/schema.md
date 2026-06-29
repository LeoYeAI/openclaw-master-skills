# Database Schema Reference (One Table Per Line)

## Schema Version Tracking

- schema_migrations: id, name, applied_at

## Core Activity Data

- activities: id, name, sport_type, start_date, elapsed_time, moving_time, distance, total_elevation_gain, average_speed, max_speed, average_heartrate, max_heartrate, average_watts, max_watts, weighted_average_watts, kilojoules, suffer_score, average_cadence, calories, description, workout_type, gear_id, raw_json, synced_at, source
- streams: activity_id, time_data, distance_data, heartrate_data, watts_data, cadence_data, altitude_data, velocity_data

## Athlete Profile

- athlete: id, firstname, lastname, weight, ftp, max_heartrate, raw_json, updated_at

## Training Goals

- goals: id, event_name, event_date, event_type, notes, created_at

## Sync Metadata

- sync_log: id, started_at, completed_at, activities_synced, status

## Interview System

- workout_interviews: id, workout_id, athlete_reflection_summary, coach_notes, coach_confidence, created_at
- preliminary_coach_notes: id, workout_id, note_draft, created_at
- interview_triggers: id, trigger_type, threshold_value, threshold_unit, enabled, created_at, updated_at

## Views

- weekly_volume: week, sport_type, sessions, hours, km, avg_hr, avg_effort
- recent_activities: date, sport_type, name, minutes, km, hr, suffer_score

## Indexes

- idx_activities_date on activities(start_date)
- idx_activities_sport on activities(sport_type)
- idx_activities_sport_date on activities(sport_type, start_date)
- idx_workout_interviews_workout_id on workout_interviews(workout_id)
- idx_workout_interviews_created_at on workout_interviews(created_at)
- idx_workout_interviews_workout_created on workout_interviews(workout_id, created_at)
- idx_preliminary_notes_workout_id on preliminary_coach_notes(workout_id)

## Key Constraints

### activities

- id: PRIMARY KEY (Strava activity ID)
- source: 'strava' (default) or 'manual'
- workout_type: 0=default, 1=race, 2=workout, 3=long run

### streams

- activity_id: PRIMARY KEY, FOREIGN KEY → activities(id)
- All data columns store JSON arrays

### workout_interviews

- workout_id: FOREIGN KEY → activities(id)
- coach_confidence: CHECK constraint ('Low', 'Medium', 'High')

### preliminary_coach_notes

- workout_id: FOREIGN KEY → activities(id)

### interview_triggers

- trigger_type: UNIQUE, CHECK constraint ('hr_drift', 'pace_deviation', 'lap_variability', 'early_fade')
- enabled: 1 (enabled) or 0 (disabled)

## Migration History

1. **001_initial_schema**: Core tables (activities, streams, athlete, goals, sync_log)
2. **002_interview_tables**: Interview system (workout_interviews, preliminary_coach_notes, interview_triggers)
3. **003_add_activity_source**: Added source column to activities table
