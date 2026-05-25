#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BettaFish 知识图谱生成工具
基于 BettaFish GraphRAG 思想，生成可视化图谱数据
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib


@dataclass
class GraphNode:
    """图谱节点"""
    id: str
    name: str
    type: str  # topic/engine/section/query/source/entity/sentiment
    group: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'group': self.group,
            **self.properties
        }


@dataclass
class GraphLink:
    """图谱关系"""
    source: str
    target: str
    type: str = "related"  # analyzed_by/contains/searched/found/mentions/has_sentiment
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type,
            **self.properties
        }


class KnowledgeGraphBuilder:
    """
    知识图谱构建器

    基于 BettaFish GraphRAG 架构，构建包含以下节点的知识图谱：
    - topic: 分析主题
    - engine: 分析引擎 (query/media/insight/forum)
    - section: 报告段落
    - query: 搜索查询
    - source: 信息来源
    - entity: 命名实体（品牌/人物/产品）
    - sentiment: 情感节点
    """

    def __init__(self, topic: str):
        self.topic = topic
        self.nodes: Dict[str, GraphNode] = {}
        self.links: List[GraphLink] = []
        self._node_counter = 0

    def _generate_id(self, prefix: str) -> str:
        """生成唯一ID"""
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"

    def _hash(self, text: str) -> str:
        """生成文本哈希"""
        return hashlib.md5(text.encode()).hexdigest()[:8]

    def add_topic_node(self, properties: Optional[Dict] = None) -> str:
        """
        添加主题节点

        Args:
            properties: 额外属性

        Returns:
            节点ID
        """
        node_id = f"topic_{self._hash(self.topic)}"
        node = GraphNode(
            id=node_id,
            name=self.topic,
            type="topic",
            group=1,
            properties=properties or {}
        )
        self.nodes[node_id] = node
        return node_id

    def add_engine_node(
        self,
        engine_name: str,
        report_title: str = "",
        properties: Optional[Dict] = None
    ) -> str:
        """
        添加引擎节点

        Args:
            engine_name: 引擎名称 (query/media/insight/forum)
            report_title: 报告标题
            properties: 额外属性

        Returns:
            节点ID
        """
        node_id = f"engine_{engine_name}"

        props = {
            'engine_type': engine_name,
            'report_title': report_title,
            'original_query': self.topic,
            **(properties or {})
        }

        node = GraphNode(
            id=node_id,
            name=engine_name,
            type="engine",
            group=2,
            properties=props
        )
        self.nodes[node_id] = node

        # 自动添加与主题的关系
        if f"topic_{self._hash(self.topic)}" in self.nodes:
            self.add_link(
                f"topic_{self._hash(self.topic)}",
                node_id,
                "analyzed_by"
            )

        return node_id

    def add_section_node(
        self,
        engine_id: str,
        title: str,
        summary: str = "",
        order: int = 0,
        properties: Optional[Dict] = None
    ) -> str:
        """
        添加段落节点

        Args:
            engine_id: 所属引擎ID
            title: 段落标题
            summary: 段落摘要
            order: 顺序
            properties: 额外属性

        Returns:
            节点ID
        """
        node_id = self._generate_id("section")

        props = {
            'title': title,
            'summary': summary[:200] if summary else "",
            'order': order,
            'engine': engine_id,
            **(properties or {})
        }

        node = GraphNode(
            id=node_id,
            name=title,
            type="section",
            group=3,
            properties=props
        )
        self.nodes[node_id] = node

        # 添加与引擎的关系
        self.add_link(engine_id, node_id, "contains")

        return node_id

    def add_query_node(
        self,
        section_id: str,
        query_text: str,
        search_tool: str = "",
        properties: Optional[Dict] = None
    ) -> str:
        """
        添加搜索查询节点

        Args:
            section_id: 所属段落ID
            query_text: 查询文本
            search_tool: 搜索工具
            properties: 额外属性

        Returns:
            节点ID
        """
        node_id = self._generate_id("query")

        # 截断长查询
        display_text = query_text[:50] + "..." if len(query_text) > 50 else query_text

        props = {
            'query_text': query_text,
            'search_tool': search_tool,
            'section_ref': section_id,
            **(properties or {})
        }

        node = GraphNode(
            id=node_id,
            name=display_text,
            type="query",
            group=4,
            properties=props
        )
        self.nodes[node_id] = node

        # 添加与段落的关系
        self.add_link(section_id, node_id, "searched")

        return node_id

    def add_source_node(
        self,
        query_id: str,
        url: str,
        title: str = "",
        source_type: str = "web",
        properties: Optional[Dict] = None
    ) -> str:
        """
        添加来源节点

        Args:
            query_id: 所属查询ID
            url: 来源URL
            title: 来源标题
            source_type: 来源类型
            properties: 额外属性

        Returns:
            节点ID
        """
        # 使用URL哈希作为ID，避免重复
        node_id = f"source_{self._hash(url)}"

        # 如果已存在，只添加关系
        if node_id in self.nodes:
            self.add_link(query_id, node_id, "found")
            return node_id

        props = {
            'url': url,
            'source_type': source_type,
            **(properties or {})
        }

        node = GraphNode(
            id=node_id,
            name=title or url[:30] + "...",
            type="source",
            group=5,
            properties=props
        )
        self.nodes[node_id] = node

        # 添加与查询的关系
        self.add_link(query_id, node_id, "found")

        return node_id

    def add_entity_node(
        self,
        name: str,
        entity_type: str = "brand",  # brand/person/product/location
        properties: Optional[Dict] = None
    ) -> str:
        """
        添加命名实体节点

        Args:
            name: 实体名称
            entity_type: 实体类型
            properties: 额外属性

        Returns:
            节点ID
        """
        node_id = f"entity_{self._hash(name)}"

        # 如果已存在，返回已有ID
        if node_id in self.nodes:
            return node_id

        props = {
            'entity_type': entity_type,
            **(properties or {})
        }

        node = GraphNode(
            id=node_id,
            name=name,
            type="entity",
            group=6,
            properties=props
        )
        self.nodes[node_id] = node

        return node_id

    def add_sentiment_node(
        self,
        parent_id: str,
        sentiment_type: str,  # positive/negative/neutral
        confidence: float,
        properties: Optional[Dict] = None
    ) -> str:
        """
        添加情感节点

        Args:
            parent_id: 父节点ID
            sentiment_type: 情感类型
            confidence: 置信度
            properties: 额外属性

        Returns:
            节点ID
        """
        node_id = self._generate_id("sentiment")

        props = {
            'sentiment_type': sentiment_type,
            'confidence': confidence,
            **(properties or {})
        }

        node = GraphNode(
            id=node_id,
            name=sentiment_type,
            type="sentiment",
            group=7,
            properties=props
        )
        self.nodes[node_id] = node

        # 添加与父节点的关系
        self.add_link(parent_id, node_id, "has_sentiment")

        return node_id

    def add_link(
        self,
        source: str,
        target: str,
        link_type: str = "related",
        properties: Optional[Dict] = None
    ) -> None:
        """
        添加关系

        Args:
            source: 源节点ID
            target: 目标节点ID
            link_type: 关系类型
            properties: 额外属性
        """
        # 避免自环
        if source == target:
            return

        # 检查节点是否存在
        if source not in self.nodes or target not in self.nodes:
            return

        link = GraphLink(
            source=source,
            target=target,
            type=link_type,
            properties=properties or {}
        )
        self.links.append(link)

    def build_from_analysis_result(
        self,
        query_results: List[Dict],
        media_results: List[Dict],
        insight_results: Dict
    ) -> Dict:
        """
        从分析结果构建完整知识图谱

        Args:
            query_results: QueryAgent 搜索结果
            media_results: MediaAgent 分析结果
            insight_results: InsightAgent 分析结果

        Returns:
            图谱数据字典
        """
        # 1. 创建主题节点
        topic_id = self.add_topic_node({
            'analysis_time': datetime.now().isoformat(),
            'total_sources': len(query_results) + len(media_results)
        })

        # 2. 创建引擎节点
        query_engine_id = self.add_engine_node("QueryAgent", "文本搜索报告")
        media_engine_id = self.add_engine_node("MediaAgent", "多媒体分析报告")
        insight_engine_id = self.add_engine_node("InsightAgent", "深度洞察报告")

        # 3. 为 QueryAgent 创建段落和查询节点
        if query_results:
            section_id = self.add_section_node(
                query_engine_id,
                "网络搜索结果",
                summary=f"从网络搜索获取了 {len(query_results)} 条相关信息",
                order=1
            )

            for i, result in enumerate(query_results[:5]):  # 只取前5条
                query_node_id = self.add_query_node(
                    section_id,
                    result.get('title', ''),
                    result.get('source', 'web_search')
                )

                # 添加来源
                if result.get('url'):
                    self.add_source_node(
                        query_node_id,
                        result['url'],
                        result.get('title', ''),
                        result.get('source_type', 'web')
                    )

        # 4. 为 MediaAgent 创建段落
        if media_results:
            section_id = self.add_section_node(
                media_engine_id,
                "多媒体内容分析",
                summary=f"分析了 {len(media_results)} 条多媒体内容",
                order=1
            )

        # 5. 为 InsightAgent 创建段落和实体
        sentiment_data = insight_results.get('sentiment', {})
        if sentiment_data:
            section_id = self.add_section_node(
                insight_engine_id,
                "情感分析",
                summary=f"正面 {sentiment_data.get('positive_pct', 0)}%, 负面 {sentiment_data.get('negative_pct', 0)}%",
                order=1
            )

            # 添加情感节点
            if sentiment_data.get('positive_count', 0) > 0:
                self.add_sentiment_node(
                    section_id,
                    'positive',
                    sentiment_data.get('positive_pct', 0) / 100
                )

            if sentiment_data.get('negative_count', 0) > 0:
                self.add_sentiment_node(
                    section_id,
                    'negative',
                    sentiment_data.get('negative_pct', 0) / 100
                )

        # 6. 添加关键词实体
        keywords = insight_results.get('keywords', [])
        for keyword, freq in keywords[:10]:
            entity_id = self.add_entity_node(keyword, 'keyword', {'frequency': freq})
            # 连接到主题
            self.add_link(topic_id, entity_id, 'mentions')

        return self.to_dict()

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'topic': self.topic,
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'links': [link.to_dict() for link in self.links],
            'stats': {
                'node_count': len(self.nodes),
                'link_count': len(self.links),
                'node_types': list(set(node.type for node in self.nodes.values()))
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def get_subgraph(
        self,
        center_node_id: str,
        depth: int = 1
    ) -> Dict:
        """
        获取子图谱

        Args:
            center_node_id: 中心节点ID
            depth: 扩展深度

        Returns:
            子图谱数据
        """
        if center_node_id not in self.nodes:
            return {'nodes': [], 'links': []}

        included_nodes = {center_node_id}
        included_links = []

        current_layer = {center_node_id}

        for _ in range(depth):
            next_layer = set()
            for link in self.links:
                if link.source in current_layer:
                    included_nodes.add(link.target)
                    included_links.append(link.to_dict())
                    next_layer.add(link.target)
                elif link.target in current_layer:
                    included_nodes.add(link.source)
                    included_links.append(link.to_dict())
                    next_layer.add(link.source)
            current_layer = next_layer

        return {
            'nodes': [self.nodes[nid].to_dict() for nid in included_nodes],
            'links': included_links
        }


# 便捷函数
def build_knowledge_graph(
    topic: str,
    query_results: List[Dict] = None,
    media_results: List[Dict] = None,
    insight_results: Dict = None
) -> Dict:
    """
    便捷函数：构建知识图谱

    Args:
        topic: 分析主题
        query_results: QueryAgent 结果
        media_results: MediaAgent 结果
        insight_results: InsightAgent 结果

    Returns:
        图谱数据字典
    """
    builder = KnowledgeGraphBuilder(topic)
    return builder.build_from_analysis_result(
        query_results or [],
        media_results or [],
        insight_results or {}
    )


def generate_graph_html(graph_data: Dict, width: int = 800, height: int = 600) -> str:
    """
    生成知识图谱的 HTML 代码片段

    Args:
        graph_data: 图谱数据
        width: 画布宽度
        height: 画布高度

    Returns:
        HTML 代码
    """
    nodes_json = json.dumps(graph_data.get('nodes', []))
    links_json = json.dumps(graph_data.get('links', []))

    html = f'''
<div id="knowledge-graph-container" style="width: 100%; height: {height}px;"></div>
<script>
(function() {{
    const container = document.getElementById('knowledge-graph-container');
    const width = container.clientWidth || {width};
    const height = {height};

    const svg = d3.select('#knowledge-graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const colorMap = {{
        topic: '#ff6b6b',
        engine: '#4ecdc4',
        section: '#45b7d1',
        query: '#f9ca24',
        source: '#6c5ce7',
        entity: '#a29bfe',
        sentiment: '#fd79a8'
    }};

    const graphData = {{
        nodes: {nodes_json},
        links: {links_json}
    }};

    const simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
        .selectAll('line')
        .data(graphData.links)
        .join('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', 2);

    const node = svg.append('g')
        .selectAll('g')
        .data(graphData.nodes)
        .join('g')
        .call(d3.drag()
            .on('start', (e, d) => {{
                if (!e.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x; d.fy = d.y;
            }})
            .on('drag', (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
            .on('end', (e, d) => {{
                if (!e.active) simulation.alphaTarget(0);
                d.fx = null; d.fy = null;
            }}));

    node.append('circle')
        .attr('r', d => d.type === 'topic' ? 25 : d.type === 'engine' ? 20 : 15)
        .attr('fill', d => colorMap[d.type] || '#999')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

    node.append('text')
        .text(d => d.name)
        .attr('x', 0)
        .attr('y', d => d.type === 'topic' ? 40 : d.type === 'engine' ? 35 : 28)
        .attr('text-anchor', 'middle')
        .style('font-size', '11px')
        .style('fill', 'var(--text-color)');

    simulation.on('tick', () => {{
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
    }});
}})();
</script>
'''
    return html


if __name__ == '__main__':
    # 测试
    print("=== 测试知识图谱构建 ===")

    builder = KnowledgeGraphBuilder("某咖啡连锁品牌")

    # 添加主题和引擎
    topic_id = builder.add_topic_node({'create_time': datetime.now().isoformat()})
    query_engine = builder.add_engine_node("QueryAgent", "搜索分析报告")

    # 添加段落和查询
    section_id = builder.add_section_node(
        query_engine,
        "产品评价分析",
        "分析了用户对某咖啡品牌的评价",
        order=1
    )

    query_id = builder.add_query_node(
        section_id,
        "某咖啡品牌评测",
        "web_search"
    )

    # 添加来源
    builder.add_source_node(
        query_id,
        "https://zhihu.com/question/xxx",
        "如何评价某咖啡品牌？",
        "zhihu"
    )

    # 添加实体
    builder.add_entity_node("某咖啡品牌", "brand")
    builder.add_entity_node("某创始人", "person")

    # 输出图谱数据
    graph_data = builder.to_dict()
    print(f"节点数: {graph_data['stats']['node_count']}")
    print(f"关系数: {graph_data['stats']['link_count']}")
    print(f"节点类型: {graph_data['stats']['node_types']}")
    print("\n图谱JSON:")
    print(builder.to_json())
