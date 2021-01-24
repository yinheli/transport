# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime
import openpyxl
import sqlparse
from jinja2 import Environment, FileSystemLoader


class Transport():
    env: Environment

    def __init__(self, excel: str, sqlfile: str, out: str, **kwargs):
        basedir = os.path.dirname(__file__)
        if getattr(sys, 'frozen', None):
            basedir = sys._MEIPASS
        self.env = Environment(loader=FileSystemLoader(
            os.path.join(basedir, 'template')))

        self.excel = excel
        self.sqlfile = sqlfile
        self.out = out
        self.options = kwargs

    def handle(self):
        """处理输入文件"""

        print('read :', self.excel)
        excel_data = self._read_excel(self.excel)

        print('parse:', self.sqlfile)
        table_tpl = self._parse_table(
            self.sqlfile, self.options.get('encoding', 'UTF-8'))

        # 分组内，最大表数量，通过 chunk_size 控制
        groups = self._group_data(excel_data, table_tpl, chunk_size=20)

        now = datetime.now()
        now_formated = now.strftime('%Y_%m_%d__%H_%M_%S')

        out_table_ddl = os.path.join(
            self.out, 'gen_table_ddl_{}.sql'.format(now_formated))
        out_table_procedure = os.path.join(
            self.out, 'gen_table_procedure_{}.sql'.format(now_formated))

        file_head = '-- auto generated file, DO NOT EDIT \n' + \
            '-- \n' + \
            '-- generated at: {date} \n' + \
            '-- excel: {excel} \n' + \
            '-- hql  : {sqlfile} \n\n\n'
        file_head = file_head.format(
            date=now.strftime('%Y-%m-%d %H:%M:%S'),
            excel=self.excel,
            sqlfile=self.sqlfile)

        with open(out_table_ddl, 'w+', encoding='utf8') as f:
            print('writing:', out_table_ddl)
            f.write(file_head)
            f.write(self.env.get_template(
                'table_create.sql').render(groups=groups))

        with open(out_table_procedure, 'w+', encoding='utf8') as f:
            print('writing:', out_table_procedure)
            f.write(file_head)
            f.write(self.env.get_template(
                'table_procedure.sql').render(groups=groups))

        print('done')

    def _read_excel(self, excel):
        """解析 excel"""
        wb = openpyxl.load_workbook(excel)
        sheet = wb.active
        values = [[cell.value for cell in row]
                  for row in sheet['A2':'G'+str(sheet.max_row)]]
        values = list(
            filter(lambda row: row[0] != None and row[1] != None, values))
        for row in values:
            for i, v in enumerate(row):
                if i == 0:
                    continue
                v = v.strip() if v else ''
                if i in (2, 3, 4, 5):
                    v = v.upper()
        # 按照系统和表名排序
        sorted(values, key=lambda it: it[2]+it[5])
        return values

    def _parse_table(self, sqlfile, encoding='utf8'):
        """解析 hql 文件，用正则匹配的方式，把 hql 文件的表结构提取出来"""
        tables = {}
        with open(sqlfile, 'r', encoding=encoding) as f:
            data = f.read()
            statements = sqlparse.parse(data)
            for it in statements:
                table_name, table_options = self._parse_table_item(it)
                if table_name:
                    tables[table_name] = table_options
        return tables

    def _parse_table_item(self, stmt):
        tokens = [t for t in sqlparse.sql.TokenList(
            stmt.tokens) if t.ttype != sqlparse.tokens.Whitespace]
        is_create_stmt = False
        table_name = None
        fields = []
        buckets = None

        def parse_buckets(i):
            buf = ''
            for it in tokens[i:]:
                v = it.value
                buf += ' ' + v
                if 'BUCKETS' in v.upper():
                    break
            return re.sub(r'\s*--.*', '', buf.strip())

        for i, token in enumerate(tokens):
            if token.match(sqlparse.tokens.DDL, 'CREATE'):
                is_create_stmt = True

            # 处理表名
            if is_create_stmt and table_name is None:
                if isinstance(token, sqlparse.sql.Identifier):
                    table_name = token.value.split('.')[-1]

            # 处理字段
            if is_create_stmt and not fields and isinstance(token, sqlparse.sql.Parenthesis):
                # print(token.value)
                txt = token.value
                txt = txt[txt.find('(')+1:txt.rfind(')')].strip()
                fields.append(
                    {'field': 'rpt_dt', 'type': 'STRING', 'comment': '报表跑批日期'})
                found_dt = False
                for it in [re.split(r'\s+', x.strip()) for x in re.split(r'(?:[\n\r\s]*)?(?<!\d)\,(?:[\n\r\s]*)', txt)]:
                    field = it[0].strip()
                    item = {'field': field, 'type': it[1].strip()}
                    if 'COMMENT' in it or 'comment' in it:
                        item['comment'] = it[-1].replace("'", '').strip()
                    if field.lower() == 'data_dt':
                        found_dt = True
                    fields.append(item)
                if not found_dt:
                    fields.append(
                        {'field': 'DATA_DT', 'type': 'STRING', 'comment': '数据日期'})

            # 处理分桶
            if is_create_stmt and fields and buckets is None:
                if isinstance(token, sqlparse.sql.Identifier):
                    txt = token.value
                    if txt.upper().startswith('CLUSTERED'):
                        buckets = parse_buckets(i)

        if not is_create_stmt:
            return (None, None)

        return (table_name, {'fields': fields, 'buckets': buckets})

    def _group_data(self, excel_data, table_tpl, chunk_size=5):
        """处理数据分组"""
        groups = []

        tables = []
        last_system = ''
        system = ''
        system_comment = ''
        source_db = ''
        target_db = ''

        # 按系统分组
        for idx, row in enumerate(excel_data):
            system, system_comment, source_db, target_db, table, table_comment = \
                row[2], row[1], row[3], row[4], row[5], row[6]

            if table not in table_tpl:
                continue

            if last_system != '' and last_system != system:
                groups.append({
                    'system': excel_data[idx-1][2],
                    'system_comment': excel_data[idx-1][1],
                    'target_db': excel_data[idx-1][4],
                    'tables': tables,
                })
                tables = []

            item = {
                'table': table,
                'table_comment': table_comment,
                'source_db': source_db,
                'target_db': target_db,
                'options': table_tpl[table],
            }
            tables.append(item)

            last_system = system

        if tables:
            groups.append({
                'system': system,
                'system_comment': system_comment,
                'target_db': target_db,
                'tables': tables,
            })

        # self.write_json(groups, 'out_groups.json')
        # 如果系统组内，表数量比较多，按照 chunk_size 再次分组
        chunk_groups = []
        for g in groups:
            tables = g['tables']
            if len(tables) > chunk_size:
                gid = 1
                for tbs in list([tables[i:i+chunk_size] for i in range(0, len(tables), chunk_size)]):
                    if tbs:
                        g['tables'] = tbs
                        g['group_name'] = g['system'] + str(gid)
                        chunk_groups.append(g.copy())
                        gid += 1
            else:
                g['group_name'] = g['system']
                chunk_groups.append(g)

        # self.write_json(chunk_groups, 'out_chunk_group.json')

        return chunk_groups

    def write_json(self, data, file):
        """json 输出，方便查看复杂的数据结构"""
        import json
        r = json.dumps(data, indent=2, ensure_ascii=False)
        with open(file, 'w+', encoding='utf8') as f:
            f.write(r)
