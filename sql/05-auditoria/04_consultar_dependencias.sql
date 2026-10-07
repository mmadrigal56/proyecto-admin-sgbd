SELECT 
    obj.name AS ObjectName,
    obj.type_desc AS ObjectType,
    sed.referenced_entity_name AS MissingDependency
FROM sys.sql_expression_dependencies sed
LEFT JOIN sys.objects obj ON sed.referencing_id = obj.object_id
WHERE OBJECT_ID(sed.referenced_entity_name) IS NULL 
  AND sed.is_ambiguous = 0
ORDER BY ObjectName;
