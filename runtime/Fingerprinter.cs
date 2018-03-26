using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace SchemaPilot.Runtime;

/// <summary>
/// Produces a stable contract digest identical to the Python implementation.
///
/// The algorithm: serialise the normalised contract to canonical JSON
/// (object keys sorted lexicographically, no whitespace), UTF-8 encode,
/// SHA-256, and take the first 16 hex characters. Because both runtimes
/// build the same canonical string, they agree on the fingerprint.
/// </summary>
public static class Fingerprinter
{
    public static string Compute(Contract contract)
    {
        string canonical = Canonicalize(contract);
        byte[] hash = SHA256.HashData(Encoding.UTF8.GetBytes(canonical));
        var sb = new StringBuilder(32);
        foreach (byte b in hash) sb.Append(b.ToString("x2", CultureInfo.InvariantCulture));
        return sb.ToString()[..16];
    }

    private static string Canonicalize(Contract contract)
    {
        // Mirrors json.dumps(contract.to_dict(), sort_keys=True, separators=(",",":"))
        var sb = new StringBuilder();
        sb.Append('{');
        // Keys in sorted order: fields, name, version
        sb.Append("\"fields\":");
        AppendFields(sb, contract.Fields);
        sb.Append(",\"name\":");
        AppendString(sb, contract.Name);
        sb.Append(",\"version\":").Append(contract.Version);
        sb.Append('}');
        return sb.ToString();
    }

    private static void AppendFields(StringBuilder sb, Dictionary<string, FieldSpec> fields)
    {
        sb.Append('{');
        bool first = true;
        foreach (var name in fields.Keys.OrderBy(k => k, StringComparer.Ordinal))
        {
            if (!first) sb.Append(',');
            first = false;
            AppendString(sb, name);
            sb.Append(':');
            AppendFieldSpec(sb, fields[name]);
        }
        sb.Append('}');
    }

    private static void AppendFieldSpec(StringBuilder sb, FieldSpec spec)
    {
        // Collect the same keys Python's FieldSpec.to_dict emits, then sort
        // lexicographically to mirror json.dumps(..., sort_keys=True).
        var members = new SortedDictionary<string, string>(StringComparer.Ordinal);
        members["type"] = Quoted(spec.Type);
        if (spec.Required) members["required"] = "true";
        if (spec.Nullable) members["nullable"] = "true";
        if (spec.Enum is { } en) members["enum"] = FormatJsonArray(en);
        if (spec.Minimum is { } mn) members["min"] = FormatNumber(mn);
        if (spec.Maximum is { } mx) members["max"] = FormatNumber(mx);
        if (spec.MinLen is { } ml) members["min_len"] = ml.ToString(CultureInfo.InvariantCulture);
        if (spec.MaxLen is { } xl) members["max_len"] = xl.ToString(CultureInfo.InvariantCulture);
        if (spec.Pattern is { } p) members["pattern"] = Quoted(p);
        if (spec.MinItems is { } mi) members["min_items"] = mi.ToString(CultureInfo.InvariantCulture);
        if (spec.MaxItems is { } xi) members["max_items"] = xi.ToString(CultureInfo.InvariantCulture);
        if (spec.Items is { } items)
        {
            var nested = new StringBuilder();
            AppendFieldSpec(nested, items);
            members["items"] = nested.ToString();
        }
        if (spec.HasDefault) members["default"] = FormatJsonValue(spec.DefaultValue);

        sb.Append('{');
        bool first = true;
        foreach (var kv in members)
        {
            if (!first) sb.Append(',');
            first = false;
            AppendString(sb, kv.Key);
            sb.Append(':').Append(kv.Value);
        }
        sb.Append('}');
    }

    private static string FormatJsonArray(List<JsonElement> items)
    {
        var sb = new StringBuilder();
        sb.Append('[');
        for (int i = 0; i < items.Count; i++)
        {
            if (i > 0) sb.Append(',');
            sb.Append(FormatJsonValue(items[i]));
        }
        sb.Append(']');
        return sb.ToString();
    }

    // Serialise a JSON value the way json.dumps(..., separators=(",",":")) does.
    private static string FormatJsonValue(JsonElement el) => el.ValueKind switch
    {
        JsonValueKind.String => Quoted(el.GetString() ?? ""),
        JsonValueKind.True => "true",
        JsonValueKind.False => "false",
        JsonValueKind.Null => "null",
        JsonValueKind.Number => FormatJsonNumber(el),
        JsonValueKind.Array => FormatJsonArray(el.EnumerateArray().Select(x => x.Clone()).ToList()),
        JsonValueKind.Object => FormatJsonObject(el),
        _ => "null",
    };

    private static string FormatJsonNumber(JsonElement el)
    {
        // Preserve the original numeric literal (e.g. 0.0 vs 0, 199.95) so the
        // canonical form matches Python's json round-trip of enum/default values.
        string raw = el.GetRawText();
        return raw;
    }

    private static string FormatJsonObject(JsonElement el)
    {
        var members = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (var prop in el.EnumerateObject())
            members[prop.Name] = FormatJsonValue(prop.Value);
        var sb = new StringBuilder();
        sb.Append('{');
        bool first = true;
        foreach (var kv in members)
        {
            if (!first) sb.Append(',');
            first = false;
            AppendString(sb, kv.Key);
