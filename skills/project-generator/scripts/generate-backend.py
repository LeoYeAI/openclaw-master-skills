#!/usr/bin/env python3
"""
Backend Code Generator for Spring Boot with Tech Stack Selection
Generates Java entity, repository, service, controller based on specification and tech stack
"""

import json
import os
from pathlib import Path
from datetime import datetime

TEMPLATE_DIR = Path(__file__).parent.parent / "assets" / "templates"

def generate_pom_xml(project_name, tech_stack):
    """Generate Maven pom.xml with selected tech stack"""
    java_version = tech_stack.get('javaVersion', '17')
    database = tech_stack.get('database', 'mysql')
    orm = tech_stack.get('orm', 'jpa')
    features = tech_stack.get('features', [])
    
    # Database dependencies
    db_deps = {
        'mysql': '''        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.33</version>
            <scope>runtime</scope>
        </dependency>''',
        'postgresql': '''        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>''',
        'h2': '''        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>'''
    }
    
    # ORM dependencies
    orm_deps = ''
    if orm == 'jpa':
        orm_deps = '''        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>'''
        if database != 'h2':
            orm_deps += '''
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>'''
    else:  # mybatis
        orm_deps = '''        <dependency>
            <groupId>org.mybatis.spring.boot</groupId>
            <artifactId>mybatis-spring-boot-starter</artifactId>
            <version>3.0.3</version>
        </dependency>'''
    
    # Feature dependencies
    feature_deps = []
    if 'jwt' in features:
        feature_deps.append('''        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>0.12.3</version>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-impl</artifactId>
            <version>0.12.3</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-jackson</artifactId>
            <version>0.12.3</version>
            <scope>runtime</scope>
        </dependency>''')
    
    if 'redis' in features:
        feature_deps.append('''        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>''')
    
    if 'audit' in features:
        feature_deps.append('''        <dependency>
            <groupId>org.springframework.data</groupId>
            <artifactId>spring-data-envers</artifactId>
        </dependency>''')
    
    feature_deps_str = '\n'.join(feature_deps)
    
    pom_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <java.version>{java_version}</java.version>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    
    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        
{orm_deps}
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        
{feature_deps_str}
        
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        
        <!-- Database -->
{db_deps.get(database, db_deps['mysql'])}
        
        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        
        <!-- Testing -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'''
    return pom_content

def generate_application_yml(project_name, tech_stack):
    """Generate application.yml with selected database"""
    database = tech_stack.get('database', 'mysql')
    
    template_files = {
        'mysql': 'application-mysql.yml',
        'postgresql': 'application-postgres.yml'
    }
    
    template_file = template_files.get(database, 'application-mysql.yml')
    template_path = TEMPLATE_DIR / template_file
    
    if template_path.exists():
        content = template_path.read_text(encoding='utf-8')
        return content.replace('{{projectName}}', project_name)
    else:
        # Fallback to MySQL config
        return f'''spring:
  application:
    name: {project_name}
  
  datasource:
    url: jdbc:mysql://localhost:3306/{project_name}?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: password
    driver-class-name: com.mysql.cj.jdbc.Driver
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true

server:
  port: 8080
'''

def generate_entity(entity_spec, tech_stack):
    """Generate JPA Entity class with optional audit/soft delete"""
    class_name = entity_spec['name']
    fields = entity_spec.get('fields', [])
    features = tech_stack.get('features', [])
    
    use_audit = 'audit' in features
    use_soft_delete = 'softDelete' in features
    
    imports = [
        'import jakarta.persistence.*;',
        'import java.time.LocalDateTime;'
    ]
    
    annotations = []
    if use_audit:
        imports.append('import org.springframework.data.annotation.CreatedBy;')
        imports.append('import org.springframework.data.annotation.LastModifiedBy;')
        imports.append('import org.springframework.data.jpa.domain.support.AuditingEntityListener;')
        annotations.append('@EntityListeners(AuditingEntityListener.class)')
    
    field_lines = ['    @Id', '    @GeneratedValue(strategy = GenerationType.IDENTITY)', '    private Long id;', '']
    
    for field in fields:
        field_type = field['type']
        field_name = field['name']
        nullable = 'nullable=false' if field.get('required') else 'nullable=true'
        
        if field_type == 'String':
            field_lines.append(f'    @Column({nullable})')
            field_lines.append(f'    private String {field_name};')
        elif field_type == 'Long':
            field_lines.append(f'    @Column({nullable})')
            field_lines.append(f'    private Long {field_name};')
        elif field_type == 'Integer':
            field_lines.append(f'    @Column({nullable})')
            field_lines.append(f'    private Integer {field_name};')
        elif field_type == 'BigDecimal':
            imports.append('import java.math.BigDecimal;')
            field_lines.append(f'    @Column(precision=19, scale=4, {nullable})')
            field_lines.append(f'    private BigDecimal {field_name};')
        elif field_type == 'LocalDateTime':
            field_lines.append(f'    @Column({nullable})')
            field_lines.append(f'    private LocalDateTime {field_name};')
        elif field_type == 'Boolean':
            field_lines.append(f'    @Column({nullable})')
            field_lines.append(f'    private Boolean {field_name};')
        elif field_type == 'Text':
            field_lines.append(f'    @Column(columnDefinition="TEXT", {nullable})')
            field_lines.append(f'    private String {field_name};')
        
        field_lines.append('')
    
    # Audit fields
    field_lines.append('    @Column(nullable=false, updatable=false)')
    if use_audit:
        field_lines.append('    @CreatedBy')
    field_lines.append('    private Long createdBy;')
    field_lines.append('')
    field_lines.append('    @Column(nullable=false, updatable=false)')
    field_lines.append('    private LocalDateTime createdAt;')
    field_lines.append('')
    
    if use_audit:
        field_lines.append('    @LastModifiedBy')
        field_lines.append('    private Long updatedBy;')
        field_lines.append('')
    
    field_lines.append('    @Column(nullable=false)')
    field_lines.append('    private LocalDateTime updatedAt;')
    
    if use_soft_delete:
        imports.append('import org.hibernate.annotations.SQLDelete;')
        imports.append('import org.hibernate.annotations.Where;')
        annotations.insert(0, '@SQLDelete(sql = "UPDATE ' + class_name.lower() + 's SET deleted = true WHERE id = ?")')
        annotations.insert(0, '@Where(clause = "deleted = false")')
        field_lines.append('')
        field_lines.append('    @Column(nullable=false)')
        field_lines.append('    private Boolean deleted = false;')
    
    field_lines.append('')
    field_lines.append('    @PrePersist')
    field_lines.append('    protected void onCreate() {')
    field_lines.append('        createdAt = LocalDateTime.now();')
    field_lines.append('        updatedAt = LocalDateTime.now();')
    if use_soft_delete:
        field_lines.append('        deleted = false;')
    field_lines.append('    }')
    field_lines.append('')
    field_lines.append('    @PreUpdate')
    field_lines.append('    protected void onUpdate() {')
    field_lines.append('        updatedAt = LocalDateTime.now();')
    field_lines.append('    }')
    
    annotations_str = '\n'.join([f'    {a}' for a in annotations]) + '\n' if annotations else ''
    
    template = f'''package com.example.entity;

{chr(10).join(sorted(set(imports)))}

@Entity
@Table(name = "{class_name.lower()}s")
{annotations_str}public class {class_name} {{
    
{chr(10).join(field_lines)}
    
    // Getters and Setters
    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id = id; }}
'''
    
    # Add getters/setters for each field
    getter_setters = []
    for field in fields:
        field_type = field['type']
        field_name = field['name']
        capitalized = field_name[0].upper() + field_name[1:]
        getter_setters.append(f'    public {field_type} get{capitalized}() {{ return {field_name}; }}')
        getter_setters.append(f'    public void set{capitalized}({field_type} {field_name}) {{ this.{field_name} = {field_name}; }}')
    
    if use_audit:
        getter_setters.append('    public Long getCreatedBy() { return createdBy; }')
        getter_setters.append('    public void setCreatedBy(Long createdBy) { this.createdBy = createdBy; }')
        getter_setters.append('    public Long getUpdatedBy() { return updatedBy; }')
        getter_setters.append('    public void setUpdatedBy(Long updatedBy) { this.updatedBy = updatedBy; }')
    
    getter_setters.append('    public LocalDateTime getCreatedAt() { return createdAt; }')
    getter_setters.append('    public LocalDateTime getUpdatedAt() { return updatedAt; }')
    
    if use_soft_delete:
        getter_setters.append('    public Boolean getDeleted() { return deleted; }')
        getter_setters.append('    public void setDeleted(Boolean deleted) { this.deleted = deleted; }')
    
    template += '\n' + '\n'.join(getter_setters)
    template += '\n}'
    
    return template

def main():
    """Test with sample tech stack"""
    tech_stack = {
        'javaVersion': '17',
        'buildTool': 'maven',
        'database': 'mysql',
        'orm': 'jpa',
        'features': ['jwt', 'audit', 'softDelete']
    }
    
    print(generate_pom_xml('demo-app', tech_stack))

if __name__ == '__main__':
    main()
