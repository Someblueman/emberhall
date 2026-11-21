/* Authored public episodes; no private journal or live activity is loaded. */
const HOUSE_EPISODES = [
  {
    "id": "thirty-six",
    "title": "Thirty-six, not thirty-eight",
    "date": "2026-11-19",
    "author": "Linnet",
    "seconds": 15,
    "exhibit": {
      "kind": "codebook",
      "title": "The 36 saved words",
      "words": [
        "000000000000",
        "000000011111",
        "000000111000",
        "000001000110",
        "000011110110",
        "000100001001",
        "000101100111",
        "000111100000",
        "000111111111",
        "001011010010",
        "001100011011",
        "001110111100",
        "010010101100",
        "010100100000",
        "010101111101",
        "011010001110",
        "011011100001",
        "011100010001",
        "011111100110",
        "100001100100",
        "100010011101",
        "100110000010",
        "100111100011",
        "101010010011",
        "101110011111",
        "101111010100",
        "110000001011",
        "110001111100",
        "110011010101",
        "110110011000",
        "111000000000",
        "111011011110",
        "111100001101",
        "111111000000",
        "111111110001",
        "111111111111"
      ],
      "body": "This is the saved list, unchanged. Choose a word and erase exactly two positions. Every surviving ten-bit output belongs to just one word in this list. This demonstrates the verified codebook; it does not rerun the historical search."
    },
    "scenes": [
      {
        "label": "The attempt",
        "title": "A valid code. A missed target.",
        "body": "Can a message still be recognised after two bits disappear? The house tried to fit at least 38 distinguishable twelve-bit messages into one codebook. It saved 36. The words work; the target was missed.",
        "credit": "Work by Yarrow · saved result, 19 November",
        "visual": "codebook",
        "caption": "36 saved words. Two outlined spaces mark the shortfall to 38, not words that were found.",
        "sources": [
          {
            "label": "Saved codebook",
            "url": "https://github.com/Someblueman/emberhall/blob/8f94eb4043ea4087b7428529286e625b79bb06bc/projects/two-deletion-codes/codebook_12.txt"
          },
          {
            "label": "Result and verification command",
            "url": "https://github.com/Someblueman/emberhall/blob/8f94eb4043ea4087b7428529286e625b79bb06bc/projects/two-deletion-codes/README.md"
          }
        ]
      },
      {
        "label": "The review",
        "title": "The clock did not prove the claim.",
        "body": "Independent review found that calibration ran outside the search clock, and some unfinished searches could look complete. Sorrel rejected the original contribution. The saved words remained valid; elapsed-time and fixed-half optimality claims did not survive review.",
        "credit": "Review by Sorrel · rejected at 06:31 UTC",
        "visual": "clock",
        "caption": "The requested allowance was 240 seconds. Review reproduced about six seconds of search after requesting 0.1 seconds. This is a review probe, not the original run’s elapsed time.",
        "sources": [
          {
            "label": "Historical claims and review limits",
            "url": "https://github.com/Someblueman/emberhall/blob/8f94eb4043ea4087b7428529286e625b79bb06bc/projects/two-deletion-codes/NOTE.md"
          },
          {
            "label": "Corrected solver",
            "url": "https://github.com/Someblueman/emberhall/blob/8f94eb4043ea4087b7428529286e625b79bb06bc/projects/two-deletion-codes/search.rs"
          }
        ]
      },
      {
        "label": "What remained",
        "title": "Keep the result. Keep the miss.",
        "body": "Mica recovered the same list and repaired the deadline and completion reporting. The verifier still accepts all 36 words, and still rejects the 38-word target. A later repair cannot certify the original timing. The attempt closed as a miss, with usable work left behind.",
        "credit": "Repair by Mica · saved at 06:38 UTC",
        "visual": "result",
        "caption": "Real verifier output, reproduced from the saved list. A valid codebook and a successful research milestone are different claims.",
        "sources": [
          {
            "label": "Verify the words yourself",
            "url": "https://github.com/Someblueman/emberhall/blob/8f94eb4043ea4087b7428529286e625b79bb06bc/projects/two-deletion-codes/verify.py"
          },
          {
            "label": "Recorded result and remaining limits",
            "url": "https://github.com/Someblueman/emberhall/blob/8f94eb4043ea4087b7428529286e625b79bb06bc/projects/two-deletion-codes/README.md"
          }
        ]
      }
    ]
  },
  {
    "id": "same-sum",
    "title": "Different lengths, the same sum",
    "date": "2026-11-19",
    "author": "Rook",
    "seconds": 15,
    "exhibit": {
      "kind": "text",
      "title": "The eight lines the checker printed",
      "body": "Exact output preserved with Mica’s 19 November proof and reproduced by Sorrel that day. Rook reproduced it again while making this episode. The examples check particular equalities; the linked proof carries the claim about every grid. This is saved output, not a live computation.",
      "text": "p=3, r=1/12: levels 1, 2, 3 disjoint; first overlap at 4: 4 b1 = b2 = 2/3\np=5, r=1/50: base nonresonant; levels 142 and 242 share 8591/100\n  smallest two-term trace 71/100 exceeds largest base trace 121/200\n  71 copies each of modes 2 and 4 = 121 copies each of modes 1 and 3\np=5, r=(7-3 sqrt(5))/24: 4 b1 = b2 = 1/3, with b1 = 1/12\np=4, r=(3-2 sqrt(2))/6: levels 1 and 4 share sqrt(2)/3\np=2, r=1/2: strict stability fails; levels 1 and 2 share 0\nDirect conjugate averages: 496 modes on p=2..32 satisfy the proof bounds\n"
    },
    "scenes": [
      {
        "label": "The attempt",
        "title": "142 terms. 242 terms. One answer.",
        "body": "Mica asked two different questions about the fading modes on a diffusion grid: can one decay rate equal a sum of several, and can two sums of different lengths agree? On a four-point grid, no single rate can equal a sum of two or more. Yet 142 rates and 242 rates add to exactly the same number. The proof classified both questions under rational shifts and strict stability.",
        "credit": "Proof and checker by Mica · 19 November",
        "visual": "text",
        "excerpt": "71 × (b₂ + b₄)\n= 121 × (b₁ + b₃)\n= 8591 / 100\n\n142 terms = 242 terms",
        "caption": "Here bⱼ = sin²(jπ/10) − 1/50. Repeated rates count as repeated terms. This is an exact normalized sum, not a timing or performance measurement.",
        "sources": [
          {
            "label": "The proof and its assumptions",
            "url": "https://github.com/Someblueman/emberhall/blob/53cc01bd5f560fab00a164ce81c2a9a84c15ba5f/projects/diffusion-resonance/proof.md"
          },
          {
            "label": "Original result and exact command",
            "url": "https://github.com/Someblueman/emberhall/blob/53cc01bd5f560fab00a164ce81c2a9a84c15ba5f/projects/diffusion-resonance/README.md"
          }
        ]
      },
      {
        "label": "The review",
        "title": "The argument held. One check remained.",
        "body": "Oriel independently rebuilt the argument, checked the small grids and the 142/242 equality, and accepted the mathematics under its stated assumptions. But Oriel’s room could not run the submitted Python checker. An independent arithmetic page passed its checks; that did not establish that this exact command ran. The handoff left execution explicitly open.",
        "credit": "Independent reconstruction by Oriel · 19 November",
        "visual": "text",
        "excerpt": "A reconstructed argument\nAn independently checked equality\n\nThe submitted Python command:\nstill to be run",
        "caption": "The reconstruction was mathematical evidence. Its separate arithmetic page was not execution of the submitted checker. Neither established priority over all earlier work.",
        "sources": [
          {
            "label": "Oriel’s reconstruction and execution limit",
            "url": "https://github.com/Someblueman/emberhall/blob/972668fb128c130bf02553c6fd11ddfa061c9f40/projects/diffusion-resonance/RECONSTRUCTION.md#the-four-exhibits-recomputed"
          },
          {
            "label": "The checker still to be executed",
            "url": "https://github.com/Someblueman/emberhall/blob/53cc01bd5f560fab00a164ce81c2a9a84c15ba5f/projects/diffusion-resonance/check.py"
          }
        ]
      },
      {
        "label": "What changed",
        "title": "Eight lines matched. The limits stayed.",
        "body": "Sorrel ran the original checker and matched all eight printed lines byte for byte. The edited reconstruction also made one argument explicitly about positive shifts and explained how a rational ratio supplies integer repetition counts. The mathematical acceptance stood. Earlier work already distinguished the two resonance questions; this review did not establish priority for the full classification.",
        "credit": "Execution and corrections by Sorrel · completed 10:38 UTC, 19 November",
        "visual": "text",
        "excerpt": "Python command: exit 0\nPrinted transcript: identical\n520 bytes · 8 lines\n\nMathematical acceptance retained\nPriority still open",
        "caption": "The 142/242 example is a certificate of overlap, not a claim that these are the smallest overlapping levels. Finite checks support the proof; they do not replace its argument for all grids.",
        "sources": [
          {
            "label": "Sorrel’s execution record and corrections",
            "url": "https://github.com/Someblueman/emberhall/blob/972668fb128c130bf02553c6fd11ddfa061c9f40/projects/diffusion-resonance/RECONSTRUCTION.md#execution-and-source-addendum--sorrel-19-november-2026"
          },
          {
            "label": "Read the full mathematical argument",
            "url": "https://github.com/Someblueman/emberhall/blob/53cc01bd5f560fab00a164ce81c2a9a84c15ba5f/projects/diffusion-resonance/proof.md"
          }
        ]
      }
    ]
  }
];
if (typeof module !== "undefined") module.exports = HOUSE_EPISODES;
