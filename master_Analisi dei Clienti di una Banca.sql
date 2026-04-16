-- ====================================================================
-- Progetto: Analisi dei clienti di una banca
-- Eduardo De Filippis
-- ====================================================================


-- ====================================================================
-- PARTE 1: Aggregazione di tutti i dati relativi ai conti per ogni cliente
-- ====================================================================
WITH conti_agg AS (
    SELECT
        c.id_cliente,
        COUNT(co.id_conto) AS num_conti_totali,
        -- conteggio dei conti per ogni tipologia
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Base' THEN co.id_conto END) AS num_conti_base,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Business' THEN co.id_conto END) AS num_conti_business,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Privati' THEN co.id_conto END) AS num_conti_privati,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Famiglie' THEN co.id_conto END) AS num_conti_famiglie
    FROM
        cliente c
    LEFT JOIN
        conto co ON c.id_cliente = co.id_cliente
    LEFT JOIN
        tipo_conto tc ON co.id_tipo_conto = tc.id_tipo_conto
    GROUP BY
        c.id_cliente
),



-- ====================================================================
-- PARTE 2: Aggregazione dei dati relativi alle transazioni (a livello di cliente). In questa parte vengono gestiti tutti i calcoli legati a importi e numero di transazioni
-- ====================================================================
transazioni_agg AS (
    SELECT
        c.id_cliente,
        -- indicatori totali
        COUNT(CASE WHEN tt.segno = '+' THEN t.id_conto END) AS num_trans_entrata_tot,
        COUNT(CASE WHEN tt.segno = '-' THEN t.id_conto END) AS num_trans_uscita_tot,
        SUM(CASE WHEN tt.segno = '+' THEN t.importo ELSE 0 END) AS importo_entrata_tot,
        SUM(CASE WHEN tt.segno = '-' THEN t.importo ELSE 0 END) AS importo_uscita_tot,
        -- indicatori per tipo conto: numero transazioni
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Base' AND tt.segno = '+' THEN t.id_conto END) AS num_trans_entrata_base,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Base' AND tt.segno = '-' THEN t.id_conto END) AS num_trans_uscita_base,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Business' AND tt.segno = '+' THEN t.id_conto END) AS num_trans_entrata_business,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Business' AND tt.segno = '-' THEN t.id_conto END) AS num_trans_uscita_business,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Privati' AND tt.segno = '+' THEN t.id_conto END) AS num_trans_entrata_privati,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Privati' AND tt.segno = '-' THEN t.id_conto END) AS num_trans_uscita_privati,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Famiglie' AND tt.segno = '+' THEN t.id_conto END) AS num_trans_entrata_famiglie,
        COUNT(CASE WHEN tc.desc_tipo_conto = 'Conto Famiglie' AND tt.segno = '-' THEN t.id_conto END) AS num_trans_uscita_famiglie,
        -- indicatori per tipo conto: importo transato
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Base' AND tt.segno = '+' THEN t.importo ELSE 0 END) AS importo_entrata_base,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Base' AND tt.segno = '-' THEN t.importo ELSE 0 END) AS importo_uscita_base,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Business' AND tt.segno = '+' THEN t.importo ELSE 0 END) AS importo_entrata_business,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Business' AND tt.segno = '-' THEN t.importo ELSE 0 END) AS importo_uscita_business,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Privati' AND tt.segno = '+' THEN t.importo ELSE 0 END) AS importo_entrata_privati,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Privati' AND tt.segno = '-' THEN t.importo ELSE 0 END) AS importo_uscita_privati,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Famiglie' AND tt.segno = '+' THEN t.importo ELSE 0 END) AS importo_entrata_famiglie,
        SUM(CASE WHEN tc.desc_tipo_conto = 'Conto Famiglie' AND tt.segno = '-' THEN t.importo ELSE 0 END) AS importo_uscita_famiglie
    FROM
        cliente c
    LEFT JOIN -- parto da cliente e uso LEFT JOIN
        conto co ON c.id_cliente = co.id_cliente
    LEFT JOIN -- per essere sicuro di non perdere nessun cliente (anche chi non ha conti o transazioni)
        transazioni t ON co.id_conto = t.id_conto
    LEFT JOIN 
        tipo_transazione tt ON t.id_tipo_trans = tt.id_tipo_transazione
    LEFT JOIN 
        tipo_conto tc ON co.id_tipo_conto = tc.id_tipo_conto
    GROUP BY
        c.id_cliente
)



-- ====================================================================
-- QUERY FINALE: mette insieme le informazioni anagrafiche, i conteggi dei conti e le aggregazioni delle transazioni
-- ====================================================================
SELECT
    c.id_cliente,
    -- indicatori di base
    TIMESTAMPDIFF(YEAR, c.data_nascita, CURDATE()) AS eta,

    -- indicatori sui conti
    COALESCE(ca.num_conti_totali, 0) AS num_conti_totali,
    COALESCE(ca.num_conti_base, 0) AS num_conti_base,
    COALESCE(ca.num_conti_business, 0) AS num_conti_business,
    COALESCE(ca.num_conti_privati, 0) AS num_conti_privati,
    COALESCE(ca.num_conti_famiglie, 0) AS num_conti_famiglie,

    -- indicatori sulle transazioni totali
    COALESCE(ta.num_trans_entrata_tot, 0) AS num_trans_entrata_tot,
    COALESCE(ta.num_trans_uscita_tot, 0) AS num_trans_uscita_tot,
    COALESCE(ta.importo_entrata_tot, 0) AS importo_entrata_tot,
    COALESCE(ta.importo_uscita_tot, 0) AS importo_uscita_tot,

    -- indicatori transazioni per tipo di conto
    -- Numero transazioni Entrata/Uscita
    COALESCE(ta.num_trans_entrata_base, 0) AS num_trans_entrata_base,
    COALESCE(ta.num_trans_uscita_base, 0) AS num_trans_uscita_base,
    COALESCE(ta.num_trans_entrata_business, 0) AS num_trans_entrata_business,
    COALESCE(ta.num_trans_uscita_business, 0) AS num_trans_uscita_business,
    COALESCE(ta.num_trans_entrata_privati, 0) AS num_trans_entrata_privati,
    COALESCE(ta.num_trans_uscita_privati, 0) AS num_trans_uscita_privati,
    COALESCE(ta.num_trans_entrata_famiglie, 0) AS num_trans_entrata_famiglie,
    COALESCE(ta.num_trans_uscita_famiglie, 0) AS num_trans_uscita_famiglie,
    -- Importo transato entrata/uscita
    COALESCE(ta.importo_entrata_base, 0) AS importo_entrata_base,
    COALESCE(ta.importo_uscita_base, 0) AS importo_uscita_base,
    COALESCE(ta.importo_entrata_business, 0) AS importo_entrata_business,
    COALESCE(ta.importo_uscita_business, 0) AS importo_uscita_business,
    COALESCE(ta.importo_entrata_privati, 0) AS importo_entrata_privati,
    COALESCE(ta.importo_uscita_privati, 0) AS importo_uscita_privati,
    COALESCE(ta.importo_entrata_famiglie, 0) AS importo_entrata_famiglie,
    COALESCE(ta.importo_uscita_famiglie, 0) AS importo_uscita_famiglie
FROM
    cliente c
LEFT JOIN
    conti_agg ca ON c.id_cliente = ca.id_cliente
LEFT JOIN
    transazioni_agg ta ON c.id_cliente = ta.id_cliente
ORDER BY
    c.id_cliente;