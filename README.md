# ContactCard Maker

**Effortless CSV to vCard for iOS & macOS Contacts**

A simple desktop app built with Python and Tkinter to convert CSV contact files into vCard (.vcf) files compatible with Apple Contacts on iOS and macOS. Supports field mapping, single or bulk vCard export, and photo embedding via URL.

---

## Features

- Load any CSV file with contact data
- Map CSV columns to vCard fields using dropdown menus
- Export either one vCard per contact or a single combined vCard file
- Embed photos from URLs in the vCard
- Download a sample CSV template to get started quickly
- Simple GUI interface with helpful tooltips and status updates

---

## Requirements

- Python 3.7+
- requests

## Clone or download this repository.

- Install the required packages:

  > pip install requests

### Run the application:

python csv_to_vcard.py

## Notes:
- The app provides a sample CSV template.
- Ensure your CSV has headers.
- First Name and Last Name mapping are mandatory.
- Photo URLs should point to accessible JPEG images.
- Export folder must be writable.
