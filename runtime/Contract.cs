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
