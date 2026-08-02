# Architecture

Three views of the same small package: what the modules are, how you enter them, and
what a typical session looks like.

## 1. Package Overview

Every module, the functions inside it, and how they connect.

- **Solid arrows** — call flow / data flow at runtime
- **Dotted arrows** — module-level imports

```mermaid
---
title: Modules, Functions, and Imports
---
flowchart LR
    subgraph EP["Entry Points"]
        direction TB
        SCRIPT["console script<br>[project.scripts]<br>secondbrain = cli:cli"]
        DMAIN["__main__.py<br>python -m secondbrain"]
    end

    subgraph CLIMOD["cli.py — Command Layer"]
        direction TB
        GROUP["cli()<br>@click.group"]
        CNEW["new(title)"]
        CLIST["list_notes()<br>command name: 'list'"]
        CSHOW["show(number)"]
    end

    subgraph APPMOD["app.py — Logging Layer"]
        direction TB
        CFG["configure_logging()"]
        FMT["LOG_FORMAT<br>LEVEL_ICONS"]
        AMAIN["main()<br>@logger.catch"]
    end

    subgraph NOTESMOD["notes.py — Domain Layer"]
        direction TB
        NDIR["notes_dir()"]
        NCREATE["create_note()"]
        NBUILD["build_note_path()"]
        NSLUG["slugify()"]
        NREAD["read_note()"]
        NCONST["DEFAULT_DIR_NAME<br>= 'secondbrain'"]
    end

    subgraph EXT["Third-Party"]
        direction TB
        CLICKLIB["click"]
        LOGURULIB["loguru.logger"]
    end

    subgraph IO["Environment & Filesystem"]
        direction TB
        ENVDIR["env: SECONDBRAIN_DIR<br>default ~/secondbrain"]
        ENVLOG["env: LOG_LEVEL, LOG_FILE"]
        FILES["notes dir<br>YYYY-MM-DD-slug.md"]
        LOGFILE["app.log<br>rotation 50 KB, retention 1"]
    end

    SCRIPT --> GROUP
    DMAIN --> GROUP

    GROUP --> CNEW
    GROUP --> CLIST
    GROUP --> CSHOW
    GROUP -->|"on every invocation"| CFG
    AMAIN --> CFG

    CNEW --> NDIR
    CNEW --> NCREATE
    CLIST --> NDIR
    CSHOW --> NDIR
    CSHOW --> NREAD

    NCREATE --> NBUILD
    NBUILD --> NSLUG
    NDIR --> NCONST

    CFG --> FMT
    CFG -->|"log path fallback"| NDIR
    CFG --> ENVLOG
    CFG --> LOGFILE

    NDIR --> ENVDIR
    NBUILD -->|"mkdir -p"| FILES
    NCREATE -->|"write utf-8"| FILES
    NREAD -->|"read utf-8"| FILES
    CLIST -->|"glob '*.md'"| FILES

    GROUP -.->|"import"| CLICKLIB
    GROUP -.->|"import"| LOGURULIB
    CFG -.->|"import"| LOGURULIB

    classDef entry fill:#e8eaf6,stroke:#3f51b5,color:#1a1a1a
    classDef cli fill:#e3f2fd,stroke:#1976d2,color:#1a1a1a
    classDef app fill:#fff3e0,stroke:#ef6c00,color:#1a1a1a
    classDef domain fill:#e8f5e9,stroke:#2e7d32,color:#1a1a1a
    classDef ext fill:#f3e5f5,stroke:#7b1fa2,color:#1a1a1a
    classDef io fill:#eceff1,stroke:#546e7a,color:#1a1a1a

    class SCRIPT,DMAIN entry
    class GROUP,CNEW,CLIST,CSHOW cli
    class CFG,FMT,AMAIN app
    class NDIR,NCREATE,NBUILD,NSLUG,NREAD,NCONST domain
    class CLICKLIB,LOGURULIB ext
    class ENVDIR,ENVLOG,FILES,LOGFILE io
```

!!! note "Layering"
    `cli.py` depends on `app.py` and `notes.py`; `app.py` depends on `notes.py` (only for
    the default log location). `notes.py` imports nothing from the package — it is the leaf.

## 2. Entry Points and Arguments

What you can type, which arguments each command takes, and what runs behind it.

```mermaid
---
title: Invocation, Arguments, and Command Behaviour
---
flowchart LR
    subgraph INV["1 · Invocation"]
        direction TB
        I1["uv run secondbrain ..."]
        I2["uv run python -m secondbrain ..."]
        I3["uv run --env-file .env secondbrain ...<br>loads LOG_LEVEL, LOG_FILE, SECONDBRAIN_DIR"]
    end

    subgraph ROOT["2 · Root Group"]
        direction TB
        G["cli()<br>--help provided by Click"]
        GCFG["configure_logging()<br>stderr @ LOG_LEVEL, default INFO<br>file @ DEBUG, never fatal"]
    end

    subgraph ARGS["3 · Subcommands"]
        direction TB
        A1["new TITLE<br>TITLE — required, string"]
        A2["list<br>no arguments"]
        A3["show NUMBER<br>NUMBER — required, int"]
    end

    subgraph FNEW["4a · Behind 'new'"]
        direction TB
        N1["notes_dir()"]
        N2["build_note_path()<br>mkdir -p · slugify · collision suffix -1, -2, ..."]
        N3["write '# TITLE' + ISO timestamp"]
        N4["echo absolute path<br>exit 0"]
    end

    subgraph FLIST["4b · Behind 'list'"]
        direction TB
        L1["notes_dir()"]
        L2{"directory exists?"}
        L3["echo 'Notes directory does not exist'<br>exit 0"]
        L4["glob '*.md' · sort reverse"]
        L5{"any notes?"}
        L6["echo 'No notes found.'<br>exit 0"]
        L7["echo numbered list, newest first<br>exit 0"]
    end

    subgraph FSHOW["4c · Behind 'show'"]
        direction TB
        S1["notes_dir()"]
        S2{"directory exists?"}
        S3{"any notes?"}
        S4{"1 ≤ NUMBER ≤ count?"}
        S5["read_note(files[NUMBER-1])"]
        S6["echo file contents<br>exit 0"]
        SERR["stderr message<br>SystemExit 1"]
    end

    I1 --> G
    I2 --> G
    I3 --> G
    G --> GCFG
    GCFG --> A1
    GCFG --> A2
    GCFG --> A3

    A1 --> N1 --> N2 --> N3 --> N4

    A2 --> L1 --> L2
    L2 -->|"no"| L3
    L2 -->|"yes"| L4 --> L5
    L5 -->|"no"| L6
    L5 -->|"yes"| L7

    A3 --> S1 --> S2
    S2 -->|"no"| SERR
    S2 -->|"yes"| S3
    S3 -->|"no"| SERR
    S3 -->|"yes"| S4
    S4 -->|"no"| SERR
    S4 -->|"yes"| S5 --> S6

    classDef inv fill:#e8eaf6,stroke:#3f51b5,color:#1a1a1a
    classDef root fill:#fff3e0,stroke:#ef6c00,color:#1a1a1a
    classDef arg fill:#e3f2fd,stroke:#1976d2,color:#1a1a1a
    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1a1a1a
    classDef bad fill:#ffebee,stroke:#c62828,color:#1a1a1a

    class I1,I2,I3 inv
    class G,GCFG root
    class A1,A2,A3 arg
    class N4,L7,S6 ok
    class SERR bad
```

!!! warning "Exit codes differ between `list` and `show`"
    `list` treats a missing directory or an empty result as a normal outcome and exits `0`.
    `show` treats the same conditions as errors: it writes to stderr and exits `1`.

## 3. Example User Flow

A first session: capture two notes with the same title, list them, read one back.

```mermaid
---
title: Typical Session — capture, list, read
---
flowchart LR
    subgraph STEP1["Step 1 · Capture"]
        direction TB
        U1["$ secondbrain new 'Café ideas'"]
        P1["slugify → 'cafe-ideas'<br>accents folded to ASCII"]
        F1["created<br>2026-08-02-cafe-ideas.md"]
    end

    subgraph STEP2["Step 2 · Capture again, same title"]
        direction TB
        U2["$ secondbrain new 'Café ideas'"]
        P2["path taken → append counter"]
        F2["created<br>2026-08-02-cafe-ideas-1.md"]
    end

    subgraph STEP3["Step 3 · Review"]
        direction TB
        U3["$ secondbrain list"]
        P3["glob '*.md' · sort reverse"]
        O3["1. 2026-08-02-cafe-ideas.md<br>2. 2026-08-02-cafe-ideas-1.md"]
    end

    subgraph STEP4["Step 4 · Read back"]
        direction TB
        U4["$ secondbrain show 1"]
        P4["index 1 → files[0]"]
        O4["# Café ideas<br><br>2026-08-02T18:29:23"]
    end

    subgraph SIDE["Throughout · Side effects"]
        direction TB
        DISK["~/secondbrain/<br>plain markdown, nothing else"]
        LOGS["~/secondbrain/app.log<br>DEBUG lines for every command"]
    end

    U1 --> P1 --> F1
    F1 --> U2
    U2 --> P2 --> F2
    F2 --> U3
    U3 --> P3 --> O3
    O3 --> U4
    U4 --> P4 --> O4

    F1 -.-> DISK
    F2 -.-> DISK
    P3 -.-> LOGS
    P4 -.-> LOGS

    classDef cmd fill:#e3f2fd,stroke:#1976d2,color:#1a1a1a
    classDef proc fill:#fff3e0,stroke:#ef6c00,color:#1a1a1a
    classDef out fill:#e8f5e9,stroke:#2e7d32,color:#1a1a1a
    classDef side fill:#eceff1,stroke:#546e7a,color:#1a1a1a

    class U1,U2,U3,U4 cmd
    class P1,P2,P3,P4 proc
    class F1,F2,O3,O4 out
    class DISK,LOGS side
```

!!! tip "Why `-1` is listed second"
    Listing is a reverse sort of filenames. `2026-08-02-cafe-ideas.md` sorts after
    `2026-08-02-cafe-ideas-1.md` (`.` > `-`), so the original lands at position 1 and the
    collision-suffixed copy at position 2. The numbers in `list` are positions in that
    sorted view, not stable IDs — they shift as notes are added.
