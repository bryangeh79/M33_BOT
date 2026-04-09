# CURRENT_STATUS.md

## Current stage
Core engine operational

## Completed
- Telegram bot working
- Region selection
- Bet parsing
- Bet validation
- Bet calculation
- Database storage
- Ticket numbering
- Success response formatting

## Confirmed working examples

### MT example
```
qna 11 lo1n
qna dna 11 22 lo1n
qna 11 22 da1n
qna dna 11 22 dx1n
```

### MN example
```
tp dt 11 22 dx1n
tp 11 22 lo1n
```

## System behavior
Multiple lines in one message share the same ticket number.

### Example output
```
OK - MT T9

T9 qna 11 lo1n : 18
T9 qna 11 lo1n : 18
T9 qna 22 lo1n : 18
T9 dna 11 lo1n : 18
T9 dna 22 lo1n : 18
T9 qna 11 22 da1n : 36
T9 qna dna 11 22 dx1n : 72

Total: 198
```
