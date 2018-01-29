using System.Text.Json;
using System.Text.RegularExpressions;

namespace SchemaPilot.Runtime;

/// <summary>
/// Specification for a single contract field. Mirrors the Python
/// <c>FieldSpec</c> so payloads validate identically in both runtimes.
/// </summary>
public sealed class FieldSpec
