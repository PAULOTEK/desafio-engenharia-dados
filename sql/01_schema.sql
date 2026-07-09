-- sql/01_schema.sql

CREATE TABLE IF NOT EXISTS fund (
    fund_id        BIGSERIAL PRIMARY KEY,
    fund_code      VARCHAR(20) NOT NULL UNIQUE,
    fund_name      VARCHAR(150) NOT NULL,
    fund_type      VARCHAR(50),
    administrator  VARCHAR(150),
    manager        VARCHAR(150),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS issuer (
    issuer_id      BIGSERIAL PRIMARY KEY,
    issuer_name    VARCHAR(150) NOT NULL,
    issuer_document VARCHAR(30),
    sector         VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS asset (
    asset_id       BIGSERIAL PRIMARY KEY,
    asset_code     VARCHAR(30) NOT NULL UNIQUE,
    asset_name     VARCHAR(150) NOT NULL,
    asset_type     VARCHAR(50) NOT NULL,
    issuer_id      BIGINT NOT NULL,
    CONSTRAINT fk_asset_issuer
        FOREIGN KEY (issuer_id)
        REFERENCES issuer (issuer_id)
);

CREATE TABLE IF NOT EXISTS market_price (
    price_id        BIGSERIAL PRIMARY KEY,
    asset_id        BIGINT NOT NULL,
    reference_date  DATE NOT NULL,
    price           NUMERIC(18,6) NOT NULL,
    source          VARCHAR(100),
    CONSTRAINT fk_market_price_asset
        FOREIGN KEY (asset_id)
        REFERENCES asset (asset_id)
);

CREATE TABLE IF NOT EXISTS operation (
    operation_id    BIGSERIAL PRIMARY KEY,
    fund_id         BIGINT NOT NULL,
    asset_id        BIGINT NOT NULL,
    operation_date  DATE NOT NULL,
    operation_type  VARCHAR(20) NOT NULL,
    quantity        NUMERIC(18,6) NOT NULL,
    unit_price      NUMERIC(18,6) NOT NULL,
    operation_value NUMERIC(18,6) NOT NULL,
    CONSTRAINT fk_operation_fund
        FOREIGN KEY (fund_id)
        REFERENCES fund (fund_id),
    CONSTRAINT fk_operation_asset
        FOREIGN KEY (asset_id)
        REFERENCES asset (asset_id)
);

CREATE TABLE IF NOT EXISTS position (
    position_id     BIGSERIAL PRIMARY KEY,
    fund_id         BIGINT NOT NULL,
    asset_id        BIGINT NOT NULL,
    position_date   DATE NOT NULL,
    quantity        NUMERIC(18,6) NOT NULL,
    market_price    NUMERIC(18,6) NOT NULL,
    financial_value NUMERIC(18,6) NOT NULL,
    nav_percentage  NUMERIC(10,6) NOT NULL,
    CONSTRAINT fk_position_fund
        FOREIGN KEY (fund_id)
        REFERENCES fund (fund_id),
    CONSTRAINT fk_position_asset
        FOREIGN KEY (asset_id)
        REFERENCES asset (asset_id)
);

CREATE INDEX IF NOT EXISTS idx_position_date ON position (position_date);
CREATE INDEX IF NOT EXISTS idx_operation_date ON operation (operation_date);
CREATE INDEX IF NOT EXISTS idx_market_price_date ON market_price (reference_date);
