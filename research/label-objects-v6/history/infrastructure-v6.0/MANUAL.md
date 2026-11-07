# Label attachment manual v6

What drawn thing is this marked writing attached to or placed beside? Choose one.

The left image shows native page context with a magenta box around one inscription.
The right image is a low-resolution thumbnail of the whole page. Classify the
attachment of the marked inscription, not the predominant content of the page.
Do not read, transcribe, translate, or identify the language of the writing.
Do not infer a class from a familiar manuscript page or remembered transcription.
If recognition affects your judgment, disclose it in `recognition`.

| Code | Class |
|---|---|
| STAR | star or star-like mark |
| SUN-MOON | sun, moon, face in a circle |
| PL-WHOLE | whole plant |
| PL-ROOT | root or underground part |
| PL-UPPER | leaf, flower, stem or seed head |
| VESSEL | jar, container, flask |
| FIGURE | human figure |
| WATER | tub, pool, pipe, tube |
| ROSETTE | rosette, circle, wheel |
| ANIMAL | animal on a non-zodiac page |
| OTHER | something else drawn |
| NONE | nothing nearby |
| UNCLEAR | can't tell |

Use the drawing and spatial attachment, not a guess about the inscription's
meaning. A label between equally plausible objects is UNCLEAR. Choose PL-WHOLE
only when the attachment appears to address the whole plant; proximity to a root
alone is insufficient to force PL-ROOT. Use NONE for absent attachment and
UNCLEAR for ambiguous attachment. Do not force certainty to avoid abstaining.

Return exactly one JSON object with keys `class`, `recognition`, `note`.
`class` must be one of the codes above. Keep `note` to visible spatial evidence.

Each model rating must be a fresh, plain API call containing only this manual
and one composite stimulus image. No tools, agents, prior messages, transcription,
candidate matches, analysis, metadata, or another rater's answer may be supplied.
Humans receive only this manual and the anonymous stimulus packet. A and B work
independently. C is asked only after pre-adjudication agreement has been saved.
