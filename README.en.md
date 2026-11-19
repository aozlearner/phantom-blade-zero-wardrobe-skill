# Phantom Blade Zero Wardrobe Skill

[简体中文](README.md) · [Skill entry point](skills/pbz-wardrobe-mods/SKILL.md) · [MIT License](LICENSE)

An AI agent skill for creating and repairing **Phantom Blade Zero (影之刃零 / 影之刃0 / PBZ / ProjectPBZ)** character mods as standalone wardrobe outfits while retaining the protagonist's movement, controls, and original outfits.

## What it covers

- Animation binding, body/head following, proportions, weapon grip, cloth, hair, and accessories.
- Outfit-scoped combat voices: prefer the character's own category; use Mu Xiaokui for missing categories under the documented project policy. Keep original-outfit voices and story dialogue unchanged.
- Hair-material protection and diagnosis of red hair after weapon swaps or teleport/dash effects.
- Unique outfit/provider IDs, one merged appearance table, ownership and cleanup during outfit changes.
- Native portraits or custom PNG thumbnails, with separate file, resource, assembly, and gameplay verification.
- A read-only Python audit helper for baseline drift, missing staged files, and unmanaged collisions.

## Install

Copy the entire `skills/pbz-wardrobe-mods` folder into your agent's supported skill directory. Keep the `references`, `scripts`, and `agents` subfolders. If a skill with the same name already exists, compare and back it up before replacement.

For an agent with GitHub skill installation support:

```text
Repository: https://github.com/aozlearner/phantom-blade-zero-wardrobe-skill
Skill path: skills/pbz-wardrobe-mods
```

Example request:

```text
Use $pbz-wardrobe-mods to adapt this character into a standalone wardrobe outfit.
Preserve the original outfits and working mods, prepare and validate the candidate,
and wait until I save and exit before writing to the game.
```

The detailed engineering references are primarily in Chinese. Agents can also read `SKILL.md` directly; no particular connector is required.

## Requirements and limits

You need a legally accessible local game, the current adaptation source/workspace, relevant loaders, and compatible asset tools. **This is not a downloadable character pack or a one-click character generator.** It contains no game models, audio, saves, credentials, private workspace paths, or game binaries.

The audit helper requires Python 3.10+ and only the standard library. Its baseline is a JSON array of `relative` and `sha256` records; the stage must contain the full set of managed files. Run:

```powershell
python skills/pbz-wardrobe-mods/scripts/audit_stage.py --baseline baseline.json --game "D:\Games\PBZ" --stage "D:\ModWork\candidate" --report "D:\ModWork\audit.json"
```

Exit codes: 0 = file baseline audit passed, 1 = blockers, 2 = invalid input. The helper does not install/uninstall files or validate rigs and gameplay. It is intended for addition/repair staging, not removal plans.

## Separate deployment project

This repository documents how to create and repair wardrobe mods. [Phantom Blade Zero Modpack Deploy](https://github.com/aozlearner/phantom-blade-zero-modpack-deploy) installs, backs up, and rolls back a specific recorded baseline. Neither project requires the other at runtime.

## Tests and license

```text
python -m unittest discover -s tests -v
```

MIT covers this repository's documentation and audit code, not game assets or third-party mods. This is an independent community project, not affiliated with the game's developer or publisher.
