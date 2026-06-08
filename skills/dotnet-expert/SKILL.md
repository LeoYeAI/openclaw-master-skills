---
name: dotnet-expert
version: 1.0.0
description: Use when building .NET 8/9 applications, ASP.NET Core APIs, Entity Framework Core, MediatR CQRS, modular monolith architecture, FluentValidation, Result pattern, JWT authentication, or any C# backend development question.
triggers:
  - .NET
  - dotnet
  - C#
  - ASP.NET
  - Entity Framework
  - EF Core
  - MediatR
  - CQRS
  - FluentValidation
  - Minimal API
  - controller
  - DbContext
  - migration
  - Pitbull
  - modular monolith
  - Result pattern
role: specialist
scope: implementation
output-format: code
---

# .NET Expert

Senior .NET 9 / ASP.NET Core specialist with expertise in clean architecture, CQRS, and modular monolith patterns.

## Role Definition

You are a senior .NET engineer building production-grade APIs with ASP.NET Core, Entity Framework Core 9, MediatR, and FluentValidation. You follow clean architecture principles with a pragmatic approach.

## Core Principles

1. **Result pattern over exceptions** for business logic — exceptions for infrastructure only
2. **CQRS with MediatR** — separate commands (writes) from queries (reads)
3. **FluentValidation** for all input validation in the pipeline
4. **Modular monolith** — organized by feature/domain, not by technical layer
5. **Strongly-typed IDs** to prevent primitive obsession
6. **Async all the way** — never `.Result` or `.Wait()`

---

## Project Structure (Modular Monolith)

```
src/
├── Api/                          # ASP.NET Core host
│   ├── Program.cs
│   ├── appsettings.json
│   └── Endpoints/                # Minimal API endpoint definitions
├── Modules/
│   ├── Users/
│   │   ├── Users.Core/           # Domain entities, interfaces
│   │   ├── Users.Application/    # Commands, queries, handlers
│   │   └── Users.Infrastructure/ # EF Core, external services
│   ├── Orders/
│   │   ├── Orders.Core/
│   │   ├── Orders.Application/
│   │   └── Orders.Infrastructure/
│   └── Shared/
│       ├── Shared.Core/          # Common abstractions
│       └── Shared.Infrastructure/# Cross-cutting concerns
└── Tests/
    ├── Users.Tests/
    └── Orders.Tests/
```

---

## Minimal API Patterns

### Basic Endpoint Group

```csharp
// Api/Endpoints/UserEndpoints.cs
public static class UserEndpoints
{
    public static void MapUserEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/users")
            .WithTags("Users")
            .RequireAuthorization();

        group.MapGet("/", GetUsers);
        group.MapGet("/{id:guid}", GetUserById);
        group.MapPost("/", CreateUser);
        group.MapPut("/{id:guid}", UpdateUser);
        group.MapDelete("/{id:guid}", DeleteUser);
    }

    private static async Task<IResult> GetUsers(
        [AsParameters] GetUsersQuery query,
        ISender mediator,
        CancellationToken ct)
    {
        var result = await mediator.Send(query, ct);
        return result.Match(
            success => Results.Ok(success),
            error => Results.Problem(error.ToProblemDetails()));
    }

    private static async Task<IResult> GetUserById(
        Guid id,
        ISender mediator,
        CancellationToken ct)
    {
        var result = await mediator.Send(new GetUserByIdQuery(id), ct);
        return result.Match(
            success => Results.Ok(success),
            error => error.Type == ErrorType.NotFound
                ? Results.NotFound()
                : Results.Problem(error.ToProblemDetails()));
    }

    private static async Task<IResult> CreateUser(
        CreateUserCommand command,
        ISender mediator,
        CancellationToken ct)
    {
        var result = await mediator.Send(command, ct);
        return result.Match(
            success => Results.Created($"/api/users/{success.Id}", success),
            error => Results.Problem(error.ToProblemDetails()));
    }
}
```

### Program.cs Setup

```csharp
var builder = WebApplication.CreateBuilder(args);

// Add modules
builder.Services.AddUsersModule(builder.Configuration);
builder.Services.AddOrdersModule(builder.Configuration);

// Add shared infrastructure
builder.Services.AddMediatR(cfg =>
    cfg.RegisterServicesFromAssemblies(
        typeof(UsersModule).Assembly,
        typeof(OrdersModule).Assembly));

builder.Services.AddValidatorsFromAssemblies(new[]
{
    typeof(UsersModule).Assembly,
    typeof(OrdersModule).Assembly,
});

// Add validation pipeline behavior
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!)),
        };
    });

builder.Services.AddAuthorization();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapUserEndpoints();
app.MapOrderEndpoints();

app.Run();
```

---

## Result Pattern

### Result Type

```csharp
// Shared.Core/Result.cs
public sealed class Result<T>
{
    public T? Value { get; }
    public Error? Error { get; }
    public bool IsSuccess { get; }

    private Result(T value) { Value = value; IsSuccess = true; }
    private Result(Error error) { Error = error; IsSuccess = false; }

    public static Result<T> Success(T value) => new(value);
    public static Result<T> Failure(Error error) => new(error);

    public TResult Match<TResult>(
        Func<T, TResult> onSuccess,
        Func<Error, TResult> onFailure) =>
        IsSuccess ? onSuccess(Value!) : onFailure(Error!);
}

public sealed record Error(string Code, string Message, ErrorType Type = ErrorType.Failure)
{
    public static Error NotFound(string code, string message) => new(code, message, ErrorType.NotFound);
    public static Error Validation(string code, string message) => new(code, message, ErrorType.Validation);
    public static Error Conflict(string code, string message) => new(code, message, ErrorType.Conflict);
    public static Error Forbidden(string code, string message) => new(code, message, ErrorType.Forbidden);

    public ProblemDetails ToProblemDetails() => new()
    {
        Title = Code,
        Detail = Message,
        Status = Type switch
        {
            ErrorType.NotFound => StatusCodes.Status404NotFound,
            ErrorType.Validation => StatusCodes.Status400BadRequest,
            ErrorType.Conflict => StatusCodes.Status409Conflict,
            ErrorType.Forbidden => StatusCodes.Status403Forbidden,
            _ => StatusCodes.Status500InternalServerError,
        },
    };
}

public enum ErrorType { Failure, NotFound, Validation, Conflict, Forbidden }
```

### Usage in Handlers

```csharp
// No exceptions for business logic!
public sealed class CreateUserHandler : IRequestHandler<CreateUserCommand, Result<UserResponse>>
{
    private readonly AppDbContext _db;

    public CreateUserHandler(AppDbContext db) => _db = db;

    public async Task<Result<UserResponse>> Handle(
        CreateUserCommand command, CancellationToken ct)
    {
        // Business rule validation returns errors, not exceptions
        var existingUser = await _db.Users
            .AnyAsync(u => u.Email == command.Email, ct);

        if (existingUser)
            return Result<UserResponse>.Failure(
                Error.Conflict("User.DuplicateEmail", "A user with this email already exists"));

        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = command.Email,
            Name = command.Name,
            CreatedAt = DateTime.UtcNow,
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync(ct);

        return Result<UserResponse>.Success(user.ToResponse());
    }
}
```

---

## MediatR CQRS

### Commands (Write Operations)

```csharp
// Users.Application/Commands/CreateUserCommand.cs
public sealed record CreateUserCommand(
    string Email,
    string Name,
    string Password) : IRequest<Result<UserResponse>>;
```

### Queries (Read Operations)

```csharp
// Users.Application/Queries/GetUsersQuery.cs
public sealed record GetUsersQuery(
    int Page = 1,
    int PageSize = 20,
    string? Search = null) : IRequest<Result<PagedResult<UserResponse>>>;

public sealed class GetUsersHandler : IRequestHandler<GetUsersQuery, Result<PagedResult<UserResponse>>>
{
    private readonly AppDbContext _db;

    public GetUsersHandler(AppDbContext db) => _db = db;

    public async Task<Result<PagedResult<UserResponse>>> Handle(
        GetUsersQuery query, CancellationToken ct)
    {
        var dbQuery = _db.Users.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(query.Search))
            dbQuery = dbQuery.Where(u =>
                u.Name.Contains(query.Search) || u.Email.Contains(query.Search));

        var total = await dbQuery.CountAsync(ct);

        var users = await dbQuery
            .OrderBy(u => u.Name)
            .Skip((query.Page - 1) * query.PageSize)
            .Take(query.PageSize)
            .Select(u => u.ToResponse())
            .ToListAsync(ct);

        return Result<PagedResult<UserResponse>>.Success(
            new PagedResult<UserResponse>(users, total, query.Page, query.PageSize));
    }
}
```

### Validation Pipeline Behavior

```csharp
public sealed class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        => _validators = validators;

    public async Task<TResponse> Handle(
        TRequest request,
        RequestHandlerDelegate<TResponse> next,
        CancellationToken ct)
    {
        if (!_validators.Any()) return await next();

        var context = new ValidationContext<TRequest>(request);
        var results = await Task.WhenAll(
            _validators.Select(v => v.ValidateAsync(context, ct)));

        var failures = results
            .SelectMany(r => r.Errors)
            .Where(f => f != null)
            .ToList();

        if (failures.Count > 0)
            throw new ValidationException(failures);

        return await next();
    }
}
```

---

## FluentValidation

```csharp
public sealed class CreateUserValidator : AbstractValidator<CreateUserCommand>
{
    public CreateUserValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Invalid email format")
            .MaximumLength(255);

        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Name is required")
            .MinimumLength(2)
            .MaximumLength(100)
            .Matches(@"^[a-zA-Z\s'-]+$").WithMessage("Name contains invalid characters");

        RuleFor(x => x.Password)
            .NotEmpty()
            .MinimumLength(8)
            .Matches("[A-Z]").WithMessage("Password must contain uppercase letter")
            .Matches("[a-z]").WithMessage("Password must contain lowercase letter")
            .Matches("[0-9]").WithMessage("Password must contain a number")
            .Matches("[^a-zA-Z0-9]").WithMessage("Password must contain a special character");
    }
}
```

---

## Entity Framework Core 9

### DbContext

```csharp
public sealed class AppDbContext : DbContext
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<OrderItem> OrderItems => Set<OrderItem>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }

    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        // Auto-set audit fields
        foreach (var entry in ChangeTracker.Entries<IAuditable>())
        {
            if (entry.State == EntityState.Added)
                entry.Entity.CreatedAt = DateTime.UtcNow;

            if (entry.State == EntityState.Modified)
                entry.Entity.UpdatedAt = DateTime.UtcNow;
        }

        return await base.SaveChangesAsync(ct);
    }
}
```

### Entity Configuration

```csharp
public sealed class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("users");

        builder.HasKey(u => u.Id);

        builder.Property(u => u.Email)
            .HasMaxLength(255)
            .IsRequired();

        builder.HasIndex(u => u.Email).IsUnique();

        builder.Property(u => u.Name)
            .HasMaxLength(100)
            .IsRequired();

        builder.Property(u => u.PasswordHash)
            .HasMaxLength(255)
            .IsRequired();

        builder.HasMany(u => u.Orders)
            .WithOne(o => o.User)
            .HasForeignKey(o => o.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        // Query filter for soft delete
        builder.HasQueryFilter(u => u.DeletedAt == null);
    }
}
```

### Migrations

```bash
# Create migration
dotnet ef migrations add AddUserTable -p src/Users.Infrastructure -s src/Api

# Apply migration
dotnet ef database update -p src/Users.Infrastructure -s src/Api

# Generate SQL script (for production)
dotnet ef migrations script -p src/Users.Infrastructure -s src/Api -o migrations.sql --idempotent
```

### Query Optimization

```csharp
// ❌ BAD: N+1 queries
var users = await _db.Users.ToListAsync(ct);
foreach (var user in users)
{
    var orders = await _db.Orders.Where(o => o.UserId == user.Id).ToListAsync(ct);
}

// ✅ GOOD: Eager loading
var users = await _db.Users
    .Include(u => u.Orders)
    .ToListAsync(ct);

// ✅ BEST: Projection (only load what you need)
var users = await _db.Users
    .AsNoTracking()
    .Select(u => new UserResponse
    {
        Id = u.Id,
        Name = u.Name,
        Email = u.Email,
        OrderCount = u.Orders.Count,
    })
    .ToListAsync(ct);
```

---

## ASP.NET Identity + JWT Auth

### Identity Setup

```csharp
builder.Services.AddIdentity<ApplicationUser, IdentityRole<Guid>>(options =>
{
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 8;
    options.Password.RequireUppercase = true;
    options.Password.RequireNonAlphanumeric = true;
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
    options.Lockout.MaxFailedAccessAttempts = 5;
})
.AddEntityFrameworkStores<AppDbContext>()
.AddDefaultTokenProviders();
```

### JWT Token Generation

```csharp
public sealed class TokenService : ITokenService
{
    private readonly IConfiguration _config;

    public TokenService(IConfiguration config) => _config = config;

    public string GenerateAccessToken(ApplicationUser user, IList<string> roles)
    {
        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new(ClaimTypes.Email, user.Email!),
            new(ClaimTypes.Name, user.UserName!),
        };

        claims.AddRange(roles.Select(role => new Claim(ClaimTypes.Role, role)));

        var key = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(_config["Jwt:Key"]!));

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(15),
            signingCredentials: new SigningCredentials(key, SecurityAlgorithms.HmacSha256));

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public string GenerateRefreshToken()
    {
        var randomBytes = new byte[64];
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(randomBytes);
        return Convert.ToBase64String(randomBytes);
    }
}
```

---

## Domain Entity Pattern

```csharp
public sealed class Order : IAuditable
{
    public Guid Id { get; private set; }
    public Guid UserId { get; private set; }
    public OrderStatus Status { get; private set; }
    public decimal Total { get; private set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }

    private readonly List<OrderItem> _items = [];
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();

    private Order() { } // EF Core

    public static Order Create(Guid userId)
    {
        return new Order
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            Status = OrderStatus.Pending,
            Total = 0,
        };
    }

    public Result<OrderItem> AddItem(Guid productId, int quantity, decimal unitPrice)
    {
        if (Status != OrderStatus.Pending)
            return Result<OrderItem>.Failure(
                Error.Validation("Order.NotPending", "Cannot add items to a non-pending order"));

        if (quantity <= 0)
            return Result<OrderItem>.Failure(
                Error.Validation("Order.InvalidQuantity", "Quantity must be positive"));

        var item = new OrderItem(Guid.NewGuid(), Id, productId, quantity, unitPrice);
        _items.Add(item);
        RecalculateTotal();

        return Result<OrderItem>.Success(item);
    }

    public Result<bool> Submit()
    {
        if (_items.Count == 0)
            return Result<bool>.Failure(
                Error.Validation("Order.Empty", "Cannot submit an empty order"));

        Status = OrderStatus.Submitted;
        return Result<bool>.Success(true);
    }

    private void RecalculateTotal()
    {
        Total = _items.Sum(i => i.Quantity * i.UnitPrice);
    }
}

public enum OrderStatus { Pending, Submitted, Processing, Shipped, Delivered, Cancelled }
```

---

## Anti-Patterns to Avoid

1. ❌ Throwing exceptions for validation/business logic — use Result pattern
2. ❌ Anemic domain models (entities with only properties) — put behavior in entities
3. ❌ Fat controllers/endpoints — delegate to MediatR handlers
4. ❌ `.Result` or `.Wait()` on async calls — async all the way
5. ❌ Returning `IQueryable` from repositories — materialize queries in the handler
6. ❌ Using `AutoMapper` for simple mappings — manual mapping or extension methods
7. ❌ Catching `Exception` broadly — catch specific exceptions at infrastructure boundaries
8. ❌ Hard-coding connection strings — use `IConfiguration` and environment variables
9. ❌ Missing `CancellationToken` — pass it through the entire call chain
10. ❌ Using `DbContext` without `AsNoTracking()` for read queries
