# HandshakeReports - Change Log

## Version 0.2.0 (Not Released Yet)

### Major Feature Changes

---

- Added in depth config key validation methods
- Added FilterType get include / exclude helper methods
- Greatly improved date ranges
  - Added support for multiple comma separated month ranges
  - Added support for month ranges that go between two years
  - Added support for year ranges
  - Added support for multiple comma separated year ranges
  - Added support for date ranges with no end date
  - Added error handling for invalid date ranges
  - Unified date range parsing
- Greatly improved logging
- Added support for multiple month ranges
- Split config types into separate files (config.json, reports.config.json, and files.config.json)
- Refactored entire codebase to use src folder and package structure
- Added type checking throughout codebase
- Added include/exclude keys for config values that represent filters (see [FilterType](src/utils/type_utils.py))
- Added department to referrals report
  - Added valid_departments to Referrals report
  - Added filter by departments (include/exclude)
  - Added valid_departments key to reports config - loaded as FilterType
  - Made valid_departments optional
- Added sort results for referrals report
  - Sort by referral date -> referred student email -> unique referral column -> appointment date -> appointment status

### Minor Feature Changes

---

- Added requirements.txt
- Removed download survey results functionality (see [HandshakeSurveyResults](https://github.com/CLDC/HandshakeSurveyResults) for this feature)
- Unified modules and imports
- Enforce use of typed DataSets and Columns
- Follow PEP8 style guide throughout codebase
- Update Python to 3.12.1
- Improved filter patterns
- Create module for Column types and overload for dataset types
- Separated classes of dataset types into separate files (appointment, enrollment, referral, survey)
- Separated classes of config types into separate files (config.json, reports.config.json, and files.config.json)
- Separated classes of report types into separate files (followup, referrals, survey_results)
- Refactored report specific logic into report classes
- Removed report type property from Report class - Now uses type checking to determine report type
- Added extensive type checking for all config keys and values
- Remove initialization of DataSet using type
- Separate get_col() and get_col_name() into separate functions
- Changed filter functions to modify DataSets in place
- Verify existance of DataSet columns before filtering / sorting
- Reset index after filtering / sorting
- Changed to use property attributes within classes and added type checking with .setter attributes
- Made archive optional
- Renamed valid_appointment_pattern to complete_types in referrals report
- Removed remove_cols, rename_cols, and final_cols from individual report classes and moved to Report class
- Added existence checking for enrollment in referrals report (if enrollment is not provided, it will not be merged and the report will continue)
- Updated survey results report
  - Renamed year to target_years
  - Renamed month to target_months
  - Renamed emails to staff_emails
  - Changed type of staff_emails to FilterType
  - Removed remove_cols, rename_cols, and final_cols (handled in report module)
  - Added type checking for appointments and survey_results
- Inherit Report class in all report types
- Changed all filtering methods to use regex
- Separated report loading into functions
- Added \_\_init\_\_ files
- Added debug logging for amount of rows filtered in filter functions
- Added typing hints for arguments and return types
- Moved appointment-related DataSet filters to AppointmentDataSet class
- Added enforced use of the correct Column types for each DataSet type
- Removed common column module
- Added report load, run, and progress debug logging
- Allow for unknown Enum for Column functions - Because Enum do not allow for inheritance, each Column enum is defined separately in its own files, so an incomplete Enum type chec kis used for simplicity
- Renamed remove_duplicates in referrals report module to remove_duplicate_referrals
  - Updated to remove duplicate referrals as the first thing that happens in the report
  - Changed to drop duplicate referrals instead of results (since it runs first, directly modify the results)
  - Added additional remove duplicates from results after re-merging students that were referred but had no appointment

### Bug Fixes

---

- Fixed filter patterns sometimes including values that should be excluded
- Fixed bug where filters were not being applied correctly
- Fixed DataSet deep_copy so that it actually deep copies the DataFrame and columns
- Fixed fatal error when there are no results to save by adding results checking
- Fixed circular imports in reports modules
- Fixed error where values were attempted to be retrieved from Column Enum twice
- Fixed bug where datetimes were being parsed inconsistently (sometimes as strings, sometimes as datetimes) leading to errors in sorting and filtering
- Fixed bug where dataframe could not merge with series due to not having a column name
- Fixed bug where Reports were not independent of each other because the DataSets they used were not being deep copied for each report
- Fixed bug where the class name for inherited classes was only being logged as the parent class name

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
