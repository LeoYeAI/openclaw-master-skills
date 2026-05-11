/**
 * 宜搭客户端API使用示例
 * 
 * 包含宜搭 JS-API、跨应用数据源API和钉钉 JS-API的使用示例
 */

/**
 * 1. 宜搭 JS-API 使用示例
 */
export class YidaClientAPI {
  constructor() {
    // 宜搭自定义页面的上下文环境
    this.context = null;
  }

  /**
   * 组件操作API使用示例
   */
  componentOperations() {
    // 获取组件值
    const fieldValue = this.$('field').getValue();
    
    // 设置组件值
    this.$('field').setValue('new value');
    
    // 设置组件状态
    this.$('field').setBehavior('READONLY');  // READONLY/DISABLED/HIDDEN/NORMAL
    
    // 组件校验
    const isValid = this.$('field').validate();
    this.$('field').setValidation([
      { type: 'required', message: '必填' },
      { type: 'email', message: '邮箱格式错误' }
    ]);
  }

  /**
   * 表单操作API使用示例
   */
  formOperations() {
    // 整表校验
    this.validateForm((errors) => {
      if (errors) {
        console.log('校验失败', errors);
        return;
      }
      console.log('校验通过');
    });

    // 获取/设置表单数据
    const formData = this.getFormData();
    this.setFormData({ field1: 'value1', field2: 'value2' });
  }

  /**
   * 工具函数API使用示例
   */
  utilsOperations() {
    // 消息提示
    this.utils.toast({ title: '操作成功', type: 'success' });
    
    // 对话框
    this.utils.dialog({
      type: 'confirm',
      title: '确认操作',
      content: '确定要执行此操作吗？',
      onOk: () => {
        console.log('用户点击确定');
      },
      onCancel: () => {
        console.log('用户点击取消');
      }
    });

    // 路由跳转
    this.utils.router.push('/pageId', { id: 1, name: 'test' });
    const id = this.utils.router.getQuery('id');
    
    // 用户信息
    const userId = this.utils.getLoginUserId();
    const userName = this.utils.getLoginUserName();
    
    // 环境判断
    const isMobile = this.utils.isMobile();
    const isDingTalk = this.utils.isDingTalk();
    
    // 日期格式化
    const formattedDate = this.utils.formatter('date', new Date(), 'YYYY-MM-DD HH:mm:ss');
    
    // 数字格式化
    const formattedMoney = this.utils.formatter('money', 1234.56);
  }

  /**
   * 数据源API使用示例
   */
  dataSourceOperations() {
    // 调用数据源
    this.dataSourceMap.apiName.load({ param: 'value' })
      .then(res => {
        console.log('数据源返回:', res);
      })
      .catch(err => {
        console.error('数据源错误:', err);
      });

    // 刷新数据源
    this.reloadDataSource();
    this.dataSourceMap.apiName.reload();
    
    // 获取数据源状态
    const status = this.dataSourceMap.apiName.status; // 'init' | 'loading' | 'success' | 'error'
    const data = this.dataSourceMap.apiName.data;
    const error = this.dataSourceMap.apiName.error;
  }

  /**
   * 生命周期方法
   */
  // 页面加载完成
  export function didMount() {
    console.log('页面加载完成');
    // 初始化操作
    
    // 获取页面参数
    const params = this.utils.router.getQueries();
    console.log('页面参数:', params);
  }

  // 页面卸载前
  export function willUnmount() {
    console.log('页面即将卸载');
    // 清理操作
  }

  // 页面参数变化
  export function onRouteChange(query) {
    console.log('路由参数变化:', query);
  }
}

/**
 * 2. 跨应用数据源API使用示例
 * 用于在不同宜搭应用间进行数据交互
 */
export class CrossAppDataSource {
  /**
   * 查询其他应用的表单数据
   */
  async queryCrossAppData(appId, formUuid, conditions = {}) {
    try {
      // 这通常通过配置数据源来实现，这里是概念示例
      const response = await this.dataSourceMap.crossAppQuery.load({
        appId: appId,
        formUuid: formUuid,
        conditions: conditions
      });
      
      return response;
    } catch (error) {
      console.error('跨应用数据查询失败:', error);
      throw error;
    }
  }

  /**
   * 调用其他应用的流程
   */
  async triggerCrossAppProcess(appId, processCode, formData) {
    try {
      const response = await this.dataSourceMap.crossAppProcess.load({
        appId: appId,
        processCode: processCode,
        formData: formData
      });
      
      return response;
    } catch (error) {
      console.error('跨应用流程调用失败:', error);
      throw error;
    }
  }
}

/**
 * 3. 钉钉 JS-API 使用示例
 * 宜搭运行在钉钉环境中，可以使用钉钉提供的API
 */
export class DingTalkAPI {
  /**
   * 获取钉钉用户信息
   */
  async getUserInfo() {
    try {
      // 使用钉钉API获取用户信息
      const dd = window.dd;
      if (dd) {
        const userInfo = await new Promise((resolve, reject) => {
          dd.ready(() => {
            dd.runtime.permission.requestAuthCode({
              corpId: 'your_corp_id', // 需要替换为实际的corpId
              onSuccess: (info) => {
                // 通过authCode获取用户信息
                resolve(info);
              },
              onFail: (err) => {
                reject(err);
              }
            });
          });
        });
        return userInfo;
      }
    } catch (error) {
      console.error('获取钉钉用户信息失败:', error);
      throw error;
    }
  }

  /**
   * 调用钉钉上传文件
   */
  async uploadFile() {
    try {
      const dd = window.dd;
      if (dd) {
        return new Promise((resolve, reject) => {
          dd.ready(() => {
            dd.biz.util.uploadImage({
              multiple: true,
              maxWidth: 0,
              maxHeight: 0,
              compress: true,
              onSuccess: (data) => {
                resolve(data);
              },
              onFail: (err) => {
                reject(err);
              }
            });
          });
        });
      }
    } catch (error) {
      console.error('钉钉文件上传失败:', error);
      throw error;
    }
  }

  /**
   * 调用钉钉通讯录选人
   */
  async selectUsers() {
    try {
      const dd = window.dd;
      if (dd) {
        return new Promise((resolve, reject) => {
          dd.ready(() => {
            dd.biz.contact.choose({
              startWithCorp: true,
              corpId: 'your_corp_id',
              isMulti: true,
              selectedUsers: [],
              disabledUsers: [],
              onSuccess: (data) => {
                resolve(data);
              },
              onFail: (err) => {
                reject(err);
              }
            });
          });
        });
      }
    } catch (error) {
      console.error('钉钉选人失败:', error);
      throw error;
    }
  }
}

/**
 * 4. 完整的自定义页面示例
 */
export class TodoPageExample {
  constructor() {
    // 初始化状态
    this.state = {
      todoList: [],
      newTodoText: '',
      filter: 'all'  // all, active, completed
    };
  }

  /**
   * 组件挂载时加载数据
   */
  export function didMount() {
    this.loadTodoList();
  }

  /**
   * 加载待办事项列表
   */
  async loadTodoList() {
    try {
      // 调用数据源获取待办事项
      const response = await this.dataSourceMap.getTodos.load();
      this.setState({
        todoList: response.data || []
      });
    } catch (error) {
      console.error('加载待办事项失败:', error);
      this.utils.toast({ title: '加载失败', type: 'error' });
    }
  }

  /**
   * 添加新待办事项
   */
  async addTodo() {
    const { newTodoText } = this.state;
    if (!newTodoText.trim()) {
      this.utils.toast({ title: '请输入待办事项', type: 'warning' });
      return;
    }

    try {
      // 调用保存接口
      const response = await this.dataSourceMap.addTodo.load({
        content: newTodoText,
        status: 'pending'
      });

      if (response.success) {
        // 更新本地状态
        this.setState({
          todoList: [
            {
              id: response.data.id,
              content: newTodoText,
              status: 'pending'
            },
            ...this.state.todoList
          ],
          newTodoText: ''
        });

        // 清空输入框
        this.$('todoInput').setValue('');
        
        this.utils.toast({ title: '添加成功', type: 'success' });
      }
    } catch (error) {
      console.error('添加待办事项失败:', error);
      this.utils.toast({ title: '添加失败', type: 'error' });
    }
  }

  /**
   * 切换待办事项状态
   */
  async toggleTodoStatus(itemId, currentStatus) {
    try {
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
      await this.dataSourceMap.updateTodo.load({
        id: itemId,
        status: newStatus
      });

      // 更新本地状态
      this.setState({
        todoList: this.state.todoList.map(item => {
          if (item.id === itemId) {
            return { ...item, status: newStatus };
          }
          return item;
        })
      });
    } catch (error) {
      console.error('更新待办事项状态失败:', error);
      this.utils.toast({ title: '操作失败', type: 'error' });
    }
  }

  /**
   * 删除待办事项
   */
  async deleteTodo(itemId) {
    try {
      await this.dataSourceMap.deleteTodo.load({
        id: itemId
      });

      // 更新本地状态
      this.setState({
        todoList: this.state.todoList.filter(item => item.id !== itemId)
      });
    } catch (error) {
      console.error('删除待办事项失败:', error);
      this.utils.toast({ title: '删除失败', type: 'error' });
    }
  }

  /**
   * 输入框值变化处理
   */
  export function onTodoInputChange({ value }) {
    this.setState({ newTodoText: value });
  }

  /**
   * 输入框按键处理（回车添加）
   */
  export function onTodoInputKeyDown(e) {
    if (e.keyCode === 13) {  // 回车键
      this.addTodo();
    }
  }

  /**
   * 过滤器变化处理
   */
  export function onFilterChange({ value }) {
    this.setState({ filter: value });
  }

  /**
   * 根据过滤器获取显示的列表
   */
  getFilteredTodoList() {
    const { todoList, filter } = this.state;
    
    switch (filter) {
      case 'active':
        return todoList.filter(item => item.status === 'pending');
      case 'completed':
        return todoList.filter(item => item.status === 'completed');
      default:
        return todoList;
    }
  }

  /**
   * 获取待完成数量
   */
  getPendingCount() {
    return this.state.todoList.filter(item => item.status === 'pending').length;
  }

  /**
   * 清除已完成的待办事项
   */
  async clearCompleted() {
    try {
      const completedIds = this.state.todoList
        .filter(item => item.status === 'completed')
        .map(item => item.id);

      if (completedIds.length === 0) {
        this.utils.toast({ title: '没有已完成的事项', type: 'info' });
        return;
      }

      await this.dataSourceMap.batchDeleteTodos.load({
        ids: completedIds
      });

      this.setState({
        todoList: this.state.todoList.filter(item => item.status !== 'completed')
      });

      this.utils.toast({ title: '清除完成', type: 'success' });
    } catch (error) {
      console.error('清除已完成待办事项失败:', error);
      this.utils.toast({ title: '清除失败', type: 'error' });
    }
  }

  /**
   * 在循环组件中处理单个项目
   */
  // 在循环中的组件可以使用 this.item 获取当前项
  // export function onItemToggle() {
  //   this.toggleTodoStatus(this.item.id, this.item.status);
  // }
  // 
  // export function onItemDelete() {
  //   this.deleteTodo(this.item.id);
  // }
}

/**
 * 5. 事件处理函数示例
 */
// 针对不同场景的事件处理
export default {
  // 字段值变化事件
  export function onFieldChange() {
    const value = this.$('field').getValue();
    this.setState({ value });
    
    // 可以触发其他操作
    if (value) {
      this.dataSourceMap.relatedData.load({ field: value });
    }
  },

  // 按钮点击事件
  export function onButtonClick() {
    const input = this.$('input').getValue();
    this.setState({ result: input });
  },

  // 页面参数变化
  export function onRouteChange(query) {
    console.log('新参数:', query);
    if (query.id) {
      this.dataSourceMap.detail.load({ id: query.id });
    }
  }
};