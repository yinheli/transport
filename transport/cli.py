# -*- coding: utf-8 -*-

import os
import click
from transport.transport import Transport


@click.command(no_args_is_help=True)
@click.option("-f", "--excel", default="贴源层表清单梳理.xlsx", type=click.Path(exists=True), help="梳理好的 excel 文件完整路径")
@click.option("-s", "--sql", default="gdm_table.hql", type=click.Path(exists=True), help="系统导出的 hql 文件，作为基础模板")
@click.option("-o", "--out", default=os.getcwd(), type=click.Path(exists=True), help="输出文件夹，默认输出到当前文件夹")
def main(excel: str, sql: str, out: str):
    """一个简单批处理工具，输入整理好的 excel 和 hql 表结构，基于模板输出 ddl 和 procedure"""
    transport = Transport()
    transport.handle(excel, sql, out)
