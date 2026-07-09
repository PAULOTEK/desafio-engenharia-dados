-- sql/02_seed.sql

INSERT INTO fund (fund_code, fund_name, fund_type, administrator, manager)
VALUES
('FUND001', 'Fundo Alpha', 'Ações', 'Admin A', 'Gestor A'),
('FUND002', 'Fundo Beta', 'Multimercado', 'Admin B', 'Gestor B'),
('FUND003', 'Fundo Gamma', 'Renda Fixa', 'Admin C', 'Gestor C');

INSERT INTO issuer (issuer_name, issuer_document, sector)
VALUES
('Empresa XYZ S.A.', '12.345.678/0001-90', 'Financeiro'),
('Companhia ABC S.A.', '98.765.432/0001-10', 'Energia'),
('Grupo Delta Ltda.', '11.222.333/0001-44', 'Varejo');

INSERT INTO asset (asset_code, asset_name, asset_type, issuer_id)
VALUES
('ATV001', 'Ação XYZ', 'Ação', 1),
('ATV002', 'Debênture ABC', 'Renda Fixa', 2),
('ATV003', 'Cota FII Delta', 'FII', 3),
('ATV004', 'Tesouro IPCA', 'Título Público', 1),
('ATV005', 'CDB Banco Omega', 'CDB', 2);

INSERT INTO market_price (asset_id, reference_date, price, source)
VALUES
(1, '2026-07-01', 10.50, 'B3'),
(1, '2026-07-02', 10.75, 'B3'),
(2, '2026-07-01', 1012.33, 'ANBIMA'),
(2, '2026-07-02', 1015.12, 'ANBIMA'),
(3, '2026-07-01', 98.20, 'B3'),
(4, '2026-07-01', 1234.55, 'TESOURO'),
(5, '2026-07-01', 1000.00, 'BANCO');

INSERT INTO operation (fund_id, asset_id, operation_date, operation_type, quantity, unit_price, operation_value)
VALUES
(1, 1, '2026-07-01', 'BUY', 1000, 10.50, 10500.00),
(1, 2, '2026-07-01', 'BUY', 50, 1012.33, 50616.50),
(2, 3, '2026-07-01', 'BUY', 200, 98.20, 19640.00),
(2, 1, '2026-07-02', 'BUY', 500, 10.75, 5375.00),
(3, 4, '2026-07-01', 'BUY', 80, 1234.55, 98764.00),
(3, 5, '2026-07-02', 'BUY', 120, 1000.00, 120000.00);

INSERT INTO position (fund_id, asset_id, position_date, quantity, market_price, financial_value, nav_percentage)
VALUES
(1, 1, '2026-07-02', 1000, 10.75, 10750.00, 12.50),
(1, 2, '2026-07-02', 50, 1015.12, 50756.00, 45.00),
(2, 3, '2026-07-02', 200, 98.20, 19640.00, 18.00),
(2, 1, '2026-07-02', 500, 10.75, 5375.00, 8.25),
(3, 4, '2026-07-02', 80, 1234.55, 98764.00, 20.00),
(3, 5, '2026-07-02', 120, 1000.00, 120000.00, 25.00);

