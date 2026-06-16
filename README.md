# smartsync

`smartsync.py` synchronizes a **target** codebase folder so that it mirrors a
**source** folder. Both folders represent different versions of the same
codebase.

```cmd
smartsync.py <target_folder> <source_folder>
```

Example:

```cmd
smartsync.py .\old .\new
```

This recursively copies everything from `.\new` into `.\old`, and deletes any
file or subfolder under `.\old` that has no counterpart in `.\new`.

Every copy/delete/create action is printed to the screen **and** written to a
log file. By default the log is `smartsync_<YYYYMMDD_HHMMSS>.log` in the current
directory; use `--log <path>` to choose a different location:

```cmd
smartsync.py .\old .\new --log sync.log
```

A well-known list of folder names, file extensions and file names is always
ignored (never copied, never deleted):

| Type            | Ignored values |
| --------------- | -------------- |
| Folder names    | `.git`, `external_tools`, `.settings`, `.metadata`, `target` |
| File extensions | `.class`, `.classpath`, `.db`, `.dll`, `.gz`, `.jar`, `.pdf`, `.war` |
| File names      | `.gitattributes`, `.gitignore` |

Requires Python 3.13+.

## Preparing the source codebase on a remote machine

The typical workflow is:

1. Compress the up-to-date source repo on the remote machine into a `.7z`
   archive (excluding the same folders and file types that `smartsync.py`
   ignores).
2. Transfer the archive to your local machine and extract it.
3. Run `smartsync.py` to mirror that extracted source into your local target
   codebase.

### Compressing the source repo with 7-Zip

On the remote machine, open a `cmd.exe` session and run the following command.
It creates `tci-ebx.7z` from `C:\ebx-dev-env\git\tci-ebx`, recursing through
all subfolders while excluding the ignored folders and file types
(`^` is the `cmd.exe` line-continuation character):

```cmd
7z a -t7z -mx=9 tci-ebx.7z C:\ebx-dev-env\git\tci-ebx -r ^
-xr!.git -xr!external_tools -xr!.settings -xr!.metadata -xr!target ^
-x!*.class -x!*.db -x!*.dll -x!*.gz -x!*.jar -x!*.pdf -x!*.war
```

Switch reference:

| Switch | Meaning |
| ------ | ------- |
| `a` | Add files to an archive |
| `-t7z` | Use the 7z archive format |
| `-mx=9` | Maximum (ultra) compression level |
| `-r` | Recurse into subdirectories |
| `-xr!<name>` | Exclude a folder (and its contents) at any level |
| `-x!<pattern>` | Exclude files matching the pattern |

The resulting `tci-ebx.7z` mirrors the set of files that `smartsync.py` keeps,
so once extracted locally it can be used directly as the **source** folder.
