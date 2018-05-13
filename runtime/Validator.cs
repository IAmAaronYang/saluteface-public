using System.Text.Json;

namespace SchemaPilot.Runtime;

/// <summary>A single validation failure with a stable code and field path.</summary>
public sealed record Violation(string Code, string Path, string Message);

/// <summary>Outcome of validating a payload against a contract.</summary>
public sealed class ValidationResult
{
    public bool Ok => Violations.Count == 0;
    public List<Violation> Violations { get; } = new();

    public Dictionary<string, object?> ToDict() => new()
    {
        ["ok"] = Ok,
