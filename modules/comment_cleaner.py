import tempfile
from io import TextIOWrapper


def comment_cleaner(
    file: TextIOWrapper | str, output: type[any] = None
) -> TextIOWrapper | str:
    filtered = []
    markers = {"#", "//"}
    block_markers = {"###": "###", "/*": "*/"}
    _inside_block = False
    _expected_closer = ""

    if output is None:
        output = type(file)

    lines = (
        file.splitlines(keepends=True) if isinstance(file, str) else file.readlines()
    )
    for line in lines:
        if _inside_block:
            if line.strip().startswith(_expected_closer):
                _inside_block = False
            continue

        _block_opener = next(
            (m for m in block_markers if line.strip().startswith(m)), None
        )

        if _block_opener:
            _inside_block = True
            _expected_closer = block_markers[_block_opener]
            continue

        if any(line.strip().startswith(m) for m in markers):
            continue

        pos = min((p for p in (line.find(m) for m in markers) if p != -1), default=-1)
        if pos != -1:
            newline = "\n" if not line.endswith("\n") else ""
            line = line[:pos] + newline

        filtered.append(line)

    if _inside_block:
        raise ValueError(f"Unclosed comment block. Expecting: {_expected_closer}")

    if output is TextIOWrapper:
        tmp = tempfile.NamedTemporaryFile(
            mode="w+",
            encoding="utf-8",
            delete=False,
        )

        tmp.writelines(filtered)
        tmp.flush()
        tmp.seek(0)
        return tmp

    else:
        return "".join(filtered)
