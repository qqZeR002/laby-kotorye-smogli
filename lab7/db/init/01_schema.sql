-- схема: одна таблица багов
CREATE TABLE bugs (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority    VARCHAR(10) NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    status      VARCHAR(15) NOT NULL DEFAULT 'open'
                CHECK (status IN ('open', 'in_progress', 'fixed', 'verified', 'closed')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_bugs_priority ON bugs (priority);
