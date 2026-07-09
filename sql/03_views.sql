-- sql/03_views.sql

CREATE OR REPLACE VIEW vw_position_detail AS
SELECT
    p.position_id,
    p.position_date,
    f.fund_code,
    f.fund_name,
    f.fund_type,
    a.asset_code,
    a.asset_name,
    a.asset_type,
    i.issuer_name,
    i.sector,
    p.quantity,
    p.market_price,
    p.financial_value,
    p.nav_percentage
FROM position p
JOIN fund f
    ON p.fund_id = f.fund_id
JOIN asset a
    ON p.asset_id = a.asset_id
JOIN issuer i
    ON a.issuer_id = i.issuer_id;

CREATE OR REPLACE VIEW vw_operation_detail AS
SELECT
    o.operation_id,
    o.operation_date,
    f.fund_code,
    f.fund_name,
    a.asset_code,
    a.asset_name,
    o.operation_type,
    o.quantity,
    o.unit_price,
    o.operation_value
FROM operation o
JOIN fund f
    ON o.fund_id = f.fund_id
JOIN asset a
    ON o.asset_id = a.asset_id;

CREATE OR REPLACE VIEW vw_market_price_latest AS
SELECT DISTINCT ON (mp.asset_id)
    mp.asset_id,
    a.asset_code,
    a.asset_name,
    mp.reference_date,
    mp.price,
    mp.source
FROM market_price mp
JOIN asset a
    ON mp.asset_id = a.asset_id
ORDER BY mp.asset_id, mp.reference_date DESC;
