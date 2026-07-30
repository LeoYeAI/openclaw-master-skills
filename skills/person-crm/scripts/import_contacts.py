#!/usr/bin/env python3
"""
联系人导入脚本 - 支持 CSV 和 vCard 格式
用法: python import_contacts.py <file> [--dry-run] [--feishu]

配置说明：
- 详见 SKILL.md
- 支持从 openclaw.json 或环境变量读取配置
"""

import os
import re
import json
import csv
import sys
import time
import urllib.error
from datetime import datetime
from pathlib import Path


# ========== 配置 ==========
# 注意：credentials 不要硬编码！
# 配置方式详见 SKILL.md

def get_feishu_config():
    """从 openclaw.json 读取飞书配置"""
    app_id = app_secret = app_token = table_id = ''
    
    # 方式1: 从 openclaw.json 读取
    config_path = Path.home() / '.openclaw' / 'openclaw.json'
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        # app_id/app_secret from channels.feishu
        feishu = config.get('channels', {}).get('feishu', {})
        app_id = feishu.get('appId', '')
        app_secret = feishu.get('appSecret', '')
        
        # app_token/table_id from skills config
        skills = config.get('skills', {}).get('entries', {}).get('personal-crm', {})
        cfg = skills.get('config', {})
        app_token = cfg.get('app_token', '')
        table_id = cfg.get('contacts_table_id', '')
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    
    # 方式2: 从环境变量读取（优先级更高）
    app_id = app_id or os.environ.get('FEISHU_APP_ID', '')
    app_secret = app_secret or os.environ.get('FEISHU_APP_SECRET', '')
    app_token = app_token or os.environ.get('FEISHU_APP_TOKEN', '')
    table_id = table_id or os.environ.get('FEISHU_TABLE_ID', '')
    
    return app_id, app_secret, app_token, table_id


# 初始化配置
FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_APP_TOKEN, FEISHU_TABLE_ID = get_feishu_config()


def check_config():
    """检查配置是否完整并给出提示"""
    issues = []
    
    if not FEISHU_APP_ID:
        issues.append("FEISHU_APP_ID (channels.feishu.appId)")
    if not FEISHU_APP_SECRET:
        issues.append("FEISHU_APP_SECRET (channels.feishu.appSecret)")
    if not FEISHU_APP_TOKEN:
        issues.append("FEISHU_APP_TOKEN (skills.personal-crm.config.app_token)")
    if not FEISHU_TABLE_ID:
        issues.append("FEISHU_TABLE_ID (skills.personal-crm.config.contacts_table_id)")
    
    if issues:
        print("⚠️  飞书配置不完整！")
        print("\n缺少配置项:", ", ".join(issues))
        print("\n请在 ~/.openclaw/openclaw.json 中添加配置：")
        print("""
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "你的appId",
      "appSecret": "你的appSecret"
    }
  },
  "skills": {
    "entries": {
      "personal-crm": {
        "enabled": true,
        "config": {
          "app_token": "你的bitable_app_token",
          "contacts_table_id": "你的contacts_table_id"
        }
      }
    }
  }
}
""")
        return False
    return True


# ========== 通用函数 ==========

def parse_date(date_str):
    """解析日期格式"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%m/%d', '%m-%d', '%d']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if fmt in ['%m/%d', '%m-%d', '%d']:
                dt = dt.replace(year=2024)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    return None


def parse_multiselect(value):
    """解析多选字段"""
    if not value:
        return []
    return [v.strip() for v in str(value).split(',') if v.strip()]


# ========== CSV 解析 ==========

CSV_FIELD_MAP = {
    '姓名': 'Personal CRM',
    '关系': '关系',
    '手机': '手机',
    '电话': '手机',
    '微信': '微信',
    '邮箱': '邮箱',
    '邮件': '邮箱',
    '城市': '城市',
    '公司': '公司',
    '企业': '公司',
    '职位': '职位',
    '职务': '职位',
    '生日': '生日',
    '出生日期': '生日',
    '爱好': '爱好',
    '标签': '标签',
    '备注': '备注',
}


def parse_csv(file_path):
    """解析 CSV 文件"""
    path = Path(file_path)
    if not path.exists():
        return None, [], f"文件不存在: {file_path}"
    
    content = None
    for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
        try:
            with open(path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                content = list(reader)
            break
        except UnicodeDecodeError:
            continue
    
    if not content:
        return None, [], "无法解析 CSV 文件"
    
    contacts = []
    skipped = []
    
    for i, row in enumerate(content):
        if not any(row.values()):
            continue
        
        contact = {}
        for csv_field, value in row.items():
            if not value:
                continue
            
            feishu_field = CSV_FIELD_MAP.get(csv_field, csv_field)
            
            if feishu_field == '生日':
                parsed = parse_date(value)
                if parsed:
                    contact[feishu_field] = parsed
            elif feishu_field in ['爱好', '标签']:
                contact[feishu_field] = parse_multiselect(value)
            else:
                contact[feishu_field] = value.strip()
        
        if contact.get('Personal CRM'):
            contacts.append(contact)
        else:
            skipped.append({'row': i + 2, 'reason': '无姓名'})
    
    return contacts, skipped, None


# ========== vCard 解析 ==========

def parse_vcard(file_path):
    """解析 vCard 文件"""
    path = Path(file_path)
    if not path.exists():
        return None, [], f"文件不存在: {file_path}"
    
    content = None
    for encoding in ['utf-8', 'gbk', 'gb2312']:
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    if not content:
        return None, [], "无法读取文件"
    
    pattern = r'BEGIN:VCARD.*?END:VCARD'
    vcards = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not vcards:
        return None, [], "未找到有效联系人"
    
    contacts = []
    skipped = []
    
    for i, vcard in enumerate(vcards):
        contact = {}
        
        # 姓名 FN
        match = re.search(r'FN[;:]([^\r\n]+)', vcard, re.IGNORECASE)
        if not match:
            match = re.search(r'N[;:]([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if ';' in name:
                parts = name.split(';')
                name = (parts[0] or '') + (parts[1] or '')
            contact['Personal CRM'] = name.strip()
        
        # 电话 TEL
        match = re.search(r'TEL[;](?:TYPE=[\w]+:)?([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            phone = re.sub(r'[^\d+\-]', '', match.group(1).strip())
            if phone:
                contact['手机'] = phone
        
        # 邮箱 EMAIL
        match = re.search(r'EMAIL[;](?:TYPE=[\w]+:)?([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            contact['邮箱'] = match.group(1).strip()
        
        # 公司 ORG
        match = re.search(r'ORG[;:]([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            contact['公司'] = match.group(1).strip().split(',')[0]
        
        # 职位 TITLE
        match = re.search(r'TITLE[;:]([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            contact['职位'] = match.group(1).strip()
        
        # 地址/城市 ADR
        match = re.search(r'ADR[;](?:TYPE=[\w]+:)?([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            parts = [p.strip() for p in match.group(1).split(';')]
            if len(parts) > 2 and parts[2]:
                contact['城市'] = parts[2]
        
        # 生日 BDAY
        match = re.search(r'BDAY[;:]?(\d{4}[-/]\d{2}[-/]\d{2})', vcard, re.IGNORECASE)
        if match:
            parsed = parse_date(match.group(1))
            if parsed:
                contact['生日'] = parsed
        
        # 备注 NOTE
        match = re.search(r'NOTE[;:]([^\r\n]+)', vcard, re.IGNORECASE)
        if match:
            contact['备注'] = match.group(1).strip()
        
        if contact.get('Personal CRM'):
            contacts.append(contact)
        else:
            skipped.append({'row': i + 1, 'reason': '无姓名'})
    
    return contacts, skipped, None


# ========== 飞书导入 ==========

_cached_token = None
_token_expires_at = 0


def get_feishu_token():
    """获取飞书 access_token（带过期刷新，飞书 token 有效期 2 小时）"""
    global _cached_token, _token_expires_at
    if _cached_token and time.time() < _token_expires_at:
        return _cached_token
    
    import urllib.request
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                _cached_token = result.get('tenant_access_token')
                expire = result.get('expire', 7200)
                _token_expires_at = time.time() + expire - 300
                return _cached_token
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        print(f"获取 token 失败: {e}")
    
    return ''


def check_duplicate(contact, existing_contacts):
    """检查联系人是否已存在"""
    name = contact.get('Personal CRM', '').strip().lower()
    phone = (contact.get('手机') or '').strip()
    
    for existing in existing_contacts:
        existing_name = (existing.get('Personal CRM') or '').strip().lower()
        existing_phone = (existing.get('手机') or '').strip()
        
        # 姓名完全匹配
        if name and existing_name and name == existing_name:
            return True
        # 手机号匹配
        if phone and existing_phone and phone == existing_phone:
            return True
    
    return False


def get_existing_contacts():
    """获取飞书中已有的联系人"""
    if not check_config():
        return []
    
    import urllib.request
    
    token = get_feishu_token()
    if not token:
        return []
    
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records?page_size=500'
    
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                items = result.get('data', {}).get('items', [])
                return [{'Personal CRM': i.get('fields', {}).get('Personal CRM', ''),
                        '手机': i.get('fields', {}).get('手机', '')} 
                       for i in items]
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        print(f"获取已有联系人失败: {e}")
    
    return []


def import_to_feishu(contacts):
    """导入联系到飞书（带重复检查）"""
    if not check_config():
        return {'imported': 0, 'skipped': 0, 'failed': 0, 'errors': ['配置不完整']}
    
    import urllib.request
    
    token = get_feishu_token()
    if not token:
        return {'imported': 0, 'skipped': 0, 'failed': 0, 'errors': ['无法获取飞书 access_token']}
    
    # 获取已有联系人
    print("检查已有联系人...")
    existing = get_existing_contacts()
    print(f"已有 {len(existing)} 个联系人")
    
    imported = 0
    skipped = 0
    failed = 0
    errors = []
    
    for contact in contacts:
        name = contact.get('Personal CRM', 'Unknown')
        
        # 检查重复
        if check_duplicate(contact, existing):
            skipped += 1
            print(f"  ⏭ 跳过: {name} (已存在)")
            continue
        
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_APP_TOKEN}/tables/{FEISHU_TABLE_ID}/records'
        data = json.dumps({'fields': contact}).encode('utf-8')
        
        req = urllib.request.Request(
            url, data=data,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                resp = json.loads(response.read().decode('utf-8'))
                if resp.get('code') == 0:
                    imported += 1
                    # 添加到已有列表，避免同一批重复
                    existing.append(contact)
                    print(f"  ✓ 导入: {name}")
                else:
                    failed += 1
                    errors.append(f"{name}: {resp.get('msg', 'Error')}")
                    print(f"  ✗ 失败: {name}")
        except Exception as e:
            failed += 1
            errors.append(f"{name}: {str(e)}")
            print(f"  ✗ 错误: {name}")
    
    return {'imported': imported, 'skipped': skipped, 'failed': failed, 'errors': errors}


# ========== 主函数 ==========

def import_contacts(file_path, dry_run=False, feishu=False):
    """导入联系人"""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == '.csv':
        contacts, skipped, error = parse_csv(file_path)
    elif suffix in ['.vcf', '.vcard']:
        contacts, skipped, error = parse_vcard(file_path)
    else:
        return {'success': False, 'error': f'不支持的文件格式: {suffix}，请使用 .csv 或 .vcf'}
    
    if error:
        return {'success': False, 'error': error}
    
    if not contacts:
        return {'success': False, 'error': '未找到有效联系人'}
    
    result = {
        'success': True,
        'format': suffix.lstrip('.').upper(),
        'total': len(contacts),
        'contacts': contacts[:10] if dry_run else contacts,
        'skipped': skipped,
        'preview': contacts[:3] if contacts else [],
        'imported': 0,
        'failed': 0
    }
    
    # 如果需要导入到飞书
    if feishu and not dry_run:
        feishu_result = import_to_feishu(contacts)
        result['imported'] = feishu_result.get('imported', 0)
        result['failed'] = feishu_result.get('failed', 0)
        result['errors'] = feishu_result.get('errors', [])
    
    return result


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python import_contacts.py <文件路径> [--dry-run] [--feishu]")
        print("")
        print("示例:")
        print("  python import_contacts.py ~/contacts.csv --dry-run")
        print("  python import_contacts.py ~/contacts.vcf --feishu")
        print("  python import_contacts.py ~/contacts.csv --dry-run --feishu")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    dry_run = "--dry-run" in sys.argv
    feishu = "--feishu" in sys.argv
    
    if feishu and not dry_run:
        if not check_config():
            print("\n无法导入到飞书，请先配置 credentials")
            sys.exit(1)
    
    result = import_contacts(file_path, dry_run=dry_run, feishu=feishu)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
