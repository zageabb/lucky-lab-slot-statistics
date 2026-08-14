# 8. Visual Design and Asset Brief

## 8.1 Goal

Give participants the broad familiarity of a colourful UK pub/arcade slot genre while making the product unmistakably an original classroom statistics laboratory.

The supplied concept images are original references for mood, hierarchy, colour, polish, and symbol consistency. They are not screenshots to reproduce pixel-for-pixel.

Any figures, dates, labels, reel contents, or chart values visible in a generated concept are illustrative artwork only. The implemented application must calculate and render its own valid values from the active model and ledger.

## 8.2 Required concept references

- `visuals/play-screen-concept.png` — participant play-screen direction.
- `visuals/analysis-dashboard-concept.png` — teacher/statistics direction.
- `visuals/original-symbol-style-board.png` — reel-symbol art direction.

If any reference is missing when Codex begins, continue from this written brief and create original assets. Do not fetch or copy commercial game images from the internet.

## 8.3 Familiar but original visual language

Use:

- deep emerald green and midnight navy as grounding colours;
- warm cream for analytical panels;
- restrained gold trim and highlights;
- a saturated but limited rainbow accent;
- rounded, slightly dimensional reel tiles;
- polished 2D folklore symbols with consistent lighting and outline weight;
- clear large numeric readouts for virtual balance, stake, wagered, and payout;
- modern charts and tables that visually belong to the same application.

Do not use:

- the Rainbow Riches name, wordmark, typeface imitation, leprechaun/host character, exact cabinet/reel frame, bonus titles, feature screen, soundalike audio, copied symbol compositions, or copied paytable;
- fake “almost won” animation or misleading highlighting;
- real currency symbols;
- a layout so close that users could mistake it for the commercial product.

## 8.4 Palette

| Token | Suggested value | Use |
|---|---:|---|
| `--ink-950` | `#071A22` | Main background |
| `--green-900` | `#073B32` | Game header and reel surround |
| `--green-700` | `#0B6B50` | Primary controls |
| `--cream-050` | `#FFF8E7` | Cards and tables |
| `--gold-500` | `#E2B23D` | Borders and selected states |
| `--gold-300` | `#F2D477` | Highlights |
| `--red-600` | `#B93D46` | Loss/error, used sparingly |
| `--blue-500` | `#3188C8` | Informational charts |
| `--violet-500` | `#7B5BC7` | Model comparison |

All colour combinations must meet WCAG AA for normal text. Gold is an accent, not a body-text colour on cream.

## 8.5 Typography

Use a locally bundled, open-licensed, highly legible sans-serif for interface and data. A more decorative serif or rounded display face may be used only for the original Lucky Lab title. Do not imitate a commercial game logo or wordmark.

Numbers in metrics and tables should use tabular figures. Preserve at least 16 px body text at normal desktop zoom.

## 8.6 Symbol asset manifest

Create individual production assets for:

| ID | Subject | Notes |
|---|---|---|
| `clover` | Four-leaf clover | Natural green, distinct silhouette |
| `harp` | Celtic-inspired harp | Original simplified geometry |
| `horseshoe` | Gold horseshoe | Upright, clear open centre |
| `rainbow` | Rainbow and soft cloud | Use the project accent palette |
| `emerald` | Faceted green gem | Strong contrast from clover |
| `crown` | Small gold crown | No royal insignia copied from elsewhere |
| `gold_pot` | Pot with gold pieces | No character attached |
| `wild_star` | Five-point star | Clearly labelled WILD in accessible text outside the raster if text rendering is unreliable |

Preferred delivery is one transparent PNG or WebP per symbol at 512 × 512, plus optimised 128 × 128 and 256 × 256 variants produced with an image-processing script. Keep a lossless master. Provide `alt` text and text labels in HTML; do not depend on raster text.

## 8.7 Reel and motion treatment

- Reel tiles use cream-to-pale-gold surfaces with a strong dark border.
- Winning cells receive a brief gold outline and a non-colour icon/state label.
- Spin animation should be short and optional; the server result already exists before the visual stop sequence.
- Respect reduced-motion preference and offer an instant-results mode.
- Do not extend animation after a loss or create deceptive near-miss timing.
- Sounds are off by default. If later added, use original, neutral sounds and a visible mute control.

## 8.8 Play-screen hierarchy

1. Educational virtual-credit banner.
2. Player/session identity and model version.
3. Balance, cumulative wagered, payout, and observed RTP.
4. Reel board.
5. Stake and Spin action.
6. Neutral result explanation and “how calculated” disclosure.
7. Bankroll mini-chart and recent spins.

The screen can feel game-like, but spend and probability information must never be hidden behind decoration.

## 8.9 Analysis-screen hierarchy

1. Experiment/model selector and seed.
2. Theoretical RTP, observed RTP, hit rate, volatility, and sample size.
3. RTP convergence and bankroll/distribution charts.
4. Confidence interval and exact-versus-estimated label.
5. Model comparison table.
6. Streak and risk-of-ruin analysis.
7. Export and reproducibility details.

## 8.10 Codex implementation instruction

Codex must inspect the reference graphics before creating the interface. It should translate the visual language into maintainable HTML/CSS and original production assets, not embed the full mockup as a background or build a screenshot-shaped page.

Every asset must have clear provenance in `docs/ASSET_PROVENANCE.md`, recording whether it was supplied, generated for this project, code-created, or obtained under an open licence. No commercial game asset may be included.

