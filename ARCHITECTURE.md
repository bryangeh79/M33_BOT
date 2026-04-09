# ARCHITECTURE.md

## System Pipeline

Telegram Message  
↓  
`src/app/main.py`  
↓  
`process_bet_message()` (within service orchestration)  
↓  
`parse_bet_message()`  
↓  
`validate_bet()`  
↓  
`calculate_total()`  
↓  
`reserve_ticket_numbers()`  
↓  
SQLite storage  
↓  
`format_success_response()`

## Design Principles
- 1 message block = 1 ticket number
- Multiple lines in a single message belong to the same ticket (batch)
- Each parsed bet becomes a `bet_item` in database
- Strict validation: any invalid line causes the whole batch to fail (no ticket reserved, no partial writes)
- Decimal-safe calculations (avoid floating point rounding errors in monetary paths)
- Separation of concerns: parser / validator / calculator / formatter / repository / service

## Key Modules and Locations
- Bot entry: `src/app/main.py`
- Service coordinator: `src/modules/bet/services/bet_message_service.py`
- Parser: `src/modules/bet/parsers/bet_message_parser.py`
- Validator: `src/modules/bet/validators/bet_message_validator.py`
- Calculator: `src/modules/bet/calculators/bet_total_calculator.py`
- Formatter: `src/modules/bet/formatters/`
- Repository: `src/modules/bet/repositories/`
- SQLite schema: `src/data/schema/create_schema.sql`

---

## SYSTEM ENTRY POINTS

### Main application entry
`src/app/main.py`

Responsible for:
- Starting the Telegram bot
- Handling commands
- Handling region selection
- Passing bet text into the engine

### Main engine service
`src/modules/bet/services/bet_message_service.py`

Responsible for:
- Processing full bet messages
- Coordinating parser, validator, calculator
- Reserving ticket numbers
- Writing bets into SQLite database
- Generating formatted responses

### Parser module
`src/modules/bet/parsers/bet_message_parser.py`

Responsible for:
- Parsing raw betting text
- Supporting multi-line messages
- Expanding region × number combinations
- Supporting LO / DD / XC / DA / DX

### Validator module
`src/modules/bet/validators/bet_message_validator.py`

Responsible for:
- Validating bet structure
- Validating number length
- Validating region codes
- Applying region specific rules

### Calculator module
`src/modules/bet/calculators/bet_total_calculator.py`

Responsible for:
- Applying multipliers
- Calculating bet totals
- DA combination calculations
- DX calculations

### Database schema entry
`src/data/schema/create_schema.sql`

Defines:
- bet_batches
- bet_items
- ticket counters

### Ticket counter repository
`src/modules/bet/repositories/daily_counter_repository.py`

Responsible for:
- Generating ticket numbers
- Maintaining daily sequence counters
