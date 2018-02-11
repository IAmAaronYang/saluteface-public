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
