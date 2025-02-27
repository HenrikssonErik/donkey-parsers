import sys
import math

def truncate_run(fh):
    """
    Function that defines how to truncate data in the Makefile.
    """
    fh.write("define truncate_data\n")
    fh.write("\tsed -n '$(1),$(2)p;$(3)q' ../../../data/cadets-e3/$(6)/$(4).json | ../../libpvm-rs/build/pvm2csv - ../../../data/cadets-e3/$(6)/$(4)_$(5).zip ; \\\n")
    fh.write("\tmkdir -p ../../../data/cadets-3/$(6)/$(4)_$(5) ; \\\n")
    fh.write("\tunzip ../../../data/cadets-e3/$(6)/$(4)_$(5).zip -d ../../../data/cadets-e3/$(6)/$(4)_$(5) ; \\\n")
    fh.write("\trm ../../../data/cadets-e3/$(6)/$(4)_$(5).zip\n")
    fh.write("endef\n")

def gen(filepath, name, chunks, ty, fh):
    """
    Generates makefile content for each dataset chunk.
    """
    try:
        with open(filepath, "r") as f:
            for i, l in enumerate(f):
                pass
        lc = i + 1  # Total line count
    except FileNotFoundError:
        print(f"Error: File {filepath} not found!")
        return

    fh.write(name + ":\n")

    interval = int(math.ceil(lc / int(chunks)))
    start = 1
    end = lc
    cnt = 0

    while start + interval < end:
        fh.write(f"\t$(call truncate_data,{start},{start + interval},{start + interval + 1},{name},{cnt},{ty})\n")
        start = start + interval + 1
        cnt += 1

    fh.write(f"\t$(call truncate_data,{start},{end},{end + 1},{name},{cnt},{ty})\n")

if __name__ == "__main__":
    print("Starting Makefile generation...")

    with open("Makefile", "w") as makefile:
        truncate_run(makefile)
        makefile.write("\n")
        gen("../../../data/cadets-e3/benign/benign1.json", "benign1", 50, "benign", makefile)
        makefile.write("\n")
        gen("../../../data/cadets-e3/benign/benign2.json", "benign2", 10, "benign", makefile)
        makefile.write("\n")
        gen("../../../data/cadets-e3/benign/benign3.json", "benign3", 50, "benign", makefile)
        makefile.write("\n")
        gen("../../../data/cadets-e3/attack/pandex.json", "pandex", 25, "attack", makefile)

    print("Makefile successfully created!")