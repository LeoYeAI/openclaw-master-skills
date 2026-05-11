-- 基于"请假申请单"创建新的"员工考勤管理表"
-- 源表单 ID: 777082588573766

INSERT INTO rf_form (id, name, type, createuserid, createusername, createtime, manageuser, html, subtablejson, eventjson, attrjson, defaultvaluejson, selectoptionsjson, fieldsjson, runhtml, status, note)
VALUES 
(777082588573770,  -- 新 ID: MAX(id)+1 = 777082588573770
 '员工考勤管理表',   -- name 修改为考勤主题
 1,                   -- type (沿用原表单类型)
 474677292343365,    -- createuserid (沿用原作者 ID)
 'admin',            -- createusername
 NOW(),              -- createtime (当前时间)
 'u_457447463223365,u_474677292343365,u_480697084178501',  -- manageuser (沿用)
 '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>员工考勤管理表</title></head><body style="font-family: Arial, sans-serif; padding:20px;"><h2 style="text-align:center;">📋 员工考勤管理表</h2><div style="border:1px solid #ccc; padding:15px; border-radius:8px; background:#fafafa;"><table style="width:100%; border-collapse:collapse;"><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>工号：</label></td><td style="padding:8px; border:1px solid #ddd;"><input type="text" name="empno" style="width:80px;"></td></tr><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>姓名：</label></td><td style="padding:8px; border:1px solid #ddd;"><input type="text" name="empname" style="width:80px;"></td></tr><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>部门：</label></td><td style="padding:8px; border:1px solid #ddd;"><input type="text" name="department" style="width:100px;"></td></tr><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>打卡日期：</label></td><td style="padding:8px; border:1px solid #ddd;"><input type="date" name="checkindate"></td></tr><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>出勤时间：</label></td><td style="padding:8px; border:1px solid #ddd;"><input type="time" name="starttime"></td></tr><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>出工类型：</label></td><td style="padding:8px; border:1px solid #ddd;">
  <select name="attendance_type">
    <option value="normal">正常出勤</option>
    <option value="late">迟到</option>
    <option value="early_leave">早退</option>
    <option value="absent">缺勤</option>
  </select></td></tr><tr><td style="padding:8px; border:1px solid #ddd; text-align:right;"><label>备注：</label></td><td style="padding:8px; border:1px solid #ddd;"><textarea name="note" rows="3"></textarea></td></tr><tr><td colspan="2" style="text-align:center; padding-top:10px;"><button type="submit" style="background:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:4px; cursor:pointer;">提交考勤记录</button></td></tr></table></div></body></html>',
 '[]',                -- subtablejson (空数组)
 '{}',               -- eventjson (空对象)
 '{}',               -- attrjson (空对象)
 '{}',               -- defaultvaluejson (空对象)
 '{}',               -- selectoptionsjson (空对象)
 '[{"id":"empno","type":"string","label":"工号"},{"id":"empname","type":"string","label":"姓名"},{"id":"department","type":"string","label":"部门"},{"id":"checkindate","type":"date","label":"打卡日期"},{"id":"starttime","type":"time","label":"出勤时间"},{"id":"attendance_type","type":"select","label":"出勤类型","options":["normal","late","early_leave","absent"]},{"id":"note","type":"textarea","label":"备注"}]',  -- fieldsjson (考勤主题字段)
 '',                 -- runhtml
 1,                  -- status (启用)
 '基于"请假申请单"模板生成，添加考勤主题字段'
);
