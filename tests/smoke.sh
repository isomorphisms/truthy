#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/truthy-test.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM

sh "$root/bin/truthy-new" "$work/run" 'fixture question'
sh "$root/bin/truthy-search-log" "$work/run" fixture 'alpha query' 'https://example.org/alpha'

expected="$work/expected"
actual="$work/actual"
printf '%s\n' \
  'https://example.org/alpha' \
  'https://example.org/beta' > "$expected"
python3 "$root/bin/truthy-links.py" "$root/tests/fixtures/page.html" 'https://example.org/start' > "$actual"
cmp "$expected" "$actual"

printf 'prompt body\n' | sh "$root/bin/truthy-model" "$work/run" fixture-model fixture-rev -- cat > "$work/model.out"
printf 'prompt body\n' > "$work/model.expected"
cmp "$work/model.expected" "$work/model.out"

grep -q 'fixture question' "$work/run/question.txt"
grep -q 'alpha query' "$work/run/searches.tsv"
grep -q 'fixture-model' "$work/run/trace.tsv"

echo 'truthy smoke: pass'
