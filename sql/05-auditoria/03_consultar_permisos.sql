SELECT 
    dp.class_desc AS ObjectType,
    OBJECT_NAME(dp.major_id) AS ObjectName,
    dp.permission_name AS Permission,
    dp.state_desc AS State,
    pr.name AS GranteeName,
    pr.type_desc AS GranteeType
FROM sys.database_permissions dp
JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
WHERE dp.major_id >= 0
ORDER BY GranteeName, ObjectName;
