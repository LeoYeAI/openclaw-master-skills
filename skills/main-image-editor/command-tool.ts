export type MainImageEditOp = "replace_text" | "delete_text";

export type MainImageEditItem = {
  op: MainImageEditOp;
  layerName: string;
  newText?: string;
  confidence?: number;
  positionHint?: string;
};

export type MainImageTask = {
  exactPath?: string;
  fileHint?: string;
  modifications: MainImageEditItem[];
};

export type MainImageEditorRequest = {
  requestId?: string;
  text?: string;
  screenshotPath?: string;
  confidenceThreshold?: number;
  tasks?: MainImageTask[];
  execution?: {
    dryRun?: boolean;
    force?: boolean;
    indexPath?: string;
    rollbackPolicy?: "rollback_all";
    createBackup?: boolean;
    bundleZip?: boolean;
  };
};

export type MainImageTaskPreview = {
  taskId: string;
  exactPath?: string;
  fileHint?: string;
  edits: Array<{
    layerName: string;
    op: MainImageEditOp;
    newText: string;
    confidence: number;
  }>;
  minConfidence: number;
};

export type MainImageEditorResult = {
  requestId: string;
  status: "success" | "error" | "dry-run" | "needs_confirmation";
  code: string;
  summary?: string;
  threshold: number;
  dryRun: boolean;
  forced: boolean;
  previewTasks: MainImageTaskPreview[];
  executed?: Array<{
    taskId: string;
    status: "success" | "error";
    resolvedPath?: string;
    psdOutputPath?: string;
    pngOutputPaths?: string[];
    selectedPngPath?: string;
    bundleZipPath?: string;
    code?: string;
    message?: string;
  }>;
  rolledBack?: boolean;
  rollbackCount?: number;
};
