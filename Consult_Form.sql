SELECT 
    `ID`,
    `VERSAO`,
    `CRIACAO FORM`,
    `EDICAO FORM`,
    `DESCRICAO FORM`,
    `C CUSTO`,
    `SECAO`,
    `NOME FORM`,
    `ENCARREGADO`,
    `ENGENHEIRO`,
    `RH LOCAL`,
    `SUPERINTENDENTE`,
    `DIRETOR`,
    `CONT MANUT`,
    `GRUPO USUARIOS`
FROM (
    SELECT 
        documentid AS `ID`,
        version AS `VERSAO`,
        data_create_form AS `CRIACAO FORM`,
        data_edit_form AS `EDICAO FORM`,
        descriForm AS `DESCRICAO FORM`,
        S0_txt_ccusto AS `C CUSTO`,
        S0_txt_cod AS `SECAO`,
        S0_txt_desc AS `NOME FORM`,
        S0_txt_enca AS `ENCARREGADO`,
        S0_txt_eng AS `ENGENHEIRO`,
        S0_txt_rh AS `RH LOCAL`,
        S0_txt_cordeng AS `SUPERINTENDENTE`,
        S0_txt_dire AS `DIRETOR`,
        S0_txt_controlador AS `CONT MANUT`,
        S0_txt_grupo_user AS `GRUPO USUARIOS`,
        ROW_NUMBER() OVER (PARTITION BY S0_txt_ccusto ORDER BY version DESC) AS ranking
    FROM ML1010_APROVADOR_SECAO
    WHERE documentid > 42241 
      AND documentid <> 45613
      AND documentid <> 42893
      AND documentid <> 42299
      AND documentid <> 42293
      AND documentid <> 42295
) AS consulta_rankeada
WHERE ranking = 1;