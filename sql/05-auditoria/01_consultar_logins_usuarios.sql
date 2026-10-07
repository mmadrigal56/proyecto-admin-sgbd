SELECT 
    principal_id,
    name AS LoginName,
    type_desc AS LoginType,
    is_disabled AS IsDisabled,
    create_date AS CreateDate
FROM sys.server_principals
WHERE type IN ('S', 'U', 'G') AND name NOT LIKE '##%##'
ORDER BY name;

SELECT 
    principal_id,
    name AS UserName,
    type_desc AS UserType,
    authentication_type_desc AS AuthType,
    create_date AS CreateDate
FROM sys.database_principals
WHERE type IN ('S', 'U', 'G')
ORDER BY name;
