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
        }
        catch (FormatException ex)
        {
            Console.Error.WriteLine($"contract error: {ex.Message}");
            return 3;
        }
    }

    private static int Unknown(string cmd)
    {
        Console.Error.WriteLine($"unknown command: {cmd}");
        return 64;
    }

    private static int Inspect(string[] args)
    {
        var contract = Contract.Parse(File.ReadAllText(args[1]));
        var summary = new Dictionary<string, object?>
        {
            ["name"] = contract.Name,
            ["version"] = contract.Version,
            ["fields"] = contract.Fields.Keys.ToList(),
            ["required"] = contract.RequiredFields.ToList(),
            ["fingerprint"] = Fingerprinter.Compute(contract),
        };
        Console.WriteLine(JsonSerializer.Serialize(summary, JsonOpts));
        return 0;
    }

    private static int Validate(string[] args)
    {
        var contract = Contract.Parse(File.ReadAllText(args[1]));
        using var doc = JsonDocument.Parse(File.ReadAllText(args[2]));
        var result = new Validator(contract).Validate(doc.RootElement);
        Console.WriteLine(JsonSerializer.Serialize(result.ToDict(), JsonOpts));
        return result.Ok ? 0 : 1;
    }

    private static int Fingerprint(string[] args)
    {
        var contract = Contract.Parse(File.ReadAllText(args[1]));
        Console.WriteLine(Fingerprinter.Compute(contract));
        return 0;
    }

    private static readonly JsonSerializerOptions JsonOpts = new() { WriteIndented = true };
}

<!-- draft note 1338 -->
