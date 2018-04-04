using System.Text.Json;

namespace SchemaPilot.Runtime;

/// <summary>
/// SchemaPilot runtime CLI. Mirrors a subset of the Python CLI so the same
/// contracts and payloads can be validated in a .NET service or edge worker.
///
/// Commands:
///   inspect  &lt;contract.json&gt;                 print normalised contract
///   validate &lt;contract.json&gt; &lt;payload.json&gt;  validate payload, exit 1 on failure
///   fingerprint &lt;contract.json&gt;             print the stable contract digest
/// </summary>
public static class Program
{
    public static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.Error.WriteLine("usage: SchemaPilot.Runtime <inspect|validate|fingerprint> <args...>");
            return 64;
        }

        try
        {
            return args[0] switch
            {
                "inspect" => Inspect(args),
                "validate" => Validate(args),
                "fingerprint" => Fingerprint(args),
                _ => Unknown(args[0]),
            };
        }
        catch (FileNotFoundException ex)
        {
            Console.Error.WriteLine($"file not found: {ex.FileName}");
            return 4;
        }
        catch (JsonException ex)
        {
            Console.Error.WriteLine($"invalid JSON: {ex.Message}");
            return 5;
