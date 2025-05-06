# Clalit Appointments Checker

## Overview

This project automates the process of checking available doctor appointments on the Clalit Health Services website. The script logs into the Clalit portal, searches for available doctor appointments for the next 30 days, and sends an SMS alert if any appointments are found. It also saves the available appointments data to an AWS S3 bucket.

## Features

- Logs into the Clalit website using a user ID and birth year.
- Searches for available appointments with a specific doctor in a given city.
- Selects a medical specialization from a dropdown.
- Finds appointments available within the next 30 days.
- Sends an SMS notification with the appointment details via AWS SNS.
- Saves appointment data to AWS S3 in JSON format.

## Prerequisites

To run this script, you will need:

- Python 3.x
- Selenium WebDriver
- ChromeDriver (version matching your installed Chrome)
- AWS account with access to SNS and S3 services
- `boto3` AWS SDK for Python
- The `selenium` package

## Setup

1. **Install required dependencies**:
   ```bash
   pip install selenium boto3
