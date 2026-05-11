"""
Example usage of SQL Query Generator
Demonstrates various features and use cases
"""

from sql_query_generator import (
    SQLQueryGenerator,
    DatabaseType,
    NaturalLanguageParser
)


def example_1_basic_select():
    """Example 1: Basic SELECT query"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic SELECT Query")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    query = generator.generate_select_query(
        tables=['products'],
        columns=['product_id', 'product_name', 'price', 'stock_quantity'],
        where_conditions=['price > $1', 'stock_quantity > $2'],
        order_by=['price ASC'],
        limit=50
    )
    
    print("\nGenerated Query:")
    print(query)
    
    print("\nPython Implementation:")
    print(generator.generate_implementation_example(
        query,
        "python",
        [('min_price', 10.00), ('min_stock', 0)]
    ))


def example_2_complex_join():
    """Example 2: Complex JOIN with aggregation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Complex JOIN with Aggregation")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    query = generator.generate_select_query(
        tables=['customers c'],
        columns=[
            'c.customer_id',
            'c.customer_name',
            'c.email',
            'COUNT(DISTINCT o.order_id) AS total_orders',
            'SUM(oi.quantity * oi.unit_price) AS total_revenue',
            'AVG(o.total_amount) AS avg_order_value'
        ],
        joins=[
            {
                'type': 'LEFT',
                'table': 'orders o',
                'on': 'c.customer_id = o.customer_id'
            },
            {
                'type': 'LEFT',
                'table': 'order_items oi',
                'on': 'o.order_id = oi.order_id'
            }
        ],
        where_conditions=[
            'c.status = $1',
            'o.order_date >= $2'
        ],
        group_by=[
            'c.customer_id',
            'c.customer_name',
            'c.email'
        ],
        having='COUNT(DISTINCT o.order_id) >= $3',
        order_by=['total_revenue DESC'],
        limit=100
    )
    
    print("\nGenerated Query:")
    print(query)
    
    # Analyze optimization
    _, suggestions = generator.optimize_query(query)
    print("\nOptimization Suggestions:")
    for suggestion in suggestions:
        print(f"  ✓ {suggestion}")


def example_3_insert_query():
    """Example 3: INSERT query with RETURNING"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: INSERT Query")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    query = generator.generate_insert_query(
        table='customers',
        columns=[
            'customer_name',
            'email',
            'phone',
            'address',
            'created_at'
        ],
        returning=['customer_id', 'created_at']
    )
    
    print("\nGenerated Query:")
    print(query)
    
    print("\nJavaScript Implementation:")
    print(generator.generate_implementation_example(
        query,
        "javascript",
        [
            ('customer_name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('address', '123 Main St'),
            ('created_at', 'NOW()')
        ]
    ))


def example_4_update_query():
    """Example 4: UPDATE query"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: UPDATE Query")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    query = generator.generate_update_query(
        table='products',
        set_columns=['price', 'stock_quantity', 'updated_at'],
        where_conditions=['product_id = $4', 'category_id = $5']
    )
    
    print("\nGenerated Query:")
    print(query)
    
    # Security validation
    warnings = generator.validate_query_security(query)
    if warnings:
        print("\nSecurity Warnings:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    else:
        print("\n✓ No security issues detected")


def example_5_delete_query():
    """Example 5: DELETE query"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: DELETE Query")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    query = generator.generate_delete_query(
        table='old_logs',
        where_conditions=[
            'created_at < $1',
            'status = $2'
        ]
    )
    
    print("\nGenerated Query:")
    print(query)


def example_6_create_table():
    """Example 6: CREATE TABLE query"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: CREATE TABLE Query")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    query = generator.generate_create_table_query(
        table='orders',
        columns=[
            {'name': 'order_id', 'type': 'SERIAL', 'not_null': True},
            {'name': 'customer_id', 'type': 'INTEGER', 'not_null': True},
            {'name': 'order_date', 'type': 'TIMESTAMP', 'not_null': True, 'default': 'CURRENT_TIMESTAMP'},
            {'name': 'total_amount', 'type': 'DECIMAL(10, 2)', 'not_null': True},
            {'name': 'status', 'type': 'VARCHAR(50)', 'default': "'pending'"},
            {'name': 'shipping_address', 'type': 'TEXT'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'},
            {'name': 'updated_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}
        ],
        primary_key='order_id',
        foreign_keys=[
            {
                'column': 'customer_id',
                'references_table': 'customers',
                'references_column': 'customer_id'
            }
        ]
    )
    
    print("\nGenerated Query:")
    print(query)


def example_7_multi_database():
    """Example 7: Compare queries across different databases"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Multi-Database Comparison")
    print("=" * 80)
    
    databases = [
        DatabaseType.POSTGRESQL,
        DatabaseType.MYSQL,
        DatabaseType.SQLITE,
        DatabaseType.MSSQL
    ]
    
    for db_type in databases:
        generator = SQLQueryGenerator(db_type)
        
        query = generator.generate_select_query(
            tables=['users'],
            columns=['id', 'username', 'email'],
            where_conditions=['created_at > ?'],  # Will be adapted per database
            order_by=['created_at DESC'],
            limit=10
        )
        
        print(f"\n{db_type.value.upper()}:")
        print(query)


def example_8_window_functions():
    """Example 8: Window functions query"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Window Functions")
    print("=" * 80)
    
    generator = SQLQueryGenerator(DatabaseType.POSTGRESQL)
    
    # Manual construction for complex window function
    query = """SELECT
    product_id,
    product_name,
    category_id,
    price,
    AVG(price) OVER (PARTITION BY category_id) AS category_avg_price,
    price - AVG(price) OVER (PARTITION BY category_id) AS price_diff_from_avg,
    ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC) AS price_rank_in_category,
    SUM(price) OVER (ORDER BY product_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM
    products
WHERE
    status = $1
ORDER BY
    category_id,
    price_rank_in_category;"""
    
    print("\nGenerated Query:")
    print(query)
    
    # Analyze
    _, suggestions = generator.optimize_query(query)
    print("\nOptimization Suggestions:")
    for suggestion in suggestions:
        print(f"  ✓ {suggestion}")


def example_9_cte():
    """Example 9: Common Table Expression (CTE)"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: CTE (Common Table Expression)")
    print("=" * 80)
    
    query = """WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS monthly_revenue,
        COUNT(DISTINCT customer_id) AS unique_customers
    FROM
        orders
    WHERE
        order_date >= $1
        AND status = $2
    GROUP BY
        DATE_TRUNC('month', order_date)
),
growth_calculation AS (
    SELECT
        month,
        monthly_revenue,
        unique_customers,
        LAG(monthly_revenue) OVER (ORDER BY month) AS prev_month_revenue,
        monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month) AS revenue_growth
    FROM
        monthly_sales
)
SELECT
    month,
    monthly_revenue,
    unique_customers,
    prev_month_revenue,
    revenue_growth,
    ROUND((revenue_growth / NULLIF(prev_month_revenue, 0) * 100), 2) AS growth_percentage
FROM
    growth_calculation
ORDER BY
    month DESC;"""
    
    print("\nGenerated Query:")
    print(query)


def example_10_natural_language():
    """Example 10: Natural language parsing"""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Natural Language Parsing")
    print("=" * 80)
    
    parser = NaturalLanguageParser()
    
    descriptions = [
        "Get all users who registered after January 1st",
        "Show me the total sales by product category",
        "Find the top 10 customers by revenue",
        "Update the price of product with ID 123",
        "Delete all inactive users created before 2020"
    ]
    
    for description in descriptions:
        print(f"\nDescription: '{description}'")
        components = parser.parse_description(description)
        print(f"Parsed Action: {components['action']}")
        print(f"Aggregations: {components['aggregations']}")
        print(f"Sorting: {components['sorting']}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SQL QUERY GENERATOR EXAMPLES" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    examples = [
        example_1_basic_select,
        example_2_complex_join,
        example_3_insert_query,
        example_4_update_query,
        example_5_delete_query,
        example_6_create_table,
        example_7_multi_database,
        example_8_window_functions,
        example_9_cte,
        example_10_natural_language
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
