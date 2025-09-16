PLOS ONE Data Extraction Tool
A set of Python scripts for automated data extraction from the PLOS ONE academic journal website. This tool collects key information including articles, author contributions, peer reviews, and article view counts, with support for storing data in a MySQL database.

GitHub Repository: https://github.com/Zihao10086/Plos_one_data_extract.git

Overview
This project consists of three core Python scripts that work together to complete the entire process from data request, parsing, processing to storage. It is suitable for academic research, data analysis, journal studies, and other scenarios requiring bulk collection of PLOS ONE metadata.

Project Structure
text
Plos_one_data_extract/
├── plos_one_data_extract.py  # Main extraction script
├── MyMySQL.py                # Database operations module
├── util.py                   # Utility functions
└── README.md                 # Project documentation
Core Files Description
plos_one_data_extract.py

The main script of the project.

Contains extraction methods for different data types, organized in a step-by-step approach with one method per step:

article: Article metadata (title, abstract, publication date, keywords, etc.)

author contribution: Author information and their contributions

peer_review: Peer review history and comments

article view count: Article metrics (views, downloads, citations, etc.)

Contains the main program logic, such as iterating through article IDs and calling functions from other modules.

MyMySQL.py

A wrapper module for MySQL database operations (using mysql-connector-python or similar libraries).

Provides common database operations:

Connecting to and disconnecting from the database

Executing SQL statements (INSERT, SELECT, UPDATE, etc.)

Error handling and connection pool management (if implemented)

Enables cleaner and more secure interaction with MySQL database from the main script.

util.py

Contains common utility functions for the project.

Includes functionality such as:

HTTP request methods (using requests library with error handling)

MD5 encryption methods

Dynamic IP acquisition methods (proxy rotation)

Data cleaning and formatting functions

Logging configuration

Prerequisites
To run this project, you need to install the following Python libraries:

requests - For sending HTTP requests

beautifulsoup4 - For parsing HTML content

mysql-connector-python or pymysql - For connecting to MySQL database

You can install all dependencies using pip:

bash
pip install requests beautifulsoup4 mysql-connector-python
Installation & Usage
Clone the repository

bash
git clone https://github.com/Zihao10086/Plos_one_data_extract.git
cd Plos_one_data_extract
Database Setup

Create a new database on your MySQL server.

Set up the required tables according to the schema used in plos_one_data_extract.py.

Modify the database connection configuration in MyMySQL.py with your own credentials:

python
# Example configuration
config = {
  'user': 'your_username',
  'password': 'your_password',
  'host': 'localhost',
  'database': 'your_database_name',
  'raise_on_warnings': True
}
Run the script

Execute the main script to start data collection:

bash
python plos_one_data_extract.py
Features
Step-by-step extraction: Each data type is extracted using separate methods in a logical sequence

Robust database operations: Comprehensive MySQL wrapper for reliable data storage

Advanced utilities: Includes HTTP request handling, MD5 encryption, and dynamic IP rotation

Error handling: Built-in mechanisms to handle network issues and website changes

Important Notes
Respectful Scraping: Before using this script to scrape PLOS ONE data, please read and comply with their robots.txt file and terms of service. Ensure your scraping activities are compliant and implement appropriate request intervals to avoid overwhelming the target server.

Code Maintenance: Website structures may change over time, which could break the parsing logic. If you encounter issues, check and adjust the parsing code in plos_one_data_extract.py.

Error Handling: While the script includes some error handling mechanisms (such as network retries), monitoring logs during extended runs is recommended to ensure data completeness.

Disclaimer
This project is developed for technical exchange and academic research purposes only. The developers are not responsible for any issues or consequences that may arise from using this tool. Users must ensure their data collection activities comply with relevant laws, regulations, and website policies.

