{%- for group in groups -%}
{%- for table in group.tables -%}
DROP TABLE IF EXISTS {{group.user}}.{{table.table}};
CREATE TABLE {{group.user}}.{{table.table}} (
  {%- for field in table.fields %}
    {% if loop.index > 1 %},{% endif %}{{field.field}} {{field.type}} {% if field.comment %}COMMENT '{{field.comment}}'{% endif %}
  {%- endfor %}
)
{%- if table.table_comment %}
COMMENT '{{table.table_comment}}'
{%- endif %}
PARTITIONED BY (DATA_DT STRING)       --按照数据日期天分区
CLUSTERED BY  (UUID)  INTO 3 BUCKETS  --分桶
STORED AS ORC TBLPROPERTIES ("transactional"="true"); --ORC事务表


{% endfor -%}
{% endfor -%}