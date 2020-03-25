import argparse
import nixio as nix
import h5py


def get_file_version(fname):
    with h5py.File(fname, mode="r") as hfile:
        return tuple(hfile.attrs["version"])


def has_valid_file_id(fname):
    with h5py.File(fname, mode="r") as hfile:
        fileid = hfile.attrs.get("id")
        if fileid and nix.util.is_uuid(fileid):
            return True
    return False


def add_file_id(fname):
    """
    Returns a closure that binds the filename. When the return value is
    called, it adds a UUID to the file header.
    """
    def add_id():
        "Add a UUID to the file header"
        with h5py.File(fname, mode="a") as hfile:
            hfile.attrs["id"] = nix.util.create_id()
    return add_id


def update_property_values(fname):
    """
    Returns a closure that binds the filename. When the return value is
    called, it modifies rewrites all the metadata Property objects to the new
    format.
    """
    props = list()

    with h5py.File(fname, mode="r") as hfile:
        sections = hfile["metadata"]

        def find_props(name, group):
            if isinstance(group, h5py.Dataset) and len(group.dtype):
                # structured/compound dtypes have non-zero length
                props.append(group.name)

        sections.visititems(find_props)

    def update_props():
        for propname in props:
            with h5py.File(fname, mode="a") as hfile:
                prop = hfile[propname]

                # pull out the old extra attributes
                uncertainty = prop["uncertainty"]
                reference = prop["reference"]
                filename = prop["filename"]
                encoder = prop["encoder"]
                checksum = prop["checksum"]

                # replace base prop
                values = prop["value"]
                dt = values.dtype
                del hfile[propname]
                newprop = create_property(hfile, propname,
                                          dtype=dt, data=values)

                # Create properties for any extra attrs that are set
                if len(set(uncertainty)) > 1:
                    # multiple values, make new prop
                    create_property(hfile, propname + ".uncertainty",
                                    dtype=float, data=uncertainty)
                elif any(uncertainty):
                    # single, unique, non-zero value; add to main prop attr
                    newprop.attrs["uncertainty"] = uncertainty[0]

                if any(reference):
                    create_property(hfile, propname + ".reference",
                                    dtype=nix.util.vlen_str_dtype,
                                    data=reference)

                if any(filename):
                    create_property(hfile, propname + ".filename",
                                    dtype=nix.util.vlen_str_dtype,
                                    data=filename)

                if any(encoder):
                    create_property(hfile, propname + ".encoder",
                                    dtype=nix.util.vlen_str_dtype,
                                    data=encoder)

                if any(checksum):
                    create_property(hfile, propname + ".checksum",
                                    dtype=nix.util.vlen_str_dtype,
                                    data=checksum)

    update_props.__doc__ = "Update {} properties".format(len(props))
    return update_props


def create_property(hfile, name, dtype, data):
    prop = hfile.create_dataset(name, dtype=dtype, data=data)
    prop.attrs["name"] = name.split("/")[-1]
    prop.attrs["entity_id"] = nix.util.create_id()
    prop.attrs["created_at"] = nix.util.time_to_str(nix.util.now_int())
    prop.attrs["updated_at"] = nix.util.time_to_str(nix.util.now_int())
    return prop


def update_format_version(fname):
    """
    Returns a closure that binds the filename. When the return value is
    called, it updates the version in the header to the version in the library.
    """
    def update_ver():
        with h5py.File(fname, mode="a") as hfile:
            hfile.attrs["version"] = nix.file.HDF_FF_VERSION
    lib_verstr = ".".join(str(v) for v in nix.file.HDF_FF_VERSION)
    update_ver.__doc__ = f"Update the file format version to {lib_verstr}"
    return update_ver


def collect_tasks(fname):
    file_ver = get_file_version(fname)
    file_verstr = ".".join(str(v) for v in file_ver)
    lib_verstr = ".".join(str(v) for v in nix.file.HDF_FF_VERSION)
    if file_ver >= nix.file.HDF_FF_VERSION:
        print(f"{fname}: Up to date ({file_verstr})")
        return

    # even if the version string indicates the file is old, check format
    # details before scheduling tasks
    tasks = list()
    if not has_valid_file_id(fname):
        tasks.append(add_file_id(fname))
        tasks.append(update_property_values(fname))

    # always update the format last
    tasks.append(update_format_version(fname))
    print(f"{fname}: {file_verstr} -> {lib_verstr}")
    print("  - " + "\n  - ".join(t.__doc__ for t in tasks) + "\n")

    return tasks


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade NIX files to newest version"
    )
    parser.add_argument("-f", "--force", action="store_true",
                        help="overwrite existing files without prompting")
    parser.add_argument("file", type=str, nargs="+",
                        help="path to file to upgrade (at least one)")
    args = parser.parse_args()
    filenames = args.file

    tasks = dict()
    for fname in filenames:
        tasklist = collect_tasks(fname)
        if not tasklist:
            continue

        tasks[fname] = tasklist

    if not tasks:
        return

    force = args.force
    if not force:
        print("""
PLEASE READ CAREFULLY

If you choose to continue, the changes listed above will be applied to the
respective files. This will make the files unreadable by older NIX library
versions. Although this procedure is generally fast and safe, interrupting it
may leave files in a corrupted state.

MAKE SURE YOUR FILES AND DATA ARE BACKED UP BEFORE CONTINUING.
        """)
        conf = None

        while conf not in ("y", "n", "yes", "no"):
            conf = input("Continue with changes? [yes/no] ")
            conf = conf.lower()
    else:
        conf = "yes"

    if conf in ("y", "yes"):
        for fname, tasklist in tasks.items():
            print(f"Processing {fname} ", end="", flush=True)
            for task in tasklist:
                task()
            print("done")


if __name__ == "__main__":
    main()
