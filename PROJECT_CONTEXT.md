# M33 Lotto Bot – Project Context

This document describes the current development state of the M33 Lotto Bot project so future coding sessions do not lose context.

## Tech Stack

Language:
Python

Telegram Framework:
python-telegram-bot

Database:
SQLite

Project Entry:
src/app/main.py

Environment:
.env file containing BOT_TOKEN

--------------------------------------

# Current System Architecture

src/
 ├─ app/
 │ └─ main.py
 │
 ├─ modules/
 │ ├─ bet/
 │ ├─ result/
 │ └─ report/ (next module to build)
 │
 └─ bot/
 └─ menus/

--------------------------------------

# Module Status

## 1 Bet Module (COMPLETED)

Location:
src/modules/bet/

Purpose:
Handle all user betting input.

Features implemented:

bet_message_parser
bet_message_validator
bet_total_calculator
bet_success_formatter
bet_error_formatter
daily_counter_repository

Bet messages can already be processed correctly.

Bet module must NOT be modified when adding new modules.

--------------------------------------

## 2 Result Module (COMPLETED)

Location:
src/modules/result/

Purpose:
Fetch official lottery results and store them in database.

Data source:

MN
https://xosodaiphat.com/xsmn-xo-so-mien-nam.html

MT
https://xosodaiphat.com/xsmt-xo-so-mien-trung.html

MB
https://xosodaiphat.com/xsmb-xo-so-mien-bac.html

Architecture:

constants/
providers/
parsers/
repositories/
services/
formatters/

Features:

HTML scraping using httpx
Parsing using BeautifulSoup
Region support MN MT MB
SQLite storage
Telegram result display
Refresh support
Cache logic implemented

Database tables used:

draw_results
draw_result_items

Result module is fully working.

--------------------------------------

# Current Telegram Menu

Main Menu Buttons

Bet
Report
Result
Other Day Input
Admin
Info

--------------------------------------

# Next Module To Build

Report Module

Location:

src/modules/report/

Purpose:

Generate daily betting reports for the operator.

Report must summarize betting activity.

--------------------------------------

# Report Requirements

User presses:

Report

Bot should return report data including:

MN

2C
3C
4C
LO
DA
TR
Total Bet
Total Payout
Profit / Loss

MT

same structure

MB

same structure

TC

Total Calculation across all regions.

--------------------------------------

# Report Module Architecture Plan

src/modules/report/

repositories/
report_repository.py

services/
report_service.py

calculators/
report_calculator.py

formatters/
report_formatter.py

--------------------------------------

# Important Development Rules

DO NOT MODIFY:

src/modules/bet/
src/modules/result/

New modules must be isolated.

main.py should only receive minimal integration.

--------------------------------------

End of document.

--------------------------------------
