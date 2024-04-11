# Test_task_for_jooble
___
## Overview
Python script for parsing ads on a [Residental: For Rent](https://realtylink.org/en/properties~for-rent). And saving data in json.

## Table of Contents
- [Features](#features)
- [Installation Git](#installation)

---
### Features:
The Library Service Project incorporates a range of features to efficiently manage library operations and provide a seamless experience for users. Here are some key features:

1. **Utils:**
   - Module for data storage util.
   - A configuration module for logging.
   - Custom context manager module for Selenium.

2. **Scrapers:**
   - properties_links is used by Selenium.
   - property_detail uses asyncio, httpx, BeautifulSoup

3. **Data:**
   - Storing data in json in the data package.
   - Storing log file in the data package.
---
## Installation

1. Python 3.x must be installed.

2. Clone the repository:

   ```
   https://github.com/bezhevets/Test_task_for_jooble.git
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:

   - On macOS and Linux:
   ```source venv/bin/activate```
   - On Windows:
   ```venv\Scripts\activate```
5. Install project dependencie:
   ```
    pip install -r requirements.txt
   ```
6. Run the script using the following command::
    ```
   python main.py
    ```
---
**IMPORTANT**: The result is saved in json in the data folder.
