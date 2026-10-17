# Learn2Earn — README

A small command-line inventory and loan-management system for a program where fellows can borrow shared resources (equipment) from a common pool.
Table of Contents

    Overview

    Features

    Requirements

    Installation

    Quick Start

    Usage — Menu Options

    Data Model

    Persistence

    Running the Demonstration

    Example Walkthrough

    Rules & Validation

    Resetting the Data

    Project Structure

    Troubleshooting

    Limitations & Possible Extensions

    License

## Overview

Learn2Earn is a lightweight Python program that lets an administrator:

    Track a catalog of resources (laptops, keyboards, headsets, etc.)

    Register fellows (the people who can borrow)

    Lend resources to fellows and receive them back

    Search and filter the catalog

    Generate an inventory report (totals, low stock, most-borrowed items)

    Persist everything to a JSON file between runs

It runs entirely in the terminal — no web server, no database, no external dependencies.
Features
Feature	Description
 1. Resource management	Add and list resources with ID, name, category, total units, and available units.
 2. Fellow management	Register and list fellows who are allowed to borrow.
 3. Borrowing	Lend a quantity of a resource to a fellow, with full validation.
 4. Returning	Return units back to the pool; supports returns spread across multiple loan records.
 5. Search	Case-insensitive substring search by resource name.
 6. Filter	Case-insensitive exact filter by category.
 7. Reporting	Inventory totals, low-stock alerts, and current most-borrowed resources.
 8. Persistence	Auto-loads on start, auto-saves on exit to learn2earn_data.json.
 9. Demo mode	A built-in demonstration runs through happy paths and rejection cases.

## Requirements

    Python 3.7+ (uses f-strings and standard library only)

    No third-party packages required

## Installation

    Save the program as learn2earn.py.

    Ensure Python 3 is installed:
    bash

    python3 --version

That's it — there are no dependencies to install.
Quick Start
bash

python3 learn2earn.py

You'll see the main menu:
text

===== Learn2Earn Menu =====
1. List resources
2. Add resource
3. Borrow resource
4. Return resource
5. Search by name
6. Filter by category
7. Generate report
8. Run demonstration (steps 1-7)
9. List fellows
10. Add fellow
0. Exit

Type a number and press Enter. On exit (option 0), your changes are saved automatically.
Usage — Menu Options
1 — List resources

Prints the full inventory as a formatted table:
text

ID    Name           Category       Total   Available
------------------------------------------------------
R001  Laptop         Electronics    10      8
R002  Keyboard       Accessories    5       2
R003  Headset        Accessories    3       3

2 — Add resource

Prompts for Resource ID, Name, Category, and Total units.

    IDs must be unique.

    Total units must be a positive integer.

    New resources start with available = total.

3 — Borrow resource

Prompts for Fellow ID, Resource ID, and Quantity.

The borrow is rejected if:

    The fellow ID is not registered.

    The resource ID does not exist.

    The quantity is not a positive integer.

    Not enough units are currently available.

4 — Return resource

Prompts for Fellow ID, Resource ID, and Quantity.

The return is rejected if:

    The fellow or resource does not exist.

    The quantity is not a positive integer.

    The fellow is trying to return more than they currently have on loan.

5 — Search by name

Case-insensitive substring search on resource names. Searching laptop finds Laptop.
6 — Filter by category

Case-insensitive exact match on category. Filtering Accessories returns all accessories.
7 — Generate report

Prints:
text

===== INVENTORY REPORT =====
Total units       : 18
Available units   : 13
Borrowed units    : 5

Low stock (< 3 available):
  Keyboard: 2 available

Most borrowed resource(s) currently out on loan:
  Keyboard: 3 unit(s)

8 — Run demonstration

Runs a scripted set of operations exercising both success and rejection paths. Useful for quickly verifying the program works.
9 — List fellows

Prints all registered fellows:
text

ID    Name
--------------------------
F001  Ada
F002  John
F003  Grace

10 — Add fellow

Registers a new fellow. IDs must be unique; names cannot be empty.
0 — Exit

Saves data automatically to learn2earn_data.json and quits.
Data Model
Resource
json

{
  "id": "R001",
  "name": "Laptop",
  "category": "Electronics",
  "total": 10,
  "available": 8
}

Invariant: available = total − (sum of currently-borrowed quantities for this resource).
Fellow

A simple id → name mapping, e.g. {"F001": "Ada", "F002": "John"}.
Borrow record
json

{
  "fellow_id": "F001",
  "resource_id": "R001",
  "quantity": 2
}

Multiple records for the same fellow_id + resource_id are allowed (e.g., borrowed on two different days). Returns reduce across these records and delete any that reach zero quantity.
Persistence

    File: learn2earn_data.json (in the current working directory)

    When it loads: once, when main() starts

    When it saves: when you choose option 0 (Exit)

    Fields saved: resources, fellows, borrow_records

If the file is missing or corrupt, the program starts with the default seed data and prints a warning if relevant.

Sharing / backup: the JSON file is human-readable and can be copied, versioned, or edited by hand (though careful — if you edit, keep the invariant available = total − borrowed intact).
Running the Demonstration
bash

python3 learn2earn.py
# then choose option 8

The demo performs:

    Ada (F001) borrows 2 laptops → success

    John (F002) borrows 3 keyboards → success

    Ada returns 1 laptop → success

    Grace (F003) requests 4 headsets (only 3 exist) → rejected

    John tries to return 4 keyboards (only 3 on loan) → rejected

    Case-insensitive search for "LAPtop" → finds Laptop

    Inventory report printed

The demo operates on current in-memory state. To run it on a clean slate, delete learn2earn_data.json first (see below).
Example Walkthrough

A typical session:
text

Choose an option: 10
Fellow ID: F004
Fellow name: Kemi
Added fellow Kemi (F004).

Choose an option: 3
Fellow ID: F004
Resource ID: R001
Quantity: 1
Kemi borrowed 1 x Laptop.
Available Laptop units = 7.

Choose an option: 4
Fellow ID: F004
Resource ID: R001
Quantity: 1
Kemi returned 1 x Laptop.
Available Laptop units = 8.

Choose an option: 0
Data saved to learn2earn_data.json.
Goodbye!

## Rules & Validation

    IDs must be non-empty and unique within their type (resource IDs unique, fellow IDs unique).

    Quantities must be positive integers. Booleans (True/False) are explicitly rejected to avoid the Python gotcha where isinstance(True, int) is True.

    Borrowing is blocked if there isn't enough stock.

    Returning is blocked if the fellow isn't holding that many units.

    Empty names are rejected for resources and fellows.

    Empty categories default to Uncategorized.

    All operations validate first, mutate later — a failed operation leaves state completely unchanged.

Resetting the Data

To restore the original seed data:
bash

rm learn2earn_data.json

The next launch will use the built-in defaults:

    Resources: R001 Laptop (10), R002 Keyboard (5), R003 Headset (3)

    Fellows: F001 Ada, F002 John, F003 Grace

    Borrow records: empty

## Project Structure

The single-file program is organized into clearly labeled sections:
text

learn2earn.py
├── Persistence           → save_data(), load_data()
├── Default data          → DEFAULT_RESOURCES, DEFAULT_FELLOWS + working copies
├── Helpers               → find_resource, find_fellow, get_borrowed,
│                           add_fellow, list_fellows
├── Resource operations   → add_resource, list_resources
├── Borrowing             → borrow_resource
├── Returning             → return_resource
├── Search & filter       → search_by_name, filter_by_category
├── Reporting             → generate_report
├── Menu & input          → print_menu, get_positive_int, main
└── Demo                  → run_demonstration

## Troubleshooting
Symptom	Cause	Fix
Data loaded... never appears	No JSON file yet	Normal on first run; will appear after first exit
Warning: could not load ...	Corrupt or malformed JSON	Delete learn2earn_data.json to reset
"Fellow ID not found" when borrowing	You haven't registered them	Use option 10 first
Can't add a resource	ID already exists	Pick a new resource ID
Report says "No borrowing activity yet"	No outstanding loans	Either all loans were returned, or none were made
Changing the JSON by hand broke availability	Edited available/total inconsistently	Reset by deleting the file
Limitations & Possible Extensions

Current limitations

    All state lives in module-level globals — fine for a CLI, not ideal for testing or embedding.

    No concurrency protection (single-user CLI by design).

    No historical/audit log — returned records are deleted rather than archived.

    Category matching is exact (not fuzzy).

    Case-sensitivity is only handled for search and filter, not for IDs.

Ideas for extension

    Add a loan history (append-only log) instead of deleting returned records.

    Track due dates and flag overdue loans.

    Add fellow roles/permissions (e.g., admins can add resources; fellows cannot).

    Export the report to CSV or PDF.

    Add a --demo CLI flag to run the demo without the menu.

    Migrate to SQLite for reliability at scale.

    Wrap the state in a class (Learn2Earn) to make unit testing straightforward.

    Add unit tests with pytest for all validation paths.

## License

This is a teaching/demo project. Use it freely; adapt as needed. If you redistribute it, keep this README with the code.
