// ============================================================
// Code Flow Graph — Example Data
// Demonstrates all node types, connection styles, call chains,
// field detail panels, and data flow visualization.
// ============================================================

var DIAGRAMS = {};
DIAGRAMS._projectTitle = 'MVVM Demo App';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Page 1: Node Overview — All node types showcase
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGRAMS.node_overview = {
  title: 'Node Overview — All Node Types',
  sub: 'Showcase of every node type supported by Code Flow Graph',
  navLabel: '节点总览',
  navSub: 'All node types',

  NODES: [
    // Entry node
    {
      id: 'EntryDemo', label: 'EntryPoint', type: 'entry', x: 60, y: 80, w: 260,
      sections: [
        {
          title: 'Entry Functions',
          attrs: [
            {
              id: 'EntryDemo.func1', name: 'func1()',
              sig: '<span class="sig-name">func1</span>(<span class="sig-params">args: <span class="sig-type">list</span></span>)\n<span class="sig-return">→ None</span>',
              desc: 'Entry point function, application bootstrap',
            },
            {
              id: 'EntryDemo.func2', name: 'func2()',
              desc: 'Secondary entry for CLI mode',
            },
          ],
        },
      ],
    },
    // Module node
    {
      id: 'ModuleDemo', label: 'ModuleNode', type: 'module', x: 60, y: 340, w: 260,
      sections: [
        {
          title: 'Module Functions',
          attrs: [
            {
              id: 'ModuleDemo.func1', name: 'func1()',
              sig: '<span class="sig-name">func1</span>(<span class="sig-params">path: <span class="sig-type">str</span></span>)\n<span class="sig-return">→ Config</span>',
              desc: 'Load module configuration from path',
            },
            {
              id: 'ModuleDemo.func2', name: 'func2()',
              desc: 'Module initialization helper',
            },
          ],
        },
      ],
    },
    // Class node
    {
      id: 'ClassDemo', label: 'ClassNode', type: 'class', x: 400, y: 80, w: 280,
      sections: [
        {
          title: 'Public Methods',
          attrs: [
            {
              id: 'ClassDemo.func1', name: 'func1()',
              sig: '<span class="sig-name">func1</span>(<span class="sig-params">data: <span class="sig-type">dict</span></span>)\n<span class="sig-return">→ Result</span>',
              desc: 'Main class method, process input data',
              children: [
                { id: 'ClassDemo.subfunc1', name: '→ subfunc1()', desc: 'Preprocessing step' },
                { id: 'ClassDemo.subfunc2', name: '→ subfunc2()', desc: 'Validation step' },
              ],
              childrenCollapsed: false,
            },
            {
              id: 'ClassDemo.func2', name: 'func2()',
              desc: 'Build internal state from config',
            },
          ],
        },
        {
          title: 'Private Methods',
          attrs: [
            {
              id: 'ClassDemo._internal', name: '_internal()',
              desc: 'Internal processing (private)',
            },
          ],
        },
      ],
    },
    // Function node
    {
      id: 'FuncDemo', label: 'FuncNode', type: 'function', x: 400, y: 400, w: 260,
      sections: [
        {
          title: 'Utility Functions',
          attrs: [
            {
              id: 'FuncDemo.func1', name: 'func1()',
              sig: '<span class="sig-name">func1</span>(<span class="sig-params">value: <span class="sig-type">Any</span></span>)\n<span class="sig-return">→ str</span>',
              desc: 'Format value to string representation',
              children: [
                { id: 'FuncDemo.subfunc1', name: '→ subfunc1()', desc: 'Type conversion helper' },
              ],
              childrenCollapsed: true,
            },
            {
              id: 'FuncDemo.func2', name: 'func2()',
              desc: 'Retry with exponential backoff',
            },
          ],
        },
      ],
    },
    // Data node
    {
      id: 'DataDemo', label: 'DataNode', type: 'data', x: 760, y: 80, w: 260,
      sections: [
        {
          title: 'Fields',
          attrs: [
            { id: 'DataDemo.field1', name: 'field1', val: ': str', desc: 'Primary data field' },
            { id: 'DataDemo.field2', name: 'field2', val: ': int', desc: 'Numeric counter field' },
            { id: 'DataDemo.field3', name: 'field3', val: ': list', desc: 'Collection of items' },
          ],
        },
        {
          title: 'Methods',
          attrs: [
            { id: 'DataDemo.func1', name: 'func1()', desc: 'Validate all data fields' },
            { id: 'DataDemo.func2', name: 'func2()', desc: 'Serialize data to dict' },
          ],
        },
      ],
    },
    // Widget node
    {
      id: 'WidgetDemo', label: 'WidgetNode', type: 'widget', x: 760, y: 340, w: 260,
      sections: [
        {
          title: 'UI Components',
          attrs: [
            { id: 'WidgetDemo.func1', name: 'func1()', desc: 'Render widget layout' },
            { id: 'WidgetDemo.func2', name: 'func2()', desc: 'Handle user interaction' },
          ],
        },
      ],
    },
    // Slots node
    {
      id: 'SlotsDemo', label: 'SlotsNode', type: 'slots', x: 760, y: 530, w: 260,
      sections: [
        {
          title: 'Signal Slots',
          attrs: [
            { id: 'SlotsDemo.func1', name: 'func1()', desc: 'Slot: handle click event' },
            { id: 'SlotsDemo.func2', name: 'func2()', desc: 'Slot: handle data change' },
          ],
        },
      ],
    },
    // External module node
    {
      id: 'ExternalDemo', label: 'ExternalLib', type: 'module', external: true, x: 1100, y: 80, w: 240,
      sections: [
        {
          title: 'External API',
          attrs: [
            { id: 'ExternalDemo.func1', name: 'func1()', desc: 'External library call (3rd party)' },
            { id: 'ExternalDemo.func2', name: 'func2()', desc: 'External helper function' },
          ],
        },
      ],
    },
  ],

  CONNECTIONS: [
    // call (green)
    ['EntryDemo.func1', 'ClassDemo.func1', '#a6e3a1', false],
    ['EntryDemo.func1', 'ModuleDemo.func1', '#a6e3a1', false],
    ['ClassDemo.func1', 'FuncDemo.func1', '#a6e3a1', false],
    ['ClassDemo.subfunc1', 'DataDemo.func1', '#a6e3a1', false],
    // data (blue)
    ['ModuleDemo.func1', 'ClassDemo.func2', '#89b4fa', false],
    ['DataDemo.func2', 'FuncDemo.func1', '#89b4fa', false],
    // extern (peach)
    ['ClassDemo._internal', 'ExternalDemo.func1', '#fab387', false],
    ['FuncDemo.func2', 'ExternalDemo.func2', '#fab387', false],
    // signal (pink dashed)
    ['WidgetDemo.func2', 'SlotsDemo.func1', '#f5c2e7', true],
    ['WidgetDemo.func2', 'SlotsDemo.func2', '#f5c2e7', true],
    ['SlotsDemo.func2', 'DataDemo.field1', '#f5c2e7', true],
  ],

  GROUPS: [
    { id: 'g-type-entry', label: 'ENTRY — Entry Points', color: '#f9e2af', bg: 'rgba(249,226,175,0.04)', nodes: ['EntryDemo'] },
    { id: 'g-type-module', label: 'MODULE — Modules', color: '#a6e3a1', bg: 'rgba(166,227,161,0.04)', nodes: ['ModuleDemo'] },
    { id: 'g-type-class', label: 'CLASS — OOP Classes', color: '#89b4fa', bg: 'rgba(137,180,250,0.04)', nodes: ['ClassDemo'] },
    { id: 'g-type-func', label: 'FUNC — Functions', color: '#cba6f7', bg: 'rgba(203,166,247,0.04)', nodes: ['FuncDemo'] },
    { id: 'g-type-data', label: 'DATA — Data & Models', color: '#fab387', bg: 'rgba(250,179,135,0.04)', nodes: ['DataDemo'] },
    { id: 'g-type-ui', label: 'UI — Widget & Slots', color: '#74c7ec', bg: 'rgba(116,199,236,0.04)', nodes: ['WidgetDemo', 'SlotsDemo'] },
    { id: 'g-type-ext', label: 'EXTERNAL — 3rd Party', color: '#6c7086', bg: 'rgba(108,112,134,0.04)', nodes: ['ExternalDemo'] },
  ],
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Page 2: Overview — MVVM Architecture Module Relationships
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGRAMS.overview = {
  title: 'Overview — MVVM Architecture',
  sub: 'src/ — Module relationships in an MVVM design pattern',
  navLabel: 'Overview 示例',
  navSub: 'MVVM architecture',

  NODES: [
    // Entry
    {
      id: 'main', label: 'main', type: 'entry', x: 60, y: 200, w: 240,
      sections: [
        {
          title: 'Entry Point',
          attrs: [
            { id: 'main.bootstrap', name: 'bootstrap()', desc: 'Initialize app, wire up MVVM layers' },
            { id: 'main.run', name: 'run()', desc: 'Start the application event loop' },
            { id: 'main.shutdown', name: 'shutdown()', desc: 'Graceful shutdown and cleanup' },
          ],
        },
      ],
    },
    // Model layer
    {
      id: 'UserModel', label: 'UserModel', type: 'data', x: 400, y: 60, w: 260,
      sections: [
        {
          title: 'Fields',
          attrs: [
            { id: 'UserModel.id', name: 'id', val: ': int' },
            { id: 'UserModel.name', name: 'name', val: ': str' },
            { id: 'UserModel.email', name: 'email', val: ': str' },
          ],
        },
        {
          title: 'Methods',
          attrs: [
            { id: 'UserModel.validate', name: 'validate()', desc: 'Validate user data constraints' },
            { id: 'UserModel.save', name: 'save()', desc: 'Persist user to database' },
          ],
        },
      ],
    },
    {
      id: 'TaskModel', label: 'TaskModel', type: 'data', x: 400, y: 340, w: 260,
      sections: [
        {
          title: 'Fields',
          attrs: [
            { id: 'TaskModel.id', name: 'id', val: ': int' },
            { id: 'TaskModel.title', name: 'title', val: ': str' },
            { id: 'TaskModel.status', name: 'status', val: ': Status' },
            { id: 'TaskModel.assignee', name: 'assignee', val: ': User' },
          ],
        },
        {
          title: 'Methods',
          attrs: [
            { id: 'TaskModel.assign', name: 'assign()', desc: 'Assign task to user' },
            { id: 'TaskModel.complete', name: 'complete()', desc: 'Mark task as done' },
          ],
        },
      ],
    },
    // ViewModel layer
    {
      id: 'UserVM', label: 'UserViewModel', type: 'class', x: 760, y: 60, w: 280,
      sections: [
        {
          title: 'Reactive Properties',
          attrs: [
            { id: 'UserVM.currentUser', name: 'currentUser', val: ': Observable<User>' },
            { id: 'UserVM.userList', name: 'userList', val: ': Observable<List>' },
          ],
        },
        {
          title: 'Commands',
          attrs: [
            { id: 'UserVM.loadUsers', name: 'loadUsers()', desc: 'Fetch and populate user list from API' },
            { id: 'UserVM.selectUser', name: 'selectUser()', desc: 'Set current user and notify observers' },
            { id: 'UserVM.updateUser', name: 'updateUser()', desc: 'Validate and save user changes' },
          ],
        },
      ],
    },
    {
      id: 'TaskVM', label: 'TaskViewModel', type: 'class', x: 760, y: 340, w: 280,
      sections: [
        {
          title: 'Reactive Properties',
          attrs: [
            { id: 'TaskVM.taskList', name: 'taskList', val: ': Observable<List>' },
            { id: 'TaskVM.selectedTask', name: 'selectedTask', val: ': Observable<Task>' },
            { id: 'TaskVM.filter', name: 'filter', val: ': Observable<Filter>' },
          ],
        },
        {
          title: 'Commands',
          attrs: [
            { id: 'TaskVM.loadTasks', name: 'loadTasks()', desc: 'Fetch tasks and apply current filter' },
            { id: 'TaskVM.createTask', name: 'createTask()', desc: 'Create new task with validation' },
            { id: 'TaskVM.completeTask', name: 'completeTask()', desc: 'Mark selected task as complete' },
          ],
        },
      ],
    },
    // View layer (UI)
    {
      id: 'UserListView', label: 'UserListView', type: 'widget', x: 1140, y: 60, w: 260,
      sections: [
        {
          title: 'UI Components',
          attrs: [
            { id: 'UserListView.render', name: 'render()', desc: 'Render user list table' },
            { id: 'UserListView.onSelect', name: 'onSelect()', desc: 'User row click handler' },
            { id: 'UserListView.onEdit', name: 'onEdit()', desc: 'Open user edit form' },
          ],
        },
      ],
    },
    {
      id: 'TaskBoardView', label: 'TaskBoardView', type: 'widget', x: 1140, y: 300, w: 260,
      sections: [
        {
          title: 'UI Components',
          attrs: [
            { id: 'TaskBoardView.render', name: 'render()', desc: 'Render kanban task board' },
            { id: 'TaskBoardView.onDrag', name: 'onDrag()', desc: 'Handle task card drag' },
            { id: 'TaskBoardView.onFilter', name: 'onFilter()', desc: 'Filter change handler' },
            { id: 'TaskBoardView.onComplete', name: 'onComplete()', desc: 'Complete button handler' },
          ],
        },
      ],
    },
    {
      id: 'NotificationView', label: 'NotificationView', type: 'widget', x: 1140, y: 540, w: 260,
      sections: [
        {
          title: 'UI Components',
          attrs: [
            { id: 'NotificationView.show', name: 'show()', desc: 'Display toast notification' },
            { id: 'NotificationView.dismiss', name: 'dismiss()', desc: 'Auto dismiss after timeout' },
          ],
        },
      ],
    },
    // Utils
    {
      id: 'utils', label: 'utils', type: 'function', x: 400, y: 600, w: 260,
      sections: [
        {
          title: 'Helper Functions',
          attrs: [
            { id: 'utils.formatDate', name: 'formatDate()', desc: 'Format date to locale string' },
            { id: 'utils.debounce', name: 'debounce()', desc: 'Debounce function wrapper' },
            { id: 'utils.deepClone', name: 'deepClone()', desc: 'Deep clone object utility' },
          ],
        },
      ],
    },
    // External
    {
      id: 'api', label: 'api', type: 'module', external: true, x: 60, y: 500, w: 220,
      sections: [
        {
          title: 'REST API',
          attrs: [
            { id: 'api.fetchUsers', name: 'fetchUsers()', desc: 'GET /api/users' },
            { id: 'api.fetchTasks', name: 'fetchTasks()', desc: 'GET /api/tasks' },
            { id: 'api.postTask', name: 'postTask()', desc: 'POST /api/tasks' },
          ],
        },
      ],
    },
  ],

  CONNECTIONS: [
    // Entry → layers (green call)
    ['main.bootstrap', 'UserVM.loadUsers', '#a6e3a1', false],
    ['main.bootstrap', 'TaskVM.loadTasks', '#a6e3a1', false],
    ['main.run', 'UserListView.render', '#a6e3a1', false],
    ['main.run', 'TaskBoardView.render', '#a6e3a1', false],
    // ViewModel → Model (green call)
    ['UserVM.loadUsers', 'UserModel.validate', '#a6e3a1', false],
    ['UserVM.updateUser', 'UserModel.save', '#a6e3a1', false],
    ['TaskVM.createTask', 'TaskModel.assign', '#a6e3a1', false],
    ['TaskVM.completeTask', 'TaskModel.complete', '#a6e3a1', false],
    // View → ViewModel (blue data binding)
    ['UserListView.onSelect', 'UserVM.selectUser', '#89b4fa', false],
    ['UserListView.onEdit', 'UserVM.updateUser', '#89b4fa', false],
    ['TaskBoardView.onFilter', 'TaskVM.filter', '#89b4fa', false],
    ['TaskBoardView.onComplete', 'TaskVM.completeTask', '#89b4fa', false],
    ['TaskBoardView.onDrag', 'TaskVM.createTask', '#89b4fa', false],
    // ViewModel → View (signal notification)
    ['UserVM.currentUser', 'UserListView.render', '#f5c2e7', true],
    ['TaskVM.taskList', 'TaskBoardView.render', '#f5c2e7', true],
    ['TaskVM.selectedTask', 'NotificationView.show', '#f5c2e7', true],
    // External API calls (peach)
    ['UserVM.loadUsers', 'api.fetchUsers', '#fab387', false],
    ['TaskVM.loadTasks', 'api.fetchTasks', '#fab387', false],
    ['TaskVM.createTask', 'api.postTask', '#fab387', false],
    // Utils usage (green)
    ['TaskVM.loadTasks', 'utils.formatDate', '#a6e3a1', false],
    ['TaskBoardView.onFilter', 'utils.debounce', '#a6e3a1', false],
  ],

  GROUPS: [
    { id: 'g-model', label: 'Model Layer', color: '#fab387', bg: 'rgba(250,179,135,0.04)', nodes: ['UserModel', 'TaskModel'] },
    { id: 'g-viewmodel', label: 'ViewModel Layer', color: '#89b4fa', bg: 'rgba(137,180,250,0.04)', nodes: ['UserVM', 'TaskVM'] },
    { id: 'g-view', label: 'View Layer', color: '#74c7ec', bg: 'rgba(116,199,236,0.04)', nodes: ['UserListView', 'TaskBoardView', 'NotificationView'] },
    { id: 'g-utils', label: 'Utils', color: '#585b70', bg: 'rgba(88,91,112,0.04)', nodes: ['utils'] },
    { id: 'g-api', label: 'External API', color: '#6c7086', bg: 'rgba(108,112,134,0.04)', nodes: ['api'] },
  ],
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Page 3: Main Call — Complete call chain of main()
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGRAMS.main_call = {
  title: 'Main Call — Entry Point Call Chain',
  sub: 'src/main.py — Complete call chain from bootstrap to execution',
  navLabel: 'Main Call',
  navSub: 'main() call chain',

  NODES: [
    {
      id: 'main', label: 'main', type: 'entry', x: 60, y: 120, w: 280,
      sections: [
        {
          title: 'Entry Point',
          attrs: [
            {
              id: 'main.bootstrap', name: 'bootstrap()',
              sig: '<span class="sig-name">bootstrap</span>(<span class="sig-params">config_path: <span class="sig-type">str</span> = "config.yaml"</span>)\n<span class="sig-return">→ App</span>',
              desc: 'Initialize the entire application: load config, setup logging, create MVVM layers, wire bindings',
              detail: 'Core bootstrap sequence:\n1. Parse CLI args\n2. Load config from file\n3. Setup logger with config\n4. Initialize Model layer (DB connection)\n5. Create ViewModels with Model refs\n6. Create Views bound to ViewModels\n7. Return assembled App instance',
              io: { input: 'config_path: str — path to YAML config file', output: 'App — fully initialized application' },
              callChain: [
                {
                  id: 'main.bootstrap', name: 'bootstrap()', module: 'main.py',
                  desc: 'Application bootstrap — the root orchestrator',
                  calls: [
                    {
                      id: 'main._parse_args', name: '_parse_args()', module: 'main.py',
                      desc: 'Parse CLI arguments (--config, --debug, --port)',
                    },
                    {
                      id: 'ConfigLoader.load', name: 'ConfigLoader.load()', module: 'config.py',
                      desc: 'Load and validate YAML config file',
                      calls: [
                        {
                          id: 'ConfigLoader._read_file', name: '_read_file()', module: 'config.py',
                          desc: 'Read YAML file from disk with encoding detection',
                        },
                        {
                          id: 'ConfigLoader._validate', name: '_validate()', module: 'config.py',
                          desc: 'Schema validation against config spec',
                          calls: [
                            {
                              id: 'ConfigLoader._check_required', name: '_check_required()', module: 'config.py',
                              desc: 'Verify all required fields are present',
                            },
                            {
                              id: 'ConfigLoader._apply_defaults', name: '_apply_defaults()', module: 'config.py',
                              desc: 'Fill in missing optional fields with defaults',
                            },
                          ],
                        },
                      ],
                    },
                    {
                      id: 'Logger.setup', name: 'Logger.setup()', module: 'logger.py',
                      desc: 'Configure logging handlers, formatters and log level',
                      calls: [
                        {
                          id: 'Logger._create_handler', name: '_create_handler()', module: 'logger.py',
                          desc: 'Create file/console handlers based on config',
                        },
                        {
                          id: 'Logger._set_format', name: '_set_format()', module: 'logger.py',
                          desc: 'Apply log format pattern with timestamp',
                        },
                      ],
                    },
                    {
                      id: 'Database.connect', name: 'Database.connect()', module: 'db.py',
                      desc: 'Establish database connection pool',
                      external: true,
                      calls: [
                        {
                          id: 'Database._init_pool', name: '_init_pool()', module: 'db.py',
                          desc: 'Create connection pool with min/max limits',
                          external: true,
                        },
                      ],
                    },
                    {
                      id: 'UserVM.init', name: 'UserViewModel()', module: 'viewmodels/user_vm.py',
                      desc: 'Create UserViewModel, bind to UserModel and API service',
                    },
                    {
                      id: 'TaskVM.init', name: 'TaskViewModel()', module: 'viewmodels/task_vm.py',
                      desc: 'Create TaskViewModel, bind to TaskModel and API service',
                    },
                    {
                      id: 'Router.setup', name: 'Router.setup()', module: 'router.py',
                      desc: 'Register routes and bind views to URL patterns',
                      calls: [
                        {
                          id: 'Router._bind_views', name: '_bind_views()', module: 'router.py',
                          desc: 'Map each view component to its route path',
                        },
                      ],
                    },
                  ],
                },
              ],
            },
            {
              id: 'main.run', name: 'run()',
              sig: '<span class="sig-name">run</span>(<span class="sig-params">app: <span class="sig-type">App</span></span>)\n<span class="sig-return">→ None</span>',
              desc: 'Start event loop, render initial views, begin listening',
              io: { input: 'app: App — initialized application', output: 'None (blocks until shutdown)' },
              children: [
                { id: 'main._render_views', name: '→ _render_views()', desc: 'Render all registered views' },
                { id: 'main._start_loop', name: '→ _start_loop()', desc: 'Start the main event loop' },
              ],
              childrenCollapsed: false,
            },
            {
              id: 'main.shutdown', name: 'shutdown()',
              desc: 'Graceful shutdown: save state, close connections, cleanup',
              children: [
                { id: 'main._save_state', name: '→ _save_state()', desc: 'Persist unsaved state to disk' },
                { id: 'main._close_connections', name: '→ _close_connections()', desc: 'Close DB and API connections' },
              ],
              childrenCollapsed: true,
            },
          ],
        },
      ],
    },
    {
      id: 'ConfigLoader', label: 'ConfigLoader', type: 'class', x: 440, y: 60, w: 280,
      sections: [
        {
          title: 'Config Loading',
          attrs: [
            {
              id: 'ConfigLoader.load', name: 'load()',
              sig: '<span class="sig-name">load</span>(<span class="sig-params">path: <span class="sig-type">str</span></span>)\n<span class="sig-return">→ Config</span>',
              desc: 'Load and validate configuration from YAML file',
              children: [
                { id: 'ConfigLoader._read_file', name: '→ _read_file()', desc: 'Read YAML with encoding detection' },
                { id: 'ConfigLoader._validate', name: '→ _validate()', desc: 'Schema validation' },
              ],
              childrenCollapsed: false,
            },
          ],
        },
        {
          title: 'Internal',
          attrs: [
            { id: 'ConfigLoader._check_required', name: '_check_required()', desc: 'Verify required fields' },
            { id: 'ConfigLoader._apply_defaults', name: '_apply_defaults()', desc: 'Fill default values' },
            { id: 'ConfigLoader._merge_env', name: '_merge_env()', desc: 'Merge environment variable overrides' },
          ],
        },
      ],
    },
    {
      id: 'Logger', label: 'Logger', type: 'module', x: 440, y: 380, w: 260,
      sections: [
        {
          title: 'Setup',
          attrs: [
            {
              id: 'Logger.setup', name: 'setup()',
              desc: 'Configure logging system',
              children: [
                { id: 'Logger._create_handler', name: '→ _create_handler()', desc: 'Create file/console handlers' },
                { id: 'Logger._set_format', name: '→ _set_format()', desc: 'Apply log format pattern' },
              ],
              childrenCollapsed: false,
            },
          ],
        },
        {
          title: 'Logging',
          attrs: [
            { id: 'Logger.info', name: 'info()', desc: 'Log INFO message' },
            { id: 'Logger.error', name: 'error()', desc: 'Log ERROR message' },
            { id: 'Logger.debug', name: 'debug()', desc: 'Log DEBUG message' },
          ],
        },
      ],
    },
    {
      id: 'Database', label: 'Database', type: 'module', external: true, x: 800, y: 60, w: 260,
      sections: [
        {
          title: 'Connection',
          attrs: [
            {
              id: 'Database.connect', name: 'connect()',
              desc: 'Establish connection pool',
              children: [
                { id: 'Database._init_pool', name: '→ _init_pool()', desc: 'Create pool with limits' },
              ],
              childrenCollapsed: false,
            },
            { id: 'Database.query', name: 'query()', desc: 'Execute SQL query' },
            { id: 'Database.close', name: 'close()', desc: 'Close all connections' },
          ],
        },
      ],
    },
    {
      id: 'Router', label: 'Router', type: 'class', x: 800, y: 320, w: 260,
      sections: [
        {
          title: 'Routing',
          attrs: [
            {
              id: 'Router.setup', name: 'setup()',
              desc: 'Register routes and bind views',
              children: [
                { id: 'Router._bind_views', name: '→ _bind_views()', desc: 'Map views to URL paths' },
              ],
              childrenCollapsed: false,
            },
            { id: 'Router.navigate', name: 'navigate()', desc: 'Navigate to a route' },
            { id: 'Router.back', name: 'back()', desc: 'Go back in history' },
          ],
        },
      ],
    },
    {
      id: 'EventBus', label: 'EventBus', type: 'class', x: 800, y: 530, w: 260,
      sections: [
        {
          title: 'Events',
          attrs: [
            { id: 'EventBus.emit', name: 'emit()', desc: 'Emit event to listeners' },
            { id: 'EventBus.on', name: 'on()', desc: 'Register event listener' },
            { id: 'EventBus.off', name: 'off()', desc: 'Remove event listener' },
          ],
        },
      ],
    },
  ],

  CONNECTIONS: [
    // main → config (green call)
    ['main.bootstrap', 'ConfigLoader.load', '#a6e3a1', false],
    ['main.bootstrap', 'Logger.setup', '#a6e3a1', false],
    ['main.bootstrap', 'Router.setup', '#a6e3a1', false],
    // config internal
    ['ConfigLoader.load', 'ConfigLoader._check_required', '#a6e3a1', false],
    ['ConfigLoader.load', 'ConfigLoader._apply_defaults', '#a6e3a1', false],
    ['ConfigLoader._validate', 'ConfigLoader._merge_env', '#a6e3a1', false],
    // data flow (blue)
    ['ConfigLoader.load', 'Logger.setup', '#89b4fa', false],
    ['ConfigLoader.load', 'main.run', '#89b4fa', false],
    // external (peach)
    ['main.bootstrap', 'Database.connect', '#fab387', false],
    ['main._close_connections', 'Database.close', '#fab387', false],
    // signal (pink dashed)
    ['main.run', 'EventBus.emit', '#f5c2e7', true],
    ['main.shutdown', 'EventBus.emit', '#f5c2e7', true],
    ['Logger.error', 'EventBus.emit', '#f5c2e7', true],
    // routing
    ['Router.setup', 'EventBus.on', '#a6e3a1', false],
  ],

  GROUPS: [
    { id: 'g-boot', label: 'Bootstrap', color: '#f9e2af', bg: 'rgba(249,226,175,0.04)', nodes: ['main'] },
    { id: 'g-config', label: 'Configuration', color: '#a6e3a1', bg: 'rgba(166,227,161,0.04)', nodes: ['ConfigLoader', 'Logger'] },
    { id: 'g-runtime', label: 'Runtime', color: '#89b4fa', bg: 'rgba(137,180,250,0.04)', nodes: ['Router', 'EventBus', 'Database'] },
  ],
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Page 4: Data Flow — Tree structure & data transformation
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGRAMS.data_flow = {
  title: 'Data Flow — State Tree & Transformation',
  sub: 'src/state/ — Data structures, computation process, and data flow',
  navLabel: '数据结构',
  navSub: 'State tree & data flow',

  NODES: [
    // Root state tree
    {
      id: 'AppState', label: 'AppState', type: 'data', x: 60, y: 80, w: 300,
      sections: [
        {
          title: 'Root State Fields',
          attrs: [
            {
              id: 'AppState.users', name: 'users', val: ': UserState',
              desc: 'User domain state subtree',
              fieldDetail: {
                field: 'users',
                type: 'UserState',
                summary: 'Manages the complete user domain state including the user list, current selection, and loading status. Updated via UserReducer.',
                sources: [
                  {
                    mode: 'INITIAL', fn: 'createStore()',
                    steps: [
                      'Call createStore() with rootReducer',
                      'rootReducer combines userReducer + taskReducer',
                      'userReducer returns initial UserState: { list: [], current: null, loading: false }',
                    ],
                  },
                  {
                    mode: 'ON FETCH', fn: 'userReducer(state, action)',
                    steps: [
                      'Component dispatches FETCH_USERS action',
                      'Middleware intercepts → calls api.fetchUsers()',
                      'API returns User[] array',
                      'Dispatch FETCH_USERS_SUCCESS with payload',
                      'userReducer sets state.list = action.payload',
                      'state.loading transitions false → true → false',
                    ],
                  },
                ],
              },
            },
            {
              id: 'AppState.tasks', name: 'tasks', val: ': TaskState',
              desc: 'Task domain state subtree',
              fieldDetail: {
                field: 'tasks',
                type: 'TaskState',
                summary: 'Manages task list, filters, and selected task. The filtered view is computed from tasks + filter via a selector.',
                sources: [
                  {
                    mode: 'INITIAL', fn: 'taskReducer()',
                    steps: [
                      'Returns initial TaskState: { list: [], filter: "all", selected: null }',
                    ],
                  },
                  {
                    mode: 'ON FILTER', fn: 'taskReducer(state, SET_FILTER)',
                    steps: [
                      'User selects filter in TaskBoardView',
                      'Dispatch SET_FILTER with filter value ("all" | "active" | "done")',
                      'taskReducer updates state.filter',
                      'selectFilteredTasks() recomputes filtered list',
                      'View re-renders with new filtered data',
                    ],
                  },
                ],
              },
            },
            {
              id: 'AppState.ui', name: 'ui', val: ': UIState',
              desc: 'UI state (theme, sidebar, modals)',
            },
            {
              id: 'AppState.router', name: 'router', val: ': RouterState',
              desc: 'Current route and navigation history',
            },
          ],
        },
      ],
    },
    // UserState subtree
    {
      id: 'UserState', label: 'UserState', type: 'data', x: 460, y: 60, w: 280,
      sections: [
        {
          title: 'State Fields',
          attrs: [
            {
              id: 'UserState.list', name: 'list', val: ': User[]',
              desc: 'Array of all loaded users',
              fieldDetail: {
                field: 'list',
                type: 'User[]',
                summary: 'The complete user list fetched from API. Each item is a User object with id, name, email fields.',
                sources: [
                  {
                    mode: 'FETCH', fn: 'api.fetchUsers() → userReducer',
                    steps: [
                      'api.fetchUsers() sends GET /api/users',
                      'Server returns JSON array of User objects',
                      'Middleware dispatches FETCH_USERS_SUCCESS',
                      'userReducer replaces state.list with new array',
                      'All subscribed components re-render',
                    ],
                  },
                ],
              },
            },
            {
              id: 'UserState.current', name: 'current', val: ': User | null',
              desc: 'Currently selected user',
            },
            {
              id: 'UserState.loading', name: 'loading', val: ': boolean',
              desc: 'Loading state flag',
            },
          ],
        },
        {
          title: 'Selectors',
          attrs: [
            { id: 'UserState.selectById', name: 'selectById()', desc: 'Get user by ID from list' },
            { id: 'UserState.selectActive', name: 'selectActive()', desc: 'Get all active users' },
          ],
        },
      ],
    },
    // TaskState subtree
    {
      id: 'TaskState', label: 'TaskState', type: 'data', x: 460, y: 380, w: 280,
      sections: [
        {
          title: 'State Fields',
          attrs: [
            {
              id: 'TaskState.list', name: 'list', val: ': Task[]',
              desc: 'Array of all tasks',
              fieldDetail: {
                field: 'list',
                type: 'Task[]',
                summary: 'All tasks loaded from API. Each task has id, title, status, assignee, priority. Filtered view computed by selector.',
                sources: [
                  {
                    mode: 'FETCH', fn: 'api.fetchTasks() → taskReducer',
                    steps: [
                      'api.fetchTasks() sends GET /api/tasks',
                      'Server returns Task[] with status and assignee',
                      'taskReducer sets state.list = action.payload',
                    ],
                  },
                  {
                    mode: 'CREATE', fn: 'taskReducer(state, CREATE_TASK)',
                    steps: [
                      'User fills form → dispatch CREATE_TASK',
                      'Middleware calls api.postTask(data)',
                      'On success: taskReducer appends new task to list',
                      'selectFilteredTasks() recomputes if needed',
                    ],
                  },
                ],
              },
            },
            {
              id: 'TaskState.filter', name: 'filter', val: ': string',
              desc: 'Current filter: "all" | "active" | "done"',
            },
            {
              id: 'TaskState.selected', name: 'selected', val: ': Task | null',
              desc: 'Currently selected task',
            },
          ],
        },
        {
          title: 'Selectors',
          attrs: [
            { id: 'TaskState.selectFiltered', name: 'selectFiltered()', desc: 'Compute filtered task list from filter + list' },
            { id: 'TaskState.selectByUser', name: 'selectByUser()', desc: 'Get tasks assigned to user' },
          ],
        },
      ],
    },
    // Reducers (computation)
    {
      id: 'UserReducer', label: 'userReducer', type: 'function', x: 820, y: 60, w: 280,
      sections: [
        {
          title: 'Action Handlers',
          attrs: [
            { id: 'UserReducer.FETCH_USERS', name: 'FETCH_USERS', desc: 'Set loading=true, begin fetch' },
            { id: 'UserReducer.FETCH_SUCCESS', name: 'FETCH_USERS_SUCCESS', desc: 'Set list=payload, loading=false' },
            { id: 'UserReducer.FETCH_ERROR', name: 'FETCH_USERS_ERROR', desc: 'Set error, loading=false' },
            { id: 'UserReducer.SELECT_USER', name: 'SELECT_USER', desc: 'Set current=payload user' },
            { id: 'UserReducer.UPDATE_USER', name: 'UPDATE_USER', desc: 'Update user in list by id' },
          ],
        },
      ],
    },
    {
      id: 'TaskReducer', label: 'taskReducer', type: 'function', x: 820, y: 350, w: 280,
      sections: [
        {
          title: 'Action Handlers',
          attrs: [
            { id: 'TaskReducer.FETCH_TASKS', name: 'FETCH_TASKS', desc: 'Begin task fetch' },
            { id: 'TaskReducer.FETCH_SUCCESS', name: 'FETCH_TASKS_SUCCESS', desc: 'Set list=payload' },
            { id: 'TaskReducer.CREATE_TASK', name: 'CREATE_TASK', desc: 'Append new task to list' },
            { id: 'TaskReducer.COMPLETE_TASK', name: 'COMPLETE_TASK', desc: 'Set task status=done' },
            { id: 'TaskReducer.SET_FILTER', name: 'SET_FILTER', desc: 'Update filter value' },
          ],
        },
      ],
    },
    // Middleware (side effects)
    {
      id: 'Middleware', label: 'apiMiddleware', type: 'class', x: 820, y: 640, w: 280,
      sections: [
        {
          title: 'Side Effects',
          attrs: [
            { id: 'Middleware.handleFetchUsers', name: 'handleFetchUsers()', desc: 'Intercept FETCH_USERS → call API → dispatch result' },
            { id: 'Middleware.handleFetchTasks', name: 'handleFetchTasks()', desc: 'Intercept FETCH_TASKS → call API → dispatch result' },
            { id: 'Middleware.handleCreateTask', name: 'handleCreateTask()', desc: 'Intercept CREATE_TASK → POST to API → dispatch result' },
            { id: 'Middleware.handleError', name: 'handleError()', desc: 'Catch errors → dispatch error action + show notification' },
          ],
        },
      ],
    },
    // API layer
    {
      id: 'api', label: 'api', type: 'module', external: true, x: 1200, y: 200, w: 240,
      sections: [
        {
          title: 'REST API',
          attrs: [
            { id: 'api.fetchUsers', name: 'fetchUsers()', desc: 'GET /api/users → User[]' },
            { id: 'api.fetchTasks', name: 'fetchTasks()', desc: 'GET /api/tasks → Task[]' },
            { id: 'api.postTask', name: 'postTask()', desc: 'POST /api/tasks → Task' },
            { id: 'api.patchTask', name: 'patchTask()', desc: 'PATCH /api/tasks/:id → Task' },
          ],
        },
      ],
    },
  ],

  CONNECTIONS: [
    // State tree composition (blue data flow)
    ['AppState.users', 'UserState.list', '#89b4fa', false],
    ['AppState.tasks', 'TaskState.list', '#89b4fa', false],
    // Reducer → State (green, reducers produce state)
    ['UserReducer.FETCH_SUCCESS', 'UserState.list', '#a6e3a1', false],
    ['UserReducer.SELECT_USER', 'UserState.current', '#a6e3a1', false],
    ['UserReducer.UPDATE_USER', 'UserState.list', '#a6e3a1', false],
    ['TaskReducer.FETCH_SUCCESS', 'TaskState.list', '#a6e3a1', false],
    ['TaskReducer.CREATE_TASK', 'TaskState.list', '#a6e3a1', false],
    ['TaskReducer.COMPLETE_TASK', 'TaskState.list', '#a6e3a1', false],
    ['TaskReducer.SET_FILTER', 'TaskState.filter', '#a6e3a1', false],
    // Middleware → Reducer (signal, dispatches actions)
    ['Middleware.handleFetchUsers', 'UserReducer.FETCH_SUCCESS', '#f5c2e7', true],
    ['Middleware.handleFetchTasks', 'TaskReducer.FETCH_SUCCESS', '#f5c2e7', true],
    ['Middleware.handleCreateTask', 'TaskReducer.CREATE_TASK', '#f5c2e7', true],
    ['Middleware.handleError', 'UserReducer.FETCH_ERROR', '#f5c2e7', true],
    // Middleware → API (external peach)
    ['Middleware.handleFetchUsers', 'api.fetchUsers', '#fab387', false],
    ['Middleware.handleFetchTasks', 'api.fetchTasks', '#fab387', false],
    ['Middleware.handleCreateTask', 'api.postTask', '#fab387', false],
    // Selectors read from state (blue data)
    ['UserState.list', 'UserState.selectById', '#89b4fa', false],
    ['UserState.list', 'UserState.selectActive', '#89b4fa', false],
    ['TaskState.list', 'TaskState.selectFiltered', '#89b4fa', false],
    ['TaskState.filter', 'TaskState.selectFiltered', '#89b4fa', false],
    ['TaskState.list', 'TaskState.selectByUser', '#89b4fa', false],
  ],

  GROUPS: [
    { id: 'g-state', label: 'State Tree', color: '#fab387', bg: 'rgba(250,179,135,0.04)', nodes: ['AppState', 'UserState', 'TaskState'] },
    { id: 'g-reducers', label: 'Reducers', color: '#cba6f7', bg: 'rgba(203,166,247,0.04)', nodes: ['UserReducer', 'TaskReducer'] },
    { id: 'g-side-effects', label: 'Side Effects', color: '#89b4fa', bg: 'rgba(137,180,250,0.04)', nodes: ['Middleware'] },
    { id: 'g-api', label: 'External API', color: '#6c7086', bg: 'rgba(108,112,134,0.04)', nodes: ['api'] },
  ],
};

// ═══════════════════════════════════════════════════════════
//  UI Layout Views (optional — widget hierarchy visualization)
// ═══════════════════════════════════════════════════════════

var UI_LAYOUT_VIEWS = {};

UI_LAYOUT_VIEWS.main_window = {
  title: 'MainWindow — 完整布局',
  sub: 'app/main_window.py — QMainWindow',
  navLabel: '🏠 MainWindow',
  navSub: '主窗口完整布局',
  root: {
    name: 'MainWindow', obj: 'QMainWindow', color: 'blue',
    badge: 'WINDOW', layout: 'v',
    note: 'setWindowTitle("MVVM Demo App")',
    children: [
      {
        name: 'menu_bar', obj: 'QMenuBar', color: 'yellow', badge: 'MENU',
        layout: 'h', h: 30,
        children: [
          { name: '"File"', obj: 'QMenu', color: 'overlay', badge: 'MENU', leaf: true },
          { name: '"Edit"', obj: 'QMenu', color: 'overlay', badge: 'MENU', leaf: true },
          { name: '"View"', obj: 'QMenu', color: 'overlay', badge: 'MENU', leaf: true },
        ]
      },
      {
        name: 'central_widget', obj: 'QWidget', color: 'blue', badge: 'FRAME',
        layout: 'h', flex: 1,
        children: [
          {
            name: 'sidebar', obj: 'QListWidget', color: 'mauve', badge: 'LIST',
            layout: 'v', w: 200,
            children: [
              { name: '"Users"', obj: 'QListWidgetItem', color: 'overlay', badge: 'ITEM', leaf: true },
              { name: '"Tasks"', obj: 'QListWidgetItem', color: 'overlay', badge: 'ITEM', leaf: true },
              { name: '"Settings"', obj: 'QListWidgetItem', color: 'overlay', badge: 'ITEM', leaf: true },
            ]
          },
          {
            name: 'content_stack', obj: 'QStackedWidget', color: 'lavender', badge: 'STACK',
            layout: 'stack', flex: 1,
            stackTabs: [
              { label: '[0] Users', key: 'users', active: true },
              { label: '[1] Tasks', key: 'tasks' },
              { label: '[2] Settings', key: 'settings' },
            ],
            stackPages: {
              users: { name: 'user_list_view', obj: 'UserListView', color: 'green', badge: 'VIEW', placeholder: '用户列表视图 (QTableView)' },
              tasks: { name: 'task_board_view', obj: 'TaskBoardView', color: 'peach', badge: 'VIEW', placeholder: '任务看板视图 (QGraphicsView)' },
              settings: { name: 'settings_form', obj: 'SettingsForm', color: 'teal', badge: 'FORM', placeholder: '设置表单 (QFormLayout)' },
            },
          },
        ]
      },
      {
        name: 'status_bar', obj: 'QStatusBar', color: 'overlay', badge: 'BAR',
        leaf: true, h: 24, note: '底部状态栏',
      },
    ]
  }
};
