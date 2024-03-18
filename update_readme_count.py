import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No string given to update readme with")
        sys.exit(1)

    count_str = sys.argv[1]
    print(f'Updating readme with "{count_str}"')

    with open("README.md", "r") as readme:
        lines = readme.readlines()

    for index, line in enumerate(lines):
        if "### Possible combinations" in line:
            line_index = index + 1

    lines[line_index] = count_str + "\n"

    with open("README.md", "w") as readme:
        readme.writelines(lines)
