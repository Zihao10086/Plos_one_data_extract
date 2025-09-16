# PLOS ONE Data Extraction Tool

A set of Python scripts for automated data extraction from the **PLOS ONE** academic journal website. This tool collects key information including articles, author contributions, peer reviews, and article view counts, with support for storing data in a MySQL database.

**GitHub Repository:** [https://github.com/Zihao10086/Plos_one_data_extract.git](https://github.com/Zihao10086/Plos_one_data_extract.git)

## Overview

This project consists of three core Python scripts that work together to complete the entire process from data request, parsing, processing to storage. It is suitable for academic research, data analysis, journal studies, and other scenarios requiring bulk collection of PLOS ONE metadata.

## Project Structure
Plos_one_data_extract/

├── plos_one_data_extract.py # Main extraction script

├── MyMySQL.py # Database operations module

├── util.py # Utility functions

└── README.md # Project documentation

text

### Core Files Description

1.  **`plos_one_data_extract.py`**
    *   The main script of the project.
    *   Contains extraction methods for different data types, organized in a step-by-step approach with one method per step:
        *   `article`: Article metadata (title, abstract, publication date, keywords, etc.)
        *   `author contribution`: Author information and their contributions
        *   `peer_review`: Peer review history and comments
        *   `article view count`: Article metrics (views, downloads, citations, etc.)
    *   Contains the main program logic, such as iterating through article IDs and calling functions from other modules.

2.  **`MyMySQL.py`**
    *   A wrapper module for MySQL database operations (using `mysql-connector-python` or similar libraries).
    *   Provides common database operations:
        *   Connecting to and disconnecting from the database
        *   Executing SQL statements (INSERT, SELECT, UPDATE, etc.)
        *   Error handling and connection pool management (if implemented)
    *   Enables cleaner and more secure interaction with MySQL database from the main script.

3.  **`util.py`**
    *   Contains common utility functions for the project.
    *   Includes functionality such as:
        *   HTTP request methods (using `requests` library with error handling)
        *   MD5 encryption methods
        *   Dynamic IP acquisition methods (proxy rotation)
