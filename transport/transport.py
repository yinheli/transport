# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
import openpyxl
from jinja2 import Environment, FileSystemLoader


class Transport():
    env = Environment(loader=FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'template')))

    def handle(self, excel: str, sqlfile: str, out: str):
        print('read :', excel)
        excel_data = self._read_excel(excel)

        print('parse:', sqlfile)
        table_tpl = self._parse_table(sqlfile)

        groups = self._group_data(excel_data, table_tpl)

        now = datetime.now()
        now_formated = now.strftime('%Y_%m_%d__%H_%M_%S')

        out_table_ddl = os.path.join(
            out, 'gen_table_ddl_{}.sql'.format(now_formated))
        out_table_procedure = os.path.join(
            out, 'gen_table_procedure_{}.sql'.format(now_formated))

        file_head = '-- auto generated file, DO NOT EDIT \n' + \
            '-- \n' + \
            '-- generated at: {date} \n' + \
            '-- excel: {excel} \n' + \
            '-- hql  : {sqlfile} \n\n\n'
        file_head = file_head.format(
            date=now.strftime('%Y-%m-%d %H:%M:%S'),
            excel=excel,
            sqlfile=sqlfile)

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
                  for row in sheet['A2':'E'+str(sheet.max_row)]]
        values = list(filter(lambda row: row[0] != None, values))
        for row in values:
            for i, v in enumerate(row):
                if i == 0:
                    continue
                v = v.strip() if v else ''
                if i in (2, 3):
                    v = v.upper()
        sorted(values, key=lambda it: it[2]+it[3])
        return values

    def _parse_table(self, sqlfile):
        """解析 hql 文件，用正则匹配的方式，把 hql 文件的表结构提取出来"""
        tables = {}
        with open(sqlfile, 'r', encoding='utf8') as f:
            data = f.read()
            data = re.split(r"DROP\s+TABLE\s+IF\s+EXISTS.*\n",
                            data, flags=re.IGNORECASE)
            for item in data:
                try:
                    table, fields = self._parse_table_item(item)
                    if table:
                        tables[table] = fields
                except Exception as e:
                    print('parse sql file exception')
                    raise e
        return tables

    def _parse_table_item(self, table):
        m = re.search(r"CREATE\sTABLE\s(.*)\s?\(([\s\S]*)\)\nCOMMENT", table,
                      re.MULTILINE | re.IGNORECASE)
        if not m:
            return (None, None)
        name = m.group(1).split('.')[1].upper().strip()
        fields = []
        found_dt = False
        for it in [re.split(r'\s+', x.strip()) for x in re.split(r'[\n\s]+\,', m.group(2))]:
            field = it[0].strip()
            item = {'field': field, 'type': it[1].strip()}
            if len(it) > 3:
                item['comment'] = it[3].replace("'", '').strip()
            if field.lower() == 'data_dt':
                found_dt = True
            fields.append(item)

        if not found_dt:
            fields.append(
                {'field': 'DATA_DT', 'type': 'STRING', 'comment': '数据日期'})
        return (name, fields)

    def _group_data(self, excel_data, table_tpl):
        groups = []

        tables = []
        last_user = ''
        user = ''
        user_comment = ''

        # 按用户/系统分组
        for idx, row in enumerate(excel_data):
            user, user_comment, table, table_comment = row[2], row[1], row[3], row[4]

            if table not in table_tpl:
                continue

            if last_user != '' and last_user != user:
                groups.append({
                    'user': excel_data[idx-1][2],
                    'user_comment': excel_data[idx-1][1],
                    'tables': tables,
                })
                tables = []

            item = {
                'table': table,
                'table_comment': table_comment,
                'fields': table_tpl[table],
            }
            tables.append(item)

            last_user = user

        if tables:
            groups.append({
                'user': user,
                'user_comment': user_comment,
                'tables': tables,
            })

        # self.write_json(groups, 'out.json')
        # 将 table 数量超过的拆分为小的分组
        chunk_groups = []
        chunk_size = 5
        for g in groups:
            tables = g['tables']
            if len(tables) > chunk_size:
                gid = 1
                for tbs in list([tables[i:i+chunk_size] for i in range(0, len(tables), chunk_size)]):
                    if tbs:
                        g['tables'] = tbs
                        g['group_name'] = g['user'] + str(gid)
                        chunk_groups.append(g)
                        gid += 1
            else:
                g['group_name'] = g['user']
                chunk_groups.append(g)

        self.write_json(chunk_groups, 'out.json')

        return chunk_groups

    def write_json(self, data, file):
        import json
        r = json.dumps(data, indent=2, ensure_ascii=False)
        with open(file, 'w+', encoding='utf8') as f:
            f.write(r)
