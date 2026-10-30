Native file-system places, whole files and directory trees, with explicit unsuccessful outcomes and no dependency on another package; how a target's standard library provides these operations is not stated here.

## Structure

```
  path     a place in a file system, held opaquely in the operating system's native form
  name     one file or directory component within a [path], as text rather than [path] syntax
  content  the complete sequence of bytes stored in a file, with no text encoding chosen
  kind     what stands at a [path]: a file, directory, symbolic link or another sort of object
  failure  an explicit unsuccessful outcome: for an operation, the [path] concerned and the
           operating system's reason; for a text conversion, the rejected value and its reason
  entry    one result of listing a directory: its [path], its [name] or the [failure] to
           convert that [name], and its [kind]
```

## Flow

```
  construct  convert the operating system's native textual form into a [path]
  render     return a [path]'s native textual form
  join       append a [name] to a [path], returning the joined [path]
  extract    return each [name] composing a [path] as text
  list       return every [entry] immediately within the directory at a [path], in native
             order with no ordering promise
  inspect    return the [kind] at a [path], following a symbolic link
  read       return the complete [content] of the file at a [path], following a symbolic link
  write      create a missing file and any missing parent directories, replace all existing
             [content] with the supplied [content], following a symbolic link; a [failure] may
             leave a partial result
  remove     delete the object of any [kind] at a [path], recursively removing everything below
             a directory without following symbolic links; a [failure] may leave part removed
```

## Rules

```
  ensures:
    completion    every action returns a [failure] when it cannot complete its stated
                  conversion, effect or result
```
