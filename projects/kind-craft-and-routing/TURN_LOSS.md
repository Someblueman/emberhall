# Would one family lose its last turn?

A reader can follow one proposed change to a task offer through the 32-start work rotation. The command shows the first window in which that change would erase the receiving family's last turn. Each offer is checked separately against the house's actual sequence of starts.

From the repository root, supply a covering status and consecutive journal pages containing proposal 20915. The trial guide explains how to obtain those files from an assigned room. [Reading the trial](README.md)

```sh
python3 projects/kind-craft-and-routing/turn_loss.py \
  --status /tmp/craft-status.json /tmp/craft-page-01.json /tmp/craft-page-02.json
```

Add `--json` for the verified receipt numbers, uncovered work starts, offer, comparison and first loss. The last-turn question applies when the existing earlier-outcome comparison prefers a different family within the recorded tie. [How preferences are computed](TIE_REPLAY.md)

## Reading a result

Suppose a family has two starts in the last 32 and its older start leaves the window tomorrow. Giving its newer start to another family would leave it with one turn today and zero tomorrow. Checking just the day of the offer misses that loss.

The reader rebuilds work starts from the verified status, compares admissions inside the supplied pages with their journal entries, and checks each work assignment's recorded count for all four families. The 32-start window follows the controller's work-lane definition. Helpers, Explorers and review-lane starts each have their own treatment outside this count. A work start that later exhausts quota took a turn in the rotation. The separate performance comparison excludes that exit.

For each different preference, the reader substitutes that one family and holds every later recorded start fixed. Only the window ending at the offer and the following 31 work windows can contain it. A lost turn identifies the first affected window, its endpoints and the controller receipt. A missing receipt, a change in the recorded choice modules, or the end of the supplied pages can cut follow-up short. A disagreement with a recorded count stops the command and names the receipt.

This measures one necessary fairness condition. A family can retain one turn and still have less than its share. The comparison also depends on holding later admissions fixed. Evidence about capacity, subsequent scheduling decisions and matched work outcomes would be needed to justify changing live routing.

## A recorded run

A fixed-channel page covering 20915–21114 and status 21691 gave this result on 19 November.

```text
Through 21114 | installation not observed | routing weight 0
5 work receipts matched their prior turns | 0 starts without a comparable receipt
0 enrolled offers
```

At receipt 20989 the previous 32 work starts were 26 Codex, four agy and two OpenCode. At 20998 the next window had 27 Codex, three agy and two OpenCode. Muse had zero in both. These historical readings check the reconstruction. The live twenty-task trial begins with the installation described in the trial guide.
