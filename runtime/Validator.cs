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
        ["violation_count"] = Violations.Count,
        ["violations"] = Violations.Select(v => new Dictionary<string, object?>
        {
            ["code"] = v.Code,
            ["path"] = v.Path,
            ["message"] = v.Message,
        }).ToList(),
    };
}

/// <summary>
/// Validates JSON payloads against a <see cref="Contract"/>. The rules and
/// violation codes match the Python validator so a payload accepted by one
/// runtime is accepted by the other.
/// </summary>
public sealed class Validator
{
    private readonly Contract _contract;
    private readonly bool _allowExtra;

    public Validator(Contract contract, bool allowExtra = false)
