# Weekly Handshake Reports Script For the Career and Life Design Center at Oakland University

A script that combines data collected through Handshake (https://joinhandshake.com) to generate a variable number of reports that give insight on performance of Career Services staff members, students that need a followup appointment, and referral data.

> [!NOTE]
>
> This script only generates csv files with the data of each report contained. If you need these reports in a better format (Google Sheets), that will have to be done separately.

> [!IMPORTANT]
>
> For this script to function, data files (.csv) need to be stored somewhere accessible by the script. This can be an attached network drive or Google Drive, but it must be accessible on the device running the script. To automatically download Handshake survey data, use the {ADD survey results} script. Appointments data can be automatically downloaded using a scheduled Handshake Analytics Report. Any other data (i.e. referrals) can be saved and downloaded using Google Apps Script.


### Chromium Driver
- Download the most recent version [here](https://googlechromelabs.github.io/chrome-for-testing/). The Stable version should be good. Open the chromedriver URL for your system
