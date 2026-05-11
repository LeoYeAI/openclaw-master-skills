/**
 * 宜搭平台前后端API集成示例
 * 
 * 演示如何将服务端开放API与客户端JS-API结合使用
 */

/**
 * 1. 服务端API管理器
 * 用于处理需要在服务端执行的操作
 */
class ServerAPIManager {
  constructor(config) {
    this.config = config;
    this.accessToken = null;
    this.tokenExpireTime = 0;
  }

  /**
   * 获取访问令牌
   */
  async getAccessToken() {
    if (this.accessToken && Date.now() < this.tokenExpireTime) {
      return this.accessToken;
    }

    try {
      const response = await fetch(`${this.config.baseUrl}/gettoken?appkey=${this.config.appKey}&appsecret=${this.config.appSecret}`);
      const data = await response.json();
      
      if (data.errcode === 0) {
        this.accessToken = data.access_token;
        this.tokenExpireTime = Date.now() + (data.expires_in - 300) * 1000; // 提前5分钟刷新
        return this.accessToken;
      } else {
        throw new Error(`获取令牌失败: ${data.errmsg}`);
      }
    } catch (error) {
      console.error('获取访问令牌失败:', error);
      throw error;
    }
  }

  /**
   * 创建远程数据服务
   */
  async callRemoteAPI(endpoint, data) {
    const accessToken = await this.getAccessToken();
    
    const response = await fetch(`${this.config.baseUrl}${endpoint}?access_token=${accessToken}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    return await response.json();
  }

  /**
   * 审批流程相关API
   */
  async startApprovalProcess(processCode, formContent, userId) {
    return this.callRemoteAPI('/yida/process/start', {
      processCode,
      processName: processCode, // 可以从配置中获取名称
      formContent,
      userId
    });
  }

  /**
   * 数据管理API
   */
  async manageFormData(operation, params) {
    const endpoints = {
      query: '/yida/form/data/query',
      save: '/yida/form/data/save',
      update: '/yida/form/data/update',
      delete: '/yida/form/data/delete'
    };

    return this.callRemoteAPI(endpoints[operation], params);
  }
}

/**
 * 2. 客户端API包装器
 * 用于统一处理客户端API调用
 */
class ClientAPIWrapper {
  constructor(context) {
    this.context = context;
  }

  /**
   * 组件操作封装
   */
  getComponentValue(alias) {
    try {
      const component = this.context.$(alias);
      return component ? component.getValue() : null;
    } catch (error) {
      console.error(`获取组件 ${alias} 值失败:`, error);
      return null;
    }
  }

  setComponentValue(alias, value) {
    try {
      const component = this.context.$(alias);
      if (component) {
        component.setValue(value);
      }
    } catch (error) {
      console.error(`设置组件 ${alias} 值失败:`, error);
    }
  }

  validateComponent(alias) {
    try {
      const component = this.context.$(alias);
      return component ? component.validate() : false;
    } catch (error) {
      console.error(`校验组件 ${alias} 失败:`, error);
      return false;
    }
  }

  /**
   * 表单操作封装
   */
  validateForm(callback) {
    return this.context.validateForm(callback);
  }

  getFormData() {
    return this.context.getFormData();
  }

  setFormData(data) {
    return this.context.setFormData(data);
  }

  /**
   * 工具函数封装
   */
  showToast(title, type = 'info') {
    this.context.utils.toast({ title, type });
  }

  showDialog(options) {
    return this.context.utils.dialog(options);
  }

  navigateTo(path, params) {
    this.context.utils.router.push(path, params);
  }

  getCurrentUserId() {
    return this.context.utils.getLoginUserId();
  }

  /**
   * 数据源操作封装
   */
  callDataSource(dataSourceName, params) {
    if (this.context.dataSourceMap && this.context.dataSourceMap[dataSourceName]) {
      return this.context.dataSourceMap[dataSourceName].load(params);
    }
    return Promise.reject(new Error(`数据源 ${dataSourceName} 不存在`));
  }

  reloadDataSource() {
    if (typeof this.context.reloadDataSource === 'function') {
      return this.context.reloadDataSource();
    }
  }
}

/**
 * 3. 业务逻辑处理器
 * 整合客户端和服务端API，处理具体业务场景
 */
class BusinessLogicHandler {
  constructor(context, serverConfig) {
    this.client = new ClientAPIWrapper(context);
    this.server = new ServerAPIManager(serverConfig);
    this.context = context;
  }

  /**
   * 处理请假申请流程
   */
  async handleLeaveApplication() {
    // 1. 客户端校验
    const startDate = this.client.getComponentValue('startDate');
    const endDate = this.client.getComponentValue('endDate');
    const reason = this.client.getComponentValue('reason');
    const leaveType = this.client.getComponentValue('leaveType');

    if (!startDate || !endDate || !reason || !leaveType) {
      this.client.showToast('请填写完整信息', 'error');
      return false;
    }

    // 2. 数据格式化
    const formData = {
      '请假类型': leaveType,
      '开始日期': startDate,
      '结束日期': endDate,
      '请假原因': reason,
      '申请人': this.client.getCurrentUserId(),
      '申请时间': new Date().toISOString()
    };

    try {
      // 3. 调用服务端API发起审批
      const result = await this.server.startApprovalProcess(
        'LEAVE_APPLICATION', // 流程编码
        formData,
        this.client.getCurrentUserId()
      );

      if (result.errcode === 0) {
        this.client.showToast('申请已提交', 'success');
        // 重置表单
        this.client.setFormData({});
        return true;
      } else {
        this.client.showToast(`申请失败: ${result.errmsg}`, 'error');
        return false;
      }
    } catch (error) {
      console.error('处理请假申请失败:', error);
      this.client.showToast('系统错误，请稍后重试', 'error');
      return false;
    }
  }

  /**
   * 处理员工考勤打卡
   */
  async handleAttendancePunch() {
    const punchType = this.client.getComponentValue('punchType');
    const location = await this.getCurrentLocation(); // 需要实现位置获取
    
    if (!punchType) {
      this.client.showToast('请选择打卡类型', 'error');
      return false;
    }

    try {
      // 保存打卡记录
      const punchData = {
        '打卡类型': punchType,
        '打卡时间': new Date().toISOString(),
        '打卡人员': this.client.getCurrentUserId(),
        '打卡位置': location,
        '设备信息': this.getDeviceInfo()
      };

      const result = await this.server.manageFormData('save', {
        formUuid: 'ATTENDANCE_FORM',
        formData: punchData,
        userId: this.client.getCurrentUserId()
      });

      if (result.errcode === 0) {
        this.client.showToast(`${punchType}打卡成功`, 'success');
        return true;
      } else {
        this.client.showToast(`打卡失败: ${result.errmsg}`, 'error');
        return false;
      }
    } catch (error) {
      console.error('处理考勤打卡失败:', error);
      this.client.showToast('打卡失败，请检查网络', 'error');
      return false;
    }
  }

  /**
   * 获取当前位置（模拟实现）
   */
  async getCurrentLocation() {
    return new Promise((resolve) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
              accuracy: position.coords.accuracy
            });
          },
          () => {
            // 如果无法获取精确位置，返回默认值
            resolve({
              latitude: 0,
              longitude: 0,
              accuracy: '无法获取位置'
            });
          }
        );
      } else {
        resolve({
          latitude: 0,
          longitude: 0,
          accuracy: '浏览器不支持位置服务'
        });
      }
    });
  }

  /**
   * 获取设备信息
   */
  getDeviceInfo() {
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language
    };
  }

  /**
   * 处理数据查询
   */
  async handleDataQuery(formUuid, conditions) {
    try {
      const result = await this.server.manageFormData('query', {
        formUuid: formUuid,
        queryConditions: conditions
      });

      if (result.errcode === 0) {
        // 在客户端更新状态
        this.context.setState({
          queryResult: result.data
        });
        return result.data;
      } else {
        throw new Error(result.errmsg);
      }
    } catch (error) {
      console.error('数据查询失败:', error);
      this.client.showToast('查询失败: ' + error.message, 'error');
      return null;
    }
  }

  /**
   * 处理批量操作
   */
  async handleBatchOperation(operation, items) {
    if (!items || items.length === 0) {
      this.client.showToast('没有选择任何项目', 'warning');
      return false;
    }

    try {
      // 可以根据操作类型执行不同的批量处理
      switch (operation) {
        case 'approve':
          return await this.batchApprove(items);
        case 'reject':
          return await this.batchReject(items);
        case 'delete':
          return await this.batchDelete(items);
        default:
          throw new Error('不支持的操作类型');
      }
    } catch (error) {
      console.error(`批量${operation}失败:`, error);
      this.client.showToast(`批量操作失败: ${error.message}`, 'error');
      return false;
    }
  }

  /**
   * 批量审批
   */
  async batchApprove(items) {
    // 实现批量审批逻辑
    // 可以通过服务端API逐个处理或使用批量接口
    let successCount = 0;
    let failCount = 0;

    for (const item of items) {
      try {
        // 调用单个审批接口
        // await this.server.executeApproval(item.id, 'approve');
        successCount++;
      } catch (error) {
        failCount++;
      }
    }

    if (failCount === 0) {
      this.client.showToast(`批量审批完成，成功${successCount}个`, 'success');
    } else {
      this.client.showToast(`批量审批完成，成功${successCount}个，失败${failCount}个`, 'warning');
    }

    return true;
  }

  /**
   * 批量驳回
   */
  async batchReject(items) {
    // 类似批量审批逻辑
    return true;
  }

  /**
   * 批量删除
   */
  async batchDelete(items) {
    // 实现批量删除逻辑
    return true;
  }
}

/**
 * 4. 实际使用示例
 */
export class PracticalExample {
  constructor() {
    this.state = {
      loading: false,
      data: [],
      filters: {}
    };
  }

  /**
   * 初始化业务处理器
   */
  initBusinessHandler() {
    // 服务器配置
    const serverConfig = {
      appKey: 'your_app_key',
      appSecret: 'your_app_secret',
      baseUrl: 'https://oapi.dingtalk.com'
    };

    // 创建业务逻辑处理器
    this.handler = new BusinessLogicHandler(this, serverConfig);
  }

  /**
   * 页面加载完成
   */
  export function didMount() {
    this.initBusinessHandler();
    
    // 加载初始数据
    this.loadInitialData();
  }

  /**
   * 加载初始数据
   */
  async loadInitialData() {
    try {
      this.setState({ loading: true });
      
      // 通过服务端API获取数据
      const data = await this.handler.handleDataQuery('EMPLOYEE_FORM', {
        filter: { 'status': 'active' },
        pageNo: 1,
        pageSize: 50
      });

      if (data) {
        this.setState({
          data: data,
          loading: false
        });
      }
    } catch (error) {
      console.error('加载初始数据失败:', error);
      this.setState({ loading: false });
    }
  }

  /**
   * 提交表单
   */
  export async function onSubmit() {
    // 根据当前页面功能调用相应的处理方法
    const pageType = this.utils.router.getQuery('type');
    
    switch (pageType) {
      case 'leave':
        await this.handler.handleLeaveApplication();
        break;
      case 'attendance':
        await this.handler.handleAttendancePunch();
        break;
      default:
        // 处理通用表单提交
        if (this.validateForm()) {
          this.submitGenericForm();
        }
    }
  }

  /**
   * 通用表单提交
   */
  async submitGenericForm() {
    try {
      const formData = this.getFormData();
      
      // 通过服务端API保存数据
      const result = await this.handler.server.manageFormData('save', {
        formUuid: 'GENERIC_FORM',
        formData: formData,
        userId: this.utils.getLoginUserId()
      });

      if (result.errcode === 0) {
        this.utils.toast({ title: '提交成功', type: 'success' });
        this.utils.router.back();
      } else {
        throw new Error(result.errmsg);
      }
    } catch (error) {
      console.error('提交表单失败:', error);
      this.utils.toast({ title: '提交失败: ' + error.message, type: 'error' });
    }
  }

  /**
   * 搜索功能
   */
  export async function onSearch(keyword) {
    try {
      const result = await this.handler.handleDataQuery('SEARCH_FORM', {
        filter: [
          { field: 'name', operator: 'like', value: keyword },
          { field: 'status', operator: 'eq', value: 'active' }
        ],
        pageNo: 1,
        pageSize: 20
      });

      if (result) {
        this.setState({ data: result });
      }
    } catch (error) {
      console.error('搜索失败:', error);
    }
  }

  /**
   * 刷新数据
   */
  export async function onRefresh() {
    await this.loadInitialData();
  }

  /**
   * 批量操作
   */
  export async function onBatchOperation(operation, selectedItems) {
    await this.handler.handleBatchOperation(operation, selectedItems);
  }
}

// 导出主要类供使用
export {
  ServerAPIManager,
  ClientAPIWrapper,
  BusinessLogicHandler
};