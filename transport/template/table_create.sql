{%- for group in groups -%}
{%- for table in group.tables -%}
DROP TABLE IF EXISTS {{table.target_db}}.{{table.table}};
CREATE TABLE {{table.target_db}}.{{table.table}} (
  {%- for field in table.options.fields %}
    {% if loop.index > 1 %},{% endif %}{{field.field}} {{field.type}} DEFAULT NULL {% if field.comment %}COMMENT '{{field.comment}}'{% endif %}
  {%- endfor %}
)
{%- if table.table_comment %}
COMMENT '{{table.table_comment}}'
{%- endif %}
{%- if table.options.buckets %}
{{table.options.buckets}}
{%- endif %}
STORED AS ORC
TBLPROPERTIES ( "transactional"="true");


{% endfor -%}
{% endfor -%}