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
  }
];
if (typeof module !== "undefined") module.exports = HOUSE_EPISODES;
