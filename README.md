# Handshake Reports Script For the Career and Life Design Center at Oakland University

A script that combines data collected through Handshake (https://joinhandshake.com) to generate a variable number of reports that give insight on performance of Career Services staff members, students that need a followup appointment, and referral data.

> [!NOTE]
>
> This script only generates csv files with the data of each report contained. If you need these reports in a better format (Google Sheets), that will have to be done separately.

> [!IMPORTANT]
>
> For this script to function, data files (.csv) need to be stored somewhere accessible by the script. This can be an attached network drive or Google Drive, but it must be accessible on the device running the script. To automatically download Handshake survey data, use the {ADD survey results} script. Appointments data can be automatically downloaded using a scheduled Handshake Analytics Report. Any other data (i.e. referrals) can be saved and downloaded using Google Apps Script.

See [Setup](#setup) for the necessary setup for these scripts to run automatically.

## Features

This script can currently create 3 different types of reports based on a user-defined config file.

- [x] Report survey results by staff member
- [x] Report students that need a followup appointment
- [x] Report referrals with merged followup appointment data
- [x] Fully configurable reports
  - [x] Filter one or more months and by year
  - [ ] Filter a range of followup appointments
- [x] Variable number of files to run reports on
- [x] Variable number of reports
- [x] Creates csv files in variable locations for each report
- [x] Support for archiving report with all columns, but saving a report with specific columns
- [ ] Automatically download Handshake survey results
- [ ] Download multiple survey results
- [ ] Configurable survey results by school
- [ ] Support for both institutional and non-institutional Handshake logins

### Survey Results Report

Combines Handshake survey response data with appointments data to link each survey response to the staff member that the appointment was with.

The purpose of this report is to easily see which staff member each response refers to so that staff members can gauge their performance or the performance of the staff members they are supervising.

> [!IMPORTANT]
>
> **The results of this report are an approximation of the true report data!** There may be inconsistencies.
>
> Since Handshake does not include an appointment ID (or any other identifier) with survey responses that were filled out through post appointment survey links, the script tries to associate each survey response with an appointment using the student's email address and completion dates. This may identify incorrect appointments if a student had multiple appointments in a short period of time (defined in the config).

Reports can be filtered by months, year, and staff member email addresses

### Followup Report

Searches appointments data to find students that had a specific appointment type and have not yet scheduled a defined "followup" appointment. Any followup appointment scheduled after the appointment that needs a followup counts as being followed up. Followup appointments scheduled for a date before the appointment that needs a followup do not count towards being followed up, but will be recorded in the report as a note.

This report can be filtered by months, year, student college/school (e.g. College of Arts and Sciences), valid appointment type, and valid followup appointment types.

> [!IMPORTANT]
>
> Valid appointment types (the appointments that students need a followup after)
> are filtered by containing a string specified in the config (e.g., "Walk-In" includes all appointments that include the text "Walk-In" somewhere in the appointment name). Specific appointments to disclude can be specified as an array (e.g., ["Walk-In Headshot"] would include all "Walk-In" appointments except for "Walk-In Headshot")
>
> Valid followup appointments (appointments that count as a followup) on the other hand, matches with an array of appointment names. An empty array specifies the inclusion of all appointments that aren't the same as the valid appointment type.

### Referrals Report

> [!NOTE]
>
> This report uses data collected external to Handshake.
>
> We use a Google Apps Script to save student referrals sent by email in a Google Sheet that is downloaded (with another Apps Script) to then be accessed by this script.

Searches appointment data to merge with the referral data to add columns for whether each referred student has scheduled or completed a followup appointment. The resulting data will look something like this:

| ...[Referral Columns] | Scheduled     | [Date Scheduled] | [Appointment Date] | [Appointment Type]  | Completed     |
| --------------------- | ------------- | ---------------- | ------------------ | ------------------- | ------------- |
| ...                   | TRUE \| FALSE | DateTime         | DateTime           | AppointmentTypeName | TRUE \| FALSE |

The ...Referral Columns, Date Scheduled, Appointment Date, and Appointment Type columns may be specified in config. The Scheduled and Completed columns are static.

Cancelled appointments (or appointments that were otherwise never completed) are also included in the report. These rows can be identified as rows where the Appointment Date has already passed but the appointment is not "Completed". If a new appointment is scheduled, a new row for the referral will be added. This may be repeated until one appointment is completed.

The format of the Scheduled and Completed columns are formatted in such a way that they can be checkboxes in Google Sheets.

## Setup

1. Ensure all [dependencies](#dependencies) are configured and running properly
2. Clone the repository
   - If installing from github, use `-git clone https://github.com/CLDC-OU/HandshakeReports.git`
3. Configure the [Environmental Variables](#environmental-variables)
4. Configure [Files](#configuring-files)
5. Configure [Reports](#configuring-reports)
6. Run main.py

> [!IMPORTANT]

## Dependencies

### Chromium Driver

- Download the most recent version [here](https://googlechromelabs.github.io/chrome-for-testing/). The Stable version should be good. Open the chromedriver URL for your system
- Place it in a

```python
python -m pip install python-dotenv
python -m pip install selenium
```

## Environmental Variables

> [!NOTE]
>
> Environmental variables are only needed in order to download survey results from Handshake. If you are not using this feature, this step is not necessary.

It is recommended that you create a dedicated Handshake account using an extra email address to access the survey results. Make sure to setup this Handshake account as a Career Services staff member with the "Surveys" Role.

1. Create a file called ".env" in the root of the project directory.
2. Add the following environmental variables (see an example in [example.env](example.env)):
   - `HS_USERNAME` - The username of the Handshake account that will be downloading the survey results
   - `HS_PASSWORD` - The password of the Handshake account that will be downloading the survey results
   - (optional) `INSTITUTIONAL_EMAIL` - TRUE if `HS_USERNAME` refers to an institutional email address (e.g. oakland.edu). FALSE or omitted otherwise.

## Configuring Files

Files are configured in [files.config.json](files.config.json). Create this file in the root of the project directory.

## Configuring Reports

Reports are configured in [reports.config.json](reports.config.json). Create this file in the root of the project directory.

