/**
 * 宜搭服务端开放API使用示例
 * 
 * 根据文档: https://developers.aliwork.com/docs/api/serverAPI
 * 
 * 宜搭平台除了提供用于在 Client 端调用的开放 API，还提供了支持通过服务端进行调用的开放 API
 */

/**
 * 1. 获取 access_token
 * access_token 相当于是身份凭证，调用接口时通过 access_token 来鉴权调用者身份
 */
class YidaServerAPI {
  constructor(appKey, appSecret, baseUrl = 'https://oapi.dingtalk.com') {
    this.appKey = appKey;
    this.appSecret = appSecret;
    this.baseUrl = baseUrl;
    this.accessToken = null;
    this.tokenExpireTime = 0;
  }

  /**
   * 获取 access_token
   * 企业内部应用和第三方企业应用获取方式有所不同
   */
  async getAccessToken() {
    // 检查是否已存在有效token
    if (this.accessToken && Date.now() < this.tokenExpireTime) {
      return this.accessToken;
    }

    try {
      const response = await fetch(`${this.baseUrl}/gettoken?appkey=${this.appKey}&appsecret=${this.appSecret}`);
      const data = await response.json();
      
      if (data.errcode === 0) {
        this.accessToken = data.access_token;
        // 设置过期时间，提前60秒刷新
        this.tokenExpireTime = Date.now() + (data.expires_in - 60) * 1000;
        return this.accessToken;
      } else {
        throw new Error(`获取 access_token 失败: ${data.errmsg}`);
      }
    } catch (error) {
      console.error('获取 access_token 异常:', error);
      throw error;
    }
  }

  /**
   * 发起宜搭审批流程
   * POST https://oapi.dingtalk.com/yida/process/start
   */
  async startProcess(processCode, processName, formContent, userId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/process/start?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processCode: processCode,
          processName: processName,
          formContent: formContent, // 表单内容
          userId: userId // 发起人用户ID
        })
      });

      return await response.json();
    } catch (error) {
      console.error('发起审批流程异常:', error);
      throw error;
    }
  }

  /**
   * 删除流程实例
   */
  async deleteProcessInstance(processInstanceId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/process/instance/delete?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processInstanceId: processInstanceId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('删除流程实例异常:', error);
      throw error;
    }
  }

  /**
   * 终止流程实例
   */
  async terminateProcessInstance(processInstanceId, reason) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/process/instance/terminate?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processInstanceId: processInstanceId,
          reason: reason
        })
      });

      return await response.json();
    } catch (error) {
      console.error('终止流程实例异常:', error);
      throw error;
    }
  }

  /**
   * 查询表单实例数据
   */
  async queryFormInstanceData(formUuid, processInstanceId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/form/instance/query?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          formUuid: formUuid,
          processInstanceId: processInstanceId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('查询表单实例数据异常:', error);
      throw error;
    }
  }

  /**
   * 保存表单数据
   */
  async saveFormData(formUuid, formData, userId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/form/data/save?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          formUuid: formUuid,
          formData: formData,
          userId: userId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('保存表单数据异常:', error);
      throw error;
    }
  }

  /**
   * 更新表单数据
   */
  async updateFormData(formUuid, formInstanceId, updateFormData, userId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/form/data/update?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          formUuid: formUuid,
          formInstanceId: formInstanceId,  // 需要更新的具体实例ID
          updateFormData: updateFormData,
          userId: userId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('更新表单数据异常:', error);
      throw error;
    }
  }

  /**
   * 查询表单数据
   */
  async queryFormData(formUuid, queryConditions) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/form/data/query?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          formUuid: formUuid,
          queryConditions: queryConditions
        })
      });

      return await response.json();
    } catch (error) {
      console.error('查询表单数据异常:', error);
      throw error;
    }
  }

  /**
   * 删除表单数据
   */
  async deleteFormData(formUuid, formInstanceId, userId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/form/data/delete?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          formUuid: formUuid,
          formInstanceId: formInstanceId,
          userId: userId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('删除表单数据异常:', error);
      throw error;
    }
  }

  /**
   * 获取审批记录
   */
  async getApprovalRecord(processInstanceId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/approval/record/query?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          processInstanceId: processInstanceId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('获取审批记录异常:', error);
      throw error;
    }
  }

  /**
   * 同意或拒绝审批任务
   */
  async executeApprovalTask(taskId, action, comment, userId) {
    try {
      const token = await this.getAccessToken();
      const response = await fetch(`${this.baseUrl}/yida/approval/task/execute?access_token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          taskId: taskId,
          action: action,  // 'agree' 或 'reject'
          comment: comment,
          userId: userId
        })
      });

      return await response.json();
    } catch (error) {
      console.error('执行审批任务异常:', error);
      throw error;
    }
  }
}

/**
 * 使用示例
 */
async function example() {
  // 创建API实例 - 需要配置自己的appKey和appSecret
  const yidaAPI = new YidaServerAPI(
    'your_app_key', 
    'your_app_secret'
  );

  try {
    // 示例1: 发起审批流程
    const processResult = await yidaAPI.startProcess(
      'PROC-XXXXX',  // 流程定义编码
      '请假申请',      // 流程名称
      {              // 表单内容
        '请假类型': '年假',
        '请假天数': 3,
        '开始时间': '2024-01-01',
        '结束时间': '2024-01-03',
        '请假原因': '个人事务'
      },
      'userId123'    // 发起人用户ID
    );
    console.log('发起流程结果:', processResult);

    // 示例2: 保存表单数据
    const saveResult = await yidaAPI.saveFormData(
      'FORM-XXXXX',   // 表单UUID
      {               // 表单数据
        '姓名': '张三',
        '部门': '技术部',
        '职位': '工程师'
      },
      'userId123'     // 操作人用户ID
    );
    console.log('保存表单数据结果:', saveResult);

    // 示例3: 查询表单数据
    const queryResult = await yidaAPI.queryFormData(
      'FORM-XXXXX',   // 表单UUID
      {               // 查询条件
        'filter': [
          { 'field': '姓名', 'operator': 'eq', 'value': '张三' }
        ],
        'pageNo': 1,
        'pageSize': 20
      }
    );
    console.log('查询表单数据结果:', queryResult);

  } catch (error) {
    console.error('API调用异常:', error);
  }
}

// 导出类供使用
module.exports = YidaServerAPI;