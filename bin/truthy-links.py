#!/usr/bin/env python3
"""Extract a stable, sorted list of candidate links from one frozen HTML body."""

from __future__ import annotations

import argparse
import datetime as dt
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() not in {"a", "area", "link"}:
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)
                return


def clean_tsv(s: str) -> str:
    return s.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("body", type=Path)
    p.add_argument("base_url")
    p.add_argument("--same-origin", action="store_true")
    p.add_argument("--max", type=int, default=0, help="0 means no output limit")
    p.add_argument("--run", type=Path, help="Truthy run directory to append trace edges")
    p.add_argument("--artifact-hash", help="hash corresponding to BODY when --run is used")
    args = p.parse_args()

    if bool(args.run) != bool(args.artifact_hash):
        p.error("--run and --artifact-hash must be supplied together")

    parser = LinkParser()
    parser.feed(args.body.read_text(encoding="utf-8", errors="replace"))

    base = urlparse(args.base_url)
    out: set[str] = set()
    for raw in parser.links:
        absolute, _fragment = urldefrag(urljoin(args.base_url, raw.strip()))
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        if args.same_origin and (parsed.scheme, parsed.netloc) != (base.scheme, base.netloc):
            continue
        out.add(absolute)

    links = sorted(out)
    if args.max > 0:
        links = links[: args.max]

    if args.run:
        edges = args.run / "edges.tsv"
        trace = args.run / "trace.tsv"
        if not edges.exists() or not trace.exists():
            p.error(f"not a Truthy run: {args.run}")
        with edges.open("a", encoding="utf-8") as f:
            for link in links:
                f.write(
                    f"artifact\t{clean_tsv(args.artifact_hash)}\tlinks-to\turl\t"
                    f"{clean_tsv(link)}\t\n"
                )
        utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with trace.open("a", encoding="utf-8") as f:
            f.write(
                f"{utc}\tlinks\t{clean_tsv(args.artifact_hash)}\t"
                f"count={len(links)} base={clean_tsv(args.base_url)}\n"
            )

    for link in links:
        print(link)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
