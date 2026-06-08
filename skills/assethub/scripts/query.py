#!/usr/bin/env python3
"""
AssetHub 快速查询工具 v4.0
用法: python query.py <command> [options]
      python query.py -i          # 交互式模式

功能:
  - 每次调用自动获取 Token (安全)
  - 支持配置文件多租户切换
  - 数据缓存减少 API 调用
  - 自动重试机制
  - 交互式 REPL 模式
"""

import urllib.request, urllib.parse, json, sys, time, random, string, os
from datetime import datetime, timedelta
from collections import defaultdict

# ===== 配置文件管理 =====
CONFIG_DIR = os.path.expanduser("~/.assethub")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    """加载配置文件"""
    # 默认配置
    config = {
        "base_url": "http://160ttth72797.vicp.fun:59745/api",
        "tenant_id": "2",
        "username": "su",
        "password": "",
        "token_cache_seconds": 300,
        "cache_ttl": 60,  # 数据缓存 TTL (秒)
        "max_retries": 3,
        "default_pageSize": 1000,  # 默认每页数量
    }
    
    # 环境变量覆盖
    config["base_url"] = os.environ.get("ASSETHUB_URL", config["base_url"])
    config["tenant_id"] = os.environ.get("ASSETHUB_TENANT", config["tenant_id"])
    config["username"] = os.environ.get("ASSETHUB_USER", config["username"])
    config["password"] = os.environ.get("ASSETHUB_PASS", config["password"])
    
    # 配置文件覆盖
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"⚠️ 配置文件读取失败: {e}")
    
    return config

# 初始化配置
CFG = load_config()
BASE_URL = CFG["base_url"]
TENANT_ID = CFG["tenant_id"]
USERNAME = CFG["username"]
PASSWORD = CFG["password"]

# ===== Token 缓存 =====
_cached_token = None
_token_cache_time = 0

def get_token():
    """获取 Token (带缓存)"""
    global _cached_token, _token_cache_time
    
    now = time.time()
    if _cached_token and (now - _token_cache_time) < CFG["token_cache_seconds"]:
        return _cached_token
    
    if not PASSWORD:
        # 交互式输入密码
        import getpass
        print("\n🔐 请输入 AssetHub 登录信息")
        input_username = input("用户名: ").strip()
        input_password = getpass.getpass("密码: ").strip()
        
        if not input_password:
            print("错误: 密码不能为空")
            sys.exit(1)
        
        # 更新全局变量
        if input_username:
            globals()['USERNAME'] = input_username
        globals()['PASSWORD'] = input_password
        globals()['TENANT_ID'] = input("租户ID [2]: ").strip() or TENANT_ID
    
    url = f"{BASE_URL}/users/login"
    req = urllib.request.Request(url, data=json.dumps({"username": USERNAME, "password": PASSWORD}).encode('utf-8'))
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Tenant-ID", TENANT_ID)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            if data.get("success"):
                _cached_token = data["data"]["token"]
                _token_cache_time = now
                return _cached_token
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        sys.exit(1)

# ===== 数据缓存 =====
_data_cache = {}  # {"path+params": {"data": ..., "time": ...}}

def getCached(key):
    """获取缓存"""
    if key in _data_cache:
        if time.time() - _data_cache[key]["time"] < CFG["cache_ttl"]:
            return _data_cache[key]["data"]
    return None

def setCache(key, data):
    """设置缓存"""
    _data_cache[key] = {"data": data, "time": time.time()}

# ===== API 调用 (带重试和分页) =====
def api_get(path, params=None, useCache=True, getAllPages=False):
    # 缓存 key
    cache_key = f"{path}?{urllib.parse.urlencode(params) if params else ''}"
    
    if useCache and not getAllPages:
        cached = getCached(cache_key)
        if cached:
            return cached
    
    # 获取所有页面
    if getAllPages:
        all_data = []
        page = 1
        pageSize = params.get("pageSize", CFG["default_pageSize"]) if params else CFG["default_pageSize"]
        
        while True:
            p = dict(params) if params else {}
            p["page"] = page
            p["pageSize"] = pageSize
            
            url = f"{BASE_URL}{path}?{urllib.parse.urlencode(p)}"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {get_token()}")
            req.add_header("X-Tenant-ID", TENANT_ID)
            
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.loads(r.read().decode())
                    items = data.get("data", {}).get("list", []) if isinstance(data.get("data"), dict) else data.get("data", [])
                    all_data.extend(items)
                    
                    # 检查是否还有更多页面
                    pagination = data.get("data", {}).get("pagination", {}) if isinstance(data.get("data"), dict) else {}
                    total = pagination.get("total", 0)
                    if len(all_data) >= total:
                        break
                    page += 1
            except Exception as e:
                return {"error": str(e)}
        
        return {"data": {"list": all_data, "pagination": {"total": len(all_data)}}}
    
    # 单页请求
    url = f"{BASE_URL}{path}"
    if params: url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {get_token()}")
    req.add_header("X-Tenant-ID", TENANT_ID)
    
    # 自动重试
    for attempt in range(CFG["max_retries"]):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
                if useCache:
                    setCache(cache_key, data)
                return data
        except Exception as e:
            if attempt < CFG["max_retries"] - 1:
                time.sleep(1)  # 重试前等待
                continue
            return {"error": str(e)}
    return {"error": "重试失败"}

def api_post(path, data):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
    req.add_header("Authorization", f"Bearer {get_token()}")
    req.add_header("X-Tenant-ID", TENANT_ID)
    req.add_header("Content-Type", "application/json")
    req.add_header("Idempotency-Key", ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)))
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read().decode())
    except Exception as e: return {"error": str(e)}

# ===== 交互式 REPL =====
def interactive_mode():
    """交互式菜单模式"""
    print("\n" + "="*50)
    print("  AssetHub 交互式查询 (v4.0)")
    print("="*50)
    print(f"当前租户: {TENANT_ID} | 用户: {USERNAME}")
    print(f"缓存TTL: {CFG['cache_ttl']}秒 | Token缓存: {CFG['token_cache_seconds']}秒")
    print("="*50)
    
    while True:
        print("\n📋 功能菜单:")
        print("  1. 资产查询 (assets)")
        print("  2. 资产详情 (asset)")
        print("  3. 维修记录 (repair)")
        print("  4. 工单列表 (workorder)")
        print("  5. 维护计划 (plans)")
        print("  6. 部门统计 (stats-by-dept)")
        print("  7. 分类统计 (stats-by-category)")
        print("  8. 资产状态 (stats-by-status)")
        print("  9. 闲置资产 (idle-assets)")
        print(" 10. 即将过保 (expiring-warranty)")
        print(" 11. 统计概览 (stats)")
        print(" 12. 仪表盘 (dashboard)")
        print(" 13. 清除缓存")
        print(" 14. 切换租户")
        print("  0. 退出")
        
        choice = input("\n👉 请选择: ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            kw = input("关键词 (直接回车查全部): ").strip()
            query_assets(kw)
        elif choice == "2":
            aid = input("资产ID或编码: ").strip()
            query_asset_detail(aid)
        elif choice == "3":
            query_repairs()
        elif choice == "4":
            query_workorders()
        elif choice == "5":
            query_plans()
        elif choice == "6":
            query_stats_by_dept()
        elif choice == "7":
            query_stats_by_category()
        elif choice == "8":
            query_stats_by_status()
        elif choice == "9":
            query_idle_assets()
        elif choice == "10":
            days = input("天数 (默认30): ").strip()
            query_expiring_warranty(int(days) if days else 30)
        elif choice == "11":
            query_stats()
        elif choice == "12":
            dashboard()
        elif choice == "13":
            global _data_cache
            _data_cache = {}
            print("✅ 缓存已清除")
        elif choice == "14":
            new_tenant = input("新租户ID: ").strip()
            if new_tenant:
                # 修改全局变量需要先声明 global
                globals()['TENANT_ID'] = new_tenant
                globals()['_cached_token'] = None  # 清除 token 缓存
                print(f"✅ 已切换到租户: {new_tenant}")
        else:
            print("❌ 无效选择")

# 初始化时创建配置目录 (如果不存在)
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# 查询函数
def query_assets(kw=""):
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    print(f"{'编码':<22} {'名称':<28} {'部门':<20} {'状态':<6}")
    print("-"*78)
    c = 0
    for a in assets:
        if kw and kw not in a.get("asset_name","") and kw not in a.get("department_new",""): continue
        print(f"{a.get('asset_code','')[-20]:<22} {a.get('asset_name','')[:26]:<28} {a.get('department_new','')[:18]:<20} {a.get('status',''):<6}")
        c += 1
    print(f"\n共 {c} 条")

def query_asset_detail(aid):
    d = api_get(f"/assets/{aid}")
    if "error" in d: print(f"Error: {d['error']}"); return
    a = d.get("data",{})
    if not a: print("资产不存在"); return
    print("="*50); print("资产详情"); print("="*50)
    print(f"编码:{a.get('asset_code','-')}\n名称:{a.get('asset_name','-')}\n分类:{a.get('category_name','-')}")
    print(f"部门:{a.get('department_new','-')}\n地点:{a.get('location','-')}\n状态:{a.get('status','-')}")
    print(f"采购价:¥{float(a.get('purchase_price') or 0):,.2f}\n当前值:¥{float(a.get('current_value') or 0):,.2f}")

def query_repairs():
    d = api_get("/maintenance/requests", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for r in d.get("data",[]):
        print(f"{r.get('request_no',''):<22} {r.get('asset_name','')[:16]:<18} {r.get('fault_description','')[:16]:<18} {r.get('status',''):<8}")

def query_workorders():
    d = api_get("/maintenance/workorders", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for w in d.get("data",[]):
        print(f"{w.get('work_order_no',''):<22} {w.get('asset_name','')[:18]:<20} {w.get('status',''):<10} {w.get('priority',''):<6}")

def query_departments():
    d = api_get("/departments")
    if "error" in d: print(f"Error: {d['error']}"); return
    for dpt in d.get("data",[]):
        print(f"{dpt.get('department_code',''):<12} {dpt.get('department_name',''):<40}")

def query_dept_assets(dname):
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = [a for a in d.get("data",{}).get("list",[]) if dname in a.get("department_new","")]
    if not assets: print(f"未找到: {dname}"); return
    total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
    print(f"=== {dname} === 数量:{len(assets)} 价值:¥{total:,.0f}")

def query_plans():
    d = api_get("/maintenance/plans", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for p in d.get("data",[]):
        print(f"{p.get('plan_name',''):<28} {p.get('asset_code',''):<18} {p.get('status',''):<8}")

def query_costs():
    d = api_get("/maintenance/costs", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    total = sum(float(c.get("total_cost",0) or 0) for c in d.get("data",[]))
    print(f"维修费用合计: ¥{total:,.0f}")

def query_inventory():
    d = api_get("/inventory", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for t in d.get("data",[]):
        print(f"{t.get('plan_name',''):<28} {t.get('status',''):<10}")

def query_procurement():
    d = api_get("/procurement/requests", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for p in d.get("data",[]):
        print(f"{p.get('request_no',''):<22} {p.get('asset_name',''):<18} ¥{float(p.get('estimated_price',0) or 0):>10,.0f} {p.get('status',''):<8}")

def query_transfer():
    d = api_get("/transfer", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for t in d.get("data",[]):
        print(f"{t.get('transfer_no',''):<22} {t.get('asset_code',''):<18} {t.get('status',''):<10}")

def query_scrapping():
    d = api_get("/scrapping", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for s in d.get("data",[]):
        print(f"{s.get('request_no',''):<22} {s.get('asset_name',''):<18} {s.get('status',''):<10}")

def query_location(code):
    d = api_get(f"/asset-location/assets/{code}/location")
    if "error" in d: print(f"Error: {d['error']}"); return
    loc = d.get("data",{})
    if loc: print(f"位置: {loc.get('building_name','')} {loc.get('room_number','')} {loc.get('floor','')}")
    else: print(f"无位置数据")

def query_acceptance():
    d = api_get("/acceptance", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for a in d.get("data",[]):
        print(f"{a.get('acceptance_no',''):<22} {a.get('asset_name',''):<18} {a.get('status',''):<10}")

def query_metrology():
    d = api_get("/quality-control/metrology", {"page":1,"pageSize":50})
    if "error" in d: print(f"Error: {d['error']}"); return
    for m in d.get("data",[]):
        print(f"{m.get('device_name',''):<28} {m.get('result',''):<8}")

# 统计函数
def query_stats():
    print("📥 正在获取全部资产数据...")
    d = api_get("/assets", {"page":1,"pageSize":1000}, getAllPages=True)
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
    status, dept, cat = {}, {}, {}
    for a in assets:
        status[a.get("status","")] = status.get(a.get("status",""),0) + 1
        dept[a.get("department_new","")] = dept.get(a.get("department_new",""),0) + 1
        cat[a.get("category_name","")] = cat.get(a.get("category_name",""),0) + 1
    print("="*50); print("资产统计 (全量)"); print("="*50)
    print(f"总数:{len(assets)} 价值:¥{total:,.0f}")
    print(f"\n状态: {dict(sorted(status.items(), key=lambda x:-x[1]))}")
    print(f"\n部门TOP5: {dict(sorted(dept.items(), key=lambda x:-x[1])[:5])}")
    print(f"\n分类: {dict(sorted(cat.items(), key=lambda x:-x[1]))}")

def query_stats_by_dept():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    ds = {}
    for a in assets:
        dpt = a.get("department_new","未知")
        if dpt not in ds: ds[dpt] = {"c":0,"v":0}
        ds[dpt]["c"] += 1
        ds[dpt]["v"] += float(a.get("purchase_price",0) or 0)
    print("="*55); print("按部门统计"); print("="*55)
    for dpt,st in sorted(ds.items(), key=lambda x:-x[1]["v"]):
        print(f"{dpt:<28} {st['c']:>4}项 ¥{st['v']:>12,.0f}")

def query_stats_by_category():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    cs = {}
    for a in assets:
        c = a.get("category_name","未知")
        if c not in cs: cs[c] = {"c":0,"v":0}
        cs[c]["c"] += 1
        cs[c]["v"] += float(a.get("purchase_price",0) or 0)
    for c,st in sorted(cs.items(), key=lambda x:-x[1]["v"]):
        print(f"{c:<18} {st['c']:<4} ¥{st['v']:>12,.0f}")

def query_stats_by_status():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    ss = {}
    for a in assets:
        s = a.get("status","未知")
        if s not in ss: ss[s] = {"c":0,"v":0}
        ss[s]["c"] += 1
        ss[s]["v"] += float(a.get("purchase_price",0) or 0)
    for s,st in sorted(ss.items(), key=lambda x:-x[1]["v"]):
        pct = st['c']/len(assets)*100 if assets else 0
        print(f"{s:<8} {st['c']:<4} ¥{st['v']:>12,.0f} ({pct:.1f}%)")

def query_stats_value():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    ranges = [(0,1e3,"<1千"),(1e3,5e3,"1千-5千"),(5e3,1e4,"5千-1万"),(1e4,5e4,"1万-5万"),(5e4,1e5,"5万-10万"),(1e5,5e5,"10万-50万"),(5e5,1e9,">50万")]
    dist = {r[2]:0 for r in ranges}
    for a in assets:
        p = float(a.get("purchase_price",0) or 0)
        for l,h,n in ranges:
            if l<=p<h: dist[n]+=1; break
    for n,c in sorted(dist.items(), key=lambda x:x[1], reverse=True):
        if c: print(f"  {n:<12} {c:>4}")

def query_stats_age():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    now = datetime.now()
    ranges = [(0,1,"<1年"),(1,3,"1-3年"),(3,5,"3-5年"),(5,10,"5-10年"),(10,50,">10年")]
    dist = {r[2]:0 for r in ranges}
    for a in assets:
        pd = a.get("purchase_date")
        if pd:
            try:
                age = (now - datetime.strptime(pd[:10],"%Y-%m-%d")).days/365
                for l,h,n in ranges:
                    if l<=age<h: dist[n]+=1; break
            except: pass
    for n,c in sorted(dist.items()): print(f"  {n:<10} {c:>4}")

def query_top(n=15):
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = sorted(d.get("data",{}).get("list",[]), key=lambda x:float(x.get("purchase_price",0) or 0), reverse=True)
    for i,a in enumerate(assets[:n],1):
        p = float(a.get("purchase_price",0) or 0)
        if p: print(f"{i:<2} {a.get('asset_name','')[:26]:<28} ¥{p:>12,.0f} {a.get('department_new','')[:16]:<18}")

def query_idle_assets():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = [a for a in d.get("data",{}).get("list",[]) if a.get("status")=="闲置"]
    if assets: print(f"闲置资产: {len(assets)}")
    else: print("无闲置资产")

def query_expiring_warranty(days=30):
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    exp = []
    for a in assets:
        we = a.get("warranty_end_date")
        if we:
            try:
                left = (datetime.strptime(we[:10],"%Y-%m-%d")-datetime.now()).days
                if 0<=left<=days: exp.append({"a":a,"d":left})
            except: pass
    if exp:
        for e in sorted(exp, key=lambda x:x["d"])[:10]:
            print(f"  {e['a'].get('asset_name','')[:20]:<22} {e['d']}天")
    else: print(f"未来{days}天无过保")

def query_repair_trend():
    d = api_get("/maintenance/requests", {"page":1,"pageSize":100})
    if "error" in d: print(f"Error: {d['error']}"); return
    m = {}
    for r in d.get("data",[]):
        mm = r.get("created_at","")[:7]
        m[mm] = m.get(mm,0) + 1
    for mm,c in sorted(m.items(), reverse=True): print(f"  {mm}: {c}")

def query_repair_by_dept():
    d = api_get("/maintenance/requests", {"page":1,"pageSize":100})
    if "error" in d: print(f"Error: {d['error']}"); return
    dept = {}
    for r in d.get("data",[]):
        dpt = r.get("department","未知")
        dept[dpt] = dept.get(dpt,0) + 1
    for dpt,c in sorted(dept.items(), key=lambda x:-x[1]): print(f"  {dpt[:26]:<28}{c}")

# 分析函数
def analysis_full():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
    current = sum(float(a.get("current_value",0) or 0) for a in assets)
    print("="*60); print("📊 资产全量分析"); print("="*60)
    print(f"总数:{len(assets)} 采购值:¥{total:,.0f} 当前值:¥{current:,.0f}")
    print(f"折旧:¥{total-current:,.0f} ({(total-current)/total*100:.1f}%)" if total else "")
    rd = api_get("/maintenance/requests", {"page":1,"pageSize":50})
    if "error" not in rd: print(f"维修申请:{len(rd.get('data',[]))}")
    print("="*60)

def analysis_dept(name=""):
    if not name: name = input("部门:")
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = [a for a in d.get("data",{}).get("list",[]) if name in a.get("department_new","")]
    if not assets: print(f"未找到:{name}"); return
    total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
    print(f"=== {name} === 数量:{len(assets)} 价值:¥{total:,.0f}")

def analysis_repair():
    d = api_get("/maintenance/requests", {"page":1,"pageSize":100})
    if "error" in d: print(f"Error: {d['error']}"); return
    repairs = d.get("data",[])
    print(f"维修申请:{len(repairs)}")
    status = {}
    for r in repairs:
        s = r.get("status","")
        status[s] = status.get(s,0) + 1
    print(f"状态: {status}")

def analysis_warranty():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = d.get("data",{}).get("list",[])
    now = datetime.now()
    expired = expiring = valid = 0
    for a in assets:
        we = a.get("warranty_end_date")
        if we:
            try:
                days = (datetime.strptime(we[:10],"%Y-%m-%d")-now).days
                if days < 0: expired += 1
                elif days <= 30: expiring += 1
                else: valid += 1
            except: pass
    print(f"已过保:{expired} 30天内过保:{expiring} 在保:{valid}")

def analysis_depreciation():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = d.get("data",{}).get("list",[])
    total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
    current = sum(float(a.get("current_value",0) or 0) for a in assets)
    print(f"折旧分析: 原值¥{total:,.0f} 净值¥{current:,.0f} 折旧¥{total-current:,.0f}")

# 导出函数
def export_csv():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    fn = f"assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(fn, 'w', encoding='utf-8-sig') as f:
        f.write("编码,名称,分类,部门,状态,采购价\n")
        for a in assets:
            f.write(f"{a.get('asset_code','')},{a.get('asset_name','')},{a.get('category_name','')},{a.get('department_new','')},{a.get('status','')},{a.get('purchase_price',0)}\n")
    print(f"已导出: {fn}")

def export_summary():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = d.get("data",{}).get("list",[])
    depts = {}
    for a in assets:
        dpt = a.get("department_new","")
        if dpt not in depts: depts[dpt] = {"c":0,"v":0}
        depts[dpt]["c"] += 1
        depts[dpt]["v"] += float(a.get("purchase_price",0) or 0)
    fn = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(fn, 'w') as f:
        f.write("资产汇总报表\n="*30+"\n")
        f.write(f"总数:{len(assets)}\n")
        for dpt,st in sorted(depts.items(), key=lambda x:-x[1]["v"]):
            f.write(f"{dpt:<25} {st['c']:>4} ¥{st['v']:>12,.0f}\n")
    print(f"已导出: {fn}")

# 提醒函数
def check_warranty_reminder():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: print(f"Error: {d['error']}"); return
    assets = d.get("data",{}).get("list",[])
    now = datetime.now()
    reminders = []
    for a in assets:
        we = a.get("warranty_end_date")
        if we:
            try:
                end = datetime.strptime(we[:10],"%Y-%m-%d")
                days = (end - now).days
                if 0 < days <= 30: reminders.append({"a":a,"days":days})
            except: pass
    if reminders:
        print(f"⚠️ {len(reminders)} 项资产保修即将到期:")
        for r in sorted(reminders, key=lambda x:x["days"])[:10]:
            print(f"  {r['a'].get('asset_name','')[:20]:<20} 剩余{r['days']}天")
    else: print("✅ 无保修即将到期的资产")

def check_idle_reminder():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = [a for a in d.get("data",{}).get("list",[]) if a.get("status")=="闲置"]
    if assets:
        total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
        print(f"⚠️ 发现 {len(assets)} 项闲置资产, 总价值 ¥{total:,.0f}")
    else: print("✅ 无闲置资产")

def check_pending_repairs():
    d = api_get("/maintenance/requests", {"page":1,"pageSize":100})
    if "error" in d: return
    repairs = [r for r in d.get("data",[]) if r.get("status")=="待审批"]
    if repairs:
        print(f"⚠️ {len(repairs)} 项维修申请待审批:")
        for r in repairs[:5]:
            print(f"  {r.get('request_no',''):<20} {r.get('asset_name',''):<15} {r.get('fault_level',''):<4}")
    else: print("✅ 无待审批维修")

def daily_summary():
    print("\n" + "="*60)
    print("📋 每日资产汇总报告")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" not in d:
        assets = d.get("data",{}).get("list",[])
        total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
        idle = len([a for a in assets if a.get("status")=="闲置"])
        print(f"\n📊 资产: {len(assets)}项 ¥{total:,.0f} 闲置:{idle}")
    
    rd = api_get("/maintenance/requests", {"page":1,"pageSize":100})
    if "error" not in rd:
        repairs = rd.get("data",[])
        pending = len([r for r in repairs if r.get("status")=="待审批"])
        print(f"\n🔧 维修: {len(repairs)}项 待审批:{pending}")
    
    check_warranty_reminder()
    print("="*60 + "\n")

# 报表函数
def report_department_detail():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = d.get("data",{}).get("list",[])
    depts = {}
    for a in assets:
        dpt = a.get("department_new","未知")
        if dpt not in depts:
            depts[dpt] = {"total":0,"count":0,"categories":{}}
        depts[dpt]["total"] += float(a.get("purchase_price",0) or 0)
        depts[dpt]["count"] += 1
        cat = a.get("category_name","未知")
        depts[dpt]["categories"][cat] = depts[dpt]["categories"].get(cat,0) + 1
    
    print("\n部门资产详细报表")
    print("="*70)
    for dpt,st in sorted(depts.items(), key=lambda x:-x[1]["total"])[:10]:
        print(f"\n【{dpt}】")
        print(f"  资产数量: {st['count']}")
        print(f"  总价值: ¥{st['total']:,.0f}")
        print(f"  分类: {st['categories']}")

def report_category_detail():
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" in d: return
    assets = d.get("data",{}).get("list",[])
    cats = {}
    for a in assets:
        cat = a.get("category_name","未知")
        if cat not in cats:
            cats[cat] = {"total":0,"count":0,"depts":{}}
        cats[cat]["total"] += float(a.get("purchase_price",0) or 0)
        cats[cat]["count"] += 1
        dpt = a.get("department_new","未知")
        cats[cat]["depts"][dpt] = cats[cat]["depts"].get(dpt,0) + 1
    
    print("\n分类资产详细报表")
    print("="*70)
    for cat,st in sorted(cats.items(), key=lambda x:-x[1]["total"]):
        print(f"\n【{cat}】")
        print(f"  数量: {st['count']} 价值: ¥{st['total']:,.0f}")
        top_depts = sorted(st["depts"].items(), key=lambda x:-x[1])[:3]
        print(f"  主要部门: {dict(top_depts)}")

# 工具函数
def dashboard():
    print("\n" + "="*50)
    print("🏥 AssetHub 仪表盘")
    print("="*50)
    d = api_get("/assets", {"page":1,"pageSize":500})
    if "error" not in d:
        assets = d.get("data",{}).get("list",[])
        total = sum(float(a.get("purchase_price",0) or 0) for a in assets)
        idle = len([a for a in assets if a.get("status")=="闲置"])
        print(f"\n📊 资产: {len(assets)} 项, ¥{total:,.0f}, 闲置:{idle}")
    rd = api_get("/maintenance/requests", {"page":1,"pageSize":50})
    if "error" not in rd:
        repairs = rd.get("data",[])
        pending = len([r for r in repairs if r.get("status")=="待审批"])
        print(f"🔧 维修: {len(repairs)} 申请, {pending} 待审批")
    print("="*50 + "\n")

def validate():
    d = api_get("/assets", {"page":1,"pageSize":1})
    if "error" in d: print("❌ API失败")
    else: print("✅ API正常")

# Main
def main():
    # 交互式模式
    if len(sys.argv) == 2 and sys.argv[1] in ["-i", "--interactive", "interactive"]:
        interactive_mode()
        return
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n💡 提示: 使用 -i 进入交互式模式")
        return
    cmd = sys.argv[1].lower()
    arg = " ".join(sys.argv[2:])
    
    cmds = {
        # 查询
        "assets": lambda: query_assets(arg),
        "asset": lambda: query_asset_detail(arg or input("ID:")),
        "repair": query_repairs,
        "workorder": query_workorders,
        "plans": query_plans,
        "costs": query_costs,
        "dept": query_departments,
        "department": query_departments,
        "dept-assets": lambda: query_dept_assets(arg or input("部门:")),
        "inventory": query_inventory,
        "procurement": query_procurement,
        "transfer": query_transfer,
        "scrapping": query_scrapping,
        "location": lambda: query_location(arg or input("编码:")),
        "acceptance": query_acceptance,
        "metrology": query_metrology,
        # 统计
        "stats": query_stats,
        "stats-by-dept": query_stats_by_dept,
        "stats-by-category": query_stats_by_category,
        "stats-by-status": query_stats_by_status,
        "stats-value": query_stats_value,
        "stats-age": query_stats_age,
        "top": lambda: query_top(int(arg) if arg else 10),
        "idle-assets": query_idle_assets,
        "expiring-warranty": lambda: query_expiring_warranty(int(arg) if arg else 30),
        "repair-trend": query_repair_trend,
        "repair-by-dept": query_repair_by_dept,
        # 分析
        "analysis-full": analysis_full,
        "analysis-dept": lambda: analysis_dept(arg),
        "analysis-repair": analysis_repair,
        "analysis-warranty": analysis_warranty,
        "analysis-depreciation": analysis_depreciation,
        # 导出
        "export-csv": export_csv,
        "export-summary": export_summary,
        # 提醒
        "warranty-reminder": check_warranty_reminder,
        "idle-reminder": check_idle_reminder,
        "pending-reminder": check_pending_repairs,
        "daily-summary": daily_summary,
        # 报表
        "report-dept": report_department_detail,
        "report-category": report_category_detail,
        # 工具
        "dashboard": dashboard,
        "validate": validate,
        "help": lambda: print(__doc__),
    }
    
    if cmd in cmds:
        cmds[cmd]()
    else:
        print(f"未知: {cmd}")

if __name__ == "__main__":
    main()
