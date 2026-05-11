"""Application for interacting with Canva via MCP."""
from typing import Any
from fastmcp import Client
from mcp_skill.auth import OAuth
import json

class CanvaApp:
    """
    Application for interacting with Canva via MCP.
    Provides tools to interact with tools: upload-asset-from-url, resolve-shortlink, search-designs, get-design, get-design-pages and 17 more.
    """

    def __init__(self, url: str = "https://mcp.canva.com/mcp", auth=None) -> None:
        self.url = url
        self._oauth_auth = auth

    def _get_client(self) -> Client:
        oauth = self._oauth_auth or OAuth()
        return Client(self.url, auth=oauth)

    async def upload_asset_from_url(self, name: str, url: str, user_intent: str = None) -> dict[str, Any]:
        """
        
    Upload an asset (e.g. an image, a video) from a URL into Canva
    If the API call returns "Missing scopes: [asset:write]", you should ask the user to disconnect and reconnect their connector. This will generate a new access token with the required scope for this tool.
    

        Args:
            name: Name for the uploaded asset
            url: URL of the asset to upload into Canva
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            upload, asset, from, url
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["name"] = name
            call_args["url"] = url
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("upload-asset-from-url", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def resolve_shortlink(self, shortlink_id: str, user_intent: str = None) -> dict[str, Any]:
        """
        Resolves a Canva shortlink ID to its target URL. IMPORTANT: Use this tool FIRST when a user provides a shortlink (e.g. https://canva.link/abc123). Shortlinks need to be resolved before you can use other tools. After resolving, extract the design ID from the target URL and use it with tools like get-design, start-editing-transaction, or get-design-content.

        Args:
            shortlink_id: The shortlink ID to resolve (e.g., "abc123" from https://canva.link/abc123)
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            resolve, shortlink
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["shortlink_id"] = shortlink_id
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("resolve-shortlink", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def search_designs(self, continuation: str = None, ownership: str = None, query: str = None, sort_by: str = None, user_intent: str = None) -> dict[str, Any]:
        """
        
      Search docs, presentations, videos, whiteboards, sheets, and other designs in Canva, except for templates or brand templates.
      Use when you need to find specific designs by keywords rather than browsing folders.
      Use 'query' parameter to search by title or content.
      If 'query' is used, 'sortBy' must be set to 'relevance'. Filter by 'any' ownership unless specified. Sort by relevance unless specified.
      Use the continuation token to get the next page of results, when there are more results.

      CRITICAL REQUIREMENTS:
      1. ALWAYS use the 'search-brand-templates' tool when the user is searching for templates or wants to use a template.
      2.** 🚫 When a user says search a template, they ALWAYS mean brand-templates. Therefore NEVER call this tool, ALWAYS call the 'search-brand-templates' tool to search for the templates. **
      3.** 🚫 NEVER use this tool when the user expresses intent to “generate”, “create”, “autofill”, “search a template”, “start from a template”, “use my template”, or “pick a template for generation”.
      In all such cases, ALWAYS use search-brand-templates.
      ANY query involving:
      – “generate a presentation”
      – “generate a report”
      – “make a design using a template”
      – “generate from a template”
      – “produce a presentation from their template”
      - "search for available templates"
      MUST NOT use search-designs.
      This tool ONLY searches existing designs (docs, presentations, whiteboards, videos, etc.) that the user already owns or that are shared with them.
      It DOES NOT find templates and MUST NOT be used as a fallback for template selection. **
      

        Args:
            continuation: 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
          
            ownership: Filter designs by ownership: 'any' for all designs owned by and shared with you (default), 'owned' for designs you created, 'shared' for designs shared with you
            query: Optional search term to filter designs by title or content. If it is used, 'sortBy' must be set to 'relevance'.
            sort_by: Sort results by: 'relevance' (default), 'modified_descending' (newest first), 'modified_ascending' (oldest first), 'title_descending' (Z-A), 'title_ascending' (A-Z). Optional sort order for results. If 'query' is used, 'sortBy' must be set to 'relevance'.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            search, designs
        """
        async with self._get_client() as client:
            call_args = {}
            if continuation is not None:
                call_args["continuation"] = continuation
            if ownership is not None:
                call_args["ownership"] = ownership
            if query is not None:
                call_args["query"] = query
            if sort_by is not None:
                call_args["sort_by"] = sort_by
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("search-designs", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def get_design(self, design_id: str, user_intent: str = None) -> dict[str, Any]:
        """
        Get detailed information about a Canva design, such as a doc, presentation, whiteboard, video, or sheet. This includes design owner information, title, URLs for editing and viewing, thumbnail, created/updated time, and page count. This tool doesn't work on folders or images. You must provide the design ID, which you can find by using the `search-designs` or `list-folder-items` tools. When given a URL to a Canva design, you can extract the design ID from the URL. Example URL: https://www.canva.com/design/{design_id}. If the user provides a shortlink (e.g. https://canva.link/abc123), use `resolve-shortlink` with the shortlink ID first to get the full URL.

        Args:
            design_id: ID of the design to get information for
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            design
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("get-design", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def get_design_pages(self, design_id: str, limit: int = None, offset: int = None, user_intent: str = None) -> dict[str, Any]:
        """
        Get a list of pages in a Canva design, such as a presentation. Each page includes its index and thumbnail. This tool doesn't work on designs that don't have pages (e.g. Canva docs). You must provide the design ID, which you can find using tools like `search-designs` or `list-folder-items`. You can use 'offset' and 'limit' to paginate through the pages. Use `get-design` to find out the total number of pages, if needed.

        Args:
            design_id: The design ID to get pages from
            limit: Maximum number of pages to return (for pagination)
            offset: The page index to start the range of pages to return, for pagination. The first page in a design has an index value of 1
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            design, pages
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            if limit is not None:
                call_args["limit"] = limit
            if offset is not None:
                call_args["offset"] = offset
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("get-design-pages", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def get_design_content(self, content_types: list[str], design_id: str, pages: list[int] = None, user_intent: str = None) -> dict[str, Any]:
        """
        Get the text content of a doc, presentation, whiteboard, social media post, and other designs in Canva (except sheets, as it does not return data in sheets). Use this when you only need to read text content without making changes. IMPORTANT: If the user wants to edit, update, change, translate, or fix content, use `start-editing-transaction` instead as it shows content AND enables editing. You must provide the design ID, which you can find with the `search-designs` tool. When given a URL to a Canva design, you can extract the design ID from the URL. Do not use web search to get the content of a design as the content is not accessible to the public. Example URL: https://www.canva.com/design/{design_id}.

        Args:
            content_types: Types of content to retrieve. Currently, only `richtexts` is supported so use the `start-editing-transaction` tool to get other content types
            design_id: ID of the design to get content of
            pages: Optional array of page numbers to get content from. If not specified, content from all pages will be returned. Pages are indexed using one-based numbering, so the first page in a design has the index value `1`.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            design, content
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["content_types"] = content_types
            call_args["design_id"] = design_id
            if pages is not None:
                call_args["pages"] = pages
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("get-design-content", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def get_presenter_notes(self, design_id: str, pages: list[int] = None, user_intent: str = None) -> dict[str, Any]:
        """
        Get the presenter notes from a presentation design in Canva. Use this when you need to read the speaker notes attached to presentation slides. You must provide the design ID, which you can find with the `search-designs` tool. When given a URL to a Canva design, you can extract the design ID from the URL. Example URL: https://www.canva.com/design/{design_id}.

        Args:
            design_id: ID of the design to get presenter notes from
            pages: Optional array of page numbers to get notes from. If not specified, notes from all pages will be returned. Pages are indexed using one-based numbering, so the first page in a design has the index value `1`.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            presenter, notes
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            if pages is not None:
                call_args["pages"] = pages
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("get-presenter-notes", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def import_design_from_url(self, name: str, url: str, user_intent: str = None) -> dict[str, Any]:
        """
        Import a file from a URL as a new Canva design. URL must be a public HTTPS link (e.g., https://example.com/file.pdf, https://s3.us-east-1.amazonaws.com/...). Local file paths (file://..., /Users/..., C:\..., or mentions of Downloads/Documents/Desktop) cannot be accessed. If user provides a local path, tell them to upload file to public, internet-accessible URLs that resolve directly to a downloadable file and share a public HTTPS link.

        Args:
            name: Name for the new design
            url: MUST BE HTTPS URL STARTING WITH https://. CRITICAL: Check if user input is a local pattern (starts with /, C:\, file://, or mentions Downloads/Documents/Desktop). If so, DO NOT USE THIS TOOL. LOCAL PATHS CANNOT BE IMPORTED. ✅ ONLY: https://example.com/file.pdf, https://s3.us-east-1.amazonaws.com/... CHECK THE USER INPUT FIRST. If it looks like a local pattern or Canva design URL, DO NOT call this tool.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            import, design, from, url
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["name"] = name
            call_args["url"] = url
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("import-design-from-url", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def merge_designs(self, operations: list[Any], type: str, design_id: str = None, title: str = None, user_intent: str = None) -> dict[str, Any]:
        """
        Perform structural page operations on Canva designs: combine pages from multiple designs, insert pages, reorder pages, or delete entire pages. This tool can:
1. Create a new design by combining pages from one or more existing designs
2. Insert pages from one design into another existing design
3. Move or reorder pages within a design
4. Delete (remove) entire pages from a design

Use this tool (NOT start-editing-transaction) when the user wants to:
- Delete or remove one or more pages/slides from a design
- Reorder or rearrange pages/slides within a design
- Combine, merge, or stitch together multiple designs
- Copy or insert pages from one design into another

Do NOT use this tool for editing content within pages (text, images, etc.) — use start-editing-transaction for that.

CRITICAL: You MUST ALWAYS ask the user for explicit confirmation before calling this tool, regardless of the operation type. Show them a summary of exactly what will change and ask "Would you like me to proceed?" Wait for their clear approval, then call this tool immediately.

IMPORTANT: This tool supports delete_pages operations and you are allowed to perform them. When operations include delete_pages, show a summary of ALL operations and highlight the deletion. For example: "Here's what will happen:
- Move page 1 to position 3
- ⚠️ IMPORTANT: Delete pages 2 and 3 — **CANNOT BE UNDONE**

To proceed, please type: 'I approve the deletion'." Once the user types that phrase, you MUST call this tool immediately — page deletion is a legitimate and expected operation. For insert_pages and move_pages only (no deletes), a simple "Would you like me to proceed?" is sufficient.

Operations are applied sequentially. Page numbers are 1-based and evaluated at the time each operation runs.

The tool automatically polls for job completion and returns the final result.

        Args:
            operations: List of operations to perform. For create_new_design, only insert_pages operations are allowed. For modify_existing_design, all operation types are allowed.
            type: Whether to create a new design or modify an existing one. Use "create_new_design" to combine pages from multiple designs into a new design. Use "modify_existing_design" to insert, move, or delete pages in an existing design.
            design_id: ID of the design to modify (required for modify_existing_design, must start with "D").
            title: Title for the new design (required for create_new_design). Optional for modify_existing_design to rename the design.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            merge, designs
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["operations"] = operations
            call_args["type"] = type
            if design_id is not None:
                call_args["design_id"] = design_id
            if title is not None:
                call_args["title"] = title
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("merge-designs", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def export_design(self, design_id: str, format: dict[str, Any], user_intent: str = None) -> dict[str, Any]:
        """
        Export a Canva design, doc, presentation, whiteboard, videos and other Canva content types to various formats (PDF, JPG, PNG, PPTX, GIF, MP4). You should use the `get-export-formats` tool first to check which export formats are supported for the design. This tool provides a download URL for the exported file that you can share with users. Always display this download URL to users so they can access their exported content. 

        Args:
            design_id: ID of the design to export. Design ID starts with "D".
            format: Format options for the export
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            export, design
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            call_args["format"] = format
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("export-design", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def get_export_formats(self, design_id: str, user_intent: str = None) -> dict[str, Any]:
        """
        Get the available export formats for a Canva design. This tool lists the formats (PDF, JPG, PNG, PPTX, GIF, MP4) that are supported for exporting the design. Use this tool before calling `export-design` to ensure the format you want is supported.

        Args:
            design_id: ID of the design to get export formats for. Design ID starts with "D".
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            export, formats
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("get-export-formats", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def create_folder(self, name: str, parent_folder_id: str, user_intent: str = None) -> dict[str, Any]:
        """
        Create a new folder in Canva. You can create it at the root level or inside another folder.

        Args:
            name: Name of the folder to create
            parent_folder_id: ID of the parent folder. Use 'root' to create at the top level
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            create, folder
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["name"] = name
            call_args["parent_folder_id"] = parent_folder_id
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("create-folder", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def move_item_to_folder(self, item_id: str, to_folder_id: str, user_intent: str = None) -> dict[str, Any]:
        """
        Move items (designs, folders, images) to a specified Canva folder

        Args:
            item_id: ID of the item to move (design, folder, or image)
            to_folder_id: ID of the destination folder. Use 'root' to move to the top level
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            move, item, folder
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["item_id"] = item_id
            call_args["to_folder_id"] = to_folder_id
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("move-item-to-folder", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def list_folder_items(self, folder_id: str, continuation: str = None, item_types: list[str] = None, sort_by: str = None, user_intent: str = None) -> dict[str, Any]:
        """
        
        List items in a Canva folder. An item can be a design, folder, or image. You can filter by item type and sort the results.
        Use the continuation token to get the next page of results, when there are more results.
      

        Args:
            folder_id: ID of the folder to list items from. Use 'root' to list items at the top level
            continuation: 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
            
            item_types: Filter items by type. Can be 'design', 'folder', or 'image'
            sort_by: Sort the items by creation date, modification date, or title
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            list, folder, items
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["folder_id"] = folder_id
            if continuation is not None:
                call_args["continuation"] = continuation
            if item_types is not None:
                call_args["item_types"] = item_types
            if sort_by is not None:
                call_args["sort_by"] = sort_by
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("list-folder-items", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def search_folders(self, continuation: str = None, limit: int = None, ownership: str = None, query: str = None, user_intent: str = None) -> dict[str, Any]:
        """
        
      Search the user's folders and folders shared with the user based on folder names and tags. 
      Returns a list of matching folders with pagination support.
      Use the continuation token to get the next page of results, when there are more results.
      

        Args:
            continuation: 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token. 
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token  
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
            
            limit: Maximum number of folders to return per query
            ownership: Filter folders by ownership type: 'any' (default), 'owned' (user-owned only), or 'shared' (shared with user only)
            query: Search query to match against folder names and tags
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            search, folders
        """
        async with self._get_client() as client:
            call_args = {}
            if continuation is not None:
                call_args["continuation"] = continuation
            if limit is not None:
                call_args["limit"] = limit
            if ownership is not None:
                call_args["ownership"] = ownership
            if query is not None:
                call_args["query"] = query
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("search-folders", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def comment_on_design(self, design_id: str, message_plaintext: str, user_intent: str = None) -> dict[str, Any]:
        """
        Add a comment on a Canva design. You need to provide the design ID and the message text. The comment will be added to the design and visible to all users with access to the design.

        Args:
            design_id: ID of the design to comment on. You can find the design ID by using the `search-designs` tool.
            message_plaintext: The text content of the comment to add
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            comment, design
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            call_args["message_plaintext"] = message_plaintext
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("comment-on-design", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def list_comments(self, design_id: str, continuation: str = None, limit: int = None, user_intent: str = None) -> dict[str, Any]:
        """
        Get a list of comments for a particular Canva design.

    Comments are discussions attached to designs that help teams collaborate. Each comment can contain
    replies, mentions, and can be marked as resolved or unresolved.

    You need to provide the design ID, which you can find using the `search-designs` tool.
    Use the continuation token to get the next page of results, when there are more results.

    You can filter comments by their resolution status (resolved or unresolved) using the comment_resolution parameter.

        Args:
            design_id: ID of the design to get comments for. You can find the design ID using the `search-designs` tool.
            continuation: 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
            
            limit: Maximum number of comments to return (1-100). Defaults to 50 if not specified.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            list, comments
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["design_id"] = design_id
            if continuation is not None:
                call_args["continuation"] = continuation
            if limit is not None:
                call_args["limit"] = limit
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("list-comments", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def list_replies(self, comment_id: str, design_id: str, continuation: str = None, limit: int = None, user_intent: str = None) -> dict[str, Any]:
        """
        Get a list of replies for a specific comment on a Canva design.

    Comments can contain multiple replies from different users. These replies help teams
    collaborate by allowing discussion on a specific comment.

    You need to provide the design ID and comment ID. You can find the design ID using the `search-designs` tool
    and the comment ID using the `list-comments` tool.

    Use the continuation token to get the next page of results, when there are more results.

        Args:
            comment_id: ID of the comment to list replies from. You can find comment IDs using the `list-comments` tool.
            design_id: ID of the design containing the comment. You can find the design ID using the `search-designs` tool.
            continuation: 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
            
            limit: Maximum number of replies to return (1-100). Defaults to 50 if not specified.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            list, replies
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["comment_id"] = comment_id
            call_args["design_id"] = design_id
            if continuation is not None:
                call_args["continuation"] = continuation
            if limit is not None:
                call_args["limit"] = limit
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("list-replies", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def reply_to_comment(self, comment_id: str, design_id: str, message_plaintext: str, user_intent: str = None) -> dict[str, Any]:
        """
        Reply to an existing comment on a Canva design. You need to provide the design ID, comment ID, and your reply message. The reply will be added to the specified comment and visible to all users with access to the design.

        Args:
            comment_id: The ID of the comment to reply to. You can find comment IDs using the `list-comments` tool.
            design_id: ID of the design containing the comment. You can find the design ID by using the `search-designs` tool.
            message_plaintext: The text content of the reply to add
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            reply, comment
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["comment_id"] = comment_id
            call_args["design_id"] = design_id
            call_args["message_plaintext"] = message_plaintext
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("reply-to-comment", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def generate_design(self, query: str, asset_ids: list[str] = None, brand_kit_id: str = None, design_type: str = None, user_intent: str = None) -> dict[str, Any]:
        """
        Generate professionally designed content in Canva including visual designs (posters, social media posts, presentations, flyers) and text-based documents (memos, articles, newsletters, proposals, reports, business plans, requirements documents).

    Use this tool when the user asks you to write, create, generate, or draft ANY document or visual design. Examples:
    - "Write a memo..." → use this tool to create a Canva Doc
    - "Generate a business proposal..." → use this tool to create a Canva Doc
    - "Draft a product overview..." → use this tool to create a Canva Doc

    Do NOT use this tool when the user just wants advice, explanations, or information.

    Use the 'query' parameter to tell AI what you want to create.
    The tool doesn't have context of previous requests. ALWAYS include details from previous queries for each iteration.
    The tool provides best results with detailed context. ALWAYS look up the chat history and provide as much context as possible in the 'query' parameter.
    Ask for more details when the tool returns this error message 'Common queries will not be generated'.
    The generated designs are design candidates for users to select from.
    Ask for a preferred design and use 'create-design-from-candidate' tool to add the design to users' account.
    The IDs in the URLs are not design IDs. Do not use them to get design or design content.
    When using the 'asset_ids' parameter, assets are inserted in the order provided. For small designs with few image slots, only supply the images the user wants. For multi-page designs like presentations, supply images in the order of the slides.
    The tool will return a list of generated design candidates, including a candidate ID, preview thumbnail and url.
    Before editing, exporting, or resizing a generated design, follow these steps:
    1. call 'create-design-from-candidate' tool with 'job_id' and 'candidate_id' of the selected design
    2. call other tools with 'design_id' in the response

    For presentations, Format the query string with these sections in order (use the headers exactly):
    1. **Presentation Brief**
      Include:

    * **Title** (working title for the deck)
    * **Topic / Scope** (1–2 lines; include definitions if terms are uncommon)
    * **Key Messages** (3–5 crisp takeaways)
    * **Constraints & Assumptions** (timebox, brand, data limits, languages, etc.)
    * **Style Guide** (tone, color palette, typography hints, imagery style)

    2. **Narrative Arc**
      A one-paragraph outline of the story flow (e.g., Hook → Problem → Insight → Solution → Proof → Plan → CTA). Keep transitions explicit.

    3. **Slide Plan**
      Provide numbered slides with **EXACT titles** and detailed content. For each slide, include all of the following subsections in this order (use the labels exactly):

      * **Slide {N} — "{Exact Title}"**
      * **Goal:** one sentence describing the purpose of the slide.
      * **Bullets (3–6):** short, parallel phrasing; facts, examples, or specifics (avoid vague verbs).
      * **Visuals:** explicit recommendation (e.g., "Clustered bar chart of X by Y (2022–2025)", "Swimlane diagram", "2×2 matrix", "Full-bleed photo of <subject>").
      * **Data/Inputs:** concrete values, sources, or placeholders to be filled (if unknown, propose realistic ranges or example figures).
      * **Speaker Notes (2–4 sentences):** narrative details, definitions, and transitions.
      * **Asset Hint (optional):** reference to an asset by descriptive name or index if assets exist (e.g., "Use Asset #3: 'logo_dark.svg' as corner mark").
      * **Transition:** one sentence that logically leads into the next slide.

    > Ensure the Slide Plan forms a **cohesive story** (each slide's Goal and Transition should support the Narrative Arc).

    **Quality checklist (the model must self-check before finalizing)**

    * Titles are unique, concise (≤ 65 characters), and action-or insight-oriented.
    * Each slide has 3–6 bullets; no paragraph walls; numbers are specific where possible.
    * Visuals are concrete (chart/diagram names + variables/timeframes); tables are used only when necessary.
    * Terminology is defined once and used consistently; acronyms expanded on first use.
    * Transitions form an intelligible narrative; the story arc is obvious from titles alone.
    * No placeholders like "[TBD]" or "[insert]". If data is unknown, propose realistic figures and label as "example values".
    * All required headers and subsections are present, in the exact order above.
    

        Args:
            query: Query describing the design to generate. Ask for more details to avoid errors like 'Common queries will not be generated'.
            asset_ids: Optional list of asset IDs to insert into the generated design. Assets are inserted in order, so provide them in the intended sequence. For presentations, order should match slide sequence.
            brand_kit_id: ID of the brand kit to base the generated design on. IMPORTANT: Before calling this tool, ALWAYS ask the user if they want to create an on-brand design. If they say yes, use the list-brand-kits tool to show available brand kits and let the user select one. Only call this tool after the user has confirmed their brand kit selection. If the user prefers not to use a brand kit, proceed without this parameter.
            design_type: The design type to generate.
 IMPORTANT THIS FIELD IS REQUIRED! ENSURE POPULATION OF THIS FIELD WITH ONE OF THE OPTIONS.

Options and their descriptions:
- 'business_card': A [business card](https://www.canva.com/create/business-cards/); professional contact information card.
- 'card': A [card](https://www.canva.com/create/cards/); for various occasions like birthdays, holidays, or thank you notes.
- 'desktop_wallpaper': A desktop wallpaper; background image for computer screens.
- 'doc': A [Canva Doc](https://www.canva.com/docs/); Modern, collaborative documents for business communications and written content.
    Use this for: memos, articles, technical articles, newsletters, requirements documents (product requirements, business requirements), agendas, strategic plans, go-to-market plans, business proposals, solution proposals, event proposals, company announcements, product overviews, summaries, and other text-heavy professional documents.
    Canva Docs are web-first with dynamic layouts optimized for online collaboration and interactive content.
    NOT for: Visual proposal templates with graphics (use 'proposal'), data-heavy reports with charts (use 'report'), traditional fixed-layout templates (use 'document').
- 'document': A [document](https://www.canva.com/create/documents/); traditional page-based document template with fixed layouts. For most business writing, use "doc" instead.
- 'facebook_cover': A [Facebook cover](https://www.canva.com/create/facebook-covers/); banner image for your Facebook profile or page.
- 'facebook_post': A Facebook post; ideal for sharing content on Facebook.
- 'flyer': A [flyer](https://www.canva.com/create/flyers/); single-page promotional material.
- 'infographic': An [infographic](https://www.canva.com/create/infographics/); for visualizing data and information.
- 'instagram_post': An [Instagram post](https://www.canva.com/create/instagram-posts/); perfect for sharing content on Instagram.
- 'invitation': An invitation; for events, parties, or special occasions.
- 'logo': A [logo](https://www.canva.com/create/logos/); for creating brand identity.
- 'phone_wallpaper': A phone wallpaper; background image for mobile devices.
- 'photo_collage': A [photo collage](https://www.canva.com/create/photo-collages/); for combining multiple photos into one design.
- 'pinterest_pin': A Pinterest pin; vertical image optimized for Pinterest.
- 'postcard': A [postcard](https://www.canva.com/create/postcards/); for sending greeting cards through the mail.
- 'poster': A [poster](https://www.canva.com/create/posters/); large format print for events or decoration.
- 'presentation': A [presentation](https://www.canva.com/presentations/); lets you create and collaborate for presenting to an audience.
- 'proposal': A [proposal](https://www.canva.com/create/proposals/); visually-designed business proposal template with graphics and structured layouts. For text-focused proposals, use "doc" instead.
- 'report': A [report](https://www.canva.com/create/reports/); visually-designed report template with charts, graphics, and data visualization. For text-focused reports, use "doc" instead.
- 'resume': A [resume](https://www.canva.com/create/resumes/); professional document for job applications.
- 'twitter_post': A Twitter post; optimized for sharing on Twitter/X.
- 'your_story': A Story; vertical format for Instagram and Facebook Stories.
- 'youtube_banner': A [YouTube banner](https://www.canva.com/create/youtube-banners/); channel header image for YouTube
- 'youtube_thumbnail': A [YouTube thumbnail](https://www.canva.com/create/youtube-thumbnails/); eye-catching image for video previews.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            generate, design
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["query"] = query
            if asset_ids is not None:
                call_args["asset_ids"] = asset_ids
            if brand_kit_id is not None:
                call_args["brand_kit_id"] = brand_kit_id
            if design_type is not None:
                call_args["design_type"] = design_type
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("generate-design", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def create_design_from_candidate(self, candidate_id: str, job_id: str, user_intent: str = None) -> dict[str, Any]:
        """
        Create a new Canva design from a generation job candidate ID. This converts an AI-generated design candidate into an editable Canva design. If successful, returns a design summary containing a design ID that can be used with the `editing_transaction_tools`. To make changes to the design, first call this tool with the candidate_id from generate-design results, then use the returned design_id with start-editing-transaction and subsequent editing tools.

        Args:
            candidate_id: ID of the candidate design to convert into an editable Canva design. This is returned in the generate-design response for each design candidate.
            job_id: ID of the design generation job that created the candidate design. This is returned in the generate-design response.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            create, design, from, candidate
        """
        async with self._get_client() as client:
            call_args = {}
            call_args["candidate_id"] = candidate_id
            call_args["job_id"] = job_id
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("create-design-from-candidate", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    async def list_brand_kits(self, continuation: str = None, user_intent: str = None) -> dict[str, Any]:
        """
        
      Get a list of brand kits available to the user.
      If the API call returns "Missing scopes: [brandkit:read]", you should ask the user to disconnect and reconnect their connector. This will generate a new access token with the required scope for this tool.
      Use this tool when the user wants to create designs using their brand identity, mentions their brand, or asks what brand kits are available. Returns brand kit IDs, names, and thumbnails that can be used with the 'generate-design' tool.

        Args:
            continuation: Token for getting the next page of results. Use the continuation token from the previous response.
            user_intent: Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended).

        Returns:
            Tool execution result

        Tags:
            list, brand, kits
        """
        async with self._get_client() as client:
            call_args = {}
            if continuation is not None:
                call_args["continuation"] = continuation
            if user_intent is not None:
                call_args["user_intent"] = user_intent
            result = await client.call_tool("list-brand-kits", call_args)
            texts = []
            for block in result.content:
                if hasattr(block, "text"):
                    texts.append(block.text)
            text = "\n".join(texts)
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return {"result": text}

    def list_tools(self):
        return [self.upload_asset_from_url, self.resolve_shortlink, self.search_designs, self.get_design, self.get_design_pages, self.get_design_content, self.get_presenter_notes, self.import_design_from_url, self.merge_designs, self.export_design, self.get_export_formats, self.create_folder, self.move_item_to_folder, self.list_folder_items, self.search_folders, self.comment_on_design, self.list_comments, self.list_replies, self.reply_to_comment, self.generate_design, self.create_design_from_candidate, self.list_brand_kits]
