# Service Catalog

## Overview
Software catalog entities including services, teams, domains, and their relationships and ownership.

## dx_catalog_entities
Core catalog entries (services, teams, domains).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| entity_type_id | bigint | FK to dx_catalog_entity_types |
| domain_entity_id | bigint | Parent domain entity |
| source_id | text | External identifier |
| public_id | text | Public identifier |
| identifier | varchar | Unique identifier |
| entity_type_identifier | varchar | Type: service, team, domain |
| name | text | Entity name |
| description | text | Entity description |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last update |

**Entity types:**
- `service`: Individual software components/services
- `team`: DX teams (mirrors dx_teams)
- `domain`: Vertical groupings of services

**Common queries:**
```sql
-- List all services
SELECT identifier, name, description
FROM dx_catalog_entities
WHERE entity_type_identifier = 'service';

-- Services by domain
SELECT d.name as domain, s.name as service
FROM dx_catalog_entities s
JOIN dx_catalog_entities d ON s.domain_entity_id = d.id
WHERE s.entity_type_identifier = 'service'
ORDER BY d.name, s.name;

-- Count services per team
SELECT t.name as team, COUNT(e.id) as service_count
FROM dx_catalog_entity_owners eo
JOIN dx_catalog_entities e ON eo.entity_id = e.id
JOIN dx_teams t ON eo.team_id = t.id
WHERE e.entity_type_identifier = 'service'
GROUP BY t.name ORDER BY service_count DESC;
```

## dx_catalog_entity_types
Entity type definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| identifier | varchar | Type identifier |
| icon | text | Display icon |
| description | text | Type description |
| public_id | text | Public identifier |

Current types:
- `service`: Individual software components
- `team`: DX teams
- `domain`: Vertical groupings of entities

## dx_catalog_entity_owners
Ownership mapping between entities and teams/users.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| entity_id | bigint | FK to dx_catalog_entities |
| team_id | bigint | FK to dx_teams (owner team) |
| user_id | bigint | FK to dx_users (owner user) |
| source_id | text | External identifier |

**Common queries:**
```sql
-- Find service owners
SELECT e.name as service, t.name as owning_team
FROM dx_catalog_entity_owners eo
JOIN dx_catalog_entities e ON eo.entity_id = e.id
JOIN dx_teams t ON eo.team_id = t.id
WHERE e.entity_type_identifier = 'service';

-- Services without owners
SELECT e.name FROM dx_catalog_entities e
LEFT JOIN dx_catalog_entity_owners eo ON e.id = eo.entity_id
WHERE e.entity_type_identifier = 'service' AND eo.id IS NULL;
```

## dx_catalog_entity_relations
Relationships between catalog entities.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| from_entity_id | bigint | Source entity |
| to_entity_id | bigint | Target entity |
| relation_id | bigint | FK to dx_catalog_relations |

## dx_catalog_relations
Relation type definitions (depends_on, owned_by, etc.).

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| name | text | Relation name |
| identifier | varchar | Relation identifier |

## dx_catalog_entity_properties
Custom properties on entities.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| entity_id | bigint | FK to dx_catalog_entities |
| property_id | bigint | FK to dx_catalog_properties |
| value | text | Property value |

## dx_catalog_properties
Property definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| name | text | Property name |
| identifier | varchar | Property identifier |
| data_type | text | Value data type |

## dx_catalog_entity_aliases / dx_catalog_entity_alias_entries
Alias names for entities (for matching across systems).

## dx_catalog_entity_incidents
Links incidents to affected catalog entities.

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | Primary key |
| entity_id | bigint | FK to dx_catalog_entities |
| incident_id | bigint | FK to incidents |

**Common queries:**
```sql
-- Services with most incidents
SELECT e.name, COUNT(i.id) as incident_count
FROM dx_catalog_entity_incidents ei
JOIN dx_catalog_entities e ON ei.entity_id = e.id
JOIN incidents i ON ei.incident_id = i.id
WHERE i.started_at > NOW() - INTERVAL '90 days'
GROUP BY e.name ORDER BY incident_count DESC;
```

## Linking Catalog to Deployments

```sql
-- Deployment frequency by service
SELECT e.name as service, COUNT(d.id) as deploys
FROM deployments d
JOIN deployment_services ds ON d.deployment_service_id = ds.id
JOIN dx_catalog_entities e ON ds.service_id = e.id
WHERE d.deployed_at > NOW() - INTERVAL '30 days'
GROUP BY e.name ORDER BY deploys DESC;
```

## Linking Catalog to Pull Requests

Services can be linked to PRs through repository mapping:

```sql
-- PRs by service (via repo matching)
SELECT e.name as service, COUNT(p.id) as prs
FROM dx_catalog_entities e
JOIN dx_catalog_entity_aliases ea ON e.id = ea.entity_id
JOIN dx_catalog_entity_alias_entries eae ON ea.id = eae.alias_id
JOIN repos r ON r.name ILIKE '%' || eae.value || '%'
JOIN pull_requests p ON p.repo_id = r.id
WHERE e.entity_type_identifier = 'service'
  AND p.merged IS NOT NULL AND p.created > NOW() - INTERVAL '30 days'
GROUP BY e.name ORDER BY prs DESC;
```
