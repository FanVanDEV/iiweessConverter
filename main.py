import argparse
import re
import sys
import toml

constants = {}


def validate_name(name):
    pattern = r'^[_a-zA-Z][_a-zA-Z0-9]*$'
    if not re.match(pattern, name):
        raise SyntaxError(f"Invalid name: '{name}'")


def convert_value(value, indent_level=0):
    if isinstance(value, dict):
        return convert_dict(value, indent_level)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if value.startswith('?(') and value.endswith(')'):
            var_name = value[2:-1]
            validate_name(var_name)
            if var_name in constants:
                return str(constants[var_name])
            else:
                raise SyntaxError(f"Constant {var_name} not defined")

    raise SyntaxError(f"Unsupported value type: {type(value)}")


def convert_comment(comment):
    comment = comment.strip().lstrip("#")
    return f'"{comment}'


def parse_toml_file(file):
    comments = []
    file = file.split("\n")

    for line in file:
        if line.strip().startswith("#"):
            comments.append(convert_comment(line))
            continue
        comments.append(None)
    return comments


def convert_inline_table(name, table, indent_level=0):
    validate_name(name)

    indent = "    " * indent_level
    result = [f"{indent}(["]

    for key, value in table.items():
        validate_name(key)
        converted_value = convert_value(value, indent_level + 1)
        result.append(f"{indent}    {key} : {converted_value},")

    result.append(f"{indent}]) -> {name}")
    return "\n".join(result)


def convert_dict(d, indent_level=0):
    indent = "    " * indent_level
    result = [f"(["]

    for key, value in d.items():
        validate_name(key)
        if isinstance(value, dict):
            nested = convert_dict(value, indent_level + 1)
            result.append(f"{indent}    {key} : {nested},")
        else:
            converted_value = convert_value(value, indent_level + 1)
            result.append(f"{indent}    {key} : {converted_value},")

    result.append(f"{indent}])")
    return "\n".join(result)


def transform_toml_to_custom(toml_data, toml_file):
    result = []

    comments = parse_toml_file(toml_file)

    i = 0
    for key, value in toml_data.items():
        validate_name(key)

        if comments[i] is not None:
            result.append(comments[i])

        if isinstance(value, dict):
            constants[key] = convert_dict(value)
            result.append(convert_inline_table(key, value))
        elif isinstance(value, (int, float, str)):
            converted_value = convert_value(value)
            constants[key] = converted_value
            result.append(f"{converted_value} -> {key}")
        else:
            raise SyntaxError(f"Unsupported top-level item type: {type(value)}")
        i += 1

    for j in range(i, len(comments)):
        if comments[j] is not None:
            result.append(comments[j])

    return "\n".join(result)


def main():
    parser = argparse.ArgumentParser(description="Convert TOML to a custom config format.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file.")
    args = parser.parse_args()

    try:

        with open(args.output, "w") as output_file:
            output_file.write(translate(sys.stdin.read()))
        print(f"Conversion successful. Output written to {args.output}.")
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def translate(text):
    parsed_toml = toml.loads(text)
    return transform_toml_to_custom(parsed_toml, text)


if __name__ == "__main__":
    main()
