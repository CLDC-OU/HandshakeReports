# Weekly Handshake Reports Script For the Career and Life Design Center at Oakland University

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
> are filtered by containing a string specified in the config (i.e. "Walk-In" includes all appointments that include the text "Walk-In" somewhere in the appointment name). Specific appointments to disclude can be specified as an array (i.e ["Walk-In Headshot"] would include all "Walk-In" appointments except for "Walk-In Headshot")
>
> Valid followup appointments (appointments that count as a followup) on the other hand, matches with an array of appointment names. An empty array specifies the inclusion of all appointments that aren't the same as the valid appointment type.

### Referrals Report

> [!NOTE]
>
> This report uses data collected external to Handshake. 
>
> We use a Google Apps Script to save student referrals sent by email in a Google Sheet that is downloaded (with another Apps Script) to then be accessed by this script.

Searches appointment data to merge with the referral data to add columns for whether each referred student has scheduled or completed a followup appointment. The resulting data will look something like this:

| ...[Referral Columns] | Scheduled | [Date Scheduled] | [Appointment Date] | [Appointment Type] | Completed |
|--|--|--|--|--|--|
| ... | TRUE \| FALSE | DateTime | DateTime | AppointmentTypeName | TRUE \| FALSE |

The ...Referral Columns, Date Scheduled, Appointment Date, and Appointment Type columns may be specified in config. The Scheduled and Completed columns are static.

Cancelled appointments (or appointments that were otherwise never completed) are also included in the report. These rows can be identified as rows where the Appointment Date has already passed but the appointment is not "Completed". If a new appointment is scheduled, a new row for the referral will be added. This may be repeated until one appointment is completed.

The format of the Scheduled and Completed columns are setup to be formatted as checkboxes in Google Sheets.

## Setup

> [!IMPORTANT]
> 
> 
> 



### Chromium Driver
- Download the most recent version [here](https://googlechromelabs.github.io/chrome-for-testing/). The Stable version should be good. Open the chromedriver URL for your system
- Place it in a 

```python
python -m pip install python-dotenv
python -m pip install selenium
```