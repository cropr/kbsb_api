import csv
from pathlib import Path

rootpath = Path("..")


def main():
    with (rootpath / "share" / "data" / "translations - kbsb.csv").open(
        newline=""
    ) as csvfile:
        reader = csv.DictReader(csvfile)
        allrows = []
        for r in reader:
            allrows.append(r)
    for l in ["en", "fr", "nl", "de"]:
        with (rootpath / "kbsb_frontend" / "lang" / f"{l}.js").open(
            "w", encoding="utf8"
        ) as f:
            f.write("export default {\n")
            for r in allrows:
                f.write(f'"{r["key"]}": `{r[l]}`,\n')
            f.write("}\n")
    print("i18n files written")


if __name__ == "__main__":
    main()
