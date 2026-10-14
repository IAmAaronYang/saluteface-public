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
            throw new FormatException("contract requires 'name' and 'fields'");
        }

        var fields = new Dictionary<string, FieldSpec>();
        foreach (var prop in fieldsEl.EnumerateObject())
        {
            fields[prop.Name] = ParseField(prop.Name, prop.Value);
        }

        return new Contract
        {
            Name = nameEl.GetString() ?? "",
            Version = root.TryGetProperty("version", out var v) ? v.GetInt32() : 1,
            Fields = fields,
        };
    }

    private static FieldSpec ParseField(string name, JsonElement raw)
    {
        string type = raw.TryGetProperty("type", out var t) ? t.GetString() ?? "string" : "string";
        if (!AllTypes.Contains(type))
            throw new FormatException($"field '{name}' has unknown type '{type}'");

        List<JsonElement>? enums = null;
        if (raw.TryGetProperty("enum", out var e) && e.ValueKind == JsonValueKind.Array)
            enums = e.EnumerateArray().Select(x => x.Clone()).ToList();

        FieldSpec? items = null;
        if (raw.TryGetProperty("items", out var it))
            items = ParseField(name + "[]", it);

        bool hasDefault = raw.TryGetProperty("default", out var defEl);

        return new FieldSpec
        {
            Name = name,
            Type = type,
            Required = raw.TryGetProperty("required", out var r) && r.GetBoolean(),
            Nullable = raw.TryGetProperty("nullable", out var n) && n.GetBoolean(),
            Enum = enums,
            Minimum = raw.TryGetProperty("min", out var mn) ? mn.GetDouble() : null,
            Maximum = raw.TryGetProperty("max", out var mx) ? mx.GetDouble() : null,
            MinLen = raw.TryGetProperty("min_len", out var ml) ? ml.GetInt32() : null,
            MaxLen = raw.TryGetProperty("max_len", out var xl) ? xl.GetInt32() : null,
            Pattern = raw.TryGetProperty("pattern", out var p) ? p.GetString() : null,
            MinItems = raw.TryGetProperty("min_items", out var mi) ? mi.GetInt32() : null,
            MaxItems = raw.TryGetProperty("max_items", out var xi) ? xi.GetInt32() : null,
            Items = items,
            HasDefault = hasDefault,
            DefaultValue = hasDefault ? defEl.Clone() : default,
        };
    }
}
