CREATE TABLE GDM.BASE_CASH_ACCT (
    AccNo STRING DEFAULT NULL COMMENT '账号'
   ,OpInst_No STRING DEFAULT NULL COMMENT '营业机构号'
   ,Ccy_CdNm STRING DEFAULT NULL COMMENT '货币代号'
   ,Csh_Acc_Cgy STRING DEFAULT NULL COMMENT '现金账户类别'
   ,Csh_BnkTailBox STRING COMMENT '现金尾箱'
   ,BnkTailBox_Cgy STRING COMMENT '尾箱类别'
   ,Acc_Chn_Nm STRING COMMENT '帐户中文名'
   ,AccBal DECIMAL(22,2) COMMENT '帐户余额'
   ,AccNo_Dtl_SN STRING COMMENT '账号明细序号'
   ,OpnAcc_Dt STRING COMMENT '开户日期'
   ,CnclAcct_Dt STRING COMMENT '销户日期'
   ,Tlr_No STRING COMMENT '柜员号'
   ,BnkTailBox_Ind STRING COMMENT '尾箱标志'
   ,BnkTailBox_Ahr_St STRING COMMENT '尾箱权限状态'
   ,UUID STRING COMMENT 'UUID'
)
COMMENT '现金基础表'
STORED AS ORC TBLPROPERTIES ("transactional"="true"); --ORC事务表


CREATE TABLE GDM.BASE_CREDIT_CARD (
   AccNo STRING COMMENT '账号'
  ,CardNo STRING COMMENT '卡号'
  ,HstCrd_No STRING COMMENT '主卡号'
  ,Cst_No STRING COMMENT '客户号'
  ,Acc_Nm STRING COMMENT '帐户名称'
  ,Acc_Own_Crd_No STRING COMMENT '帐户拥有者证件号码'
  ,Acc_St STRING COMMENT '账户状态'
  ,CrdIsu_Inst STRING COMMENT '发卡机构'
  ,TLmt DECIMAL(22,2) COMMENT '总额度'
  ,Rglr_Od_Amt DECIMAL(22,2) COMMENT '正常透支额'
  ,Odu_Od_Amt DECIMAL(22,2) COMMENT '逾期透支额'
  ,Instm_Od_Amt DECIMAL(22,2) COMMENT '分期透支额'
  ,OvflwPymt	DECIMAL(22,2) COMMENT '溢缴款'
  ,CrdIsu_Dt	STRING COMMENT '发卡日期'
  ,Actvt_Dt	STRING COMMENT '激活日期'
  ,UUID STRING COMMENT 'UUID'
)
COMMENT '信用卡基础表'
PARTITIONED BY (DATA_DT STRING)       --按照数据日期天分区
CLUSTERED BY  (UUID)  INTO 3 BUCKETS  --分桶
STORED AS ORC TBLPROPERTIES ("transactional"="true"); --ORC事务表
