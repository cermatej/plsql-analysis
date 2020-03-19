

SELECT warehouse_name warehouse,
   warehouse2."Water", warehouse2."Rail", warehouse2."Box"
   FROM warehouses,
   XMLTABLE(xmlnamespaces ('http://www.example.com/xml/path' AS "a"),
      '/Warehouse'
      PASSING warehouses.warehouse_spec
      COLUMNS 
         "Water" varchar2(6) PATH '/Warehouse/WaterAccess',
         "Rail" varchar2(6) PATH '/Warehouse/RailAccess',
         "Box" varchar2(6) PATH '/Warehouse/BoxAccess')
      warehouse2;