-- Últimos respaldos de la base configurada en la conexión.
SELECT TOP (20)
    bs.backup_finish_date AS fecha_finalizacion,
    CASE bs.type
        WHEN 'D' THEN N'Completo'
        WHEN 'I' THEN N'Diferencial'
        WHEN 'L' THEN N'Registro'
        ELSE N'Otro'
    END AS tipo,
    bs.is_copy_only AS es_copia_independiente,
    bs.is_damaged AS marcado_como_dañado,
    bs.backup_size / 1048576.0 AS tamaño_mb,
    medio.physical_device_name AS archivo
FROM msdb.dbo.backupset AS bs
OUTER APPLY (
    SELECT TOP (1) bmf.physical_device_name
    FROM msdb.dbo.backupmediafamily AS bmf
    WHERE bmf.media_set_id = bs.media_set_id
    ORDER BY bmf.family_sequence_number
) AS medio
WHERE bs.database_name = DB_NAME()
ORDER BY bs.backup_finish_date DESC;