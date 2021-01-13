{%- for group in groups -%}
------------------------------------
--- start {{group.group_name}} ---
------------------------------------
CREATE OR REPLACE PACKAGE {{group.target_db}}.PKG_S_GET_{{group.group_name}} AS
V_DAY STRING;
{% for table in group.tables -%}
PROCEDURE p_s_{{table.table}}(P_DATE STRING);
{% endfor -%}
PROCEDURE P_S_GET_{{group.group_name}}_MAIN(P_DATE STRING);
END;
/

CREATE OR REPLACE PACKAGE BODY {{group.target_db}}.PKG_S_GET_{{group.group_name}} IS 
{% for table in group.tables -%}
{% if table.table_comment %}/*{{table.table_comment}}*/{% endif %} 
PROCEDURE {{group.target_db}}.p_s_{{table.table}}(P_DATE IN STRING) AS
V_SEQ_ID   INT;               --任务号
V_ERR_DESC STRING;            --任务描述 

BEGIN

set_env('inceptor.insert.data.format.check','true');--数据类型有误报错
set_env('transaction.type','inceptor');             --设置事务类型

SELECT {{group.target_db}}.SEQ_ETL.NEXTVAL INTO V_SEQ_ID FROM SYSTEM.DUAL; 
INSERT INTO {{group.target_db}}.log_etl_main 
VALUES (V_SEQ_ID,'PKG_S_GET_{{group.group_name}}','P_S_{{table.table}}',P_date,systimestamp,NULL,null);
COMMIT;


EXECUTE IMMEDIATE 'TRUNCATE TABLE {{group.target_db}}.{{table.table}}';

/* {{table.table_comment}} */
INSERT INTO {{group.target_db}}.{{table.table}} (
 {%- for field in table.options.fields %}
 ,{{'%-40s' | format(field.field)}}   {% if field.comment %} /*{{field.comment}}*/ {% endif %} 
 {%- endfor %}
)                                                                   
SELECT                                                              
 TO_CHAR(SYSDATE,'YYYYMMDD') AS RPT_DT        /*报表跑批日期*/                    
 {%- for field in table.options.fields if field.field != 'rpt_dt' %}
 ,{{'%-40s' | format(field.field)}}   {% if field.comment %} /*{{field.comment}}*/ {% endif %} 
 {%- endfor %}
FROM {{table.source_db}}.{{table.table}} A
WHERE A.txn_dt=P_DATE;  /*取当日数据*/
COMMIT;
UPDATE {{group.target_db}}.log_etl_main  T SET T.END_DT=SYSTIMESTAMP,T.SUCCESS_FLAG='Y' /*更新日志表成功与否标志*/
WHERE T.SEQ_NO=V_SEQ_ID;
COMMIT;

exception
  when others then
    V_ERR_DESC := substr(' error code [' || sqlcode() || ']' || 'error message [' ||     sqlerrm() || ']',1,250);
    RAISE;
    ROLLBACK;
    
UPDATE {{group.target_db}}.log_etl_main  T SET T.END_DT=SYSTIMESTAMP,T.SUCCESS_FLAG='N' WHERE T.SEQ_NO=V_SEQ_ID;
INSERT INTO {{group.target_db}}.LOG_ETL_SUB (seq_no,PKG_name,PRO_NAME,ERR_dt,err_info) VALUES
(V_SEQ_ID,'PKG_S_GET_{{group.group_name}}','P_S_{{table.table}}',SYSTIMESTAMP,V_ERR_DESC);
COMMIT;
END P_S_{{table.table}};
{% endfor %}

/*调用函数*/
PROCEDURE P_S_GET_{{group.group_name}}_MAIN (P_DATE STRING) IS
declare
V_SEQ_ID   INT;               --任务号
V_ERR_DESC STRING;            --任务描述
BEGIN

set_env('inceptor.insert.data.format.check','true');--数据类型有误报错
set_env('transaction.type','inceptor');             --设置事务类型

V_DAY:=SUBSTR(P_DATE,1,4)||'-'||SUBSTR(P_DATE,5,2)||'-'||SUBSTR(P_DATE,7,2);

SELECT {{group.target_db}}.SEQ_ETL.NEXTVAL INTO V_SEQ_ID FROM SYSTEM.DUAL; 
INSERT INTO {{group.target_db}}.log_etl_main 
VALUES (V_SEQ_ID,'PKG_S_GET_{{group.group_name}}','P_S_GET_{{group.group_name}}_MAIN',P_date,systimestamp,NULL,null);
COMMIT;

{% for table in group.tables -%}
{{group.target_db}}.pkg_s_get_{{group.group_name}}.p_s_{{table.table}}(p_date);
{% endfor %}

UPDATE {{group.target_db}}.log_etl_main  T SET T.END_DT=SYSTIMESTAMP,T.SUCCESS_FLAG='Y'
WHERE T.SEQ_NO=V_SEQ_ID;
COMMIT;

exception
  when others then
    V_ERR_DESC := substr(' error code [' || sqlcode() || ']' || 'error message [' ||     sqlerrm() || ']',1,250);
    RAISE;
    ROLLBACK;
    
UPDATE {{group.target_db}}.log_etl_main  T SET T.END_DT=SYSTIMESTAMP,T.SUCCESS_FLAG='N' WHERE T.SEQ_NO=V_SEQ_ID;
INSERT INTO {{group.target_db}}.LOG_ETL_SUB (seq_no,PKG_name,PRO_NAME,ERR_dt,err_info) VALUES
(V_SEQ_ID,'PKG_S_GET_{{group.group_name}}','P_S_GET_{{group.group_name}}_MAIN',SYSTIMESTAMP,V_ERR_DESC);
COMMIT;
END P_S_GET_{{group.group_name}}_MAIN;
END;

/
------------------------------------
--- end {{group.group_name}} ---
------------------------------------


{% endfor -%}

