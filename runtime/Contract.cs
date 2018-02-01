using System.Text.Json;
using System.Text.RegularExpressions;

namespace SchemaPilot.Runtime;

/// <summary>
/// Specification for a single contract field. Mirrors the Python
/// <c>FieldSpec</c> so payloads validate identically in both runtimes.
/// </summary>
public sealed class FieldSpec
{
    public string Name { get; init; } = "";
    public string Type { get; init; } = "string";
    public bool Required { get; init; }
    public bool Nullable { get; init; }
    public List<JsonElement>? Enum { get; init; }
    public double? Minimum { get; init; }
    public double? Maximum { get; init; }
    public int? MinLen { get; init; }
    public int? MaxLen { get; init; }
    public string? Pattern { get; init; }
    public int? MinItems { get; init; }
    public int? MaxItems { get; init; }
    public FieldSpec? Items { get; init; }
    public bool HasDefault { get; init; }
    public JsonElement DefaultValue { get; init; }

    private Regex? _compiled;
    public Regex? CompiledPattern =>
        Pattern is null ? null : _compiled ??= new Regex("^(?:" + Pattern + ")$");
}

/// <summary>A parsed contract: named fields plus version metadata.</summary>
public sealed class Contract
{
    public string Name { get; init; } = "";
    public int Version { get; init; } = 1;
    public Dictionary<string, FieldSpec> Fields { get; init; } = new();

    public IEnumerable<string> RequiredFields =>
        Fields.Where(kv => kv.Value.Required).Select(kv => kv.Key);

    public static readonly HashSet<string> AllTypes = new()
    {
        "string", "integer", "number", "boolean", "array", "object", "null"
    };

    /// <summary>Parse a contract from a JSON document.</summary>
    public static Contract Parse(string json)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;
        if (!root.TryGetProperty("name", out var nameEl) ||
            !root.TryGetProperty("fields", out var fieldsEl))
        {
