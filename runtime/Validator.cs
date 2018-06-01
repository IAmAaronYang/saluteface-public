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
    {
        _contract = contract;
        _allowExtra = allowExtra;
    }

    public ValidationResult Validate(JsonElement payload)
    {
        var result = new ValidationResult();
        if (payload.ValueKind != JsonValueKind.Object)
        {
            result.Violations.Add(new Violation("TYPE_MISMATCH", "$", "payload must be an object"));
            return result;
        }

        var present = payload.EnumerateObject().Select(p => p.Name).ToHashSet();

        foreach (var name in _contract.RequiredFields)
        {
            if (!present.Contains(name))
                result.Violations.Add(new Violation("MISSING_REQUIRED", name, $"required field '{name}' is missing"));
        }

        if (!_allowExtra)
        {
            foreach (var name in present)
            {
                if (!_contract.Fields.ContainsKey(name))
                    result.Violations.Add(new Violation("UNEXPECTED_FIELD", name, $"field '{name}' is not in the contract"));
            }
        }

        foreach (var (name, spec) in _contract.Fields)
        {
            if (payload.TryGetProperty(name, out var value))
                CheckField(name, spec, value, result.Violations);
        }

        return result;
    }

    private static bool TypeOk(JsonElement v, string type) => type switch
    {
        "string" => v.ValueKind == JsonValueKind.String,
        "boolean" => v.ValueKind is JsonValueKind.True or JsonValueKind.False,
        "integer" => v.ValueKind == JsonValueKind.Number && v.TryGetInt64(out _),
        "number" => v.ValueKind == JsonValueKind.Number,
        "array" => v.ValueKind == JsonValueKind.Array,
        "object" => v.ValueKind == JsonValueKind.Object,
        "null" => v.ValueKind == JsonValueKind.Null,
        _ => false,
    };

    private void CheckField(string path, FieldSpec spec, JsonElement value, List<Violation> outv)
    {
        if (value.ValueKind == JsonValueKind.Null)
        {
            if (spec.Nullable || spec.Type == "null") return;
            outv.Add(new Violation("NULL_NOT_ALLOWED", path, $"field '{path}' may not be null"));
            return;
        }

        if (!TypeOk(value, spec.Type))
        {
            outv.Add(new Violation("TYPE_MISMATCH", path, $"expected {spec.Type}"));
            return;
        }

        if (spec.Enum is not null)
        {
            bool inEnum = spec.Enum.Any(e => JsonEquals(e, value));
            if (!inEnum) outv.Add(new Violation("ENUM_VIOLATION", path, "value not in enum"));
        }

