# HandshakeReports - Change Log

## Version 0.1.0 (2023/12/12)

### Major Feature Changes
---
 + Added example .env
 + Added readme
    + Added Chromium Driver installation instructions
    + Added project description
    + Added setup instructions/steps
    + Added Reports documentation
    + Added feature checklist
    + Added environmental variable setup
+ Added generic utilities
+ Added file utilities
+ Added DataSet class
    + Defined known columns and types
    + Added filtering functions (by email, date, status, majors, etc.)
    + Added remove numbers from columns for surveys (Handshake puts them there by default at this time)
    + Added user input if emails or dates missing
+ Added Report controller
    + Added handling for each type of report
    + Added basic run/save report functions
+ Added SurveyResult report
    + Added key check upon initialization
    + Added run logic to sort by date -> filter appointment status -> filter dates -> filter by staff emails -> merge appointment data with survey results -> filter time difference
+ Added Followup report
    + Added run logic to filter dates -> filter followup appointments -> add latest followup column -> remove followed up -> filter most recent followup -> add past followup count
+ Added Referrals report
    + Added run logic to filter valid appointments -> merge referrals with appointments -> remove past appointments -> add appointment scheduled and completed columns -> merge enrollment data -> remove duplicates
+ Added Driver
+ Added Config controller
    + Added FilesConfig
        + Added load files from config
    + Added ReportsConfig
        + Added load reports from FilesConfig


### Minor Feature Changes
---
 - Removed download Handshake survey results - moved to independent repository
 = Changed to regex patterns for filters
 + Added filter pattern from list
 = Split config into two files - reports and files config
 + Added default config fallbacks (for missing keys) for each report type
 + Added handling missing optional config keys as None/undefined
 + Added duplicate referral handling - initially thought to be irrelevant
 + Add debug logging throughout script

### Bug Fixes
---
N/A