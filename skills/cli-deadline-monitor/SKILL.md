---
name: cli-deadline-monitor
description: CLI tool for tracking Greek tax deadlines (AADE, EFKA). Real-time monitoring with configurable alerts via Slack, SMS, email, or local files.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "deadlines", "compliance", "aade", "efka"]
metadata: {"openclaw": {"requires": {"bins": ["jq"], "env": ["OPENCLAW_DATA_DIR"]}, "optional_env": {"SLACK_WEBHOOK_URL": "Webhook URL for Slack deadline alerts", "SMS_GATEWAY_URL": "SMS gateway API endpoint for urgent deadline alerts", "SMTP_HOST": "Email server for deadline notifications", "SMTP_USER": "Email account for sending notifications", "SMTP_PASSWORD": "Email account password", "GOOGLE_CALENDAR_ID": "Google Calendar ID for deadline event sync", "OUTLOOK_CALENDAR_ID": "Outlook Calendar ID for deadline event sync"}, "notes": "Core deadline tracking works with no credentials. Optional channels (Slack, SMS, email, Google Calendar, Outlook Calendar) require their env vars. Unconfigured channels are silently skipped."}}
---

# CLI Deadline Monitor

This skill provides comprehensive command-line tools for monitoring Greek government websites and APIs to track tax deadlines, regulatory changes, and compliance requirements in real-time.


## Setup

```bash
# 1. Set data directory
export OPENCLAW_DATA_DIR="/data"

# 2. Ensure jq is installed
which jq || sudo apt install jq

# 3. Ensure client data exists
ls $OPENCLAW_DATA_DIR/clients/*/compliance/obligations.json
```

No external credentials required. This skill reads deadline data from local files only.


## Core Philosophy

- **Real-time Monitoring**: Continuous checking of AADE and EFKA websites for deadline changes
- **API-First Approach**: Use official APIs where available, intelligent scraping where necessary
- **Proactive Alerts**: Early warning system for deadline changes and new requirements
- **CLI Efficiency**: Fast, scriptable commands for integration with automated workflows
- **Reliability**: Robust error handling and fallback mechanisms for critical compliance monitoring

## Key Capabilities

### 1. AADE Deadline Monitoring
- **Tax Return Deadlines**: Monitor individual and corporate tax return due dates
- **VAT Return Tracking**: Monthly and quarterly VAT submission deadlines
- **myDATA Requirements**: Real-time invoice submission deadline monitoring
- **System Status**: TAXIS and myDATA system availability checking
- **Rate Change Alerts**: VAT rate changes and effective dates
- **Form Updates**: New tax forms and requirement changes

### 2. EFKA Social Security Monitoring
- **Contribution Deadlines**: Monthly social security payment due dates
- **Rate Updates**: Changes to social security contribution rates
- **Employer Obligations**: New employer reporting requirements
- **System Maintenance**: EFKA portal downtime and maintenance schedules
- **Legislative Changes**: New social security laws and regulations

### 3. Municipal Tax & License Monitoring
- **Property Tax (TAP)**: Municipal property tax monitoring (0.025%-0.035% of property value)
- **Business License Renewals**: Track municipal business license expiration and renewal requirements
- **Municipal Permits**: Construction, signage, zoning, and operational permits by municipality
- **Waste Collection & Lighting Fees**: Municipality-specific rates and payment schedules
- **Municipal Transfer Tax Surcharge**: 0.09% municipal surcharge on property transfers
- **Local Business Taxes**: Municipality-specific business activity taxes and fees
- **Building Permits**: Municipal construction permit deadlines and requirements

### 3. CLI Command Interface
- **Quick Status Commands**: Fast deadline checking and status overview
- **Automated Scheduling**: Cron-compatible commands for regular monitoring
- **Alert Configuration**: Customizable notification thresholds and methods
- **Batch Processing**: Multiple deadline checks in single command execution
- **Export Options**: JSON, CSV, and structured output formats

### 4. Integration & Automation
- **Email Notifications**: Automated email alerts for deadline changes
- **Notification System**: Alert notifications via configured channels
- **Deadline Tracking**: Deadline alerts and tracking via CLI
- **API Webhooks**: REST API endpoints for external system integration
- **Log Management**: Comprehensive logging of all monitoring activities

## Implementation Guidelines

### Command Structure Design

#### Core CLI Commands
```bash
# Primary monitoring commands
openclaw deadline check aade          # Check all AADE deadlines
openclaw deadline check efka          # Check all EFKA deadlines  
openclaw deadline check all           # Check all government deadlines

# Specific deadline types
openclaw deadline vat monthly         # Monthly VAT return deadlines
openclaw deadline vat quarterly       # Quarterly VAT deadlines
openclaw deadline tax individual      # Individual tax return deadlines
openclaw deadline tax corporate       # Corporate tax deadlines
openclaw deadline social monthly      # Monthly social security deadlines

# Municipal monitoring commands
openclaw deadline municipal --city athens    # Athens municipality deadlines
openclaw deadline municipal --city thessaloniki # Thessaloniki municipality deadlines
openclaw deadline municipal all       # All municipal deadlines by taxpayer location
openclaw licenses check renewals      # Business license renewal deadlines
openclaw permits check construction   # Construction permit deadlines
openclaw municipal rates update       # Municipal tax rate changes

# System status checks
openclaw status aade                  # AADE system availability
openclaw status efka                  # EFKA system status
openclaw status mydata               # myDATA platform status
openclaw status taxis               # TAXIS system status

# Alert management
openclaw alerts setup               # Configure alert preferences
openclaw alerts test                # Test notification systems
openclaw alerts history            # View alert history
openclaw alerts disable            # Temporarily disable alerts
```

#### Advanced Monitoring Commands
```bash
# Historical tracking
openclaw deadline history aade      # Show AADE deadline change history
openclaw deadline compare 2025 2026 # Compare deadlines between years
openclaw deadline export json       # Export deadlines to JSON
openclaw deadline export calendar   # Export to calendar format

# Rate monitoring
openclaw rates vat current          # Current VAT rates
openclaw rates vat changes          # VAT rate change history
openclaw rates social current       # Current social security rates
openclaw rates social changes       # Social security rate changes

# Form and requirement monitoring  
openclaw forms check updates        # Check for new tax forms
openclaw forms download new         # Download updated forms
openclaw requirements changes       # Check requirement changes
```

### API Integration Architecture

#### AADE API Integration
```yaml
AADE_Endpoints:
  taxis_status:
    url: "https://www1.aade.gr/taxisnet/api/status"
    method: "GET"
    auth_required: false
    rate_limit: "100/hour"
    
  mydata_status:
    url: "https://mydatapi.aade.gr/api/status"
    method: "GET" 
    auth_required: false
    rate_limit: "100/hour"
    
  deadline_tracker:
    url: "https://www.aade.gr/api/deadlines/current"
    method: "GET"
    auth_required: false
    rate_limit: "50/hour"
    
  vat_rates:
    url: "https://www.aade.gr/api/rates/vat/current"
    method: "GET"
    auth_required: false
    rate_limit: "20/hour"

AADE_Scraping_Targets:
  deadline_announcements:
    url: "https://www.aade.gr/epiheiriseis/forologikes-ypohreosieis"
    selector: ".announcement-deadline"
    frequency: "every_4_hours"
    
  rate_changes:
    url: "https://www.aade.gr/epiheiriseis/fpa"
    selector: ".rate-change-notice"
    frequency: "daily"
    
  system_maintenance:
    url: "https://www.aade.gr/systima/sytirika-minymata"
    selector: ".maintenance-notice"
    frequency: "hourly"
```

#### EFKA API Integration  
```yaml
EFKA_Endpoints:
  portal_status:
    url: "https://www.efka.gov.gr/api/status"
    method: "GET"
    auth_required: false
    rate_limit: "100/hour"
    
  contribution_rates:
    url: "https://www.efka.gov.gr/api/rates/current"
    method: "GET"
    auth_required: false
    rate_limit: "20/hour"
    
  deadline_tracker:
    url: "https://www.efka.gov.gr/api/deadlines/monthly"
    method: "GET"
    auth_required: false
    rate_limit: "50/hour"

EFKA_Scraping_Targets:
  contribution_deadlines:
    url: "https://www.efka.gov.gr/el/ypodomes/efka/asfalikes-eisfores"
    selector: ".deadline-table"
    frequency: "every_6_hours"
    
  rate_announcements:
    url: "https://www.efka.gov.gr/el/anakoinoseis"
    selector: ".rate-announcement"
    frequency: "daily"
    
  legislative_changes:
    url: "https://www.efka.gov.gr/el/nomothesia"
    selector: ".law-change"
    frequency: "daily"

#### Municipal API Integration
```yaml
Major_Municipality_Endpoints:
  athens_municipality:
    url: "https://www.cityofathens.gr/epixeiriseis"
    business_licenses: "https://www.cityofathens.gr/adeiodotisi"
    permit_tracker: "https://www.cityofathens.gr/adeia-kataskevi"
    
  thessaloniki_municipality:
    url: "https://www.thessaloniki.gr/epixeiriseis"
    business_services: "https://www.thessaloniki.gr/ypiresies"
    
  piraeus_municipality:
    url: "https://www.pireasnet.gr/epixeiriseis"
    
  patras_municipality:
    url: "https://www.patras.gr/epixeirein"

Municipal_Tax_Monitoring:
  tap_rates:
    athens: "0.025% base rate"
    thessaloniki: "0.030% base rate" 
    other_major: "0.025%-0.035% range"
    
  business_license_cycles:
    standard_renewal: "Annual - varies by municipality"
    construction_permits: "Project-based with municipal timelines"
    operational_permits: "Annual or biennial depending on activity"
    
  municipal_fee_structures:
    waste_collection: "Per square meter - municipal council rates"
    street_lighting: "Per property area - council determined"
    signage_permits: "Annual fees varying by municipality"
    
Municipal_Scraping_Targets:
  business_license_announcements:
    frequency: "weekly"
    target_selectors: ".business-announcement, .license-renewal"
    
  construction_permit_changes:
    frequency: "bi-weekly" 
    target_selectors: ".permit-update, .construction-deadline"
    
  municipal_tax_rate_changes:
    frequency: "monthly"
    target_selectors: ".tax-rate-change, .municipal-fee-update"
```

### Alert System Configuration

#### Alert Types and Triggers
```yaml
Critical_Alerts:
  deadline_approaching:
    trigger: "7 days before deadline"
    channels: ["email", "slack", "sms"]  # Channels with unconfigured credentials are silently skipped
    frequency: "daily"
    
  deadline_changed:
    trigger: "immediate on detection"
    channels: ["email", "slack", "sms"]  # Channels with unconfigured credentials are silently skipped
    frequency: "immediate"
    
  system_outage:
    trigger: "AADE/EFKA system unavailable >30min"
    channels: ["email", "slack", "sms"]  # Channels with unconfigured credentials are silently skipped 
    frequency: "immediate"

Warning_Alerts:
  rate_change_announced:
    trigger: "VAT or social security rate changes"
    channels: ["email", "slack", "sms"]  # Channels with unconfigured credentials are silently skipped
    frequency: "immediate"
    
  new_requirements:
    trigger: "New tax forms or compliance requirements"
    channels: ["email"]
    frequency: "daily_digest"
    
  maintenance_scheduled:
    trigger: "Planned system maintenance detected"
    channels: ["email", "slack", "sms"]  # Channels with unconfigured credentials are silently skipped
    frequency: "24_hours_before"

Info_Alerts:
  monthly_summary:
    trigger: "1st of each month"
    channels: ["email"]
    content: "Monthly deadline tracker and compliance summary"
    
  quarterly_review:
    trigger: "Start of each quarter"
    channels: ["email", "slack", "sms"]  # Channels with unconfigured credentials are silently skipped
    content: "Quarterly compliance requirements and deadlines"
```

#### Notification Channel Configuration
```yaml
Email_Configuration:
  smtp_server: "configurable"
  templates:
    deadline_alert: "Greek tax deadline approaching: {deadline_type} due {due_date}"
    system_outage: "AADE/EFKA system outage detected - {system} unavailable"
    rate_change: "Greek tax rate change: {rate_type} changing from {old_rate} to {new_rate}"
    
Slack_Integration:
  webhook_url: "configurable"
  channels: 
    critical: "#accounting-alerts"
    warnings: "#tax-updates"
    info: "#compliance-digest"
    
SMS_Configuration:
  provider: "configurable (Twilio, etc.)"
  numbers: "configurable emergency contacts"
  critical_only: true
```

## Deadline Monitoring Workflows

### Daily Monitoring Routine
```bash
#!/bin/bash
# Daily deadline monitoring script

# Check all critical systems
openclaw status all --format json > /tmp/system_status.json

# Check upcoming deadlines (next 30 days)
openclaw deadline check all --days 30 --format json > /tmp/upcoming_deadlines.json

# Check for any deadline changes since yesterday
openclaw deadline changes --since yesterday --format json > /tmp/deadline_changes.json

# Check for rate updates
openclaw rates check changes --since yesterday > /tmp/rate_changes.json

# Generate daily summary
openclaw summary generate daily --include-status --include-deadlines --include-changes
```

### Weekly Deep Monitoring
```bash
#!/bin/bash
# Weekly comprehensive monitoring script

# Full deadline tracker refresh
openclaw deadline refresh --full-update

# Historical deadline analysis
openclaw deadline analyze --weeks 4 --detect-patterns

# Rate change trend analysis
openclaw rates analyze --months 3 --predict-changes

# System reliability report
openclaw status report --days 7 --include-uptime

# Generate weekly compliance report
openclaw report generate weekly --email-recipients --include-recommendations
```

### Municipal Compliance Workflow
```bash
#!/bin/bash
# Municipal tax and license monitoring

# Identify taxpayer municipality based on business address
openclaw taxpayer locate --address "$BUSINESS_ADDRESS" --output municipality

# Check municipality-specific deadlines
openclaw deadline municipal --city "$MUNICIPALITY" --days 30

# Monitor business license renewals
openclaw licenses check --municipality "$MUNICIPALITY" --business-type "$BUSINESS_TYPE"

# Check construction permit requirements if applicable
if [ "$HAS_CONSTRUCTION_PERMITS" == "true" ]; then
    openclaw permits check construction --municipality "$MUNICIPALITY"
fi

# Monitor municipal tax rate changes
openclaw municipal rates monitor --city "$MUNICIPALITY" --alert-on-change

# Generate municipal compliance summary
openclaw municipal summary --taxpayer "$VAT_NUMBER" --include-deadlines --include-rates
```

### Municipality Detection & Configuration
```yaml
Taxpayer_Location_Detection:
  methods:
    vat_registration: "Use VAT number to determine registered municipality"
    business_address: "Parse business address to identify municipality" 
    property_location: "For property taxes, use property municipality"
    manual_configuration: "Allow manual municipality specification"
    
Municipality_Database:
  major_municipalities:
    - code: "ATH", name: "Athens", tax_office: "A' ΑΜΗΝΩΝ"
    - code: "THE", name: "Thessaloniki", tax_office: "A' ΜΕΣΣΑ΀ºθΝΙΡΗΣ"
    - code: "PIR", name: "Piraeus", tax_office: "ΠΕΙΡΑΙΑ"  
    - code: "PAT", name: "Patras", tax_office: "ΠΑΤΡΩΝ"
    - code: "HER", name: "Heraklion", tax_office: "ΗΡΑΡ΀ºΕΙθΥ"
    
  municipality_specific_rates:
    TAP_rates:
      athens: 0.025
      thessaloniki: 0.030
      piraeus: 0.025
      default: 0.025
      
    waste_lighting_fees:
      calculated_by: "square_meter_municipal_rate"
      varies_by: "municipal_council_decision"
      frequency: "annual_billing_via_electricity"
```
```bash
#!/bin/bash
# Emergency response for critical deadline changes

# Immediate notification to all channels
openclaw alerts emergency --message "Critical deadline change detected" \
  --channels all --priority high

# Generate emergency report
openclaw deadline emergency-report --deadline "$1" --old-date "$2" --new-date "$3"

# Update calendar integrations immediately
openclaw calendar update-emergency --deadline "$1" --new-date "$3"

# Log emergency response
openclaw log emergency "Deadline change: $1 moved from $2 to $3"
```

## Greek-Specific Implementation Details

### Greek Holiday Deadline Integration
```yaml
Greek_National_Holidays:
  fixed_holidays:
    - "01-01": "New Year's Day"
    - "01-06": "Epiphany"
    - "03-25": "Independence Day" 
    - "05-01": "Labour Day"
    - "08-15": "Assumption of Mary"
    - "10-28": "Ohi Day"
    - "12-25": "Christmas Day"
    - "12-26": "Boxing Day"
    
  variable_holidays:
    - "Clean Monday": "48 days before Easter"
    - "Good Friday": "Friday before Easter"
    - "Easter Monday": "Day after Easter"
    - "Holy Spirit Monday": "50 days after Easter"
    
Business_Day_Calculations:
  exclude_weekends: true
  exclude_holidays: true
  custom_business_hours: "08:00-15:00 EET"
  deadline_extensions:
    weekend_extension: "Next business day"
    holiday_extension: "Next business day"
```

### Greek Language Support
```yaml
Language_Configuration:
  primary_language: "Greek (el-GR)"
  fallback_language: "English (en-US)"
  
Date_Formats:
  greek_format: "dd/MM/yyyy"
  iso_format: "yyyy-MM-dd"
  display_preference: "greek_format"
  
Greek_Month_Names:
  - "Ιανουάριοπš"  # January
  - "Φεβρουάριοπš" # February  
  - "Μάρπžιοπš"     # March
  - "Απρίλιοπš"    # April
  - "Μάιοπš"       # May
  - "Ιούνιοπš"     # June
  - "Ιούλιοπš"     # July
  - "Αύγουσπžοπš"   # August
  - "Σεππžέμβριοπš" # September
  - "θκπžϽβριοπš"   # October
  - "Νοέμβριοπš"   # November
  - "Δεκέμβριοπš"  # December
```

### Timezone and Regional Settings
```yaml
Timezone_Configuration:
  primary_timezone: "Europe/Athens"
  dst_handling: "automatic"
  business_hours: "08:00-15:00 EET/EEST"
  
Regional_Settings:
  currency: "EUR"
  number_format: "1.234,56"
  percentage_format: "12,34%"
  
Government_Office_Hours:
  aade_offices: "08:00-14:30 Monday-Friday"
  efka_offices: "08:00-14:00 Monday-Friday"
  system_maintenance_window: "02:00-06:00 EET typically"
```

## Error Handling & Reliability

### Robust Error Management
```bash
# API failure handling
openclaw deadline check aade --retry-attempts 3 --backoff-strategy exponential
openclaw deadline check efka --fallback-method scraping --timeout 30s

# Network connectivity issues
openclaw status network --test-connectivity --log-failures
openclaw deadline cache --use-cached-if-offline --max-age 24h

# Data validation and consistency
openclaw deadline validate --check-consistency --flag-anomalies
openclaw rates validate --historical-comparison --detect-errors
```

### Monitoring and Logging
```yaml
Log_Configuration:
  log_level: "INFO"
  log_file: "/var/log/openclaw/deadline-monitor.log"
  log_rotation: "daily"
  retention_days: 90
  
Monitoring_Metrics:
  api_response_times: "Track API performance"
  success_rates: "Monitor API reliability"
  alert_delivery: "Track notification success"
  deadline_accuracy: "Validate deadline information"
  
Health_Checks:
  self_monitoring: "Internal system health checks"
  external_validation: "Cross-check with official sources"
  data_consistency: "Validate data integrity"
  alert_system_test: "Regular notification testing"
```

## Performance Optimization

### Caching Strategy
```yaml
Cache_Configuration:
  deadline_cache_ttl: "4 hours"
  rate_cache_ttl: "24 hours"
  status_cache_ttl: "5 minutes"
  
Cache_Invalidation:
  force_refresh_on_change: true
  scheduled_refresh: "Every 6 hours"
  emergency_cache_clear: "On critical alerts"
  
Performance_Tuning:
  concurrent_requests: 5
  request_timeout: 30
  retry_delays: [1, 2, 5, 10]
  rate_limiting: "Respect API limits"
```

## Integration Examples

### OpenClaw Integration
```bash
# Add to OpenClaw daily routine
openclaw skills add cli-deadline-monitor
openclaw schedule add daily "09:00" "deadline check all --alert-if-changes"
openclaw schedule add weekly "monday 08:00" "deadline report generate weekly"

# Integration with other accounting skills
openclaw deadline check vat --integrate-with accounting-workflows
openclaw deadline check efka --integrate-with greek-compliance-aade
```

### External System Integration
```bash
# Deadline export
openclaw deadline sync calendar --provider google --calendar-id "accounting@company.com"
openclaw deadline export --format ical --output /data/reports/deadlines.ics
openclaw deadline sync calendar --provider google --calendar-id $GOOGLE_CALENDAR_ID  # Optional: sync to Google Calendar
openclaw deadline sync calendar --provider outlook --calendar-id $OUTLOOK_CALENDAR_ID  # Optional: sync to Outlook

# Accounting software integration
openclaw deadline export --format csv --period 2026-Q1
openclaw deadline export --format json --period 2026-02
openclaw deadline export --format ical --upcoming 30d

# Business communication platforms
openclaw alerts setup slack --webhook-url $SLACK_WEBHOOK_URL  # Optional: configure if Slack alerts desired
openclaw alerts setup teams --webhook-url $TEAMS_WEBHOOK
openclaw alerts setup email --smtp-config /etc/openclaw/smtp.conf
```

## Usage Examples

### Example 1: Daily Deadline Check
```bash
$ openclaw deadline check all

AADE Deadlines (Next 30 Days):
✓ Monthly VAT Return (February 2026) - Due: March 20, 2026 (31 days)
⚠ Individual Tax Returns (2025) - Due: June 30, 2026 (133 days)
✓ Quarterly VAT Return (Q1 2026) - Due: April 25, 2026 (67 days)

EFKA Deadlines (Next 30 Days):  
⚠ Monthly Social Security Contributions (February 2026) - Due: March 15, 2026 (26 days)
✓ Quarterly Social Security Report (Q1 2026) - Due: April 30, 2026 (72 days)

System Status:
✓ AADE TAXIS: Online
✓ AADE myDATA: Online  
✓ EFKA Portal: Online

Alerts: 1 deadline approaching in <30 days
```

### Example 2: Deadline Change Detection
```bash
$ openclaw deadline changes --since yesterday

CHANGES DETECTED:
🚨 CRITICAL: Monthly VAT deadline moved from March 25 to March 20, 2026
   - Reason: Updated AADE announcement
   - Impact: 5 days earlier than expected
   - Action: Notifications sent to all channels

📧 Notifications sent:
   - Email: accounting@company.com ✓
   - Slack: #accounting-alerts (if SLACK_WEBHOOK_URL configured) ✓  
   - SMS: +30-xxx-xxx-xxx ✓

📅 Calendar updates:
   - Google Calendar: Updated ✓
   - Outlook Calendar: Updated ✓
```

### Example 4: Municipal License Renewal Check
```bash
$ openclaw licenses check renewals --municipality athens --business-type restaurant

MUNICIPAL LICENSE STATUS - ATHENS:
📀¹ Business License Renewals Due:
⚠ General Business License - Due: April 15, 2026 (57 days)
✓ Food Service Permit - Renewed until December 31, 2026 (318 days)  
🚨 EFET Health Certificate - Due: March 1, 2026 (12 days) - URGENT!

ðŸÂ—ï¸ Construction/Operational Permits:
✓ Signage Permit - Valid until August 30, 2026 (194 days)
⚠ Fire Department Certificate - Due: May 20, 2026 (92 days)

💰 Municipal Fees Due:
✓ TAP (Municipal Property Tax) - Paid via electricity bill (0.025%)
⚠ Waste Collection Fee - Due: March 20, 2026 (31 days)
✓ Street Lighting Fee - Automatically charged (current)

📞 Municipality Contact: Athens Business Services - 210-527-7000
📧 Automated alerts will be sent 30, 15, and 7 days before each deadline
```

### Example 5: Multi-Municipality Business Monitoring  
```bash
$ openclaw deadline municipal all --business-vat EL123456789

MULTI-LOCATION BUSINESS MONITORING:
ðŸÂ¢ Primary Business (Athens):
├─ VAT Registration: Α' ΑΜΗΝΩΝ Tax Office
├─ Municipal License: Due April 15, 2026
├─ TAP Rate: 0.025% of property value
└─ Special Requirements: Athens Municipality signage regulations

ðŸÂª Branch Office (Thessaloniki):  
├─ Local Business Permit: Due June 30, 2026
├─ TAP Rate: 0.030% of property value  
├─ Municipal Fees: Higher waste collection rates
└─ Special Requirements: Thessaloniki commercial zone restrictions

ðŸÂ­ Warehouse (Patras):
├─ Industrial Permit: Due September 15, 2026
├─ TAP Rate: 0.025% of property value
├─ Environmental Permits: Required for industrial activity
└─ Special Requirements: Port authority coordination needed

Summary: 3 locations monitored across 3 municipalities
Next Action: Athens EFET certificate renewal in 12 days
```
```bash
$ openclaw status all --detailed

AADE Systems:
├─ TAXIS Portal: ✓ Online (Response: 245ms)
├─ myDATA API: ✓ Online (Response: 180ms)  
├─ VIES Validation: ✓ Online (Response: 320ms)
└─ Public Website: ✓ Online (Response: 410ms)

EFKA Systems:
├─ Main Portal: ✓ Online (Response: 380ms)
├─ Contribution Portal: ⚠ Slow (Response: 2.1s)
├─ Employer Services: ✓ Online (Response: 290ms)
└─ Public Website: ✓ Online (Response: 350ms)

Overall Health: ✓ All Critical Systems Operational
Last Updated: 2026-02-17 09:30:15 EET
```

## OpenClaw Integration & Deployment

### OpenClaw Installation & Setup
```bash
# Install CLI deadline monitor skill
npx openclaw skills add cli-deadline-monitor

# Configure for Greek timezone and holidays
openclaw config set timezone "Europe/Athens"
openclaw config set country "Greece"
openclaw config set language "el-GR"

# Set up monitoring credentials (if available)
openclaw config set aade-api-key "your-api-key"  # If available
openclaw config set efka-api-key "your-api-key"  # If available

# Test installation
openclaw deadline test-connection --aade --efka --municipal
```

### Automated Scheduling in OpenClaw
```bash
# Set up automated monitoring schedules
openclaw schedule add "0 9 * * *" "openclaw deadline check all --alert-changes"
openclaw schedule add "0 */4 * * *" "openclaw status aade --log-uptime"
openclaw schedule add "0 8 * * 1" "openclaw deadline report weekly --email-summary"

# Emergency monitoring for critical changes
openclaw monitor add "deadline-changes" --trigger immediate --channels all
openclaw monitor add "system-outages" --trigger 30min --priority high
```

### File-Based Processing (OpenClaw Preferred)
```yaml
File_Processing_Approach:
  # Instead of direct API calls, use file monitoring
  input_monitoring:
    - /data/incoming/government/*.html    # Government HTML announcements
    - /data/incoming/government/*.pdf     # AADE/EFKA deadline change PDFs
    - /data/incoming/government/*.xml     # Rate announcement XML feeds
    
  processing_workflow:
    step_1: "openclaw deadline scan-files --government-sources"
    step_2: "openclaw deadline extract-changes --compare-previous"
    step_3: "openclaw deadline alert-users --if-changes-detected"
    
  output_generation:
    - /data/reports/daily/{YYYY-MM-DD}_deadline-summary.json
    - /data/dashboard/state/current-alerts.json
    - /data/dashboard/state/deadline-tracker.json
    - /data/exports/compliance-deadlines.json
```

### Offline Operation & Caching
```bash
# Cache management for reliable operation
openclaw deadline cache-update --source aade-backup --municipal-sites
openclaw deadline cache-validate --check-freshness --alert-stale

# Offline mode when APIs unavailable
openclaw deadline offline-mode --enable --use-cached-data
openclaw deadline emergency-data --load-backup --continue-monitoring
```

### Data Protection
- **No Authentication Storage**: Never store government portal credentials
- **Secure Communications**: All API calls over HTTPS/TLS
- **Data Minimization**: Only collect necessary deadline and status information
- **Audit Logging**: Complete log of all monitoring activities
- **Access Controls**: Restrict command execution to authorized users

### Compliance & Privacy
- **GDPR Compliance**: No personal data collection beyond system operation
- **Data Retention**: Automatic cleanup of old logs and cached data
- **Transparency**: Clear logging of all external system interactions
- **Reliability**: Redundant checking methods for critical deadlines

## Success Metrics

A successful CLI deadline monitoring system should achieve:
- ✅ 99.9% uptime for deadline monitoring
- ✅ <5 minute detection time for deadline changes
- ✅ 100% accuracy in deadline information  
- ✅ <30 second response time for CLI commands
- ✅ Zero missed critical deadline alerts
- ✅ Complete audit trail for all monitoring activities
- ✅ Integration with all major Greek government systems

Remember: This skill provides the foundation for proactive compliance management, ensuring Greek businesses never miss critical tax deadlines or regulatory changes.