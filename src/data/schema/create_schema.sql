CREATE TABLE IF NOT EXISTS daily_counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    counter_date TEXT NOT NULL,
    region_group TEXT NOT NULL,
    last_counter INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(counter_date, region_group)
);

CREATE TABLE IF NOT EXISTS bet_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_code TEXT,
    user_id TEXT NOT NULL,
    region_group TEXT NOT NULL,
    input_date TEXT NOT NULL,
    bet_date TEXT NOT NULL,
    raw_input TEXT NOT NULL,
    line_count INTEGER NOT NULL,
    batch_total TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'accepted',
    error_message TEXT,
    deleted_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bet_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    sequence_no INTEGER NOT NULL,
    ticket_no TEXT NOT NULL,
    region_group TEXT NOT NULL,
    region_code TEXT NOT NULL,
    bet_type TEXT NOT NULL,
    number_mode TEXT NOT NULL,
    amount TEXT NOT NULL,
    input_text TEXT NOT NULL,
    total TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'accepted',
    deleted_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES bet_batches(id)
);

CREATE TABLE IF NOT EXISTS draw_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date DATE NOT NULL,
    region_code TEXT NOT NULL,
    source_name TEXT NOT NULL DEFAULT 'unknown',
    source_url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    fetched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(draw_date, region_code)
);

CREATE INDEX IF NOT EXISTS idx_draw_results_date_region
ON draw_results(draw_date, region_code);

CREATE TABLE IF NOT EXISTS draw_result_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_result_id INTEGER NOT NULL,
    sub_region_code TEXT NOT NULL,
    sub_region_name TEXT NOT NULL,
    prize_code TEXT NOT NULL,
    prize_order INTEGER NOT NULL,
    item_order INTEGER NOT NULL,
    number_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(draw_result_id) REFERENCES draw_results(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_draw_result_items_draw_result_id
ON draw_result_items(draw_result_id);

CREATE INDEX IF NOT EXISTS idx_draw_result_items_prize_code
ON draw_result_items(prize_code);

CREATE INDEX IF NOT EXISTS idx_draw_result_items_sub_region_code
ON draw_result_items(sub_region_code);

-- =========================
-- Settlement Results Table
-- =========================
CREATE TABLE IF NOT EXISTS settlement_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    bet_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    bet_type TEXT NOT NULL,

    payout REAL NOT NULL,

    win_details TEXT,  -- JSON string

    settled_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_settlement_bet_id
ON settlement_results(bet_id);