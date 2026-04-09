# ENGINE_RULES.md

## Regions Supported
- MN
- MT
- MB

## Order of Syntax
Region → Number → BetType

Examples:
- `tp 11 lo1n`
- `tp 11 22 lo1n`
- `tp dn 11 22 lo1n`

## Supported Bet Types
- LO
- DD
- XC
- DA
- DX

## Multipliers

### LO
- 2 digits = 18
- 3 digits = 17
- 4 digits = 16

### DD
- 2 digits only
- multiplier = 2

### XC
- 3 digits or 4 digits
- multiplier = 2

## DA Rules

### MN / MT
- 2 numbers = 36
- 3 numbers = combinations × 36
- 4 numbers = combinations × 36

### MB
- 2 numbers = 54

## DX Rules
- Allowed only for MN / MT
- DX = cross region pair calculation

Example:
- `qna dna 11 22 dx1n`
