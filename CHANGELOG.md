# HandshakeReports - Change Log

## Version 0.2.1 (Not Released Yet)

### Major Feature Changes

---

- Changed date filtering configuration to use `target_date_ranges` instead of `target_months` and `target_years`

### Minor Feature Changes

---

- Removed `target_months` and `target_years` from `SurveyResults` and `Followup` reports
- Added `target_date_ranges` to `SurveyResults` and `Followup` reports
- Added `filter_target_date_ranges` to `DataSet` class

### Bug Fixes

---

- Fixed bug where date ranges would include months in overlapping years when they should not

## Version 0.2.0 (2024-01-30)

### Major Feature Changes

---

- Significantly improved logging comprehensiveness and readability
- Refactored entire codebase to use `src` folder and a package structure
- Added type checking throughout codebase
- Added FilterType class to handle include/exclude filters
- Config Updates
  - Separated config types into separate classes (Config, ReportsConfig, FilesConfig, EnvConfig)
  - Added extensive type checking and validation methods for all config keys and values
  - Split config types into separate files: `config.json`, `reports.config.json`, and `files.config.json`
  - Added include/exclude keys for config values that represent filters (see [FilterType](src/utils/type_utils.py))
- Improved Date Ranges
  - Added support for multiple comma-separated month ranges
  - Added support for month ranges spanning multiple years
  - Added support for year ranges
  - Added support for multiple comma-separated year ranges
  - Added support for date ranges without an end date
  - Added error handling for invalid date ranges
  - Unified date range parsing
- Reports Updates
  - Added Report class as the parent of all report types
  - Added departments
  - Added sorting options
  - Added `valid_departments` to Referrals report as an optional config key
  - Added filter by departments (include/exclude)
- DataSet Updates
  - Improved filter patterns
    - Changed filter functions to modify DataSets in place
    - Added existance checking of DataSet columns before filtering / sorting
    - Changed all filtering methods to use regex
    - Added Reset index after filtering / sorting
    - Added debug logging for amount of rows filtered in filter functions
  - Added enforced use of typed DataSets and Columns
  - Separated `get_col()` and `get_col_name()` into separate functions
  - Separated DataSet types into separate files and classes (appointment, enrollment, referral, survey)
  - Added Column class to DataSet and overloaded for DataSet types
  - Moved type specific DataSet functions to the respective DataSet sub-classes

### Minor Feature Changes

- General Code Enhancements
  - Added requirements.txt
  - Removed download survey results functionality (see [HandshakeSurveyResults](https://github.com/CLDC/HandshakeSurveyResults) for this feature)
  - Unified modules and imports
  - Changed to use property attributes within classes and added type checking with .setter attributes
  - Added `__init__` files
  - Added typing hints for arguments and return types
  - Updated to follow PEP8 style guide throughout codebase
  - Updated Python version to 3.12.1
- Report Logic Refactoring
  - Refactored report-specific logic into report classes
  - Added Report class as the parent of all report types
  - Removed report type property from Report class - Now uses type checking to determine report type
  - Removed `remove_cols`, `rename_cols`, and `final_cols` from individual report classes and moved to `Report` class
  - Moved handling of save/archive to `Report` class
  - Made archive optional
- Referrals Report Updates
  - Modified `remove_duplicates` from referrals report module
    - Changed name to `remove_duplicate_referrals`
    - Updated to remove duplicate referrals as the first thing that happens in the report
    - Changed to drop duplicate referrals instead of results (since it runs first, directly modify the results)
    - Added additional remove duplicates from results after re-merging students that were referred but had no appointment
  - Removed `remove_cols`, `rename_cols`, and `final_cols` (handled in Report class)
  - Renamed `valid_appointment_pattern` to `complete_types`
  - Added existence checking for enrollment DataSet
  - Added sorting by referral date -> referred student email -> unique referral column -> appointment date -> appointment status
- Survey Results Report Updates
  - Renamed `year` to `target_years`
  - Renamed `month` to `target_months`
  - Renamed `emails` to `staff_emails`
  - Changed the type of `staff_emails` to FilterType
  - Removed `remove_cols`, `rename_cols`, and `final_cols` (handled in Report class)
  - Added type checking for `appointments` and `survey_results`
- Followup Report Updates
  - Renamed `year` to `target_years`
  - Renamed `month` to `target_months`
  - Removed `remove_cols`, `rename_cols`, and `final_cols` (handled in Report class)
  - Updated language regarding followup appointments to be general
    - Renamed `appointment_types` to `require_followup`
    - Renamed `followup_types` to `followup_appointments`
    - Renamed "date of last non `appointment_types` appointment" to "date of last followup appointment"
  - Updated `require_followup` and `followup_appointments` to FilterTypes to allow for any number of followup appointment types with include/exclude filters

### Bug Fixes

---

- Fixed filter patterns sometimes including values that should be excluded
- Fixed bug where filters were not being applied correctly
- Fixed DataSet `deep_copy()` so that it actually deep copies the DataFrame and columns
- Fixed fatal error when there are no results to save by adding results checking
- Fixed circular imports in reports modules
- Fixed error where values were attempted to be retrieved from Column Enum twice
- Fixed bugs related to inconsistent parsing of datetimes
- Fixed bugs where dataframes could not merge with series due to missing column names
- Fixed bugs where Reports were not independent of each other by deep copying the DataSets for each report
- Fixed issues where the class name for inherited classes was only being logged as the parent class name

## Version 0.1.0 (2023/12/12)

### Major Feature Changes

---

- Added example .env
- Added readme
  - Added Chromium Driver installation instructions
  - Added project description
  - Added setup instructions/steps
  - Added Reports documentation
  - Added feature checklist
  - Added environmental variable setup
- Added generic utilities
- Added file utilities
- Added DataSet class
  - Defined known columns and types
  - Added filtering functions (by email, date, status, majors, etc.)
  - Added remove numbers from columns for surveys (Handshake puts them there by default at this time)
  - Added user input if emails or dates missing
- Added Report controller
  - Added handling for each type of report
  - Added basic run/save report functions
- Added SurveyResult report
  - Added key check upon initialization
  - Added run logic to sort by date -> filter appointment status -> filter dates -> filter by staff emails -> merge appointment data with survey results -> filter time difference
- Added Followup report
  - Added run logic to filter dates -> filter followup appointments -> add latest followup column -> remove followed up -> filter most recent followup -> add past followup count
- Added Referrals report
  - Added run logic to filter valid appointments -> merge referrals with appointments -> remove past appointments -> add appointment scheduled and completed columns -> merge enrollment data -> remove duplicates
- Added Driver
- Added Config controller
  - Added FilesConfig
    - Added load files from config
  - Added ReportsConfig
    - Added load reports from FilesConfig

### Minor Feature Changes

---

- Removed download Handshake survey results - moved to independent repository
  = Changed to regex patterns for filters

* Added filter pattern from list
  = Split config into two files - reports and files config
* Added default config fallbacks (for missing keys) for each report type
* Added handling missing optional config keys as None/undefined
* Added duplicate referral handling - initially thought to be irrelevant
* Add debug logging throughout script

### Bug Fixes

---

N/A
