[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/mutroll/makefun-poster-nimbara/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/mutroll/makefun-poster-nimbara/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

# NIMBARA — The Poster for a Place That Isn't There

A travel poster for **Nimbara**, an invented place: a floating glass-dune
observatory city drifting above a sea of clouds, where the sun sets twice.
Its landmark is the Sunspire — one tall mirrored tower, ringed in gold,
rising from the main dune. Warm lights wake along the dune's rim at dusk
while smaller floating isles drift nearby.

## How it works

`main.py` is pure Python 3 standard library (no network, no third-party
packages, fully deterministic). It draws the poster procedurally — sky
gradient, two suns with soft glows, layered cloud bands, floating islands,
the Sunspire and its ring — and renders the place name in a hand-rolled
5×7 bitmap font scaled up. It writes its own PNG (zlib + struct) to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`).

## Run

```sh
python3 main.py
```

Output: a 1024×1024 PNG, well under the 1 MiB limit, byte-identical on
every run.

## License

MIT — see `LICENSE`.
