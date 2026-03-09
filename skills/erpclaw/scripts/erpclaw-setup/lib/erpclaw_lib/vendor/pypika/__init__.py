"""
PyPika — Python SQL Query Builder (vendored)

Version: 0.51.1
License: Apache License 2.0
Source:  https://github.com/kayak/pypika
Vendored by ERPClaw to maintain zero-pip-dependency install.

Only core modules are vendored (no tests, no ClickHouse extensions).
"""

# Core query builder
from erpclaw_lib.vendor.pypika.queries import (
    AliasedQuery,
    Column,
    Database,
    Query,
    Schema,
    Table,
)
from erpclaw_lib.vendor.pypika.queries import (
    make_columns as Columns,
)
from erpclaw_lib.vendor.pypika.queries import (
    make_tables as Tables,
)

# Dialects
from erpclaw_lib.vendor.pypika.dialects import (
    Dialects,
    MSSQLQuery,
    MySQLQuery,
    OracleQuery,
    PostgreSQLQuery,
    SQLLiteQuery,
    VerticaQuery,
)

# Enums
from erpclaw_lib.vendor.pypika.enums import (
    DatePart,
    JoinType,
    Order,
)

# Terms
from erpclaw_lib.vendor.pypika.terms import (
    Array,
    Bracket,
    Case,
    Criterion,
    CustomFunction,
    EmptyCriterion,
    Field,
    FormatParameter,
    Index,
    Interval,
    JSON,
    NamedParameter,
    Not,
    NullValue,
    NumericParameter,
    Parameter,
    PyformatParameter,
    QmarkParameter,
    Rollup,
    SystemTimeValue,
    Tuple,
)

# Functions
from erpclaw_lib.vendor.pypika import functions as fn

# Utils / Exceptions
from erpclaw_lib.vendor.pypika.utils import (
    CaseException,
    FunctionException,
    GroupingException,
    JoinException,
    QueryException,
    RollupException,
    SetOperationException,
)

__version__ = "0.51.1"

NULL = NullValue()
SYSTEM_TIME = SystemTimeValue()
